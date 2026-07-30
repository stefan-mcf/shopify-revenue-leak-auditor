# Local API Service Mode

The optional FastAPI service wraps the same audit pipeline used by the CLI. It is intended for local use and lightweight integrations.

## Install

The API stack is optional so the CLI remains lightweight:

```bash
pip install -e '.[api]'
```

For development, include both extras:

```bash
pip install -e '.[dev,api]'
```

## Run

```bash
shopify-audit-api
```

The service binds locally by default:

```text
http://127.0.0.1:8765
```

This is intentionally local-first. Do not expose it publicly without adding authentication, rate limits, request logging policy, and explicit data-handling controls.

## Health Check

```bash
curl http://127.0.0.1:8765/health
```

Expected response:

```json
{"status":"ok"}
```

## Run an Audit

```bash
curl -X POST http://127.0.0.1:8765/audit \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com/products/demo-product",
    "output_dir": "output/api",
    "include_report_bodies": true
  }'
```

The response includes:

- normalized input URL
- final URL and domain
- score and score label
- finding count
- top findings
- generated output paths
- optional Markdown/HTML report bodies

Artifacts are written to the same report file names used by the CLI:

- `audit_data.json`
- `audit_report.md`
- `audit_report.html`
- `report.md`
- `report.html`

## Python Usage

```python
from shopify_auditor.api import AuditApiRequest, run_audit_request

response = run_audit_request(AuditApiRequest(url="https://example.com/products/demo-product"))
print(response.overall_score, response.output_paths)
```

## Scope and Safety

- The API audits public pages unless a future private-data integration is explicitly added.
- It does not guarantee revenue lift; findings are likely conversion risks and improvement opportunities.
- It writes local artifacts to disk.
- It should be treated as a local developer/demo service, not a production SaaS API.
- If the browser cannot load the target page, it returns HTTP `502` and retains
  diagnostic artifacts in the selected output directory.
