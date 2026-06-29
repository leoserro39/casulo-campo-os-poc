#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

HELPER = r'''
NEGATED_EXECUTION_PATTERNS = [
    "sem executar",
    "sem enviar",
    "sem acionar",
    "sem liberar",
    "sem aprovar",
    "não executar",
    "nao executar",
    "não enviar",
    "nao enviar",
    "não acionar",
    "nao acionar",
    "não liberar",
    "nao liberar",
    "não aprovar",
    "nao aprovar",
]

DIRECT_EXECUTION_PATTERNS = [
    "aprovar automaticamente",
    "executar automaticamente",
    "enviar automaticamente",
    "acionar automaticamente",
    "liberar automaticamente",
    "executar ação",
    "executar acao",
    "ação externa",
    "acao externa",
]

DIRECT_EXECUTION_TERMS = ["executar", "enviar", "acionar", "liberar", "aprovar"]


def _execution_text(case: Dict[str, Any]) -> str:
    return " ".join([
        str(case.get("problem_summary", "")),
        str(case.get("desired_decision_support", "")),
        " ".join(case.get("known_facts", []) if isinstance(case.get("known_facts"), list) else []),
        " ".join(case.get("assumptions", []) if isinstance(case.get("assumptions"), list) else []),
    ]).lower()


def _desired_action_text(case: Dict[str, Any]) -> str:
    return str(case.get("desired_decision_support", "")).lower()


def has_negated_execution_intent(case: Dict[str, Any]) -> bool:
    text = _execution_text(case)
    return any(pattern in text for pattern in NEGATED_EXECUTION_PATTERNS)


def has_direct_execution_intent(case: Dict[str, Any]) -> bool:
    text = _execution_text(case)
    desired = _desired_action_text(case)

    if any(pattern in text for pattern in DIRECT_EXECUTION_PATTERNS):
        return True

    if any(term in desired for term in DIRECT_EXECUTION_TERMS):
        if not any(pattern in desired for pattern in NEGATED_EXECUTION_PATTERNS):
            return True

    return False


def classify_execution_intent(case: Dict[str, Any]) -> str:
    direct = has_direct_execution_intent(case)
    negated = has_negated_execution_intent(case)

    if direct:
        return "EXECUTION_REQUEST"
    if negated:
        return "SAFE_NON_EXECUTING_REQUEST"
    return "NO_EXECUTION_REQUEST"

'''

OLD_BLOCK = '''    if case.get("business_domain") not in SUPPORTED_DOMAINS:
        return "unsupported_request"
    if any(word in text for word in ["executar", "enviar", "aprovar automaticamente", "automaticamente", "ação externa"]):
        return "execution_request"
'''

NEW_BLOCK = '''    if case.get("business_domain") not in SUPPORTED_DOMAINS:
        return "unsupported_request"
    intent = classify_execution_intent(case)
    if intent == "EXECUTION_REQUEST":
        return "execution_request"
'''

FALLBACK_PATTERN = re.compile(
    r'    if case\.get\("business_domain"\) not in SUPPORTED_DOMAINS:\n'
    r'        return "unsupported_request"\n'
    r'    if any\(word in text for word in \[[^\]]+\]\):\n'
    r'        return "execution_request"\n'
)

def patch_runner(repo: Path) -> None:
    path = repo / "product/scripts/run_business_case_interactive_runner.py"
    if not path.exists():
        raise SystemExit(f"Missing runner: {path}")

    s = path.read_text(encoding="utf-8")

    if "def classify_execution_intent" not in s:
        marker = "\ndef infer_scenario(case: Dict[str, Any]) -> str:\n"
        if marker not in s:
            raise SystemExit("Could not find infer_scenario marker in runner.")
        s = s.replace(marker, "\n" + HELPER + marker, 1)

    if OLD_BLOCK in s:
        s = s.replace(OLD_BLOCK, NEW_BLOCK, 1)
    elif 'intent = classify_execution_intent(case)' not in s:
        s2, n = FALLBACK_PATTERN.subn(NEW_BLOCK, s, count=1)
        if n != 1:
            raise SystemExit("Could not patch execution-request block in infer_scenario.")
        s = s2

    path.write_text(s, encoding="utf-8")
    print(f"patched {path}")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    patch_runner(Path(args.repo))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
