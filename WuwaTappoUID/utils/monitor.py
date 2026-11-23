"""开箱监测：复用已落库结果与角色解析，低频汇总，不访问游戏接口。"""

import json
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import ValidationError

from .command_text import command_text
from .formatting import date_text
from .schema import Item, OpenResult

if TYPE_CHECKING:
    from .cards import Cards
    from .database import ChestRecord

SUBSCRIBE_NAME = "WuwaTappo监测"
INTERVAL = 12 * 3600
INTERVAL_HOURS = INTERVAL // 3600
REPORT_LINES = 12


@dataclass(frozen=True)
class Summary:
    total: int
    counts: Counter[str]
    names: dict[str, str]
    first_at: float
    last_at: float

    @property
    def kinds(self) -> int:
        return len(self.counts)


def parse_roles(raw: str) -> set[str]:
    try:
        value = json.loads(raw or "[]")
    except ValueError:
        return set()
    if not isinstance(value, list):
        return set()
    return {str(item) for item in value if str(item)}


def summarize(cards: "Cards", records: list["ChestRecord"], roles: set[str]) -> Summary:
    """只统计解析成功且属于目标角色的成功流水；坏数据跳过，不影响其他结果。"""
    counts: Counter[str] = Counter()
    names: dict[str, str] = {}
    first_at = last_at = 0.0
    for record in records:
        if not record.result:
            continue
        try:
            opened = OpenResult.model_validate_json(record.result)
        except (ValidationError, ValueError):
            continue
        if cards.item_role(Item(asset_id=opened.asset_id, asset_name=opened.asset_name)) not in roles:
            continue
        key = str(opened.asset_id)
        counts[key] += 1
        names.setdefault(key, cards.item_name(opened.asset_id, opened.asset_name))
        first_at = record.created_at if not first_at else min(first_at, record.created_at)
        last_at = max(last_at, record.created_at)
    return Summary(sum(counts.values()), counts, names, first_at, last_at)


def report_text(role_name: str, summary: Summary) -> str:
    lines = [f"开箱监测「{role_name}」：累计新开到 {summary.total} 件"]
    ranked = sorted(summary.counts.items(), key=lambda item: (-item[1], summary.names.get(item[0], item[0])))
    for key, count in ranked[:REPORT_LINES]:
        lines.append(f"- {summary.names.get(key, key)} ×{count}")
    if len(ranked) > REPORT_LINES:
        lines.append(f"…另有 {len(ranked) - REPORT_LINES} 种物品")
    if summary.first_at and summary.last_at:
        lines.append(f"统计区间：{date_text(summary.first_at)} 至 {date_text(summary.last_at)}")
    lines.append(f"发送 {command_text('监测')} 查看，发送 {command_text('监测', '关闭')} 可关闭。")
    return "\n".join(lines)
