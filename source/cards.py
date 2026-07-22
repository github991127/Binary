import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import openpyxl

from utils import data_path

logger = logging.getLogger(__name__)


class DeckError(ValueError):
    """牌库数据相关错误。"""


# Excel 中必须包含的列
REQUIRED_COLUMNS = {'id', 'name', 'color', 'color2', 'number'}

# 匹配 tag 列名：tag1, tag2, ... 不区分大小写
TAG_COLUMN_RE = re.compile(r'^tag\d+$', re.IGNORECASE)

# 默认读取的工作表名
DEFAULT_SHEET_NAME = '160'


class Deck:
    """牌库数据容器。原数据加载后不可变，仅通过只读属性访问。"""

    def __init__(self, rows, available_tags, tag_display_names=None):
        # rows 为字典列表，每个字典代表一张牌
        self.rows = rows
        self.available_tags = available_tags
        self.tag_display_names = tag_display_names or {t: t for t in available_tags}
        self.total = len(rows)
        # 统计关键牌数量（默认空选：没有任何 tag 被选中，关键牌数为 0）
        self.key_count = 0
        self.selected_tags = set()
        # 按花色符号与点数进行分组，用于问题 2 / 问题 3
        self.groups = self._build_groups(rows)

    def display_name(self, tag):
        """返回 tag 列的显示名称。"""
        return self.tag_display_names.get(tag, tag)

    def with_tags(self, tags):
        """按选中的 tag 列生成派生统计，返回包含新 key_count / groups 的视图字典。

        保持当前 Deck 实例不变。
        """
        selected = set(tags) & set(self.available_tags)
        key_count = 0
        for r in self.rows:
            if any(_nonempty(r['tags'].get(t)) for t in selected):
                key_count += 1
        groups = self._build_groups_for_tags(self.rows, selected)
        return {
            'total': self.total,
            'key_count': key_count,
            'groups': groups,
            'rows': self.rows,
            'available_tags': self.available_tags,
            'tag_display_names': self.tag_display_names,
            'selected_tags': selected,
        }

    def _build_groups(self, rows):
        """按 (color2, number) 分组，汇总每组张数与关键牌数（.selected_tags）。"""
        return self._build_groups_for_tags(rows, self.selected_tags)

    @staticmethod
    def _build_groups_for_tags(rows, selected_tags):
        """按 (color2, number) 分组，汇总每组张数与关键牌数。"""
        groups = {}
        for r in rows:
            key = (r['color2'], r['number'])
            if key not in groups:
                groups[key] = {
                    'suit': r['color2'],   # 花色符号
                    'rank': r['number'],   # 点数
                    'color': r['color'],   # 花色数字
                    'size': 0,             # 该组合总张数
                    'keys': 0,             # 该组合关键牌张数
                }
            groups[key]['size'] += 1
            if any(_nonempty(r['tags'].get(t)) for t in selected_tags):
                groups[key]['keys'] += 1
        # 按花色、点数排序，保证顺序稳定
        return [groups[k] for k in sorted(groups, key=lambda x: (x[0], x[1]))]

    def key_rate(self):
        """返回关键牌占比（Fraction 形式），避免总牌数为 0 时除零。"""
        from fractions import Fraction
        return Fraction(self.key_count, max(1, self.total))


# 进程级牌库缓存，避免每次 API 调用都重新读取 Excel
_CARD_DATA: Optional[Deck] = None


def load_deck(excel_path: Optional[Union[str, Path]] = None) -> Deck:
    """加载牌库。默认读取 res/Card.xlsx，结果进程级缓存。"""
    global _CARD_DATA
    if _CARD_DATA is None:
        _CARD_DATA = _load_from_excel(excel_path)
    return _CARD_DATA


def reload_deck(excel_path: Optional[Union[str, Path]] = None) -> Deck:
    """强制重新读取 Excel 并刷新缓存。"""
    global _CARD_DATA
    _CARD_DATA = _load_from_excel(excel_path)
    return _CARD_DATA


