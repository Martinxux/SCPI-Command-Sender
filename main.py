#!/usr/bin/env python3
"""
SCPI Command Sender 入口文件
简化运行方式：直接 python main.py
"""

import sys
from scpi_app.gui.scpi_gui import SCPIGUI
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SCPIGUI()
    window.show()
    sys.exit(app.exec_())