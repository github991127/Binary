from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon

import Binary
from list_themes import *


class Stats:
    def __init__(self):
        # 从ui文件中加载UI定义,从UI定义中动态创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了.比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('Binary.ui')

        self.ui.toolButton_1.clicked.connect(self.handleCalc0)
        self.ui.toolButton_2.clicked.connect(self.handleCalc1)
        self.ui.toolButton_3.clicked.connect(self.handleCalc_binary_to_decimal)
        self.ui.toolButton_4.clicked.connect(self.handleCalc_decimal_to_binary)
        self.ui.toolButton_5.clicked.connect(self.handleCalc2)
        self.ui.lineEdit_1.returnPressed.connect(self.handleCalc_binary_to_decimal)
        self.ui.lineEdit_2.returnPressed.connect(self.handleCalc_decimal_to_binary)

    def handleCalc0(self):
        str = self.ui.lineEdit_1.text()
        count = int(str)
        str0 = '0' * count
        self.ui.textEdit_1.insertPlainText(str0)

    def handleCalc1(self):
        str = self.ui.lineEdit_2.text()
        count = int(str)
        str1 = '1' * count
        self.ui.textEdit_1.insertPlainText(str1)

    def handleCalc2(self):
        self.ui.textEdit_1.clear()
        self.ui.textEdit_2.clear()

    def handleCalc_binary_to_decimal(self):
        binary = self.ui.textEdit_1.toPlainText()
        decimal = Binary.binary_to_decimal(binary)
        self.ui.textEdit_2.setText(decimal)

    def handleCalc_decimal_to_binary(self):
        decimal = self.ui.textEdit_2.toPlainText()
        binary = Binary.decimal_to_binary(decimal)
        self.ui.textEdit_1.setText(binary)


if __name__ == '__main__':
    app = QApplication([])
    app.setWindowIcon(QIcon('image.png'))
    apply_stylesheet(app, theme[32], extra=extra, invert_secondary=False)  # 默认dark-False
    w = QWidget()
    w.setWindowIcon(QIcon('image.png'))
    stats = Stats()
    stats.ui.show()
    app.exec_()
