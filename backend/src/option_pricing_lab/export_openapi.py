from __future__ import annotations

from pathlib import Path

import yaml

from option_pricing_lab.api import app


def main() -> None:
    output_path = Path("openapi.yaml")
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(app.openapi(), handle, sort_keys=False, allow_unicode=True)
    print(f"Wrote OpenAPI spec to {output_path}")
