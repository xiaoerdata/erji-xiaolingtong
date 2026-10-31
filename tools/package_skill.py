#!/usr/bin/env python3
"""Create reproducible, allowlisted standard and WorkBuddy skill archives."""
import hashlib
import io
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SLUG = "erji-xiaolingtong"
VERSION = "1.0.1"
FILES = ["SKILL.md", "agents/openai.yaml", "assets/example-nav.csv", "scripts/compare_nav.py",
         *[f"references/{name}.md" for name in ["connection", "private-funds", "public-funds", "market-cases", "data-methods", "prompts"]]]
WB_METADATA = '''display_name: "二级小灵通"
display_name_en: "Secondary Market Companion"
description_zh: "用小二 MCP 或自有数据做基金比较、市场观察和交叉分析，注明来源、日期与指标口径。"
description_en: "Analyze funds and markets with Xiaoer MCP or your own data, reconciling sources, dates, metrics and supporting evidence."
version: "1.0.1"
author: "xiaoerdata"
examples_zh:
  - "比较几只基金最近半年的收益和回撤"
  - "做一份带数据日期的市场复盘"
examples_en:
  - "Compare funds over a common six-month period"
  - "Draft a source-backed market review"
'''


def archive(workbuddy=False):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in sorted(FILES):
            file = ROOT / SLUG / name
            if file.is_symlink():
                raise ValueError(f"Symlinks are not packaged: {name}")
            data = file.read_bytes()
            if workbuddy and name == "SKILL.md":
                text = data.decode("utf-8")
                front, body = text[4:].split("\n---\n", 1)
                data = ("---\n" + front + "\n" + WB_METADATA + "---\n" + body).encode("utf-8")
            info = zipfile.ZipInfo(f"{SLUG}/{name}", date_time=(2026, 10, 31, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
        info = zipfile.ZipInfo(f"{SLUG}/LICENSE", date_time=(2026, 10, 31, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        bundle.writestr(info, (ROOT / "LICENSE").read_bytes())
    return buffer.getvalue()


def main():
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    standard = archive()
    files = {f"{SLUG}.skill": standard, f"{SLUG}.zip": standard,
             f"{SLUG}-workbuddy.zip": archive(workbuddy=True)}
    for name, data in files.items():
        (output / name).write_bytes(data)
    (output / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(data).hexdigest()}  {name}\n" for name, data in sorted(files.items())), encoding="utf-8")
    print(f"Packaged {SLUG} {VERSION}: {len(FILES) + 1} files per archive")


if __name__ == "__main__":
    main()
