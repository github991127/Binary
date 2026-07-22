/**
 * 前端主入口模块。
 *
 * 负责：
 * - 主题加载与切换（持久化到 localStorage）
 * - Tab 导航与 ARIA 状态同步
 * - 牌库表格初始化
 * - 关键 tag 选择状态管理（默认选中第一个 tag）
 * - 问题 1/2/3 的请求、渲染与交互
 * - 问题 2 热力图多选状态管理，以及与牌库的筛选联动
 */
document.addEventListener('DOMContentLoaded', () => {
    const toast = document.getElementById('toast');
    const themeSelect = document.getElementById('themeSelect');
    const themeLink = document.getElementById('themeLink');
    const THEME_KEY = 'card-prob-theme';
    const TAGS_KEY = 'card-prob-selected-tags';

    let deckData = null;           // /api/deck 返回的牌库原始数据
    let selectedTags = [];         // 当前选中的关键 tag
    let charts = [];               // 当前 Tab 中活跃的 ECharts 实例，切页前销毁
    let p2Groups = [];             // 问题 2 当前返回的 52 个组合（用于无选择时回显全部）
    const p2Selections = new Map(); // 问题 2 已选组合：key = suit|rank，value = { suit, rank, group }

    /** 生成花色+点数组合的唯一键，用于 Map 索引。 */
    function getP2Key(suit, rank) {
        return `${suit}|${rank}`;
    }

    /**
     * 显示临时提示信息。
     * @param {string} msg
     * @param {number} [duration=3000] 毫秒
     */
    function showToast(msg, duration = 3000) {
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), duration);
    }

    /**
     * 通用 fetch 请求封装，统一处理 JSON 解析、后端错误码与 Toast 提示。
     * @param {string} url
     * @param {RequestInit} [options]
     * @returns {Promise<Object>}
     */
    async function apiFetch(url, options) {
        try {
            const resp = await fetch(url, options);
            const data = await resp.json();
            if (!resp.ok || !data.ok) {
                throw new Error(data.error || '请求失败');
            }
            return data;
        } catch (err) {
            showToast(err.message || '网络请求失败');
            throw err;
        }
    }

    /** 销毁当前所有 ECharts 实例，避免切页/重绘时内存泄漏。 */
    function disposeCharts() {
        charts.forEach(c => { if (c && !c.isDisposed()) { c.dispose(); } });
        charts = [];
    }

    /**
     * 切换到指定 Tab，同步按钮和面板的 active 状态及 ARIA 属性。
     * @param {string} tabName - 'deck' | 'p1' | 'p2' | 'p3'
     */
    function activateTab(tabName) {
        tabButtons.forEach(b => {
            const isTarget = b.dataset.tab === tabName;
            b.classList.toggle('active', isTarget);
            b.setAttribute('aria-selected', isTarget ? 'true' : 'false');
        });
        tabPanels.forEach(p => p.classList.remove('active'));
        const targetPanel = document.getElementById('tab-' + tabName);
        if (targetPanel) targetPanel.classList.add('active');
    }

    // Tabs：绑定点击，切换到问题 2 时若牌库已加载则自动请求数据
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            activateTab(btn.dataset.tab);
            if (btn.dataset.tab === 'p2' && deckData) {
                loadProblem2();
            }
        });
    });

    /**
     * 加载主题列表，合并后端默认主题与用户本地保存偏好，
     * 然后应用主题。
     */
    async function loadThemes() {
        try {
            const data = await apiFetch('/api/themes');
            const saved = localStorage.getItem(THEME_KEY);
            let selectedIndex = data.current;
            if (saved) {
                const idx = data.themes.indexOf(saved);
                if (idx >= 0) selectedIndex = idx;
            }
            themeSelect.innerHTML = '';
            data.themes.forEach((name, idx) => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name.replace(/\.css$/, '');
                if (idx === selectedIndex) opt.selected = true;
                themeSelect.appendChild(opt);
            });
            applyTheme(themeSelect.value);
        } catch (err) {
            console.error('loadThemes failed:', err);
            showToast('加载主题失败');
        }
    }

    /**
     * 应用指定主题 CSS 并持久化到 localStorage；短暂延迟后触发图表 resize。
     * @param {string} name
     */
    function applyTheme(name) {
        themeLink.href = '/static/css/themes/' + name;
        localStorage.setItem(THEME_KEY, name);
        setTimeout(() => {
            charts.forEach(c => { if (c && c.resize) c.resize(); });
        }, 50);
    }

    themeSelect.addEventListener('change', () => applyTheme(themeSelect.value));

    // tag 选择器
    const tagSelectorEl = document.getElementById('tagSelector');

    /**
     * 根据 /api/deck 返回的 available_tags 渲染勾选区。
     * 默认选中第一个 tag；若本地有保存则恢复。
     * @param {string[]} availableTags
     * @param {Object<string,string>} tagDisplayNames
     */
    function renderTagSelector(availableTags, tagDisplayNames) {
        const optionsEl = tagSelectorEl.querySelector('.tag-options');
        optionsEl.innerHTML = '';
        if (!availableTags || availableTags.length === 0) {
            optionsEl.textContent = '无 tag 列';
            selectedTags = [];
            return;
        }

        // 初始化选中：本地有合法保存则恢复，否则默认第一个
        const saved = localStorage.getItem(TAGS_KEY);
        let initial = [];
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                initial = parsed.filter(t => availableTags.includes(t));
            } catch { /* ignore */ }
        }
        if (initial.length === 0) {
            initial = [availableTags[0]];
        }
        selectedTags = initial;

        availableTags.forEach(tag => {
            const label = document.createElement('label');
            label.className = 'tag-option';
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.value = tag;
            cb.checked = selectedTags.includes(tag);
            cb.addEventListener('change', () => {
                if (cb.checked) {
                    selectedTags = [...selectedTags, tag];
                } else {
                    selectedTags = selectedTags.filter(t => t !== tag);
                }
                localStorage.setItem(TAGS_KEY, JSON.stringify(selectedTags));
                if (deckData) {
                    Cards.refreshTagColumn(selectedTags);
                    Cards.applyFilter();
                }
            });
            label.appendChild(cb);
            label.appendChild(document.createTextNode(tagDisplayNames?.[tag] || tag));
            optionsEl.appendChild(label);
        });
    }

    // 牌库：绑定清除筛选按钮，初始化表格并加载数据
    document.getElementById('deckClearFilter').addEventListener('click', () => {
        Cards.clearFilter();
    });
    Cards.init();
    Cards.load().then(data => {
        deckData = data;
        renderTagSelector(data.available_tags, data.tag_display_names);
        Cards.setAvailableTags(data.available_tags, data.tag_display_names);
        Cards.refreshTagColumn(selectedTags);
        Cards.applyFilter();
    }).catch(() => {});

    // 问题 1：绑定输入框回车与计算按钮
    const p1InputA = document.getElementById('p1InputA');
    const p1InputB = document.getElementById('p1InputB');
    document.getElementById('p1Calc').addEventListener('click', () => calcProblem1());
    p1InputA.addEventListener('keydown', e => { if (e.key === 'Enter') calcProblem1(); });
    p1InputB.addEventListener('keydown', e => { if (e.key === 'Enter') calcProblem1(); });

    /**
     * 读取输入 a、b，请求后端计算问题 1 的超几何分布。
     */
    async function calcProblem1() {
        const a = p1InputA.value;
        const b = p1InputB.value;
        try {
            const data = await apiFetch('/api/problem1', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ a, b, tags: selectedTags }),
            });
            renderProblem1(data);
        } catch (err) { /* apiFetch 已显示 Toast */ }
    }

    /**
     * 渲染问题 1 结果：统计卡片、柱状图、PMF 与至少 k 分概率表。
     * @param {Object} data - /api/problem1 返回数据
     */
    function renderProblem1(data) {
        const stats = document.getElementById('p1Stats');
        stats.innerHTML = `
            <div class="stat-card"><div class="label">总牌数 N</div><div class="value">${data.N}</div></div>
            <div class="stat-card"><div class="label">关键牌 K</div><div class="value">${data.K}</div></div>
            <div class="stat-card"><div class="label">抽牌数 a</div><div class="value">${data.a}</div></div>
            <div class="stat-card"><div class="label">最大得分 b</div><div class="value">${data.b}</div></div>
            <div class="stat-card"><div class="label">期望值</div><div class="value">${data.expected_value.toFixed(3)}</div></div>
        `;

        disposeCharts();
        charts = [Charts.renderProblem1('p1Chart', data.pmf, data.at_least)];

        const table = document.getElementById('p1Table');
        table.innerHTML = `
            <thead>
                <tr><th>得分 k</th><th>概率 P(X = k)</th><th>概率 P(X ≥ k)</th></tr>
            </thead>
            <tbody>
                ${data.pmf.map((p, i) => {
                    const at = data.at_least[i];
                    return `
                    <tr>
                        <td>${p.k}</td>
                        <td><strong>${p.pct.toFixed(2)}%</strong> <span class="frac">(${p.exact})</span></td>
                        <td>${at ? `<strong>${at.pct.toFixed(2)}%</strong> <span class="frac">(${at.exact})</span>` : '-'}</td>
                    </tr>`;
                }).join('')}
            </tbody>
        `;
    }

    // 问题 2：绑定清空选择、跳转牌库按钮
    document.getElementById('p2ClearSelection').addEventListener('click', clearP2Selections);
    document.getElementById('p2GotoDeck').addEventListener('click', () => {
        if (!p2Selections.size) {
            showToast('请先在热力图中选择至少一个组合');
            return;
        }
        const combos = [...p2Selections.values()].map(s => ({ suit: s.suit, rank: s.rank }));
        Cards.setFilter({ combos });
        activateTab('deck');
    });

    /** 清空问题 2 的所有选择状态，并重新渲染热力图与下方表格。 */
    function clearP2Selections() {
        p2Selections.clear();
        loadProblem2();
    }

    /**
     * 从后端加载问题 2 数据，缓存 groups，并渲染热力图。
     */
    async function loadProblem2() {
        try {
            const data = await apiFetch('/api/problem2', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tags: selectedTags }),
            });
            p2Groups = data.groups || [];
            renderProblem2(data);
        } catch (err) { /* apiFetch 已显示 Toast */ }
    }

    /**
     * 渲染问题 2：统计卡片 + 多选热力图 + 已选组合详情表格。
     * @param {Object} data - /api/problem2 返回数据
     */
    function renderProblem2(data) {
        const stats = document.getElementById('p2Stats');
        stats.innerHTML = `
            <div class="stat-card"><div class="label">总牌数 N</div><div class="value">${data.N}</div></div>
            <div class="stat-card"><div class="label">关键牌 K</div><div class="value">${data.K}</div></div>
            <div class="stat-card"><div class="label">组合数</div><div class="value">${data.groups.length}</div></div>
        `;

        disposeCharts();
        charts = [Charts.renderProblem2('p2Chart', data.groups, {
            selectedKeys: [...p2Selections.keys()],
            onCellClick: ({ suit, rank, selected }) => {
                const key = getP2Key(suit, rank);
                const group = data.groups.find(g => g.suit === suit && g.rank === rank);
                if (selected && group) {
                    p2Selections.set(key, { suit, rank, group });
                } else {
                    p2Selections.delete(key);
                }
                updateP2SelectionUI();
            },
        })];

        updateP2SelectionUI();
    }

    /**
     * 根据 p2Selections 更新标题与下方详情表格。
     * 未选择时回显全部组合；已选择时列出选中的组合汇总。
     */
    function updateP2SelectionUI() {
        const title = document.getElementById('p2SelectionTitle');
        const tbody = document.querySelector('#p2Table tbody');

        if (!p2Selections.size) {
            title.textContent = '已选组合：未选择';
            tbody.innerHTML = p2Groups.map(g => `
                <tr data-suit="${esc(g.suit)}" data-rank="${g.rank}">
                    <td>${g.suit}</td>
                    <td>${g.rank}</td>
                    <td>${g.size}</td>
                    <td>${g.keys}</td>
                    <td><strong>${g.prob_pct.toFixed(2)}%</strong> <span class="frac">(${g.prob_exact})</span></td>
                </tr>
            `).join('');
            return;
        }

        title.textContent = `已选组合：${p2Selections.size} 个`;
        tbody.innerHTML = [...p2Selections.values()].map(s => `
            <tr class="selected" data-suit="${esc(s.suit)}" data-rank="${s.rank}">
                <td>${s.suit}</td>
                <td>${s.rank}</td>
                <td>${s.group.size}</td>
                <td>${s.group.keys}</td>
                <td><strong>${s.group.prob_pct.toFixed(2)}%</strong> <span class="frac">(${s.group.prob_exact})</span></td>
            </tr>
        `).join('');
    }

    // 问题 3：绑定输入框回车与计算按钮
    const p3InputA = document.getElementById('p3InputA');
    document.getElementById('p3Calc').addEventListener('click', () => calcProblem3());
    p3InputA.addEventListener('keydown', e => { if (e.key === 'Enter') calcProblem3(); });

    /**
     * 读取输入 a，请求后端计算问题 3 的新手/高手策略概率。
     */
    async function calcProblem3() {
        const a = p3InputA.value;
        try {
            const data = await apiFetch('/api/problem3', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ a, tags: selectedTags }),
            });
            renderProblem3(data);
        } catch (err) { /* apiFetch 已显示 Toast */ }
    }

    /**
     * 渲染问题 3 结果：统计卡片与策略对比柱状图。
     * @param {Object} data - /api/problem3 返回数据
     */
    function renderProblem3(data) {
        const stats = document.getElementById('p3Stats');
        stats.innerHTML = `
            <div class="stat-card"><div class="label">总牌数 N</div><div class="value">${data.N}</div></div>
            <div class="stat-card"><div class="label">关键牌 K</div><div class="value">${data.K}</div></div>
            <div class="stat-card"><div class="label">抽牌数 a</div><div class="value">${data.a}</div></div>
            <div class="stat-card"><div class="label">新手策略</div><div class="value">${data.newbie.pct.toFixed(2)}%</div></div>
            <div class="stat-card"><div class="label">高手策略</div><div class="value">${data.expert.pct.toFixed(2)}%</div></div>
        `;

        disposeCharts();
        charts = [Charts.renderProblem3('p3Chart', data.newbie, data.expert)];
    }

    /**
     * 简单的 HTML 转义工具，防止表格内容破坏 DOM。
     * @param {string} s
     * @returns {string}
     */
    function esc(s) {
        const div = document.createElement('div');
        div.textContent = s;
        return div.innerHTML;
    }

    // 窗口大小变化时重绘所有图表
    window.addEventListener('resize', () => {
        charts.forEach(c => { if (c && c.resize) c.resize(); });
    });

    // 初始化
    loadThemes();
});
