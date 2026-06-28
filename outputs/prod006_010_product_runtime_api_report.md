# PROD-006..010 Product Runtime API Report

- Status: `PASS`
- Phase: `Product Runtime API and Case Adapter`
- Product direction: `Cubo Operacional / Operational Cube`
- Runtime mode: `local_demo`
- Default port: `8097`

## Generated

- local product API;
- product runtime service;
- case/vertical adapter;
- snapshot script;
- validation script;
- local run script;
- API docs;
- API snapshot outputs.

## Endpoints

- `GET /api/health`
- `GET /api/product/status`
- `GET /api/verticals`
- `GET /api/verticals/{vertical_id}`
- `GET /api/verticals/{vertical_id}/state-request`
- `GET /api/vesselflow/import-manifest`
- `GET /api/reports`

## Safety

No client-facing claim, automatic nomination, implementation execution or production activation is authorized.

## Recommended next bundle

`PROD-011..015 Product UI Shell and Case Workspace`
