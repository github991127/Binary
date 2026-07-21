import os
import sys
from pathlib import Path


def resource_path(rel):
    """兼容源码运行和 PyInstaller 打包后的资源路径。"""
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent
    return str(base / rel)
