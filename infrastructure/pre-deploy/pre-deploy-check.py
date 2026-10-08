#!/usr/bin/env python3
"""Pre-deploy check: reproduz localmente, de forma agnostica, os gates que a esteira executa.

Filosofia: descobrir em runtime (build, pipeline, IaC, docker) -> reproduzir o que for
reproduzivel -> classificar achado vs bloqueio -> relatar. Nao altera o repositorio.

Uso tipico:
    python infrastructure/pre-deploy/pre-deploy-check.py --repo <caminho>
    python infrastructure/pre-deploy/pre-deploy-check.py --repo <caminho> --skip-build
    python infrastructure/pre-deploy/pre-deploy-check.py --repo <caminho> --json out.json

Somente leitura sobre o repositorio. Escreve apenas no diretorio de saida informado.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------- infraestrutura


class Step:
    """Coleta o resultado de um passo para o relatorio final."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.status = "NAO_EXECUTADO"
        self.evidence: list[str] = []
        self.findings: list[dict] = []
        self.note = ""

    def ok(self, evidence: str = "") -> None:
        self.status = "OK"
        if evidence:
            self.evidence.append(evidence)

    def fail(self, note: str) -> None:
        self.status = "FALHOU"
        self.note = note

    def skip(self, note: str) -> None:
        self.status = "NAO_VERIFICADO"
        self.note = note


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 900) -> tuple[int, str]:
    """Executa comando e devolve (exit_code, saida_combinada). Nunca levanta por exit != 0."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError:
        return 127, f"comando nao encontrado: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timeout apos {timeout}s: {' '.join(cmd[:3])}"


def docker_ok() -> tuple[bool, str]:
    if not shutil.which("docker"):
        return False, "docker nao encontrado no PATH"
    code, out = run(["docker", "info", "--format", "{{.ServerVersion}}"], timeout=60)
    if code != 0:
        return False, "daemon docker inacessivel"
    return True, out.strip().splitlines()[-1] if out.strip() else "disponivel"


def mount_path(p: Path) -> str:
    """Caminho para montagem no docker. Mantem estilo Windows quando aplicavel."""
    s = str(p.resolve())
    return s.replace("\\", "/")


def _rel(raw: str, repo: Path) -> str:
    """Normaliza o caminho devolvido pelo scanner para algo legivel e relativo ao repo."""
    text = raw.replace("\\", "/")
    for marker in ("/input/", "/input"):
        if marker in text:
            text = text.split(marker, 1)[-1]
    text = text.lstrip("./")
    for part in sorted(SKIP_DIRS):
        while text.startswith(f"{part}/"):
            text = text[len(part) + 1 :]
    name = repo.name
    if text.startswith(name + "/"):
        text = text[len(name) + 1 :]
    return text or raw


# ---------------------------------------------------------------- descoberta

BUILD_MARKERS = [
    ("maven", "pom.xml"),
    ("gradle", "build.gradle"),
    ("gradle-kts", "build.gradle.kts"),
    ("npm", "package.json"),
    ("go", "go.mod"),
    ("rust", "Cargo.toml"),
    ("python", "pyproject.toml"),
    ("dotnet", "*.csproj"),
]

PIPELINE_MARKERS = [
    "Jenkinsfile",
    "Jenkinsfile_CI",
    ".gitlab-ci.yml",
    ".github/workflows",
    "azure-pipelines.yml",
    ".circleci/config.yml",
]

IAC_SUFFIXES = {
    ".yaml",
    ".yml",
    ".json",
    ".tf",
    ".tfvars",
    ".template",
    ".dockerfile",
}

IAC_NAMES = {"Dockerfile", "docker-compose.yml", "docker-compose.yaml", "Chart.yaml"}

# Arquivos que o scanner de IaC NAO cobre por causa da extensao, mas que versionamos
# e que frequentemente guardam segredo. Ausencia de achado neles nao prova nada.
OUT_OF_SCOPE_SECRET_FILES = re.compile(
    r"(^\.env($|\.)|(^|/)\.env($|\.)|(^|/)\.env\.example$|(^|/)\.envrc$)", re.IGNORECASE
)

SKIP_DIRS = {
    ".git",
    "target",
    "build",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "out",
    ".gradle",
    "__pycache__",
    ".venv",
    "venv",
    ".terraform",
}


def discover(repo: Path) -> dict:
    build = []
    for kind, marker in BUILD_MARKERS:
        if marker.startswith("*"):
            if list(repo.glob(marker)):
                build.append(kind)
        elif (repo / marker).exists():
            build.append(kind)

    pipeline = [m for m in PIPELINE_MARKERS if (repo / m).exists()]

    iac = []
    for path in repo.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in IAC_NAMES or path.suffix.lower() in IAC_SUFFIXES:
            iac.append(str(path.relative_to(repo)).replace("\\", "/"))

    return {
        "build": build,
        "pipeline": pipeline,
        "iac": sorted(iac),
        "versioned": git_tracked(repo),
    }


def git_tracked(repo: Path) -> list[str]:
    code, out = run(["git", "ls-files"], cwd=repo, timeout=120)
    if code != 0:
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


# ---------------------------------------------------------------- passo: IaC


def step_iac(repo: Path, out_dir: Path, docker: bool, docker_ver: str) -> Step:
    st = Step("IaC (engine do scanner da esteira)")
    if not docker:
        st.skip(f"docker indisponivel ({docker_ver}); IaC nao pode ser reproduzido")
        return st

    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{mount_path(repo)}:/input:ro",
        "-v",
        f"{mount_path(out_dir)}:/output",
        "checkmarx/kics:latest",
        "scan",
        "-p",
        "/input",
        "--exclude-paths",
        ",".join(f"/input/{d}" for d in sorted(SKIP_DIRS)),
        "--report-formats",
        "json",
        "-o",
        "/output",
    ]
    code, out = run(cmd, timeout=1200)
    report = out_dir / "results.json"
    if not report.exists():
        st.fail(f"scanner nao gerou relatorio (exit {code}). Trecho: {out.strip()[-300:]}")
        return st

    data = json.loads(report.read_text(encoding="utf-8"))
    sev_count: dict[str, int] = {}
    for query in data.get("queries", []):
        sev = query.get("severity", "?")
        files = query.get("files", [])
        sev_count[sev] = sev_count.get(sev, 0) + len(files)
        if sev.upper() in {"HIGH", "CRITICAL"}:
            for f in files:
                line = f.get("line")
                line = line if isinstance(line, list) else [line]
                st.findings.append(
                    {
                        "severity": sev.upper(),
                        "query": query.get("query_name"),
                        "file": _rel(f.get("file_name", ""), repo),
                        "lines": line,
                    }
                )
    st.evidence.append(f"contagem por severidade: {sev_count}")
    if st.findings:
        st.status = "ACHADOS"
    else:
        st.ok("nenhum achado HIGH/CRITICAL de IaC")
    return st


# ---------------------------------------------------------------- passo: segredos


SECRET_LINE = re.compile(
    r"""(?ix)
    (secret|passwd|password|token|api[_-]?key|apikey|credential|client[_-]?secret|private[_-]?key)
    \s*[:=]\s*
    ["']?([^\s"'#]{8,})
    """,
)

PLACEHOLDER = re.compile(
    r"(?i)^(\$\{|\$\(|%|<|changeme|change_me|placeholder|example|dummy|fake|your[_-]|xxx|todo|none|null)",
)

# Marcadores de valor claramente local/nao-producao. Reduz falso-positivo em
# application-local.yaml e afins, onde o valor e proposital e nao aponta para servico real.
LOCAL_MARKERS = re.compile(
    r"(?i)^(local|dev|test|teste|mock|sample|demo|client\d+|user\d+|admin|root|pass|pswd|123|abc)"
)

# Arquivos cujo proposito declarado e ambiente local/desenvolvimento.
LOCAL_FILE = re.compile(
    r"(?i)(application-local\.|application-local-|-local\.ya?ml$|\.local\.ya?ml$|localstack)"
)

# Valores que parecem credencial real: UUID, base64 longo, ou string aleatoria longa.
LOOKS_LIKE_REAL_SECRET = re.compile(
    r"(?i)^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"  # uuid
    r"|[A-Za-z0-9+/]{32,}={0,2}$"  # base64/hex longo
    r")"
)


def _classify_value(value: str, rel: str) -> tuple[str, str]:
    """Devolve (categoria, motivo). categoria: real | local | placeholder."""
    if PLACEHOLDER.match(value):
        return "placeholder", "valor com marcador de placeholder"
    if LOCAL_MARKERS.match(value):
        return "local", "valor com marcador local/dev/mock"
    if LOOKS_LIKE_REAL_SECRET.match(value):
        return "real", "formato de credencial real (uuid/token longo)"
    if LOCAL_FILE.search(rel):
        return "local", "arquivo de ambiente local"
    return "local", "formato nao conclusivo (revisar)"


def step_secrets_out_of_scope(repo: Path, tracked: list[str]) -> Step:
    """Verifica segredo em arquivos versionados, incluindo os que o scanner de IaC nao varre.

    Este passo existe porque o scanner de IaC cobre apenas extensoes reconhecidas
    (`.yaml`, `.json`, `.tf`...): `.env` e `.env.example` ficam FORA do escopo, e a
    ausencia de achado neles nao prova nada.
    """
    st = Step("Segredos em arquivos versionados")
    st.evidence.append(
        "nota: scanner de IaC cobre apenas extensoes reconhecidas; .env e .env.example nao entram"
    )

    candidates = [t for t in tracked if OUT_OF_SCOPE_SECRET_FILES.search(t)]
    other = [
        t
        for t in tracked
        if not OUT_OF_SCOPE_SECRET_FILES.search(t)
        and Path(t).suffix.lower() in IAC_SUFFIXES
        and not Path(t).name.startswith(".")
    ]

    if candidates:
        st.evidence.append(f"arquivos .env* versionados: {len(candidates)}")
    else:
        st.evidence.append("nenhum arquivo .env* versionado")

    scanned = 0
    for rel in candidates + other:
        path = repo / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        for idx, line in enumerate(text.splitlines(), start=1):
            m = SECRET_LINE.search(line)
            if not m:
                continue
            value = m.group(2)
            category, reason = _classify_value(value, rel)
            if category == "placeholder":
                continue
            masked = value[:4] + "***" + value[-2:] if len(value) > 8 else "***"
            weight = "HIGH" if category == "real" else "INFO"
            st.findings.append(
                {
                    "severity": weight,
                    "file": rel,
                    "line": idx,
                    "masked": masked,
                    "category": category,
                    "reason": reason,
                    "out_of_scope": bool(OUT_OF_SCOPE_SECRET_FILES.search(rel)),
                }
            )

    high = [f for f in st.findings if f["severity"] == "HIGH"]
    st.evidence.append(f"arquivos analisados: {scanned}")
    st.evidence.append(f"possiveis credenciais reais: {len(high)}")
    st.status = "ACHADOS" if st.findings else "OK"
    if not st.findings:
        st.ok("nenhum segredo literal relevante")
    return st


# ---------------------------------------------------------------- passo: dependencias


def step_deps(repo: Path, out_dir: Path, build: list[str]) -> Step:
    st = Step("Dependencias (SCA)")

    if "maven" in build and (repo / "pom.xml").exists():
        mvn = "mvnw.cmd" if os.name == "nt" and (repo / "mvnw.cmd").exists() else None
        if mvn is None and (repo / "mvnw").exists():
            mvn = "mvnw"
        exe = str(repo / mvn) if mvn else shutil.which("mvn")
        if not exe:
            st.skip("maven nao disponivel (nem wrapper)")
            return st
        out_file = out_dir / "deps.txt"
        code, out = run(
            [exe, "-o", "-q", "dependency:list", f"-DoutputFile={out_file}", "-DincludeScope=runtime"],
            cwd=repo,
            timeout=900,
        )
        if not out_file.exists():
            st.skip(f"nao foi possivel resolver dependencias (exit {code})")
            return st
        lines = [
            ln.strip()
            for ln in out_file.read_text(encoding="utf-8", errors="replace").splitlines()
            if ln.strip() and not ln.startswith((" ", "The following"))
        ]
        st.evidence.append(f"dependencias resolvidas: {len(lines)}")
        st.evidence.append(
            "cruzamento com base de advisories: execute manualmente ou veja "
            "references/pre-deploy/sca-remediation.md"
        )
        st.ok("lista de dependencias gerada")
        return st

    if "npm" in build:
        code, out = run(["npm", "audit", "--json"], cwd=repo, timeout=900)
        st.evidence.append(f"npm audit exit={code}")
        report = out_dir / "npm-audit.json"
        report.write_text(out, encoding="utf-8")
        st.ok(f"npm audit gravado em {report}")
        return st

    st.skip("build nao reconhecido para auditoria de dependencias")
    return st


# ---------------------------------------------------------------- passo: build


def step_build(repo: Path, build: list[str]) -> Step:
    st = Step("Build + testes")
    if not build:
        st.skip("build nao reconhecido")
        return st

    if "maven" in build:
        exe = str(repo / ("mvnw.cmd" if os.name == "nt" else "mvnw")) if (repo / "mvnw").exists() else shutil.which("mvn")
        if not exe:
            st.skip("maven nao disponivel")
            return st
        code, out = run([exe, "-o", "verify"], cwd=repo, timeout=3600)
    elif "gradle" in build or "gradle-kts" in build:
        exe = str(repo / ("gradlew.bat" if os.name == "nt" else "gradlew")) if (repo / "gradlew").exists() else shutil.which("gradle")
        if not exe:
            st.skip("gradle nao disponivel")
            return st
        code, out = run([exe, "check"], cwd=repo, timeout=3600)
    elif "npm" in build:
        code, out = run(["npm", "test", "--", "--run"], cwd=repo, timeout=1800)
    else:
        st.skip(f"sem comando padrao para: {build}")
        return st

    tests = re.search(r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+)", out)
    if tests:
        st.evidence.append(
            f"tests: {tests.group(1)} run, {tests.group(2)} failures, {tests.group(3)} errors"
        )
    build_ok = "BUILD SUCCESS" in out or (code == 0 and "FAIL" not in out)
    if build_ok:
        st.ok(f"build exit={code}")
    else:
        st.fail(f"build exit={code}: {out.strip()[-400:]}")
    return st


# ---------------------------------------------------------------- relatorio


def render(repo: Path, disc: dict, steps: list[Step], docker: bool, docker_ver: str) -> str:
    lines: list[str] = []
    add = lines.append
    add("=" * 78)
    add("PRE-DEPLOY CHECK")
    add("=" * 78)
    add(f"REPO      : {repo}")
    add(f"DATA      : {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    add("")
    add("DESCOBERTA")
    add(f"  build     : {', '.join(disc['build']) or 'nao reconhecido'}")
    add(f"  pipeline  : {', '.join(disc['pipeline']) or 'nao encontrada'}")
    add(f"  docker    : {'disponivel (' + docker_ver + ')' if docker else 'indisponivel (' + docker_ver + ')'}")
    add(f"  arquivos IaC: {len(disc['iac'])}")
    add("")

    for st in steps:
        add("-" * 78)
        add(f"PASSO: {st.name}")
        add(f"STATUS: {st.status}")
        for ev in st.evidence:
            add(f"  - {ev}")
        if st.note:
            add(f"  ! {st.note}")
        for f in st.findings[:25]:
            if "query" in f:
                add(f"  > [{f['severity']}] {f['query']} :: {f['file']} linha {f['lines']}")
            else:
                scope = "fora-do-escopo" if f.get("out_of_scope") else "no-escopo"
                add(
                    f"  > [{f['severity']}] {f['file']}:{f['line']} valor={f['masked']} "
                    f"({scope}, {f.get('reason','')})"
                )
        if len(st.findings) > 25:
            add(f"  > ... +{len(st.findings) - 25} achados (ver JSON)")
        add("")

    blocking = [s for s in steps if s.status == "FALHOU" or any(
        f.get("severity") in {"HIGH", "CRITICAL"} for f in s.findings
    )]
    unverified = [s for s in steps if s.status == "NAO_VERIFICADO"]
    findings_only = [s for s in steps if s.status == "ACHADOS" and s not in blocking]

    if blocking:
        verdict = "BLOQUEIA (possivelmente)"
    elif unverified:
        verdict = "PARCIAL"
    else:
        verdict = "OK"

    add("=" * 78)
    add(f"VEREDITO: {verdict}")
    add("=" * 78)
    if blocking:
        add("Achados HIGH/CRITICAL ou falha de build. Confirme na esteira qual gate tem break build:")
        for s in blocking:
            add(f"  - {s.name} ({s.status})")
    if findings_only:
        add("Achados de severidade menor (normalmente nao bloqueiam):")
        for s in findings_only:
            add(f"  - {s.name}")
    if unverified:
        add("NAO VERIFICADO localmente (nao tratar como sucesso):")
        for s in unverified:
            add(f"  - {s.name}: {s.note}")
    add("")
    add("LEMBRETE: ausencia de achado em arquivo fora do escopo do scanner nao prova nada.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Verificacao pre-deploy agnostica")
    ap.add_argument("--repo", default=".", help="caminho do repositorio (default: cwd)")
    ap.add_argument("--out-dir", default=None, help="diretorio de saida dos relatorios")
    ap.add_argument("--json", default=None, help="grava relatorio JSON consolidado")
    ap.add_argument("--skip-docker", action="store_true", help="nao usar docker")
    ap.add_argument("--skip-build", action="store_true", help="nao rodar build/testes")
    ap.add_argument("--skip-deps", action="store_true", help="nao analisar dependencias")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"repositorio invalido: {repo}", file=sys.stderr)
        return 2

    ephemeral_out = args.out_dir is None
    out_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir
        else Path(tempfile.mkdtemp(prefix="pre-deploy-"))
    )
    disc = discover(repo)

    ok_docker, docker_ver = (False, "desabilitado") if args.skip_docker else docker_ok()

    steps = [
        step_iac(repo, out_dir, ok_docker, docker_ver),
        step_secrets_out_of_scope(repo, disc["versioned"]),
    ]
    if not args.skip_deps:
        steps.append(step_deps(repo, out_dir, disc["build"]))
    if not args.skip_build:
        steps.append(step_build(repo, disc["build"]))

    report = render(repo, disc, steps, ok_docker, docker_ver)
    print(report)

    if args.json:
        payload = {
            "repo": str(repo),
            "discovery": disc,
            "docker": {"available": ok_docker, "version": docker_ver},
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "evidence": s.evidence,
                    "note": s.note,
                    "findings": s.findings,
                }
                for s in steps
            ],
        }
        Path(args.json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    blocking = any(
        s.status == "FALHOU" or any(f.get("severity") in {"HIGH", "CRITICAL"} for f in s.findings)
        for s in steps
    )
    if ephemeral_out:
        shutil.rmtree(out_dir, ignore_errors=True)
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
