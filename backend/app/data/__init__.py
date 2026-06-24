"""静态业务数据（价格表、字典等），MVP 阶段以 JSON 文件形式托管。"""

import json
from functools import lru_cache
from pathlib import Path

_BASE = Path(__file__).parent


@lru_cache
def load_price_catalog() -> dict:
    """加载维修指导价目录：部位 × 维修类型 → 工时费 + 配件费。"""
    with (_BASE / "price_catalog.json").open(encoding="utf-8") as f:
        return json.load(f)
