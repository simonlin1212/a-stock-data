"""a-stock-data 环境检查脚本。"""

from __future__ import annotations

import importlib.util
import os
import sys


def _check_module(name: str) -> tuple[str, str]:
    if importlib.util.find_spec(name):
        return "OK", name
    return "WARN", f"{name} 未安装"


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")
    for module in ["requests", "pandas", "lxml", "mootdx", "stockstats"]:
        status, message = _check_module(module)
        print(f"{status} {message}")

    if os.environ.get("IWENCAI_API_KEY"):
        print("OK IWENCAI_API_KEY 已配置")
    else:
        print("WARN IWENCAI_API_KEY 未配置：iwencai 语义研报搜索不可用")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
