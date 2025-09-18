"""
GUI样式定义模块
"""

STYLES = {
    "button": """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            min-width: 60px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QPushButton:disabled {
            background-color: #cccccc;
        }
    """,
    "input": """
        QLineEdit, QTextEdit, QListWidget, QComboBox, QSpinBox, QDoubleSpinBox {
            border: 1px solid #ccc;
            border-radius: 3px;
            padding: 3px;
        }
    """,
    "groupbox": """
        QGroupBox {
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 15px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
        }
    """,
    "textedit": """
        QTextEdit {
            font-family: 'Consolas', 'Courier New', monospace;
        }
    """
}