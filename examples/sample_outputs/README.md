# Sample Outputs

These files are public-safe demo artifacts generated from a fictional product page fixture, not from a real Shopify client store.

## Inspect the example

- [Markdown report](demo-product-audit/audit_report.md), [HTML report](demo-product-audit/audit_report.html) and [structured result](demo-product-audit/audit_data.json).
- [Desktop capture](demo-product-audit/screenshots/desktop.png) and [mobile capture](demo-product-audit/screenshots/mobile.png) of the fictional product page.
- [Report overview](demo-product-audit/screenshots/report-overview.png) and [category scorecard](demo-product-audit/screenshots/scorecard.png).

## Reproduce the sample

From the repository root, activate the project environment and install Playwright Chromium if needed:

```bash
source .venv/bin/activate
python -m playwright install chromium
python examples/generate_sample_outputs.py
```

The sample uses deterministic fixture HTML from `examples/sample_inputs/demo-product-page.html` and does not require network access, Shopify credentials, or LLM API keys.

## Use note

The storefront captures render the fixture with example styling. The report scores the fixture source with the published audit rules. Use these artifacts to inspect the report format and rule priorities.
