"""
连接配置对话框模块
支持多种连接协议：TCP/IP、PyVISA等
"""

import sys
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QComboBox,
    QGroupBox,
    QProgressBar,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
)

from scpi_app.logger import logger
from ..styles import STYLES


def is_pyvisa_available():
    """检查PyVISA是否可用"""
    try:
        import pyvisa  # noqa: F401

        return True
    except ImportError:
        return False


class DeviceScanner(QThread):
    """设备扫描线程"""

    device_found = Signal(str, str)  # 设备地址, 设备描述
    scan_finished = Signal()

    def __init__(self, protocol="VISA"):
        super().__init__()
        self.protocol = protocol
        self._is_running = True

    def stop(self):
        """停止扫描"""
        self._is_running = False

    def run(self):
        """扫描设备"""
        try:
            if self.protocol == "VISA" and is_pyvisa_available():
                self.scan_visa_devices()
            elif self.protocol == "TCP/IP":
                # 这里可以添加TCP/IP设备扫描逻辑
                pass
        except Exception as e:
            logger.error(f"设备扫描错误: {str(e)}")
        finally:
            self.scan_finished.emit()

    def scan_visa_devices(self):
        """扫描VISA设备"""
        try:
            import pyvisa

            rm = pyvisa.ResourceManager()
            devices = rm.list_resources()

            for device in devices:
                if not self._is_running:
                    break
                try:
                    # 尝试连接设备获取信息
                    instr = rm.open_resource(device)
                    instr.timeout = 1000  # 设置超时时间
                    idn = instr.query("*IDN?")
                    self.device_found.emit(device, idn.strip())
                    instr.close()
                except Exception as e:
                    # 如果无法获取设备信息，只显示设备地址
                    self.device_found.emit(device, f"无法识别设备 ({str(e)})")
        except Exception as e:
            logger.error(f"VISA设备扫描失败: {str(e)}")


