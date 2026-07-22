"""网页端启动入口。

将 source/ 加入模块搜索路径后，启动 Flask 开发服务器并自动打开浏览器。
"""

import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from app import create_app
from main import get_free_port


def main():
    """分配空闲端口、启动 Flask，并打开默认浏览器。"""
    port = get_free_port()
    app = create_app()
    url = f'http://127.0.0.1:{port}/'

    # 服务启动后自动打开默认浏览器
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    app.run(host='127.0.0.1', port=port, debug=False)


if __name__ == '__main__':
    main()
