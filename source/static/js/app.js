document.addEventListener('DOMContentLoaded', () => {
    const binaryInput = document.getElementById('binaryInput');
    const decimalInput = document.getElementById('decimalInput');
    const bit0Count = document.getElementById('bit0Count');
    const bit1Count = document.getElementById('bit1Count');
    const status = document.getElementById('status');
    const themeSelect = document.getElementById('themeSelect');
    const themeLink = document.getElementById('themeLink');

    const THEME_KEY = 'binary-theme';

    function showError(msg) {
        status.textContent = msg;
        status.style.display = 'block';
    }

    function clearError() {
        status.textContent = '';
        status.style.display = 'none';
    }

    function validateBinary(value) {
        const trimmed = value.trim();
        if (!trimmed) return '请输入二进制数';
        const parts = trimmed.replace(/^\.+|\.+$/g, '').split('.');
        for (const part of parts) {
            if (!part) continue;
            if (!/^[01]+$/.test(part)) {
                return `“${part}” 不是有效的二进制数，只能包含 0 和 1`;
            }
        }
        return null;
    }

    function validateDecimal(value) {
        const trimmed = value.trim();
        if (!trimmed) return '请输入十进制数';
        const parts = trimmed.replace(/^\.+|\.+$/g, '').split('.');
        for (const part of parts) {
            if (!part) continue;
            if (!/^-?\d+$/.test(part)) {
                return `“${part}” 不是有效的十进制数，只能包含数字`;
            }
        }
        return null;
    }

    function insertBit(textarea, countInput, bit) {
        const n = parseInt(countInput.value, 10);
        if (isNaN(n) || n <= 0) return;
        const text = bit.repeat(n);
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const before = textarea.value.slice(0, start);
        const after = textarea.value.slice(end);
        textarea.value = before + text + after;
        const cursor = start + text.length;
        textarea.selectionStart = cursor;
        textarea.selectionEnd = cursor;
        textarea.focus();
        clearError();
    }

    async function convert(endpoint, sourceEl, targetEl, validator) {
        const value = sourceEl.value;
        clearError();

        const error = validator(value);
        if (error) {
            showError(error);
            return;
        }

        try {
            const resp = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value })
            });
            const data = await resp.json();
            if (!resp.ok) {
                showError(data.error || '转换失败');
                return;
            }
            targetEl.value = data.result;
        } catch (err) {
            showError('网络请求失败：' + err.message);
        }
    }

    document.getElementById('btnBit0').addEventListener('click', () => {
        insertBit(binaryInput, bit0Count, '0');
    });

    document.getElementById('btnBit1').addEventListener('click', () => {
        insertBit(binaryInput, bit1Count, '1');
    });

    document.getElementById('btnBin2Dec').addEventListener('click', () => {
        convert('/api/binary-to-decimal', binaryInput, decimalInput, validateBinary);
    });

    document.getElementById('btnDec2Bin').addEventListener('click', () => {
        convert('/api/decimal-to-binary', decimalInput, binaryInput, validateDecimal);
    });

    document.getElementById('btnClear').addEventListener('click', () => {
        binaryInput.value = '';
        decimalInput.value = '';
        clearError();
        binaryInput.focus();
    });

    bit0Count.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            convert('/api/binary-to-decimal', binaryInput, decimalInput, validateBinary);
        }
    });

    bit1Count.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            convert('/api/decimal-to-binary', decimalInput, binaryInput, validateDecimal);
        }
    });

    // Theme switching with localStorage persistence
    async function loadThemes() {
        try {
            const resp = await fetch('/api/themes');
            const data = await resp.json();
            if (!resp.ok) {
                showError(data.error || '加载主题失败');
                return;
            }

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
            showError('加载主题失败：' + err.message);
        }
    }

    function applyTheme(name) {
        themeLink.href = `/static/css/themes/${name}`;
        localStorage.setItem(THEME_KEY, name);
    }

    themeSelect.addEventListener('change', () => {
        applyTheme(themeSelect.value);
    });

    loadThemes();
});
