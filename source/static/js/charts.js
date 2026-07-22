/**
 * ECharts 图表封装模块。
 *
 * 负责：
 * - 从 CSS 变量读取当前主题颜色
 * - 提供通用 ECharts 基础配置
 * - 渲染问题 1/2/3 所需的 ECharts 图表
 */
const Charts = (() => {
    /**
     * 读取 CSS 自定义属性作为主题颜色。
     * @param {string} name
     * @param {string} fallback
     * @returns {string}
     */
    function getCSSColor(name, fallback) {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
    }

    /** 返回通用的 ECharts 基础选项（字体、提示框样式、网格、调色板）。 */
    function baseOption() {
        const accent = getCSSColor('--accent', '#ffeb3b');
        const fg = getCSSColor('--fg', '#f5f5f5');
        const surface = getCSSColor('--surface', '#1e1e1e');
        const border = getCSSColor('--border', '#444');
        return {
            textStyle: { fontFamily: getCSSColor('--font-family', 'sans-serif').replace(/"/g, '') },
            tooltip: {
                trigger: 'axis',
                backgroundColor: surface,
                borderColor: border,
                textStyle: { color: fg },
            },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            color: [accent, '#ff7043', '#42a5f5', '#66bb6a', '#ab47bc'],
        };
    }

    /** 将百分比数值保留两位小数并加上 % 后缀。 */
    function formatPct(value) {
        return Number(value).toFixed(2) + '%';
    }

    /**
     * 通用柱状图渲染。
     * @param {string} containerId
     * @param {string} title
     * @param {string[]} xData
     * @param {Object[]} seriesList
     * @returns {echarts.ECharts|null}
     */
    function renderBar(containerId, title, xData, seriesList) {
        const el = document.getElementById(containerId);
        if (!el) return null;
        const chart = echarts.init(el);
        const fg = getCSSColor('--fg', '#f5f5f5');
        const opt = {
            ...baseOption(),
            title: { text: title, left: 'center', textStyle: { color: fg } },
            xAxis: {
                type: 'category',
                data: xData,
                axisLabel: { color: fg },
                axisLine: { lineStyle: { color: getCSSColor('--border', '#444') } },
            },
            yAxis: {
                type: 'value',
                axisLabel: { formatter: '{value}%', color: fg },
                splitLine: { lineStyle: { color: getCSSColor('--border', '#444') } },
            },
            series: seriesList,
        };
        chart.setOption(opt);
        return chart;
    }

    /**
     * 渲染问题 1 柱状图：P(X = k) 的概率分布。
     * @param {string} containerId
     * @param {Array<{k:number, pct:number}>} pmf
     * @param {Array<{k:number, pct:number}>} atLeast
     * @returns {echarts.ECharts|null}
     */
    function renderProblem1(containerId, pmf, atLeast) {
        const xPmf = pmf.map(p => p.k + ' 分');
        const sPmf = pmf.map(p => p.pct);
        return renderBar(containerId, '问题 1 概率分布 P(X = k)', xPmf, [
            {
                name: 'P(X=k)',
                type: 'bar',
                data: sPmf,
                barWidth: '50%',
                itemStyle: { borderRadius: [4, 4, 0, 0] },
                label: { show: true, position: 'top', formatter: c => formatPct(c.value) },
            },
        ]);
    }

    /**
     * 渲染问题 2 热力图：花色×点数组合下抽到关键牌的条件概率。
     *
     * 支持单元格多选/取消选择：
     * - 通过 options.selectedKeys 传入初始已选状态
     * - 点击单元格会切换其选中状态，并触发 options.onCellClick 回调
     * - 使用自定义 itemStyle 边框高亮，禁用 ECharts 内置选择以避免行为不一致
     *
     * @param {string} containerId
     * @param {Array<{suit:string, rank:number, size:number, keys:number, prob_pct:number, prob_exact:string}>} groups
     * @param {Object} [options]
     * @param {string[]} [options.selectedKeys] - 已选中单元格的键，格式为 suit|rank
     * @param {Function} [options.onCellClick] - 单元格点击回调 ({ suit, rank, suitIndex, rankIndex, selected })
     * @returns {echarts.ECharts|null}
     */
    function renderProblem2(containerId, groups, options = {}) {
        const { selectedKeys = [], onCellClick } = options;

        // 从数据中取出实际花色集合；点数固定为 1–13
        const suits = [...new Set(groups.map(g => g.suit))];
        const ranks = [...Array(13).keys()].map(i => i + 1);

        const el = document.getElementById(containerId);
        if (!el) return null;
        const chart = echarts.init(el);
        const accent = getCSSColor('--accent', '#ffeb3b');
        const bg = getCSSColor('--bg', '#121212');
        const fg = getCSSColor('--fg', '#f5f5f5');

        const keyFor = (suit, rank) => `${suit}|${rank}`;
        const selectedSet = new Set(selectedKeys);

        /**
         * 构建热力图 series 数据。
         * 未出现的组合概率视为 0；已选项通过 itemStyle 加边框高亮，不覆盖 visualMap 颜色映射。
         */
        function buildSeriesData() {
            return ranks.flatMap((rank, y) => suits.map((suit, x) => {
                const g = groups.find(grp => grp.suit === suit && grp.rank === rank);
                const val = g ? g.prob_pct : 0;
                const isSelected = selectedSet.has(keyFor(suit, rank));
                return {
                    value: [x, y, val],
                    itemStyle: isSelected ? {
                        borderColor: accent,
                        borderWidth: 3,
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)',
                    } : {},
                };
            }));
        }

        const opt = {
            ...baseOption(),
            title: { text: '花色点数组合关键牌条件概率热力图（点击单元格多选 / 取消）', left: 'center', textStyle: { color: fg, fontSize: 15 } },
            tooltip: {
                position: 'top',
                formatter: p => `${suits[p.value[0]]} · 点数 ${p.value[1] + 1}<br/>概率: ${p.value[2].toFixed(2)}%`,
            },
            xAxis: {
                type: 'category',
                data: suits,
                splitArea: { show: true },
                axisLabel: { fontSize: 16, color: fg },
                axisLine: { lineStyle: { color: getCSSColor('--border', '#444') } },
            },
            yAxis: {
                type: 'category',
                data: ranks,
                splitArea: { show: true },
                axisLabel: { color: fg },
                axisLine: { lineStyle: { color: getCSSColor('--border', '#444') } },
            },
            visualMap: {
                min: 0,
                max: 100,
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: '0%',
                inRange: { color: [bg, accent] },
                textStyle: { color: fg },
            },
            series: [{
                name: '概率',
                type: 'heatmap',
                data: buildSeriesData(),
                label: { show: true, formatter: p => Number(p.value[2]).toFixed(0), fontSize: 11 },
                emphasis: {
                    itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' },
                },
                selectedMode: false, // 禁用 ECharts 内置选择，使用自定义 itemStyle 高亮
            }],
        };
        chart.setOption(opt);

        // 点击单元格切换选中状态，并回调给调用方
        if (typeof onCellClick === 'function') {
            chart.on('click', params => {
                if (params && params.componentType === 'series') {
                    const suitIndex = params.value[0];
                    const rankIndex = params.value[1];
                    const suit = suits[suitIndex];
                    const rank = ranks[rankIndex];
                    const key = keyFor(suit, rank);
                    const wasSelected = selectedSet.has(key);
                    if (wasSelected) selectedSet.delete(key);
                    else selectedSet.add(key);

                    chart.setOption({ series: [{ data: buildSeriesData() }] });
                    onCellClick({ suit, rank, suitIndex, rankIndex, selected: !wasSelected });
                }
            });
        }

        return chart;
    }

    /**
     * 渲染问题 3 策略对比横向柱状图。
     * @param {string} containerId
     * @param {{pct:number}} newbie
     * @param {{pct:number}} expert
     * @returns {echarts.ECharts|null}
     */
    function renderProblem3(containerId, newbie, expert) {
        const data = [
            { name: '新手策略', value: newbie.pct },
            { name: '高手策略', value: expert.pct },
        ];
        const el = document.getElementById(containerId);
        if (!el) return null;
        const chart = echarts.init(el);
        const accent = getCSSColor('--accent', '#ffeb3b');
        const fg = getCSSColor('--fg', '#f5f5f5');
        const opt = {
            ...baseOption(),
            title: { text: '问题 3 策略对比', left: 'center', textStyle: { color: fg } },
            xAxis: {
                type: 'value',
                max: 100,
                axisLabel: { formatter: '{value}%', color: fg },
                splitLine: { lineStyle: { color: getCSSColor('--border', '#444') } },
            },
            yAxis: {
                type: 'category',
                data: data.map(d => d.name),
                axisLabel: { color: fg, fontSize: 14 },
                axisLine: { lineStyle: { color: getCSSColor('--border', '#444') } },
            },
            series: [{
                name: '得分概率',
                type: 'bar',
                data: data.map(d => d.value),
                barWidth: '40%',
                itemStyle: { color: accent, borderRadius: [0, 6, 6, 0] },
                label: { show: true, position: 'right', formatter: c => formatPct(c.value), fontSize: 14, fontWeight: 'bold' },
            }],
        };
        chart.setOption(opt);
        return chart;
    }

    /** 安全销毁 ECharts 实例。 */
    function dispose(chart) {
        if (chart && !chart.isDisposed()) {
            chart.dispose();
        }
    }

    return { renderProblem1, renderProblem2, renderProblem3, dispose };
})();
