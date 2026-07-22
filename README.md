# 抽牌概率计算器

加载默认牌库，根据用户输入计算三种抽牌问题的概率，操作简单，结果可视化。

## 一、项目目标

- 加载默认牌库 [`res/Card.xlsx`](res/Card.xlsx) 并展示（支持用户替换）。
- 根据用户输入计算 3 种抽牌问题的概率。
- 结果以表格和 ECharts 图表呈现，支持多种主题切换。

## 二、技术栈

- **后端**：Python + Flask（REST API）
- **前端**：原生 HTML + JavaScript + CSS（无 Vue/React/Angular）
- **图表**：ECharts
- **桌面窗口**：PyWebView
- **打包**：PyInstaller（onedir）
- **操作系统**：Windows 10+

## 三、目录结构

```text
Probability/
├── source/                 # 源代码
│   ├── app.py              # Flask 应用与 REST API
│   ├── main.py             # 桌面端服务器与窗口入口
│   ├── cards.py            # 牌库读取与数据模型
│   ├── Probability.py          # 概率计算核心
│   ├── utils.py            # 资源路径工具
│   ├── list_themes.py      # 主题列表与默认配置
│   ├── static/             # 静态资源
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   └── themes/     # 37 套明暗主题 CSS
│   │   ├── js/
│   │   │   ├── app.js      # 页面交互与 Tab 逻辑
│   │   │   ├── cards.js    # 牌库表格：分页/筛选/排序/热力图联动
│   │   │   └── charts.js   # ECharts 封装
│   │   └── vendor/
│   │       └── echarts.min.js
│   ├── templates/
│   │   └── index.html
│   └── Probability_webview.spec # PyInstaller 配置
├── res/
│   ├── Card.xlsx           # 默认牌库
│   ├── image.ico
│   └── image.png
├── desktop.py              # 桌面端启动入口
├── web.py                  # 网页端启动入口
├── build.bat               # 打包脚本
├── requirements.txt        # Python 依赖
├── README.md               # 项目说明
└── Cal.md                  # 概率问题详细说明
```

## 四、数据模型

[`res/Card.xlsx`](res/Card.xlsx) 中工作表名默认为 `160`，必须包含以下列：

| 列       | 类型   | 说明                         |
| -------- | ------ | ---------------------------- |
| id       | int    | 唯一编号                     |
| name     | str    | 牌名称                       |
| color    | int    | 花色数字（1/2/3/4）          |
| color2   | str    | 花色符号（♠/♣/♥/♦）          |
| number   | int    | 点数（1–13）                 |
| isTrue   | int    | 是否关键牌（1 = 是，0 = 否） |

## 五、功能列表

1. **牌库 Tab**
   - 展示总牌数、关键牌数、关键牌占比。
   - 表格支持分页、关键字筛选、列排序。
   - 支持点击“清除筛选”重置。

2. **问题 1 Tab**
   - 输入抽牌数 `a` 与最大得分 `b`。
   - 计算并展示 PMF 与“至少 k 分”概率分布表及柱状图。
   - 输入校验：`a ≤ 总牌数`、`b ≤ a`，中文错误提示。

3. **问题 2 Tab**
   - 列出所有花色点数组合，计算在“已知抽到某花色点数组合”的条件下，该组合对应牌为关键牌的条件概率。
   - 以热力图 + 组合摘要表格展示。
   - **交互增强**：点击热力图单元格（支持多选和一键清空选择），下方显示已选组合详情；点击“在牌库中查看”可跳转牌库 Tab 并自动筛选出这些组合的全部牌。

4. **问题 3 Tab**
   - 输入抽牌数 `a`。
   - 对比“新手随机选牌”与“高手选概率最高牌”的得分概率。

## 六、UI/UX

- Tab 导航，信息分区清晰。
- 支持 37 套明暗主题切换，主题状态本地保存（`localStorage`）。
- 操作 Toast 提示，输入超限/非法时给出中文错误。
- 响应式布局，适配较小窗口。

## 七、运行与部署

```bash
# 安装依赖
pip install -r requirements.txt

# 桌面端
python desktop.py

# 网页端（自动打开浏览器）
python web.py
```

- 自动寻找空闲端口，防止冲突。
- 桌面端自动打开窗口；网页端自动打开默认浏览器。

### 打包

```bash
build.bat
```

使用 `--onedir` 文件夹模式打包，输出 `dist\Probability_webview\Probability_webview.exe`。

## 八、API 概览

| 接口             | 方法   | 说明                 | 参数 / 请求体                            |
| ---------------- | ------ | -------------------- | ---------------------------------------- |
| `/`              | GET    | 渲染首页             | —                                        |
| `/api/themes`    | GET    | 返回主题列表与默认值 | —                                        |
| `/api/deck`      | GET    | 返回牌库与分组信息   | —                                        |
| `/api/problem1`  | POST   | 超几何分布计算       | JSON `{ a: number, b: number }`          |
| `/api/problem2`  | GET    | 花色点数组合条件概率 | —                                        |
| `/api/problem3`  | POST   | 新手/高手策略概率    | JSON `{ a: number }`                     |

返回体统一包含 `ok: true`，出错时返回 `ok: false` 与中文 `error` 字段。

## 九、质量标准

- **不要硬编码**（业务唯一字段如 `id`、`isTrue` 除外）。
- **原数据不可修改**：牌库加载后只读。
- **错误提示友好**：缺少列、输入格式错误、数量超限等都有中文提示。
- **代码结构清晰**：前后端分离、文件职责单一、全局状态集中。

## 十、常见问题

1. **抽到关键牌计分规则？**
   - 每抽到 1 张关键牌得 1 分，按无放回超几何分布计算。

2. **问题 3 的高手策略含义？**
   - 在抽出的 `a` 张牌中，选择花色点数组合条件概率最高的那张。

3. **问题 2 的概率是什么意思？**
   - 它是“已知抽到某花色点数组合”的条件下，该组合对应牌为关键牌的条件概率，不是所有牌中随机抽一张的概率。

4. **Card.xlsx 工作表名是什么？**
   - 默认读取名为 `160` 的工作表。

5. **如何替换默认牌库？**
   - 直接替换 `res/Card.xlsx` 文件，保持同名工作表 `160` 与必需列即可。程序启动时会自动加载。

6. **问题 2 支持多选吗？**
   - 支持。点击热力图单元格可多选/取消选择；点击“在牌库中查看”会筛选出所有已选组合对应的牌。

## 十一、文件映射

| 需求                 | 主要文件                                   |
| -------------------- | ------------------------------------------ |
| 牌库读取             | [`source/cards.py`](source/cards.py)       |
| 概率计算             | [`source/Probability.py`](source/Probability.py)     |
| Flask API            | [`source/app.py`](source/app.py)           |
| 桌面窗口             | [`source/main.py`](source/main.py)         |
| 启动脚本             | [`desktop.py`](desktop.py)、[`web.py`](web.py) |
| 页面交互与 Tab 状态   | [`source/static/js/app.js`](source/static/js/app.js) |
| 牌库表格与热力图联动 | [`source/static/js/cards.js`](source/static/js/cards.js) |
| 图表渲染（含热力图多选高亮） | [`source/static/js/charts.js`](source/static/js/charts.js) |
| 概率问题说明         | [`Cal.md`](Cal.md)                         |
