"""
GUI样式定义模块
"""
execution_state_STYLES = {
    'idle': {
                'text': "🟡 空闲",
                'style': """
                    QLabel {
                        background-color: #fff8e1;
                        color: #ff8f00;
                    }
                """
            },
            'executing': {
                'text': "🟠 执行中", 
                'style': """
                    QLabel {
                        background-color: #fff3e0;
                        color: #e65100;
                    }
                """
            },
            'completed': {
                'text': "🟢 完成",
                'style': """
                    QLabel {
                        background-color: #e8f5e9;
                        color: #2e7d32;
                    }
                """
            },
            'error': {
                'text': "🔴 错误",
                'style': """
                    QLabel {
                        background-color: #ffebee;
                        color: #c62828;
                    }
                """
            }
}
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
    """,
    "hostconnect": """
            QGroupBox { 
                background-color: #f9f9f9;
                padding: 10px;
            }
        """,
    "connectbtn": """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """,
    "Label_not_acquired": """
            QLabel {
                padding: 2px 8px;
                border-radius: 3px;
                background-color: #e3f2fd;
                color: #0d47a1;
                font: 9pt;
                min-width: 200px;
                qproperty-alignment: AlignCenter;
            }
        """,
    "SavePresetBtn": """
            background-color: #2196F3;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            min-width: 60px;
        """,
    "DelPresetBtn": """
            background-color: #F44336;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            min-width: 60px;
        """,
    "cmdlist": """
            QListWidget {
                border: 1px solid #ddd;
                background-color: white;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e0f7fa;
                color: black;
            }
        """,
    "loop_preset_btn": """
            QPushButton {
                background-color: #9C27B0;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """,
    "stop_loop_btn": """
            QPushButton {
                background-color: #f44336;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """,
    "progressbar": """
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """,
    "QTextEdit_output": """
            QTextEdit {
                background-color: #263238;
                color: #ECEFF1;
                border: 1px solid #37474F;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
            }
        """,
    "QStatusBar": """
            QStatusBar {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
                font-size: 9pt;
            }
        """,
    "QLabel_noconnect": """
            QLabel {
                padding: 2px 8px;
                border-radius: 3px;
                background-color: #ffebee;
                color: #c62828;
                font-weight: bold;
            }
        """,
    "QLabel_idle": """
            QLabel {
                padding: 2px 8px;
                border-radius: 3px;
                background-color: #fff8e1;
                color: #ff8f00;
                font-weight: bold;
            }
        """,
    "disconnect_status": """
                    QLabel {
                        background-color: #ffebee;
                        color: #c62828;
                    }
                """
}