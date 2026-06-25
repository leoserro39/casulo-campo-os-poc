#!/usr/bin/env python3
import argparse
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(value):
    value = unicodedata.normalize("NFKD", (value or "").lower())
    return "".join(ch for ch in value if not unicodedata.combining(ch)).strip()


def run_script(script, ask):
    cmd = [sys.executable, str(ROOT / "04_scripts" / script), "--ask", ask]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    if proc.stdout.strip():
        print(proc.stdout.rstrip())
    if proc.stderr.strip():
        print(proc.stderr.rstrip(), file=sys.stderr)
    return proc.returncode


def is_proposal_request(query):
    q = norm(query)
    triggers = [
        "propor",
        "proposta",
        "sugira",
        "sugerir",
        "melhoria",
        "gerar proposta",
    ]
    return any(t in q for t in triggers)


def handle(query):
    q = query.strip()
    nq = norm(q)

    if not q:
        return 0

    if nq in ("sair", "exit", "quit", "q"):
        return 99

    if is_proposal_request(q):
        return run_script("propose_from_mesh.py", q)

    return run_script("chat_mesh.py", q)


def interactive():
    print("CASULO Campo OS Operator")
    print("Comandos: estado, problemas, solucoes, grafo, consumo")
    print("Para gerar artefato: propor melhoria para atendimento whatsapp")
    print("Digite sair para encerrar")
    while True:
        try:
            query = input("casulo-op> ")
        except KeyboardInterrupt:
            print("\nsaindo")
            break
        code = handle(query)
        if code == 99:
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ask")
    args = parser.parse_args()

    if args.ask:
        code = handle(args.ask)
        if code == 99:
            return
        raise SystemExit(code)

    interactive()


if __name__ == "__main__":
    main()
