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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def _icon_path():
    """返回图标资源路径；源码运行时 res 在项目根目录，打包后在 _internal/res。"""
    rel = 'res/image.ico' if getattr(sys, 'frozen', False) else '../res/image.ico'
    return resource_path(rel)


def main():
    port = get_free_port()
    app = create_app()

    server = make_server('127.0.0.1', port, app, threaded=True)
    flask_thread = threading.Thread(target=server.serve_forever, daemon=True)
    flask_thread.start()
    logger.info('Flask server started on http://127.0.0.1:%s', port)

    icon_path = _icon_path()

    webview.create_window(
        'Binary',
        f'http://127.0.0.1:{port}/',
        width=480,
        height=440,
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
