"""
通用UI组件模块
"""
from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton
)


def create_labeled_input(label_text, placeholder="") -> tuple:
    """创建带标签的输入框组件"""
    layout = QHBoxLayout()
    label = QLabel(label_text)
    input_field = QLineEdit()
    input_field.setPlaceholderText(placeholder)
    layout.addWidget(label)
    layout.addWidget(input_field)
    return layout, input_field


def create_button(text, callback=None) -> QPushButton:
    """创建标准按钮"""
    button = QPushButton(text)
    if callback:
        button.clicked.connect(callback)
    return button


def create_group_box(title, layout=None) -> QGroupBox:
    """创建分组框"""
    group = QGroupBox(title)
    if layout:
        group.setLayout(layout)
    return group