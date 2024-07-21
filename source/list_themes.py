# https://github.com/UN-GCPDS/qt-material
# from qt_material import list_themes
# from pprint import pprint  # 导入pprint接口，可以打印出更加漂亮的list列表数据
from qt_material import apply_stylesheet

theme = ['dark_amber.xml',  # 琥珀0
         'dark_blue.xml',  # 蓝色1
         'dark_cyan.xml',
         'dark_lightgreen.xml',
         'dark_medical.xml',
         'dark_pink.xml',  # 粉色5
         'dark_purple.xml',  # 紫色6
         'dark_red.xml',  # 红色7
         'dark_teal.xml',  # 蓝绿8
         'dark_yellow.xml',
         'light_amber.xml',  # 琥珀10
         'light_blue.xml',
         'light_blue_500.xml',  # 蓝色12
         'light_cyan.xml',
         'light_cyan_500.xml',
         'light_lightgreen.xml',
         'light_lightgreen_500.xml',
         'light_orange.xml',
         'light_pink.xml',  # 粉色18
         'light_pink_500.xml',
         'light_purple.xml',
         'light_purple_500.xml',  # 紫色21
         'light_red.xml',
         'light_red_500.xml',  # 红色23
         'light_teal.xml',
         'light_teal_500.xml',  # 蓝绿25
         'light_yellow.xml',

         'my_dark_white.xml',  # 黑色27
         'my_light_black.xml',  # 白色28
         'my_dark_R.xml',  # 红色29
         'my_light_R.xml',  # 红色30
         'my_dark_G.xml',  # 绿色31
         'my_light_G.xml',  # 绿色32
         'my_dark_B.xml',  # 蓝色33
         'my_light_B.xml',  # 蓝色34
         'my_dark_Y.xml',  # 黄色35
         'my_light_P.xml',  # 黄色36

         ]

extra = {
    # Button colors
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#17a2b8',

    # Font
    'font_family': '微软雅黑',
    'font_size': '16px',
    'line_height': '0px',

    # Density Scale
    'density_scale': '3',

    # environ
    'pyside6': False,
    'linux': False,
}

if __name__ == '__main__':
    x = 28  # 0-28
    # app = QApplication([])
    # apply_stylesheet(app, theme[x])
    # stats = Stats()
    # stats.ui.show()
    # app.exec_()

    print(theme[x])
    # pprint('总计主题样式：{} 种！'.format(len(list_themes())))
    # pprint(list_themes())
