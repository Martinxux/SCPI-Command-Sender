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
        self.setMinimumSize(500, 400)  # 增加窗口高度以容纳USB配置

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
        self.usb_radio = QRadioButton("USB")
        
        # 如果PyVISA不可用，禁用VISA相关选项，但USB可以独立使用
        if not is_pyvisa_available():
            self.visa_radio.setEnabled(False)
            self.visa_radio.setToolTip("PyVISA未安装")
        else:
            self.usb_radio.setToolTip("支持VISA或直接USB连接")

        self.tcpip_radio.toggled.connect(self.on_protocol_changed)
        self.visa_radio.toggled.connect(self.on_protocol_changed)
        self.usb_radio.toggled.connect(self.on_protocol_changed)

        protocol_layout.addWidget(self.tcpip_radio)
        protocol_layout.addWidget(self.visa_radio)
        protocol_layout.addWidget(self.usb_radio)
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

        # USB 配置区域
        self.usb_group = QGroupBox("USB 配置")
        usb_layout = QVBoxLayout()

        # VID、PID 设置和刷新按钮在同一行
        vid_pid_refresh_layout = QHBoxLayout()
        vid_pid_refresh_layout.addWidget(QLabel("VID:"))
        self.vid_input = QLineEdit("0x0465")  # 默认VID
        self.vid_input.setFixedWidth(100)
        self.vid_input.textChanged.connect(self.validate_hex_input)
        vid_pid_refresh_layout.addWidget(self.vid_input)
        
        vid_pid_refresh_layout.addWidget(QLabel("PID:"))
        self.pid_input = QLineEdit("0x0109")  # 默认PID
        self.pid_input.setFixedWidth(100)
        self.pid_input.textChanged.connect(self.validate_hex_input)
        vid_pid_refresh_layout.addWidget(self.pid_input)
        
        # 添加刷新设备按钮
        self.usb_refresh_btn = QPushButton("刷新设备")
        self.usb_refresh_btn.clicked.connect(self.refresh_usb_devices)
        vid_pid_refresh_layout.addWidget(self.usb_refresh_btn)
        
        vid_pid_refresh_layout.addStretch()
        usb_layout.addLayout(vid_pid_refresh_layout)
        
        # USB设备列表
        usb_layout.addWidget(QLabel("检测到的USB设备:"))
        self.usb_device_list = QListWidget()
        self.usb_device_list.setMinimumHeight(100)
        self.usb_device_list.itemDoubleClicked.connect(self.on_usb_device_selected)
        usb_layout.addWidget(self.usb_device_list)
        
        # 提示信息
        hint_label = QLabel("提示: 选择USB设备或输入VID和PID后点击连接")
        hint_label.setStyleSheet("font-size: 9pt; color: #555; font-style: italic;")
        hint_label.setWordWrap(True)
        usb_layout.addWidget(hint_label)

        self.usb_group.setLayout(usb_layout)
        layout.addWidget(self.usb_group)

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
            self.usb_group.setVisible(False)
        elif self.visa_radio.isChecked():
            self.tcpip_group.setVisible(False)
            self.visa_group.setVisible(True)
            self.usb_group.setVisible(False)
        elif self.usb_radio.isChecked():
            self.tcpip_group.setVisible(False)
            self.visa_group.setVisible(False)
            self.usb_group.setVisible(True)
            # 用户切换到USB协议时，不自动刷新设备列表，等待用户点击刷新按钮



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

    def refresh_usb_devices(self):
        """刷新USB设备列表，仅检测用户输入的VID/PID对应的设备"""
        import subprocess
        import re
        
        self.usb_device_list.clear()
        self.usb_refresh_btn.setEnabled(False)
        self.usb_refresh_btn.setText("扫描中...")
        
        try:
            # 获取用户输入的VID和PID
            vid_text = self.vid_input.text().strip().upper()
            pid_text = self.pid_input.text().strip().upper()
            
            # 验证输入是否为有效的十六进制格式
            if not re.match(r'^0X[0-9A-F]{4}$', vid_text) or not re.match(r'^0X[0-9A-F]{4}$', pid_text):
                QMessageBox.warning(self, "警告", "请输入有效的十六进制VID/PID（例如：0x0465）")
                return
            
            # 提取纯十六进制部分（去掉0x前缀）
            target_vid = vid_text[2:]
            target_pid = pid_text[2:]
            
            logger.info(f"开始扫描USB设备: VID=0x{target_vid}, PID=0x{target_pid}")
            
            # 使用wmic命令获取所有即插即用设备
            cmd = "wmic path Win32_PnPEntity get DeviceID, Name"
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding='gbk')
            
            if result.returncode != 0:
                logger.error(f"执行wmic命令失败: {result.stderr}")
                QMessageBox.critical(self, "错误", "执行USB设备扫描命令失败")
                return
            
            output = result.stdout
            lines = output.strip().split('\n')[1:]  # 跳过标题行
            
            # 去重设备列表（基于DeviceID）
            device_ids = set()
            found_devices = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 提取DeviceID和Name - 使用正则表达式处理多个空格
                parts = re.split(r'\s{2,}', line)
                if len(parts) < 2:
                    continue
                    
                device_id = parts[0].strip()
                device_name = ' '.join(parts[1:]).strip()
                
                # 检查是否为USB设备且包含目标VID和PID
                if device_id.startswith('USB\\') and device_id not in device_ids:
                    # 从DeviceID中提取VID和PID
                    vid_pid_match = re.search(r'VID_(\w+)&PID_(\w+)', device_id)
                    if vid_pid_match:
                        vendor_id_hex = vid_pid_match.group(1)
                        product_id_hex = vid_pid_match.group(2)
                        
                        # 检查是否匹配目标VID和PID
                        if vendor_id_hex == target_vid and product_id_hex == target_pid:
                            device_ids.add(device_id)
                            found_devices.append((device_id, device_name, vendor_id_hex, product_id_hex))
            
            logger.info(f"找到 {len(found_devices)} 个匹配的USB设备")
            
            if found_devices:
                for i, (device_id, device_name, vendor_id_hex, product_id_hex) in enumerate(found_devices):
                    try:
                        vendor_id = int(vendor_id_hex, 16)
                        product_id = int(product_id_hex, 16)
                        
                        # 格式化设备信息（与设备管理器中格式一致）
                        display_device_id = f"USB\\VID_{vendor_id_hex}&PID_{product_id_hex}"
                        device_info = f"{display_device_id}"
                        if device_name:
                            device_info += f" - {device_name}"
                        
                        # 添加到设备列表
                        item = QListWidgetItem(device_info)
                        item.setData(Qt.UserRole, (vendor_id, product_id))  # 存储VID和PID
                        self.usb_device_list.addItem(item)
                        
                        logger.info(f"找到匹配设备: VID=0x{vendor_id_hex}, PID=0x{product_id_hex}, 名称={device_name}")
                    except Exception as e:
                        logger.error(f"处理USB设备时出错: {str(e)}")
                        continue
                
                QMessageBox.information(self, "提示", f"找到 {len(found_devices)} 个匹配的USB设备")
            else:
                QMessageBox.information(self, "提示", f"未找到VID=0x{target_vid}, PID=0x{target_pid}的USB设备")
                logger.info(f"未找到VID=0x{target_vid}, PID=0x{target_pid}的USB设备")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"扫描USB设备时出错: {str(e)}")
            logger.error(f"扫描USB设备时出错: {str(e)}")
        finally:
            self.usb_refresh_btn.setEnabled(True)
            self.usb_refresh_btn.setText("刷新设备")

    def on_usb_device_selected(self, item):
        """USB设备选择事件"""
        vendor_id, product_id = item.data(Qt.UserRole)
        
        # 填充VID和PID输入框
        self.vid_input.setText(f"0x{vendor_id:04X}")
        self.pid_input.setText(f"0x{product_id:04X}")
        
        logger.info(f"选择USB设备: VID=0x{vendor_id:04X}, PID=0x{product_id:04X}")

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
            
    def validate_hex_input(self):
        """验证十六进制输入"""
        import re
        
        # 检查VID输入
        vid_text = self.vid_input.text()
        vid_valid = bool(re.match(r'^0x[0-9A-Fa-f]{4}$', vid_text))
        if vid_valid:
            self.vid_input.setStyleSheet("")
        else:
            self.vid_input.setStyleSheet("background-color: #FFD6D6;")
            
        # 检查PID输入
        pid_text = self.pid_input.text()
        pid_valid = bool(re.match(r'^0x[0-9A-Fa-f]{4}$', pid_text))
        if pid_valid:
            self.pid_input.setStyleSheet("")
        else:
            self.pid_input.setStyleSheet("background-color: #FFD6D6;")

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
        elif self.usb_radio.isChecked():
            protocol = "USB"
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
        elif protocol == "USB":
            try:
                vid = int(self.vid_input.text().strip(), 16)
                pid = int(self.pid_input.text().strip(), 16)
            except ValueError:
                # 如果VID或PID格式错误，返回空
                return None
                
            # 获取选中的USB设备地址 (如果有)
            address = None
            if hasattr(self, 'usb_device_list'):
                selected_items = self.usb_device_list.selectedItems()
                if selected_items:
                    address = selected_items[0].data(Qt.UserRole)
            
            # 返回USB连接信息，包含VID和PID（必须），可选地址
            return {"protocol": "USB", "vid": vid, "pid": pid, "address": address}

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
