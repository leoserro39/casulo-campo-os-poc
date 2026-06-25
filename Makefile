.PHONY: validate triage apply graph rag demo chat

validate:
	python 04_scripts/validate_mesh.py

triage:
	python 04_scripts/triage_inbox.py

apply:
	python 04_scripts/apply_triage_manifest.py

graph:
	python 04_scripts/export_graph.py

rag:
	python 04_scripts/build_rag_index.py

demo:
	python 04_scripts/run_demo.py

chat:
	python 04_scripts/chat_mesh.py
