# Product UI Shell

## Purpose

Create the first navigable local UI for the product.

The UI renders:

- Home;
- Verticals;
- VesselFlow workspace;
- State Request;
- Import Manifest;
- Reports.

It is served by the local Product Runtime API at `/ui`.

## Start

```bash
python product/api/product_runtime_api.py --host 0.0.0.0 --port 8097
```

Then open the forwarded port and access `/ui`.
