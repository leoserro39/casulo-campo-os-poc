# Manual Agent Configuration Checklist

- [ ] Repo is on latest `main`.
- [ ] Unified API server runs on port 8541.
- [ ] `/health` returns `writes_allowed=false`.
- [ ] Codespaces port 8541 is public/accessible for sandbox.
- [ ] Public URL is copied.
- [ ] OpenAPI server URL is replaced.
- [ ] Instructions are copied.
- [ ] Knowledge pack is copied.
- [ ] OpenAPI schema is imported.
- [ ] Agent can call `/materials/admit`.
- [ ] Agent can call `/agent/diagnostic`.
- [ ] Agent can call `/calibration-loop/run`.
- [ ] Agent refuses production/client/commercial claim.
- [ ] Evidence log is filled.
- [ ] Result template is filled.
