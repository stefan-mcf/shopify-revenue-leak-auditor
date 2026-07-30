# Sample Outputs

These files are public-safe demo artifacts generated from a fictional product page fixture, not from a real Shopify client store.

## What is included

- `demo-product-audit/audit_data.json` — structured audit result and scorecard.
- `demo-product-audit/audit_report.md` — client-readable Markdown report.
- `demo-product-audit/audit_report.html` — client-readable HTML report.
- `demo-product-audit/screenshots/desktop.png` — desktop evidence screenshot for the demo fixture.
- `demo-product-audit/screenshots/mobile.png` — mobile evidence screenshot for the demo fixture.
- `demo-product-audit/screenshots/report-overview.png` — visual summary of the generated report sections.
- `demo-product-audit/screenshots/scorecard.png` — visual summary of the scorecard categories.

## Reproduce the sample

From the repository root:

```bash
source .venv/bin/activate
python examples/generate_sample_outputs.py
```

The sample uses deterministic fixture HTML from `examples/sample_inputs/demo-product-page.html` and does not require network access, Shopify credentials, or LLM API keys.

## Use note

The sample shows the report format and audit categories without claiming actual revenue lift or exposing private client data.
