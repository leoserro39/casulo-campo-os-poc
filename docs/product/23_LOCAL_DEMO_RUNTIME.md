# Local Demo Runtime

## Start

```bash
python product/api/product_runtime_api.py --host 127.0.0.1 --port 8097
```

## Test

```bash
curl http://127.0.0.1:8097/api/health
curl http://127.0.0.1:8097/api/verticals
curl http://127.0.0.1:8097/api/verticals/vesselflow/state-request
curl http://127.0.0.1:8097/api/vesselflow/import-manifest
```

## Browser

Open the forwarded port 8097 in Codespaces and access:

```text
/api/health
/api/verticals
/api/vesselflow/import-manifest
```
