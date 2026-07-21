import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from app import create_app


def get_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def main():
    port = get_free_port()
    app = create_app()
    url = f'http://127.0.0.1:{port}/'

    # 服务启动后自动打开默认浏览器
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    app.run(host='127.0.0.1', port=port, debug=False)


if __name__ == '__main__':
    main()
