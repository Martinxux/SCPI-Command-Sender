import os
import sys
import time
import json

# PyQt5 相关导入
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QListWidget, QComboBox, QMessageBox, QFileDialog, QGroupBox, QInputDialog,
    QStatusBar, QDialog, QProgressBar, QMenu, QTextBrowser
)

# 本地模块导入
from scpi_app.core.logger import logger
from scpi_app.core.ezsetting import DCAConfigurator
from scpi_app.core.scpi import SCPIError, SCPIInstrument
from .styles import STYLES, execution_state_STYLES

VERSION = "v2.1.0.20250918"

class SCPIWorker(QThread):
    """用于在后台执行SCPI命令的工作线程"""
    command_sent = pyqtSignal(str, str, int)  # 信号：命令发送、响应和循环次数
    progress_updated = pyqtSignal(int, int)  # 信号：当前进度和总命令数
    finished = pyqtSignal()  # 信号：任务完成
    error_occurred = pyqtSignal(str)  # 信号：错误发生

    def __init__(self, instrument, commands, repeat, interval):
        super().__init__()
        self.instrument = instrument
        self.commands = commands
        self.repeat = repeat
        self.interval = interval
        self._is_running = True

    def stop(self):
        """请求停止执行"""
        self._is_running = False

    def run(self):
        """
        线程执行的主方法
        
        注意: 此方法运行在独立线程中，所有GUI操作必须通过信号槽完成
        """
        try:
            if not self._is_running:
                return
                
            total_commands = len(self.commands) * self.repeat
            commands_executed = 0
            
            for loop in range(self.repeat):
                loop_num = loop + 1  # 循环次数从1开始计数
                for cmd in self.commands:
                    if not self._is_running:
                        self.finished.emit()
                        return
                        
                    try:
                        response = self.instrument.send_command(cmd)
                        if cmd.endswith('?'):
                            self.command_sent.emit(cmd, str(response) if response else "No response", loop_num)
                        else:
                            self.command_sent.emit(cmd, "", loop_num)
                        commands_executed += 1
                        self.progress_updated.emit(commands_executed, total_commands)

                        # 等待间隔(最后一次循环的最后一个命令后不等待)
                        if not (loop == self.repeat - 1 and cmd == self.commands[-1]):
                            time.sleep(self.interval)

                    except SCPIError as e:
                        self.error_occurred.emit(str(e))
                        return

            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(f"意外错误: {str(e)}")


