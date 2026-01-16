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
    QRadioButton,
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

    def __init__(self, protocol="VISA", vid=None, pid=None):
        super().__init__()
        self.protocol = protocol
        self.vid = vid
        self.pid = pid
        self._is_running = True
        logger.info(f"DeviceScanner初始化，协议: {protocol}, VID: {vid}, PID: {pid}")

    def stop(self):
        """停止扫描"""
        self._is_running = False
        logger.info("扫描线程已停止")

    def run(self):
        """扫描设备"""
        logger.info(f"开始扫描设备，协议: {self.protocol}")
        try:
            if not is_pyvisa_available():
                logger.error("PyVISA不可用，无法扫描设备")
                return
                
            # 不区分大小写的协议判断
            protocol_upper = self.protocol.upper()
            if protocol_upper == "VISA":
                logger.info("开始执行VISA设备扫描")
                self.scan_visa_devices()
            elif protocol_upper == "TCP/IP":
                # 这里可以添加TCP/IP设备扫描逻辑
                logger.info("TCP/IP扫描功能尚未实现")
                pass
        except Exception as e:
            logger.error(f"设备扫描错误: {str(e)}", exc_info=True)
        finally:
            logger.info("设备扫描完成")
            self.scan_finished.emit()

    def scan_visa_devices(self):
        """扫描VISA设备"""
        try:
            import pyvisa
            logger.info("成功导入PyVISA模块")

            rm = pyvisa.ResourceManager()
            logger.info("成功创建VISA资源管理器")
            
            # 使用更广泛的查询字符串来获取所有类型的VISA资源
            devices = rm.list_resources('?*')  # 获取所有资源，而不仅限于INSTR类型
            logger.info(f"找到 {len(devices)} 个VISA设备")

            for device in devices:
                if not self._is_running:
                    break
                
                logger.info(f"处理设备: {device}")
                try:
                    # 尝试连接设备获取信息
                    instr = rm.open_resource(device)
                    instr.timeout = 1000  # 设置超时时间
                    idn = instr.query("*IDN?")
                    logger.info(f"设备 {device} 识别成功: {idn.strip()}")
                    self.device_found.emit(device, idn.strip())
                    instr.close()
                except Exception as e:
                    # 如果无法获取设备信息，只显示设备地址
                    logger.info(f"设备 {device} 无法识别: {str(e)}")
                    self.device_found.emit(device, f"无法识别设备 ({str(e)})")
        except Exception as e:
            logger.error(f"VISA设备扫描失败: {str(e)}", exc_info=True)


            



class ConnectionDialog(QDialog):
    """连接配置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接配置")
        self.setModal(True)
        self.setMinimumSize(500, 400)

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
        protocol_layout = QHBoxLayout()

        self.tcpip_radio = QRadioButton("TCP/IP")
        self.tcpip_radio.setChecked(True)
        self.visa_radio = QRadioButton("PyVISA")
        
        # 如果PyVISA不可用，禁用VISA相关选项
        if not is_pyvisa_available():
            self.visa_radio.setEnabled(False)
            self.visa_radio.setToolTip("PyVISA未安装")

        self.tcpip_radio.toggled.connect(self.on_protocol_changed)
        self.visa_radio.toggled.connect(self.on_protocol_changed)

        protocol_layout.addWidget(self.tcpip_radio)
        protocol_layout.addWidget(self.visa_radio)
        protocol_layout.addStretch()
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

        # 手动输入设备地址（设置默认值）
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("设备地址:"))
        self.visa_address_input = QLineEdit()
        self.visa_address_input.setText("TCPIP::192.168.170.2::INSTR")  # 设置默认值
        manual_layout.addWidget(self.visa_address_input)
        visa_layout.addLayout(manual_layout)

        # VISA设备扫描
        scan_layout = QHBoxLayout()
        self.visa_scan_btn = QPushButton("扫描VISA设备")
        self.visa_scan_btn.clicked.connect(self.scan_visa_devices)
        scan_layout.addWidget(self.visa_scan_btn)
        scan_layout.addStretch()
        visa_layout.addLayout(scan_layout)

        # VISA设备列表
        visa_layout.addWidget(QLabel("检测到的VISA设备:"))
        self.visa_device_list = QListWidget()
        self.visa_device_list.setMinimumHeight(100)
        self.visa_device_list.itemDoubleClicked.connect(self.on_visa_device_selected)
        visa_layout.addWidget(self.visa_device_list)

        self.visa_group.setLayout(visa_layout)
        layout.addWidget(self.visa_group)

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
        self.on_protocol_changed()

    def on_protocol_changed(self):
        """协议选择改变事件"""
        if self.tcpip_radio.isChecked():
            self.tcpip_group.setVisible(True)
            self.visa_group.setVisible(False)
        elif self.visa_radio.isChecked():
            self.tcpip_group.setVisible(False)
            self.visa_group.setVisible(True)



    def scan_visa_devices(self):
        """开始扫描VISA设备"""
        if not is_pyvisa_available():
            QMessageBox.warning(self, "警告", "PyVISA未安装，无法扫描VISA设备")
            logger.error("PyVISA未安装，无法扫描VISA设备")
            return

        self.visa_device_list.clear()
        self.visa_scan_btn.setEnabled(False)
        self.visa_scan_btn.setText("扫描中...")

        # 启动扫描线程
        self.scanner = DeviceScanner("VISA")
        self.scanner.device_found.connect(self.on_visa_device_found)
        self.scanner.scan_finished.connect(self.on_visa_scan_finished)
        self.scanner.start()
        logger.info("开始扫描VISA设备")

    def on_visa_device_found(self, address, description):
        """VISA设备发现事件"""
        item = QListWidgetItem(f"{address} - {description}")
        item.setData(Qt.UserRole, address)  # 存储设备地址
        self.visa_device_list.addItem(item)

    def on_visa_scan_finished(self):
        """VISA扫描完成事件"""
        self.visa_scan_btn.setEnabled(True)
        self.visa_scan_btn.setText("扫描VISA设备")
        logger.info("VISA设备扫描完成")
        
        if self.visa_device_list.count() == 0:
            QMessageBox.information(self, "提示", "未找到VISA设备")
            logger.info("未找到VISA设备")
            
        self.scanner = None

    def on_visa_device_selected(self, item):
        """VISA设备选择事件"""
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
        if self.tcpip_radio.isChecked():
            protocol = "TCP/IP"
        elif self.visa_radio.isChecked():
            protocol = "VISA"
        else:
            protocol = "TCP/IP"  # 默认值

        if protocol == "TCP/IP":
            return {
                "protocol": "TCP/IP",
                "host": self.host_input.text(),
                "port": self.port_input.value(),
            }
        elif protocol == "VISA":
            address = self.visa_address_input.text().strip()
            return {"protocol": "VISA", "address": address}

        return None

    def closeEvent(self, event):
        """关闭事件"""
        # self.stop_scan()  # 移除扫描功能后不再需要
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