class ConnectionDialog(QDialog):
    """连接配置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接配置")
        self.setModal(True)
        self.setFixedSize(500, 400)

        # 设备扫描器
        self.scanner = None

        # 设置样式
        self.setStyleSheet(
            f"""
            QWidget {{
                font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
                font-size: 10pt;
            }}
            {STYLES["button"]}
            {STYLES["input"]}
            {STYLES["groupbox"]}
            {STYLES["Qspinbox"]}
            {STYLES["Qcombobox"]}
        """
        )

        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()

        # 协议选择
        protocol_group = QGroupBox("连接协议")
        protocol_layout = QVBoxLayout()

        protocol_selector_layout = QHBoxLayout()
        protocol_selector_layout.addWidget(QLabel("选择协议:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItem("TCP/IP", "TCP/IP")
        if is_pyvisa_available():
            self.protocol_combo.addItem("PyVISA", "VISA")
        else:
            self.protocol_combo.addItem("PyVISA (未安装)", "VISA")
            self.protocol_combo.model().item(
                self.protocol_combo.count() - 1
            ).setEnabled(False)

        self.protocol_combo.currentIndexChanged.connect(self.on_protocol_changed)
        protocol_selector_layout.addWidget(self.protocol_combo)
        protocol_selector_layout.addStretch()
        protocol_layout.addLayout(protocol_selector_layout)

        protocol_group.setLayout(protocol_layout)
        layout.addWidget(protocol_group)

        # TCP/IP 配置区域
        self.tcpip_group = QGroupBox("TCP/IP 配置")
        tcpip_layout = QVBoxLayout()

        # 主机IP设置
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("主机 IP:"))
        self.host_input = QLineEdit("127.0.0.1")
        self.host_input.setFixedWidth(120)
        self.host_input.textChanged.connect(self.validate_ip_input)
        self.host_input.editingFinished.connect(self.format_ip_input)
        ip_layout.addWidget(self.host_input)
        ip_layout.addStretch()
        tcpip_layout.addLayout(ip_layout)

        # 端口设置
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("端口:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(8805)
        self.port_input.setFixedWidth(80)
        port_layout.addWidget(self.port_input)
        port_layout.addStretch()
        tcpip_layout.addLayout(port_layout)

        self.tcpip_group.setLayout(tcpip_layout)
        layout.addWidget(self.tcpip_group)

        # VISA 配置区域
        self.visa_group = QGroupBox("PyVISA 配置")
        visa_layout = QVBoxLayout()

        # 设备扫描区域
        scan_layout = QHBoxLayout()
        self.scan_btn = QPushButton("扫描设备")
        self.scan_btn.clicked.connect(self.scan_devices)
        scan_layout.addWidget(self.scan_btn)

        self.stop_scan_btn = QPushButton("停止扫描")
        self.stop_scan_btn.clicked.connect(self.stop_scan)
        self.stop_scan_btn.setEnabled(False)
        scan_layout.addWidget(self.stop_scan_btn)
        scan_layout.addStretch()
        visa_layout.addLayout(scan_layout)

        # 设备列表
        visa_layout.addWidget(QLabel("检测到的设备:"))
        self.device_list = QListWidget()
        self.device_list.setMinimumHeight(120)
        self.device_list.itemDoubleClicked.connect(self.on_device_selected)
        visa_layout.addWidget(self.device_list)

        # 手动输入设备地址
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("手动输入设备地址:"))
        self.visa_address_input = QLineEdit()
        self.visa_address_input.setPlaceholderText("例如: TCPIP::192.168.1.100::INSTR")
        manual_layout.addWidget(self.visa_address_input)
        visa_layout.addLayout(manual_layout)

        self.visa_group.setLayout(visa_layout)
        layout.addWidget(self.visa_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 初始状态
        self.on_protocol_changed(0)

    def on_protocol_changed(self, index):
        """协议选择改变事件"""
        protocol = self.protocol_combo.currentData()

        if protocol == "TCP/IP":
            self.tcpip_group.setVisible(True)
            self.visa_group.setVisible(False)
        elif protocol == "VISA":
            self.tcpip_group.setVisible(False)
            self.visa_group.setVisible(True)

    def scan_devices(self):
        """开始扫描设备"""
        if not is_pyvisa_available():
            QMessageBox.warning(self, "警告", "PyVISA未安装，无法扫描设备")
            return

        self.device_list.clear()
        self.scan_btn.setEnabled(False)
        self.stop_scan_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条

        # 启动扫描线程
        self.scanner = DeviceScanner("VISA")
        self.scanner.device_found.connect(self.on_device_found)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.start()

    def stop_scan(self):
        """停止扫描"""
        if self.scanner and self.scanner.isRunning():
            self.scanner.stop()
            self.scanner.wait(2000)  # 等待2秒

    def on_device_found(self, address, description):
        """设备发现事件"""
        item = QListWidgetItem(f"{address} - {description}")
        item.setData(Qt.UserRole, address)  # 存储设备地址
        self.device_list.addItem(item)

    def on_scan_finished(self):
        """扫描完成事件"""
        self.scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.scanner = None

    def on_device_selected(self, item):
        """设备选择事件"""
        address = item.data(Qt.UserRole)
        self.visa_address_input.setText(address)

    def validate_ip_input(self, text):
        """实时验证IP地址输入"""
        if not text or text.count(".") > 3:
            self.host_input.setStyleSheet("background-color: #FFD6D6;")
            return

        parts = text.split(".")
        valid = True
        for part in parts:
            if not part.isdigit() or (part and int(part) > 255):
                valid = False
                break

        if valid:
            self.host_input.setStyleSheet("")
        else:
            self.host_input.setStyleSheet("background-color: #FFD6D6;")

    def format_ip_input(self):
        """自动格式化IP地址输入"""
        text = self.host_input.text()
        parts = []
        current = ""

        # 提取数字部分
        for char in text:
            if char.isdigit():
                current += char
            elif char == "." and current:
                parts.append(current)
                current = ""
        if current:
            parts.append(current)

        # 限制最多4部分，每部分最多3位
        parts = parts[:4]
        formatted = []
        for part in parts:
            if part:
                formatted.append(part[:3])
            else:
                formatted.append("0")

        # 补全为4部分
        while len(formatted) < 4:
            formatted.append("0")

        # 组合为标准IP格式
        self.host_input.setText(".".join(formatted[:4]))

    def get_connection_info(self):
        """获取连接信息"""
        protocol = self.protocol_combo.currentData()

        if protocol == "TCP/IP":
            return {
                "protocol": "TCP/IP",
                "host": self.host_input.text(),
                "port": self.port_input.value(),
            }
        elif protocol == "VISA":
            address = self.visa_address_input.text().strip()
            if not address:
                # 如果手动输入为空，使用选中的设备
                selected_items = self.device_list.selectedItems()
                if selected_items:
                    address = selected_items[0].data(Qt.UserRole)

            return {"protocol": "VISA", "address": address}

        return None

    def closeEvent(self, event):
        """关闭事件"""
        self.stop_scan()
        super().closeEvent(event)


if __name__ == "__main__":
    # 测试代码
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = ConnectionDialog()
    if dialog.exec() == QDialog.Accepted:
        info = dialog.get_connection_info()
        print("连接信息:", info)
    sys.exit()
