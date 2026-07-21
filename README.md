# Binary

二进制 / 十进制快速转换小工具。

## 技术栈

- **Flask** — 本地后端服务与 REST API
- **pywebview** — 将 Flask 页面封装为原生桌面窗口
- **PyInstaller** — 打包为独立 Windows 桌面程序

## 运行方式

### 开发调试

```bash
cd source
python main.py
```

### 打包

```bash
python -m PyInstaller source/Binary_webview.spec
```

打包产物位于 `dist/Binary_webview/Binary_webview.exe`，双击即可运行，无需安装 Python 或浏览器。

## 功能

- 二进制数 ↔ 十进制数快速转换（支持 `.` 分隔多段，如 `192.168`）
- 批量输入 0 / 1 位
- 一键清空
- 多主题切换（基于 CSS 变量）

## 项目结构

```text
source/
├── main.py              # pywebview 启动入口
├── app.py               # Flask 后端
├── Binary.py            # 转换核心逻辑
├── list_themes.py       # 主题注册表
├── templates/
│   └── index.html       # 主界面
└── static/
    ├── css/
    │   ├── base.css
    │   └── themes/      # 全部主题 CSS
    └── js/app.js
```

## 依赖

```text
Flask>=3.0
Werkzeug>=3.0
pywebview>=5.0
pyinstaller>=6.0
```

运行 `pip install -r requirements.txt` 安装。
