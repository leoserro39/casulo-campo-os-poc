# Product Runtime API

## Purpose

Expose the product runtime locally without cloud, database or authentication.

This runtime reads:

- vertical packs;
- generated state requests;
- VesselFlow import manifest;
- product reports.

## Endpoints

- `GET /api/health`
- `GET /api/product/status`
- `GET /api/verticals`
- `GET /api/verticals/{vertical_id}`
- `GET /api/verticals/{vertical_id}/state-request`
- `GET /api/vesselflow/import-manifest`
- `GET /api/reports`

## Safety

This API is local demo only. It does not authorize implementation, client-facing claims, automatic nomination or production activation.
