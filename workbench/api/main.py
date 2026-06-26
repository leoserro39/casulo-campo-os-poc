"""CASULO Workbench API stub.

The functional v0 engine is pure Python and is executed by scripts/run_demo.py.
A FastAPI/Node runtime can be attached later without changing the core contracts.
"""

def health():
    return {"status": "ok", "service": "casulo-workbench", "version": "0.1.0"}
