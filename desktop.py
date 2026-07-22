"""桌面端启动入口。

仅做路径设置，然后委托 source/main.py 中的 main() 函数运行。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from main import main

if __name__ == '__main__':
    main()
