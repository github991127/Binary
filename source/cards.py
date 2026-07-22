import logging
from pathlib import Path
from typing import Optional, Union

import openpyxl

from utils import data_path

logger = logging.getLogger(__name__)


class DeckError(ValueError):
    """牌库数据相关错误。"""


# Excel 中必须包含的列
REQUIRED_COLUMNS = {'id', 'name', 'color', 'color2', 'number', 'isTrue'}

# 默认读取的工作表名
DEFAULT_SHEET_NAME = '160'


class Deck:
    """牌库数据容器。原数据加载后不可变，仅通过只读属性访问。"""

    def __init__(self, rows):
        # rows 为字典列表，每个字典代表一张牌
        self.rows = rows
        self.total = len(rows)
        # 统计关键牌数量（isTrue == 1）
        self.key_count = sum(1 for r in rows if r['isTrue'] == 1)
        # 按花色符号与点数进行分组，用于问题 2 / 问题 3
        self.groups = self._build_groups(rows)

    @staticmethod
    def _build_groups(rows):
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
            if r['isTrue'] == 1:
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

    indices = {h: i for i, h in enumerate(headers)}
    rows = []
    for idx, raw in enumerate(raw_rows[1:], start=2):
        # 跳过可能的完全空行
        if all(v is None or str(v).strip() == '' for v in raw):
            continue
        try:
            rows.append({
                'id': _int(raw[indices['id']], 'id', idx),
                'name': _str(raw[indices['name']]),
                'color': _int(raw[indices['color']], 'color', idx),
                'color2': _str(raw[indices['color2']]),
                'number': _int(raw[indices['number']], 'number', idx),
                'isTrue': _int(raw[indices['isTrue']], 'isTrue', idx),
            })
        except DeckError:
            raise
        except Exception as exc:
            raise DeckError(f'第 {idx} 行数据格式错误：{exc}') from exc

    if not rows:
        raise DeckError('Card.xlsx 中没有有效的牌数据')

    key_count = sum(1 for r in rows if r['isTrue'] == 1)
    logger.info('Loaded deck: %s cards, %s key cards', len(rows), key_count)
    return Deck(rows)


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