class SCPIGUI(QMainWindow):
    """SCPI命令发送器的主GUI窗口"""
    def __init__(self):
        super().__init__()
        self.instrument_info = None
        self.instrument = None
        self.worker = None
        self.presets = {}  # 存储预设配置
        self.current_preset = None
        self.configurator = DCAConfigurator()  # 初始化配置加载器
        
        # 设置窗口图标
        icon_path = "./ico/logo.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.warning(f"图标文件未找到: {icon_path}")
            
        # 初始化菜单栏
        self.init_menu_bar()
        
        self.init_ui()
        self.setWindowTitle("SCPI Command Sender")
        self.resize(660, 800)
        self.load_default_presets()
        
        # 自动加载配置文件
        config_path = "config/dcasetting.ini"
        if os.path.exists(config_path):
            try:
                configurations = self.configurator.load_configurations(config_path)
                self.config_combo.clear()
                self.config_combo.addItems(configurations.keys())
                self.output_area.append(f"[设置] 加载成功: {config_path}")
            except Exception as e:
                self.output_area.append(f"[设置] 加载失败: {str(e)}")
        else:
            self.output_area.append(f"[设置] 设置文件未找到: {config_path}")
        
        # 连接输出区域的自动滚动
        self.output_area.textChanged.connect(self.auto_scroll_output)

    def init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        # 读取说明选项
        about_action = help_menu.addAction("ReadMe")
        about_action.triggered.connect(self.ShowReadMe)
        # 关于选项
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self.show_about)

    def ShowReadMe(self):
        # 渲染README.md内容到窗口
        class MarkdownViewer(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("README")
                self.setGeometry(100, 100, 800, 600)
                layout = QVBoxLayout()
                self.text_browser = QTextBrowser()
                layout.addWidget(self.text_browser)
                self.setLayout(layout)

        readme_path = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")
        if os.path.exists(readme_path):
            viewer = MarkdownViewer(self)
            with open(readme_path, "r", encoding="utf-8") as f:
                viewer.text_browser.setMarkdown(f.read())
            viewer.exec_()
        else:
            self.show_error("未找到README.md文件")
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", f"SCPI Command Sender\n版本: {VERSION}")
        
    def init_ui(self):
        """初始化用户界面"""
        # 主布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # 设置全局样式
        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }}
            {STYLES["button"]}
            {STYLES["input"]}
            {STYLES["groupbox"]}
            {STYLES["textedit"]}
            /* 连接状态指示器 */
            .connected {{ color: #4CAF50; }}
            .disconnected {{ color: #f44336; }}
        """)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 连接设置区域
        conn_group = QGroupBox("上位机连接")
        conn_group.setStyleSheet(STYLES["hostconnect"])  # 统一样式
        conn_layout = QHBoxLayout()
        conn_layout.setSpacing(10)
        conn_layout.setContentsMargins(5, 5, 5, 5)

        # 主机输入
        ip_layout = QHBoxLayout()
        ip_layout.setSpacing(2)  # 减少间距
        ip_label = QLabel("主机 IP:")
        ip_label.setStyleSheet("padding-right: 2px;")  # 标签右内边距
        ip_layout.addWidget(ip_label)
        self.host_input = QLineEdit("127.0.0.1")
        self.host_input.setFixedWidth(100)  # 设置固定宽度
        self.host_input.setStyleSheet("padding: 2px; margin-left: 0px;")  # 减少内边距
        self.host_input.setToolTip("请输入有效的IPv4地址 (例如: 192.168.1.1)")
        self.host_input.textChanged.connect(self.validate_ip_input)
        self.host_input.editingFinished.connect(self.format_ip_input)
        ip_layout.addWidget(self.host_input)
        ip_layout.addSpacing(5)  # 与下一个控件间距
        conn_layout.addLayout(ip_layout)  # 移除stretch因子

        # 端口输入
        port_layout = QHBoxLayout()
        port_layout.setSpacing(5)
        port_layout.addWidget(QLabel("端口:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(8805)
        self.port_input.setFixedWidth(70)
        self.port_input.setStyleSheet(STYLES["Qspinbox"])
        port_layout.addWidget(self.port_input)
        conn_layout.addLayout(port_layout)

        # 连接按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.setFixedWidth(80)
        self.connect_btn.setStyleSheet(STYLES["connectbtn"])
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)

        # 上位机信息显示
        self.instrument_info = QLabel("未获取")
        self.instrument_info.setStyleSheet(STYLES["Label_not_acquired"])
        self.instrument_info.setToolTip("仪器标识信息")
        conn_layout.addWidget(self.instrument_info, stretch=1)  # 设置stretch因子使其可以缩放
        # 将连接设置区域添加到主布局
        conn_group.setLayout(conn_layout)

        # 配置加载区域
        self.config_group = QGroupBox("设置管理")
        self.config_group.setStyleSheet(STYLES["groupbox"])  # 统一样式
        self.config_layout = QHBoxLayout(self.config_group)

        # 配置名称下拉框
        self.config_combo = QComboBox()
        self.config_layout.addWidget(QLabel("选择上位机设置以应用:"))
        self.config_combo.setStyleSheet(STYLES["input"])
        self.config_layout.addWidget(self.config_combo, stretch=1)

        # 应用配置按钮
        self.apply_config_btn = QPushButton("应用设置")
        self.apply_config_btn.setStyleSheet(STYLES["button"])
        self.apply_config_btn.clicked.connect(self.apply_configuration)
        self.config_layout.addWidget(self.apply_config_btn)

        # 命令设置区域
        cmd_group = QGroupBox("命令设置")
        cmd_group.setStyleSheet("QGroupBox { background-color: #f9f9f9; }")
        cmd_layout = QVBoxLayout()
        cmd_layout.setSpacing(8)

        # 预设配置
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)
        preset_layout.addWidget(QLabel("预设配置:"))
        self.preset_combo = QComboBox()
        self.preset_combo.setStyleSheet("QComboBox { min-width: 150px; }")
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        preset_layout.addWidget(self.preset_combo, stretch=1)

        # 保存和删除按钮容器
        btn_container = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(5)
        
        self.save_preset_btn = QPushButton("💾 保存预设")
        self.save_preset_btn.setToolTip("保存当前配置为预设")
        self.save_preset_btn.setStyleSheet(STYLES["SavePresetBtn"])
        self.save_preset_btn.clicked.connect(self.save_preset_to_file)
        btn_layout.addWidget(self.save_preset_btn)
        
        self.del_preset_btn = QPushButton("🗑️ 删除预设")
        self.del_preset_btn.setToolTip("删除当前选中预设")
        self.del_preset_btn.setStyleSheet(STYLES["DelPresetBtn"])
        self.del_preset_btn.clicked.connect(self.del_preset)
        btn_layout.addWidget(self.del_preset_btn)
        
        btn_container.setLayout(btn_layout)
        preset_layout.addWidget(btn_container)

        # 命令列表
        self.command_list = QListWidget()
        self.command_list.setMinimumHeight(150)
        self.command_list.setStyleSheet(STYLES["cmdlist"])
        self.command_list.setDragDropMode(QListWidget.InternalMove)  # 启用拖拽排序
        self.command_list.itemDoubleClicked.connect(self.edit_command)  # 双击编辑
        self.command_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.command_list.customContextMenuRequested.connect(self.show_command_context_menu)

        # 命令编辑
        cmd_edit_layout = QHBoxLayout()
        cmd_edit_layout.setSpacing(8)
        self.new_cmd_input = QLineEdit()
        self.new_cmd_input.setPlaceholderText("输入SCPI命令...")
        self.new_cmd_input.setStyleSheet("QLineEdit { padding: 5px; }")
        
        self.add_cmd_btn = QPushButton("➕ 添加")
        self.add_cmd_btn.setToolTip("添加当前指令到列表")
        self.add_cmd_btn.setStyleSheet("background-color: #4CAF50;")
        self.add_cmd_btn.clicked.connect(self.add_command)
        
        cmd_edit_layout.addWidget(self.new_cmd_input, stretch=1)
        cmd_edit_layout.addWidget(self.add_cmd_btn)
        
        # 添加直接发送按钮
        self.send_now_btn = QPushButton("⚡ 直接发送")
        self.send_now_btn.setStyleSheet("background-color: #2196F3;")
        self.send_now_btn.clicked.connect(self.send_single_command)
        cmd_edit_layout.addWidget(self.send_now_btn)
        
        # 创建新的垂直布局来包含命令输入
        cmd_input_and_actions = QVBoxLayout()
        cmd_input_and_actions.addLayout(cmd_edit_layout)

        # 执行设置
        exec_layout = QHBoxLayout()
        exec_layout.setSpacing(8)
        exec_layout.addWidget(QLabel("重复次数:"))
        self.repeat_input = QSpinBox()
        self.repeat_input.setRange(1, 1000)
        self.repeat_input.setValue(1)
        self.repeat_input.setStyleSheet(STYLES["Qspinbox"])
        exec_layout.addWidget(self.repeat_input)

        exec_layout.addWidget(QLabel("间隔(秒):"))
        self.interval_input = QDoubleSpinBox()
        self.interval_input.setRange(0.1, 60.0)
        self.interval_input.setValue(1.0)
        self.interval_input.setSingleStep(0.1)
        self.interval_input.setStyleSheet(STYLES["Qspinbox"])
        exec_layout.addWidget(self.interval_input)

        exec_layout.addStretch()

        # 执行按钮和进度条布局
        exec_btn_layout = QHBoxLayout()
        exec_btn_layout.setSpacing(8)
        
        self.execute_btn = QPushButton("🚀 循环执行预设命令")
        self.execute_btn.setStyleSheet(STYLES["loop_preset_btn"])
        self.execute_btn.clicked.connect(self.execute_commands)
        self.execute_btn.setEnabled(False)
        exec_btn_layout.addWidget(self.execute_btn)
        
        self.stop_btn = QPushButton("🛑 停止")
        self.stop_btn.setStyleSheet(STYLES["stop_loop_btn"])
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        exec_btn_layout.addWidget(self.stop_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(STYLES["progressbar"])
        exec_btn_layout.addWidget(self.progress_bar, stretch=1)
        
        exec_layout.addLayout(exec_btn_layout)

        cmd_layout.addLayout(preset_layout)
        cmd_layout.addWidget(self.command_list)
        cmd_layout.addLayout(cmd_input_and_actions)
        cmd_layout.addLayout(exec_layout)
        cmd_group.setLayout(cmd_layout)

        # 输出区域
        output_group = QGroupBox("输出")
        output_group.setStyleSheet("QGroupBox { background-color: #f9f9f9; }")
        output_layout = QVBoxLayout()
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet(STYLES["QTextEdit_output"])
        output_layout.addWidget(self.output_area)
        output_group.setLayout(output_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(STYLES["QStatusBar"])
        # 版本信息
        self.version_label = QLabel(f"版本: {VERSION}")
        self.version_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.status_bar.addPermanentWidget(self.version_label)
        
        # 连接状态指示器
        self.connection_status = QLabel("🔴 未连接")
        self.connection_status.setStyleSheet(STYLES["QLabel_noconnect"])
        self.status_bar.addPermanentWidget(self.connection_status)
        
        # 执行状态指示器
        self.execution_status = QLabel("🟡 空闲")
        self.execution_status.setStyleSheet(STYLES["QLabel_idle"])
        self.status_bar.addPermanentWidget(self.execution_status)
        
        self.setStatusBar(self.status_bar)
        # 主布局顺序
        self.main_layout.addWidget(conn_group)      # 上位机连接
        self.main_layout.addWidget(self.config_group)   # 配置管理
        self.main_layout.addWidget(cmd_group)       # 命令设置
        self.main_layout.addWidget(output_group)    # 输出区域

    def load_default_presets(self):
        """从配置文件加载预设"""
        try:
            with open("config/presets.json", "r", encoding='utf-8') as f:
                config = json.load(f)
                self.presets = config.get("presets", {})
                
            if not self.presets:
                raise ValueError("No presets found in config file")
                
            self.update_preset_combo()
            self.append_output("预设配置已从文件加载")
        except Exception as e:
            logger.error(f"加载预设配置失败: {str(e)}")
            QMessageBox.warning(self, "警告", f"加载预设配置失败: {str(e)}")
            self.presets = {}
            self.update_preset_combo()

    def update_preset_combo(self):
        """更新预设下拉框"""
        self.preset_combo.clear()
        self.preset_combo.addItem("---------- 选择预设 ----------")
        for preset_name in sorted(self.presets.keys()):
            self.preset_combo.addItem(preset_name)

    def load_preset(self, preset_name):
        """加载选中的预设"""
        if preset_name == "---------- 选择预设 ----------":
            self.current_preset = None
            self.command_list.clear()
            self.repeat_input.setValue(1)
            self.interval_input.setValue(1.0)
            return
            
        if preset_name not in self.presets:
            return

        preset = self.presets[preset_name]
        self.current_preset = preset_name

        # 更新UI
        self.command_list.clear()
        self.command_list.addItems(preset["commands"])
        self.repeat_input.setValue(preset["repeat"])
        self.interval_input.setValue(preset["interval"])

        # 输出预设详细信息
        timestamp = logger.get_timestamp()
        self.append_output(f"{timestamp} 加载预设: {preset_name}")
        self.append_output(f"{timestamp} 描述: {preset['description']}")
        self.append_output(f"{timestamp} 命令数量: {len(preset['commands'])}")
        self.append_output(f"{timestamp} 重复次数: {preset['repeat']}")
        self.append_output(f"{timestamp} 间隔时间: {preset['interval']}秒")

    def load_preset_from_file(self):
        """从文件加载预设"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "加载预设", "", "JSON Files (*.json);;All Files (*)", options=options)

        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    preset_data = json.load(f)

                if not isinstance(preset_data, dict):
                    raise ValueError("Invalid preset format")

                preset_name = preset_data.get("name", "未命名预设")
                self.presets[preset_name] = {
                    "description": preset_data.get("description", "无描述"),
                    "commands": preset_data.get("commands", []),
                    "repeat": preset_data.get("repeat", 1),
                    "interval": preset_data.get("interval", 1.0)
                }

                self.update_preset_combo()
                self.preset_combo.setCurrentText(preset_name)
                self.append_output(f"从文件加载预设: {preset_name}")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载预设失败: {str(e)}")

    def del_preset(self):
        """删除当前选中的预设"""
        if not hasattr(self, 'current_preset') or not self.current_preset:
            QMessageBox.warning(self, "警告", "请先选择一个预设")
            return
            
        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除预设 "{self.current_preset}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with open("config/presets.json", "r", encoding='utf-8') as f:
                    presets = json.load(f)
                
                if self.current_preset in presets["presets"]:
                    del presets["presets"][self.current_preset]
                    
                    with open("config/presets.json", "w", encoding='utf-8') as f:
                        json.dump(presets, f, indent=4, ensure_ascii=False)
                    
                    self.presets = presets["presets"]
                    self.preset_combo.clear()
                    self.preset_combo.addItem("---------- 选择预设 ----------")
                    for preset_name in sorted(self.presets.keys()):
                        self.preset_combo.addItem(preset_name)
                    self.current_preset = None
                    self.command_list.clear()
                    QMessageBox.information(self, "成功", "预设已删除")
                else:
                    QMessageBox.warning(self, "警告", f"预设 '{self.current_preset}' 不存在")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除预设失败: {str(e)}")
                logger.error(f"删除预设失败: {str(e)}")
    def apply_configuration(self):
        """应用选定的配置"""
        if not self.instrument or not self.instrument.sock:
            self.output_area.append("[配置] 错误: 请先连接仪器")
            QMessageBox.warning(self, "警告", "请先连接到仪器")
            return
            
        config_name = self.config_combo.currentText()
        if not config_name:
            self.output_area.append("[配置] 错误: 请选择一个设置")
            QMessageBox.warning(self, "警告", "请选择一个设置")
            return
            
        try:
            self.configurator.apply_configuration(self.instrument, config_name)
            self.output_area.append(f"[配置] 应用成功: {config_name}")
            QMessageBox.information(self, "应用成功", f"配置 '{config_name}' 已应用")
        except Exception as e:
            self.output_area.append(f"[配置] 应用失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"应用配置失败: {str(e)}")

    def save_preset_to_file(self):
        """保存当前命令序列到presets.json"""
        if self.command_list.count() == 0:
            QMessageBox.warning(self, "警告", "没有可保存的命令序列")
            return

        # 获取预设名称和描述
        preset_name, ok = QInputDialog.getText(
            self, "保存预设", "输入预设名称:", QLineEdit.Normal, "")
        if not ok or not preset_name:
            return
            
        preset_desc, ok = QInputDialog.getText(
            self, "保存预设", "输入预设描述:", QLineEdit.Normal, "")
        if not ok:
            return

        try:
            # 读取现有预设
            with open("config/presets.json", "r", encoding='utf-8') as f:
                presets_data = json.load(f)
                
            # 添加或更新预设
            presets_data["presets"][preset_name] = {
                "description": preset_desc,
                "commands": [self.command_list.item(i).text() for i in range(self.command_list.count())],
                "repeat": self.repeat_input.value(),
                "interval": self.interval_input.value()
            }
            
            # 写回文件
            with open("config/presets.json", "w", encoding='utf-8') as f:
                json.dump(presets_data, f, indent=4, ensure_ascii=False)
                
            # 更新内存中的预设数据
            self.presets = presets_data["presets"]
            self.update_preset_combo()
            self.preset_combo.setCurrentText(preset_name)
            
            self.append_output(f"预设 '{preset_name}' 已保存到presets.json")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存预设失败: {str(e)}")
            logger.error(f"保存预设失败: {str(e)}")

    def add_command(self):
        """添加新命令到列表"""
        cmd = self.new_cmd_input.text().strip()
        if not cmd:
            QMessageBox.warning(self, "警告", "命令不能为空")
            return
            
        self.command_list.addItem(cmd)
        self.new_cmd_input.clear()

    def send_single_command(self):
        """直接发送单个命令而不添加到列表"""
        if not self.is_connected():
            QMessageBox.warning(self, "警告", "请先连接到设备")
            return
        
        cmd = self.new_cmd_input.text().strip()
        if not cmd:
            QMessageBox.warning(self, "警告", "请输入要发送的命令")
            return
        
        try:
            response = self.instrument.send_command(cmd)
            timestamp = logger.get_timestamp()
            self.append_output(f"{timestamp} > {cmd}")
            if response:
                self.append_output(f"{timestamp} < {response}")
            else:
                self.append_output(f"{timestamp} < 无响应")
        except SCPIError as e:
            self.append_output(f"发送命令失败: {str(e)}", "ERROR")

    def remove_command(self):
        """移除选中的命令"""
        for item in self.command_list.selectedItems():
            self.command_list.takeItem(self.command_list.row(item))

    def clear_commands(self):
        """清空命令列表(带确认对话框)"""
        reply = QMessageBox.question(
            self,
            '确认清空',
            '确定要清空所有命令吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.command_list.clear()
            self.preset_combo.setCurrentIndex(0)  # 重置预设选择

    def is_connected(self):
        """检查是否真正连接到上位机"""
        return self.instrument and hasattr(self.instrument, 'sock') and self.instrument.sock

    def is_valid_ip(self, ip_str):
        """验证IP地址格式是否为xxx.xxx.xxx.xxx"""
        parts = ip_str.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True

    def validate_ip_input(self, text):
        """实时验证IP地址输入"""
        # 允许中间输入过程的不完整格式
        if not text or text.count('.') > 3:
            self.host_input.setStyleSheet("background-color: #FFD6D6; padding: 2px; margin-left: 0px;")
            return
            
        parts = text.split('.')
        valid = True
        for part in parts:
            if not part.isdigit() or (part and int(part) > 255):
                valid = False
                break
                
        if valid:
            self.host_input.setStyleSheet("padding: 2px; margin-left: 0px;")
        else:
            self.host_input.setStyleSheet("background-color: #FFD6D6; padding: 2px; margin-left: 0px;")

    def format_ip_input(self):
        """自动格式化IP地址输入"""
        text = self.host_input.text()
        parts = []
        current = ''
        
        # 提取数字部分
        for char in text:
            if char.isdigit():
                current += char
            elif char == '.' and current:
                parts.append(current)
                current = ''
        if current:
            parts.append(current)
            
        # 限制最多4部分，每部分最多3位
        parts = parts[:4]
        formatted = []
        for part in parts:
            if part:
                formatted.append(part[:3])
            else:
                formatted.append('0')
                
        # 补全为4部分
        while len(formatted) < 4:
            formatted.append('0')
            
        # 组合为标准IP格式
        self.host_input.setText('.'.join(formatted[:4]))

    def set_connection_ui(self, connected):
        """设置连接状态UI"""
        if connected:
            self._update_connection_status("🟢 已连接", "#e8f5e9", "#2e7d32", "断开", True)
        else:
            self._update_connection_status("🔴 未连接", "#ffebee", "#c62828", "连接", False)

    def _update_connection_status(self, text, bg_color, text_color, btn_text, enable_execute):
        """统一更新连接状态UI"""
        self.connection_status.setText(text)
        self.connection_status.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
            }}
        """)
        self.connect_btn.setText(btn_text)
        self.execute_btn.setEnabled(enable_execute)

    def toggle_connection(self):
        """连接/断开上位机"""
        idn = None  # 初始化idn变量
        if self.is_connected():
            try:
                self.instrument.disconnect()
                self.set_connection_ui(False)
                self.instrument_info.setText("未获取")
                self.append_output("已断开上位机连接")
                self.execution_status.setText("🟡 空闲")
                self.instrument = None
            except Exception as e:
                QMessageBox.critical(self, "错误", f"断开连接错误: {str(e)}")
        else:
            host = self.host_input.text()
            if not self.is_valid_ip(host):
                QMessageBox.warning(self, "IP地址错误", 
                                  "请输入有效的IPv4地址 (格式: xxx.xxx.xxx.xxx)")
                return
                
            try:
                port = self.port_input.value()
                self.instrument = SCPIInstrument(host, port)
                self.instrument.connect()
                
                # 获取仪器信息
                try:
                    idn = self.instrument.send_command("*IDN?")
                    if idn:
                        parts = [p.strip() for p in idn.split(',')]
                        # 确保至少有3个部分，不足的用空字符串填充
                        while len(parts) < 3:
                            parts.append('')
                        # 显示制造商、型号和序列号
                        short_id = f"{parts[0]} {parts[1]} (SN:{parts[2]})" if parts[2] else f"{parts[0]} {parts[1]}"
                        self.instrument_info.setText(short_id)
                        self.instrument_info.setToolTip(idn)
                    else:
                        self.instrument_info.setText("无响应")
                        self.append_output("仪器未返回标识信息", "WARNING")
                except Exception as e:
                    self.instrument_info.setText("获取失败")
                    self.append_output(f"获取仪器信息错误: {str(e)}", "ERROR")
                    logger.error(f"获取仪器信息失败: {str(e)}")
                
                self.set_connection_ui(True)
                self.append_output(f"已连接到 {host}:{port}")
                if idn:
                    self.append_output(f"仪器标识: {idn}")
            except SCPIError as e:
                logger.error(f"连接失败: {str(e)}")  # 新增日志记录
                QMessageBox.critical(self, "连接错误", str(e))
                if self.instrument:
                    try:
                        self.instrument.disconnect()
                    except:
                        pass
                    self.instrument = None
                self.connection_status.setText("🔴 未连接")
                self.connection_status.setStyleSheet(STYLES["disconnect_status"])
                self.connect_btn.setText("连接")
                self.execute_btn.setEnabled(False)
                self.instrument_info.setText("连接失败")
                self.append_output(f"连接失败: {str(e)}")

    def execute_commands(self):
        """执行命令序列"""
        if not self.instrument or not self.instrument.sock:
            QMessageBox.warning(self, "警告", "未连接到上位机")
            return

        commands = [self.command_list.item(i).text() for i in range(self.command_list.count())]
        if not commands:
            QMessageBox.warning(self, "警告", "没有可执行的命令")
            return

        repeat = self.repeat_input.value()
        interval = self.interval_input.value()

        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 更新UI状态
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.connect_btn.setEnabled(False)
        self.set_execution_state('executing')
        self.append_output(f"开始执行 {len(commands)} 条命令，重复 {repeat} 次...")

        # 创建工作线程
        self.worker = SCPIWorker(self.instrument, commands, repeat, interval)
        self.worker.command_sent.connect(self.handle_command_result)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.handle_execution_finished)
        self.worker.error_occurred.connect(self.handle_execution_error)
        self.worker.start()

    def handle_command_result(self, cmd, response, loop_num):
        """处理单个命令的结果"""
        timestamp = logger.get_timestamp()
        total_loops = self.repeat_input.value()
        
        # 如果只循环一次，不显示循环信息
        if total_loops > 1:
            self.append_output(f"{timestamp} [循环 {loop_num}/{total_loops}] > {cmd}")
            if response != "None":
                self.append_output(f"{timestamp} [循环 {loop_num}/{total_loops}] < {response}")
        else:
            self.append_output(f"{timestamp} > {cmd}")
            if response != "None":
                self.append_output(f"{timestamp} < {response}")

    def update_progress(self, current, total):
        """更新进度条显示"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.progress_bar.setFormat(f"{current}/{total} ({percent}%)")

    def stop_execution(self):
        """停止当前执行"""
        if self.worker:
            self.worker.stop()
            self.append_output("正在停止执行...")
            self.stop_btn.setEnabled(False)

    def set_execution_state(self, state):
        """设置执行状态UI
        Args:
            state: 执行状态 ('idle', 'executing', 'completed', 'error')
        """
        if state in execution_state_STYLES:
            self.execution_status.setText(execution_state_STYLES[state]['text'])
            self.execution_status.setStyleSheet(execution_state_STYLES[state]['style'])

    def handle_execution_finished(self):
        """处理执行完成"""
        self.append_output("命令执行完成")
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.connect_btn.setEnabled(True)
        self.set_execution_state('completed')
        self.progress_bar.setValue(100)
        self.worker = None

    def handle_execution_error(self, error_msg):
        """处理执行错误"""
        logger.error(f"执行错误: {error_msg}")
        self.append_output(f"错误: {error_msg}", "ERROR")
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.connect_btn.setEnabled(True)
        self.set_execution_state('error')
        self.progress_bar.setValue(0)
        self.worker = None
        QMessageBox.critical(self, "执行错误", error_msg)

    def move_command_up(self):
        """将选中的命令向上移动一位"""
        current_row = self.command_list.currentRow()
        if current_row > 0:
            current_item = self.command_list.takeItem(current_row)
            self.command_list.insertItem(current_row - 1, current_item)
            self.command_list.setCurrentRow(current_row - 1)

    def move_command_down(self):
        """将选中的命令向下移动一位"""
        current_row = self.command_list.currentRow()
        if current_row < self.command_list.count() - 1 and current_row >= 0:
            current_item = self.command_list.takeItem(current_row)
            self.command_list.insertItem(current_row + 1, current_item)
            self.command_list.setCurrentRow(current_row + 1)


    def show_command_context_menu(self, position):
        """显示命令列表的右键菜单"""
        menu = QMenu()
        item = self.command_list.itemAt(position)
        
        # 添加菜单项
        move_up_action = menu.addAction("⬆️ 上移")
        move_down_action = menu.addAction("⬇️ 下移")
        edit_action = menu.addAction("✏️ 编辑")
        remove_action = menu.addAction("➖ 删除") 
        clear_action = menu.addAction("🗑️ 清空")
        
        # 连接信号
        edit_action.triggered.connect(self.edit_command)
        remove_action.triggered.connect(self.remove_command)
        move_up_action.triggered.connect(self.move_command_up)
        move_down_action.triggered.connect(self.move_command_down)
        clear_action.triggered.connect(self.clear_commands)
        
        # 设置启用状态
        state = item is not None
        edit_action.setEnabled(state)
        remove_action.setEnabled(state)
        move_up_action.setEnabled(state)
        move_down_action.setEnabled(state)
        
        menu.exec_(self.command_list.viewport().mapToGlobal(position))

    def edit_command(self):
        """编辑选中的命令"""
        current_item = self.command_list.currentItem()
        if current_item is not None:
            current_text = current_item.text()
            # 创建一个输入对话框
            dialog = QInputDialog(self)
            dialog.setWindowTitle("编辑命令")
            dialog.setLabelText("修改SCPI命令:")
            dialog.setTextValue(current_text)
            dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            
            if dialog.exec_() == QDialog.Accepted:
                new_text = dialog.textValue().strip()
                if new_text:
                    current_item.setText(new_text)

    def auto_scroll_output(self):
        """自动滚动输出区域到底部"""
        scroll_bar = self.output_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
        self.output_area.ensureCursorVisible()

    def append_output(self, text, level="INFO"):
        """追加文本到输出区域并记录到日志"""
        # 添加到输出区域
        self.output_area.append(text)
        
        # 检测并去除时间戳
        if text.startswith("[") and "]" in text:
            # 找到第一个"]"的位置
            timestamp_end = text.find("]") + 1
            # 提取消息内容（不包含时间戳）
            message = text[timestamp_end:].strip()
        else:
            message = text
            
        # 记录到日志文件
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SCPIGUI()
    window.show()
    sys.exit(app.exec_())