def _resolve_path(excel_path: Optional[Union[str, Path]]) -> Path:
    """解析 Excel 路径：未指定时使用默认 res/Card.xlsx。"""
    if excel_path is None:
        return Path(data_path('Card.xlsx'))
    return Path(excel_path)


def _load_from_excel(excel_path: Optional[Union[str, Path]] = None) -> Deck:
    """从 Excel 读取牌库数据，校验列与数据格式，返回 Deck 对象。"""
    path = _resolve_path(excel_path)
    if not path.exists():
        raise DeckError(f'找不到牌库文件：{path}')

    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as exc:
        raise DeckError(f'无法读取 Card.xlsx：{exc}') from exc

    if DEFAULT_SHEET_NAME not in wb.sheetnames:
        sheets = ', '.join(wb.sheetnames)
        raise DeckError(
            f"Card.xlsx 中未找到名为 '{DEFAULT_SHEET_NAME}' 的工作表，"
            f'可用工作表：{sheets}'
        )

    ws = wb[DEFAULT_SHEET_NAME]
    raw_rows = list(ws.iter_rows(values_only=True))
    if not raw_rows:
        raise DeckError('Card.xlsx 工作表为空')

    headers = [str(h).strip() for h in raw_rows[0]]
    missing = REQUIRED_COLUMNS - set(headers)
    if missing:
        missing_cols = ', '.join(sorted(missing))
        raise DeckError(f"Card.xlsx 缺少必要列：{missing_cols}")

    # 发现并排序 tag 列：按末尾数字升序，保留原列名大小写
    tag_cols = [h for h in headers if TAG_COLUMN_RE.match(h)]
    tag_cols.sort(key=lambda h: int(h[3:]))

    indices = {h: i for i, h in enumerate(headers)}
    rows = []
    for idx, raw in enumerate(raw_rows[1:], start=2):
        # 跳过可能的完全空行
        if all(v is None or str(v).strip() == '' for v in raw):
            continue
        try:
            tags = {t: _str(raw[indices[t]]) for t in tag_cols}
            rows.append({
                'id': _int(raw[indices['id']], 'id', idx),
                'name': _str(raw[indices['name']]),
                'color': _int(raw[indices['color']], 'color', idx),
                'color2': _str(raw[indices['color2']]),
                'number': _int(raw[indices['number']], 'number', idx),
                'tags': tags,
            })
        except DeckError:
            raise
        except Exception as exc:
            raise DeckError(f'第 {idx} 行数据格式错误：{exc}') from exc

    if not rows:
        raise DeckError('Card.xlsx 中没有有效的牌数据')

    # 为每个 tag 列推导显示名称：若该列非空值唯一，则用该值；否则回退原列名
    tag_display_names = _build_tag_display_names(tag_cols, rows)

    logger.info('Loaded deck: %s cards, tags: %s', len(rows), tag_display_names)
    return Deck(rows, tag_cols, tag_display_names)


def _build_tag_display_names(tag_cols, rows):
    """为每个 tag 列推导显示名称。

    - 若某 tag 列在所有行中非空且值完全相同，则使用该值作为显示名（如"杀"）。
    - 若该列没有非空值，或存在多种不同值，则回退到原列名（如"tag1"）。
    """
    display_names = {}
    for col in tag_cols:
        values = {r['tags'][col] for r in rows if _nonempty(r['tags'][col])}
        if len(values) == 1:
            display_names[col] = values.pop()
        else:
            display_names[col] = col
    return display_names
def _int(value, label, row):
    """将单元格值解析为整数，失败时抛出带行号/列名的 DeckError。"""
    if value is None:
        raise DeckError(f'第 {row} 行 {label} 为空')
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise DeckError(f'第 {row} 行 {label} 不是有效整数：{value!r}') from exc


def _str(value):
    """将单元格值解析为字符串，None 视为空串。"""
    if value is None:
        return ''
    return str(value).strip()


def _nonempty(value):
    """判断字符串是否非空（trim 后）。"""
    return isinstance(value, str) and value != ''
