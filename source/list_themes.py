from pathlib import Path

# 主题列表对应 static/css/themes/ 下的 CSS 文件
theme = [
    'dark_amber.css',        # 琥珀 0
    'dark_blue.css',         # 蓝色 1
    'dark_cyan.css',
    'dark_lightgreen.css',
    'dark_medical.css',
    'dark_pink.css',         # 粉色 5
    'dark_purple.css',       # 紫色 6
    'dark_red.css',          # 红色 7
    'dark_teal.css',         # 蓝绿 8
    'dark_yellow.css',
    'light_amber.css',       # 琥珀 10
    'light_blue.css',
    'light_blue_500.css',    # 蓝色 12
    'light_cyan.css',
    'light_cyan_500.css',
    'light_lightgreen.css',
    'light_lightgreen_500.css',
    'light_orange.css',
    'light_pink.css',        # 粉色 18
    'light_pink_500.css',
    'light_purple.css',
    'light_purple_500.css',  # 紫色 21
    'light_red.css',
    'light_red_500.css',     # 红色 23
    'light_teal.css',
    'light_teal_500.css',    # 蓝绿 25
    'light_yellow.css',

    'my_dark_white.css',     # 黑色 27
    'my_light_black.css',    # 白色 28
    'my_dark_R.css',         # 红色 29
    'my_light_R.css',        # 红色 30
    'my_dark_G.css',         # 绿色 31
    'my_light_G.css',        # 绿色 32
    'my_dark_B.css',         # 蓝色 33
    'my_light_B.css',        # 蓝色 34
    'my_dark_Y.css',         # 黄色 35
    'my_light_P.css',        # 黄色 36
]

# 默认主题索引，与原始 Qt 版本一致（my_dark_Y）
default_theme_index = 35

extra = {
    # Button colors
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#17a2b8',

    # Font
    'font_family': '"Microsoft YaHei", "微软雅黑", "Heiti SC", sans-serif',
    'font_size': '16px',
    'line_height': '1.4',

    # Density Scale
    'density_scale': '3',
}


def theme_css_name(index=None):
    """返回用于 <link> 的主题 CSS 文件名。"""
    if index is None:
        index = default_theme_index
    return theme[int(index) % len(theme)]


if __name__ == '__main__':
    print(theme_css_name(default_theme_index))
