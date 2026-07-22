"""桌面端入口。

启动 Flask 后台服务后，使用 pywebview 创建桌面窗口加载本地页面。
"""

import logging
import os
import socket
import sys
import threading
from pathlib import Path

import webview
from werkzeug.serving import make_server

from app import create_app
from utils import resource_path

# 某些 pywebview 依赖在 Windows 使用 pywintypes，提前导入可减少打包偶发问题
try:
    import pywintypes  # noqa: F401
except Exception:
    pass


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def get_free_port():
    """绑定到 127.0.0.1:0 获取一个空闲端口。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def _icon_path():
    """返回图标资源路径。

    源码运行时 res 在项目根目录；PyInstaller 打包后在 _internal/res。
    """
    if getattr(sys, 'frozen', False):
        return resource_path('res/image.ico')
    return str(Path(__file__).resolve().parent.parent / 'res' / 'image.ico')


def main():
    """启动 Flask 并打开桌面窗口。"""
    port = get_free_port()
    app = create_app()

    # 在守护线程中运行 Flask，主线程用于 GUI 消息循环
    server = make_server('127.0.0.1', port, app, threaded=True)
    flask_thread = threading.Thread(target=server.serve_forever, daemon=True)
    flask_thread.start()
    logger.info('Flask server started on http://127.0.0.1:%s', port)

    icon_path = _icon_path()

    webview.create_window(
        '抽牌概率计算器',
        f'http://127.0.0.1:{port}/',
        width=1080,
        height=760,
        resizable=True,
        text_select=True,
    )

    try:
        webview.start(icon=icon_path if os.path.exists(icon_path) else None)
    finally:
        logger.info('Shutting down Flask server')
        server.shutdown()
        try:
            flask_thread.join(timeout=2)
        except Exception:
            pass


if __name__ == '__main__':
    main()
