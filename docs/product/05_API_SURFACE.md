# CASULO Workbench — API Surface Draft

## Case endpoints

```text
GET  /api/cases
GET  /api/cases/{case_id}
GET  /api/cases/{case_id}/status
```

## Evidence endpoints

```text
GET  /api/cases/{case_id}/evidence
GET  /api/cases/{case_id}/audit
```

## Diagnostic endpoints

```text
GET  /api/cases/{case_id}/diagnostic
GET  /api/cases/{case_id}/report
```

## Cube/Cupula endpoints

```text
GET  /api/cases/{case_id}/cube-state
GET  /api/cases/{case_id}/replay
GET  /api/cases/{case_id}/timeline
```

## Gate endpoints

```text
GET  /api/cases/{case_id}/client-readiness
GET  /api/cases/{case_id}/human-review
POST /api/cases/{case_id}/human-review
```

## Export endpoints

```text
GET /api/cases/{case_id}/export/internal-report
```
