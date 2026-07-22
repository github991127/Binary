/**
 * 牌库表格模块。
 *
 * 负责：
 * - 从 /api/deck 加载牌库数据
 * - 关键字筛选（名称 / 花色 / 点数 / tag 内容）
 * - 列排序（点击表头）
 * - 分页
 * - 动态 tag 列渲染与勾选联动
 * - 外部组合筛选：setFilter({ suit, rank }) 可与问题 2 热力图联动
 */
const Cards = (() => {
    let allRows = [];          // 全部原始牌数据
    let filteredRows = [];     // 经筛选/排序后的数据
    let pageSize = 20;         // 每页条数
    let currentPage = 1;       // 当前页码
    let sortKey = 'id';        // 当前排序列
    let sortAsc = true;        // 升序/降序
    let externalFilter = null; // { suit?, rank? } 或 { combos: [{suit, rank}, ...] }，由问题 2 热力图传入
    let availableTags = [];    // 当前牌库拥有的 tag 列名
    let selectedTags = [];     // 当前被选中的 tag 列名
    let tagDisplayNames = {};  // tag 列名 -> 显示名称

    // DOM 引用
    const table = document.getElementById('deckTable');
    const theadRow = table ? table.querySelector('thead tr') : null;
    const tbody = table ? table.querySelector('tbody') : null;
    const summaryEl = document.getElementById('deckSummary');
    const filterInput = document.getElementById('deckFilter');
    const pageSizeSelect = document.getElementById('deckPageSize');
    const pagerEl = document.getElementById('deckPager');

    /** 初始化事件监听。 */
    function init() {
        if (!table || !tbody) return;

        // 表头排序
        theadRow.addEventListener('click', e => {
            const th = e.target.closest('th[data-sort]');
            if (!th) return;
            const key = th.dataset.sort;
            if (sortKey === key) {
                sortAsc = !sortAsc;
            } else {
                sortKey = key;
                sortAsc = true;
            }
            currentPage = 1;
            applyFilter();
        });

        // 关键字筛选：实时过滤
        filterInput.addEventListener('input', () => {
            currentPage = 1;
            applyFilter();
        });

        // 每页条数改变
        pageSizeSelect.addEventListener('change', () => {
            pageSize = parseInt(pageSizeSelect.value, 10) || 20;
            currentPage = 1;
            render();
        });
    }

    /** 设置当前牌库拥有的 tag 列名与显示名称映射。 */
    function setAvailableTags(tags, displayNames) {
        availableTags = tags || [];
        tagDisplayNames = displayNames || {};
    }

    /** 根据选中的 tag 列重建表头（ID / 名称 / 花色 / 点数 + tag 列）。 */
    function refreshTagColumn(tags) {
        selectedTags = tags || [];
        if (!theadRow) return;

        // 保留前 4 个固定列，移除旧的 tag 列
        const fixed = Array.from(theadRow.children).slice(0, 4);
        theadRow.innerHTML = '';
        fixed.forEach(th => theadRow.appendChild(th));

        selectedTags.forEach(tag => {
            const th = document.createElement('th');
            th.dataset.sort = `tag:${tag}`;
            th.textContent = tagDisplayNames[tag] || tag;
            theadRow.appendChild(th);
        });
    }

    /** 从后端加载牌库数据并渲染概览表格。 */
    function load() {
        return fetch('/api/deck')
            .then(r => r.json())
            .then(data => {
                if (!data.ok) throw new Error(data.error || '加载牌库失败');
                allRows = data.rows || [];
                const displayNames = data.tag_display_names || {};
                const displayList = data.available_tags.map(t => displayNames[t] || t);
                summaryEl.innerHTML = `
                    <span>总牌数：<strong>${data.total}</strong></span>
                    <span>可选关键 tag：<strong>${displayList.join('、') || '无'}</strong></span>
                `;
                applyFilter();
                return data;
            });
    }

    /**
     * 外部设置组合筛选条件（来自问题 2 热力图）。
     * @param {Object} options
     * @param {string} [options.suit] 花色符号
     * @param {number} [options.rank] 点数
     * @param {Array<{suit:string, rank:number}>} [options.combos] 多个组合
     */
    function setFilter(filter = {}) {
        if (filter && Array.isArray(filter.combos)) {
            externalFilter = { combos: filter.combos };
        } else {
            externalFilter = { suit: filter.suit, rank: filter.rank };
        }
        filterInput.value = '';
        currentPage = 1;
        applyFilter();
    }

    /** 清除外部筛选并重新加载全部数据。 */
    function clearFilter() {
        externalFilter = null;
        filterInput.value = '';
        currentPage = 1;
        applyFilter();
    }

    /** 综合外部筛选与关键字筛选，然后排序、渲染。 */
    function applyFilter() {
        const kw = (filterInput.value || '').trim().toLowerCase();
        filteredRows = allRows.filter(r => {
            // 关键字匹配：名称、花色符号、点数、tag 字段
            const tagTexts = selectedTags.map(t => String(r.tags?.[t] || '')).filter(Boolean);
            const matchKw = !kw
                || String(r.name || '').toLowerCase().includes(kw)
                || String(r.color2 || '').includes(kw)
                || String(r.number || '').includes(kw)
                || tagTexts.some(text => text.toLowerCase().includes(kw));

            // 外部组合筛选（来自问题 2 热力图）：支持多个组合或单 suit/rank
            let matchCombo = true;
            if (externalFilter) {
                if (Array.isArray(externalFilter.combos) && externalFilter.combos.length > 0) {
                    matchCombo = externalFilter.combos.some(c =>
                        r.color2 === c.suit && r.number === c.rank
                    );
                } else {
                    const matchSuit = !externalFilter.suit || r.color2 === externalFilter.suit;
                    const matchRank = externalFilter.rank == null || r.number === externalFilter.rank;
                    matchCombo = matchSuit && matchRank;
                }
            }
            return matchKw && matchCombo;
        });
        sortRows();
        render();
    }

    /** 根据当前 sortKey / sortAsc 对筛选结果排序。 */
    function sortRows() {
        filteredRows.sort((a, b) => {
            let va, vb;
            if (sortKey.startsWith('tag:')) {
                const tag = sortKey.slice(4);
                va = a.tags?.[tag] || '';
                vb = b.tags?.[tag] || '';
            } else {
                va = a[sortKey];
                vb = b[sortKey];
            }
            if (typeof va === 'string') va = va.toLowerCase();
            if (typeof vb === 'string') vb = vb.toLowerCase();
            if (va < vb) return sortAsc ? -1 : 1;
            if (va > vb) return sortAsc ? 1 : -1;
            return 0;
        });
    }

    /** 渲染当前页数据与分页按钮。 */
    function render() {
        const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));
        if (currentPage > totalPages) currentPage = totalPages;
        const start = (currentPage - 1) * pageSize;
        const pageRows = filteredRows.slice(start, start + pageSize);

        tbody.innerHTML = pageRows.map(r => `
            <tr data-id="${r.id}">
                <td>${r.id}</td>
                <td>${esc(r.name)}</td>
                <td>${esc(r.color2)}</td>
                <td>${r.number}</td>
                ${selectedTags.map(t => `<td>${esc(r.tags?.[t] || '')}</td>`).join('')}
            </tr>
        `).join('');

        renderPager(totalPages);
    }

    /** 生成分页按钮。 */
    function renderPager(totalPages) {
        pagerEl.innerHTML = '';
        if (totalPages <= 1) return;

        const makeBtn = (label, page, disabled) => {
            const btn = document.createElement('button');
            btn.textContent = label;
            btn.disabled = disabled;
            btn.type = 'button';
            btn.addEventListener('click', () => {
                currentPage = page;
                render();
            });
            return btn;
        };

        pagerEl.appendChild(makeBtn('上一页', currentPage - 1, currentPage === 1));
        const info = document.createElement('span');
        info.textContent = ` ${currentPage} / ${totalPages} `;
        pagerEl.appendChild(info);
        pagerEl.appendChild(makeBtn('下一页', currentPage + 1, currentPage === totalPages));
    }

    /** HTML 转义，防止名称或花色符号破坏表格。 */
    function esc(s) {
        const div = document.createElement('div');
        div.textContent = s;
        return div.innerHTML;
    }

    return { init, load, setFilter, clearFilter, setAvailableTags, refreshTagColumn, applyFilter };
})();
