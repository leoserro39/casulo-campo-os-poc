# TASK: Mesh Delta Computer

Goal:
Create a deterministic mesh delta computer for CASULO Campo OS.

Concept:
The delta is not a git diff. It is the operational difference between:
1. the user intention;
2. what the current mesh supports;
3. what is missing;
4. what resists or increases risk;
5. what can safely become a controlled proposal.

Inputs:
- 05_outputs/rag/chunks.jsonl
- 05_outputs/graph/graph.json
- user question/intention

Outputs:
- 04_scripts/compute_mesh_delta.py
- 05_outputs/deltas/mesh_delta_<slug>_<timestamp>.md
- 05_outputs/deltas/mesh_delta_<slug>_<timestamp>.json

Required output fields:
- status
- question
- inferred_domain
- graph_nodes
- graph_relationships
- chunks_used
- estimated_tokens
- sources
- common_dimensions
- missing_dimensions
- support_ratio
- missing_ratio
- Delta_L
- H_pre
- gate
- next_action

Rules:
- Use Python standard library only.
- Do not call external APIs.
- Do not modify canonical state.
- Do not modify proposal artifacts.
- Do not modify case/domain files.
- Git remains source of truth.
- graph.json and chunks.jsonl are derived inputs.

Acceptance:
python 04_scripts/compute_mesh_delta.py --ask "computar malha para melhoria de atendimento whatsapp"
python 04_scripts/validate_mesh.py

Expected:
- delta artifact created
- validate_mesh.py PASS
