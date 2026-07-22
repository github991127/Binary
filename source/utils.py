"""资源路径工具。

统一处理源码运行与 PyInstaller 打包后的路径差异。
"""

import sys
from pathlib import Path


def resource_path(rel):
    """返回应用内资源路径。

    源码运行时基于 source/ 目录；PyInstaller 打包后基于 sys._MEIPASS。
    """
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent
    return str(base / rel)


def project_root():
    """返回项目根目录。

    源码运行时与 source/ 同级；打包后取 sys._MEIPASS。
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def data_path(rel=None):
    """返回 res 数据目录或 res 下的某个文件路径。

    rel 为 None 时返回 res 目录；否则返回 res/rel。
    """
    root = project_root()
    if rel is None:
        return str(root / 'res')
    return str(root / 'res' / rel)
