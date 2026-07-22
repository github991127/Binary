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

| 列     | 类型 | 说明                |
| ------ | ---- | ------------------- |
| id     | int  | 唯一编号            |
| name   | str  | 牌名称              |
| color  | int  | 花色数字（1/2/3/4） |
| color2 | str  | 花色符号（♠/♣/♥/♦） |
| number | int  | 点数（1–13）        |

此外，工作表中可包含任意 `tag1`、`tag2`、……（不区分大小写，按数字排序）列，每格填写该牌的 tag 内容。任意 tag 列非空即视为该牌拥有对应 tag。

### 关键牌规则

1. Excel 中仅存 tag 列与内容，**不预定义哪些是“关键 tag”**。
2. 前端“牌库”Tab 提供 tag 勾选区，用户勾选任意 tag 列后，这些列里**任意一个非空**的牌即视为关键牌。
3. 默认勾选第一个 tag 列（如 `tag1`）。
4. 用户在牌库页切换关键 tag 后，问题 1 / 问题 2 / 问题 3 会基于新的关键牌集合重新计算。

## 五、功能列表

1. **牌库 Tab**
   - 展示总牌数、关键 tag 列表。
   - 提供 tag 勾选区，可切换哪些 tag 作为关键 tag；勾选项保存到 `localStorage`，下次启动保留。
   - 表格展示 ID、名称、花色、点数以及当前选中的 tag 列内容。
   - 支持分页、关键字筛选（名称 / 花色 / 点数 / tag 内容）、列排序。
   - 支持点击“清除筛选”重置。

2. **问题 1 Tab**
   - 输入抽牌数 `a` 与最大得分 `b`。
   - 按当前选中的关键 tag 计算并展示 PMF 与“至少 k 分”概率分布表及柱状图。
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

| 接口            | 方法 | 说明                 | 参数 / 请求体                                    |
| --------------- | ---- | -------------------- | ------------------------------------------------ |
| `/`             | GET  | 渲染首页             | —                                                |
| `/api/themes`   | GET  | 返回主题列表与默认值 | —                                                |
| `/api/deck`     | GET  | 返回牌库与分组信息   | —                                                |
| `/api/problem1` | POST | 超几何分布计算       | JSON `{ a: number, b: number, tags?: string[] }` |
| `/api/problem2` | POST | 花色点数组合条件概率 | JSON `{ tags?: string[] }`                       |
| `/api/problem3` | POST | 新手/高手策略概率    | JSON `{ a: number, tags?: string[] }`            |

返回体统一包含 `ok: true`，出错时返回 `ok: false` 与中文 `error` 字段。

`/api/deck` 额外返回：

| 字段              | 说明                                                              |
| ----------------- | ----------------------------------------------------------------- |
| total             | 总牌数                                                            |
| key_count         | 未选 tag 时关键牌数（固定为 0）                                   |
| key_rate          | 关键牌占比字符串                                                  |
| key_rate_pct      | 关键牌占比百分比                                                  |
| available_tags    | tag 原列名数组，如 `["tag1", "tag2"]`                             |
| tag_display_names | 列名到显示名称映射，如 `{"tag1":"杀", "tag2":"桃"}`               |
| rows              | 所有牌明细，每条含 `tags: { tag名: 内容, ... }`                   |
| groups            | 花色点数组合列表                                                  |

## 九、质量标准

- **不要硬编码**（业务唯一字段如 `id` 除外）。
- **原数据不可修改**：牌库加载后只读，tag 选择仅生成派生视图。
- **错误提示友好**：缺少列、输入格式错误、数量超限、非法 tag 等都有中文提示。
- **代码结构清晰**：前后端分离、文件职责单一、全局状态集中。

## 十、常见问题

1. **抽到关键牌计分规则？**
   - 每抽到 1 张关键牌得 1 分，按无放回超几何分布计算。

2. **什么是“关键 tag”？**
   - 用户在牌库页勾选任意 tag 列后，被勾选列中非空的牌即为关键牌，用于后续概率计算。

3. **tag 列名有什么要求？**
   - 列名必须形如 `tag1`、`tag2`……不区分大小写，允许跳号（如 `tag1`、`tag3`）。
   - 读取时按数字升序排列后返回给前端。
   - 若某 tag 列内的非空值完全相同，界面上会用该值作为列标题与勾选区文字（例如 `tag1` 列全是“杀”，则显示“杀”）；若存在多种值或全为空，则回退显示原列名 `tagN`。

4. **数字 0 算不算有效 tag？**
   - 算。只要单元格 trim 后非空就算有效 tag。

5. **问题 1/2/3 会随 tag 选择变化吗？**
   - 会。三个问题都会使用当前选中的关键 tag 重新计算关键牌集合与每种花色点数组合的关键牌数。

6. **Card.xlsx 工作表名是什么？**
   - 默认读取名为 `160` 的工作表。

7. **如何替换默认牌库？**
   - 直接替换 `res/Card.xlsx` 文件，保持同名工作表 `160` 与必需列即可。程序启动时会自动加载。
   - 需要 tag 功能时，在工作表中添加 `tag1`、`tag2` 等列即可。

8. **问题 2 支持多选吗？**
   - 支持。点击热力图单元格可多选/取消选择；点击“在牌库中查看”会筛选出所有已选组合对应的牌张明细。

## 十一、文件映射

| 需求                         | 主要文件                                                   |
| ---------------------------- | ---------------------------------------------------------- |
| 牌库读取                     | [`source/cards.py`](source/cards.py)                       |
| 概率计算                     | [`source/Probability.py`](source/Probability.py)           |
| Flask API                    | [`source/app.py`](source/app.py)                           |
| 桌面窗口                     | [`source/main.py`](source/main.py)                         |
| 启动脚本                     | [`desktop.py`](desktop.py)、[`web.py`](web.py)             |
| 页面交互与 Tab 状态          | [`source/static/js/app.js`](source/static/js/app.js)       |
| 牌库表格与热力图联动         | [`source/static/js/cards.js`](source/static/js/cards.js)   |
| 图表渲染（含热力图多选高亮） | [`source/static/js/charts.js`](source/static/js/charts.js) |
| 概率问题说明                 | [`Cal.md`](Cal.md)                                         |
