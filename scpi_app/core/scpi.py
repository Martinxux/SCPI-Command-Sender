# -*- coding: utf-8 -*-
"""
SCPI仪器通信核心模块

该模块提供了SCPIInstrument类，用于与支持SCPI协议的仪器设备进行通信。支持TCP/IP和VISA连接、命令发送和响应接收等功能。

主要功能:
- 建立和断开TCP/IP连接
- 建立和断开VISA连接
- 发送SCPI命令并接收响应
- 支持批量命令发送
- 提供连接状态检查
- 完善的错误处理机制

典型使用示例:
```python
from scpi_app.core.scpi import SCPIInstrument

# 创建SCPI仪器实例(TCP/IP)
instrument = SCPIInstrument(host='192.168.1.100', port=5025)

# 连接仪器
instrument.connect()

# 发送查询命令
response = instrument.send_command('*IDN?')
print(f"仪器标识: {response}")

# 发送设置命令
instrument.send_command(':VOLTage 10.0')

# 断开连接
instrument.disconnect()

# 创建SCPI仪器实例(VISA)
instrument = SCPIInstrument(visa_address='TCPIP::192.168.1.100::5025::SOCKET')

# 连接仪器
instrument.connect()

# 发送查询命令
response = instrument.send_command('*IDN?')
print(f"仪器标识: {response}")

# 断开连接
instrument.disconnect()
```
"""

import socket
import time
from typing import List, Tuple, Optional
from scpi_app.logger import logger
from scpi_app.exceptions import (
    SCPIError,
    ConnectionTimeoutError,
    ConnectionRefusedError,
    ConnectionClosedError,
)


class SCPIInstrument:
    """
    SCPI仪器通信类

    用于与支持SCPI协议的仪器设备进行通信，支持TCP/IP、VISA和直接USB连接。

    属性:
        host: 仪器设备的IP地址
        port: 仪器设备的端口号
        visa_address: 仪器设备的VISA地址
        vid: USB设备的供应商ID
        pid: USB设备的产品ID
        sock: TCP连接套接字
        visa_instr: VISA仪器实例
        usb_serial: USB串口连接
        timeout: 连接超时时间(秒)
        connection_type: 连接类型 ('tcpip', 'visa' 或 'usb')

    参数:
        host: 仪器设备的IP地址，默认为'127.0.0.1'
        port: 仪器设备的端口号，默认为8805
        visa_address: 仪器设备的VISA地址，若提供则使用VISA连接
        vid: USB设备的供应商ID (十六进制或整数)
        pid: USB设备的产品ID (十六进制或整数)
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8805, visa_address: Optional[str] = None, vid: Optional[str] = None, pid: Optional[str] = None):
        """
        初始化SCPIInstrument实例

        参数:
            host: 仪器设备的IP地址，默认为'127.0.0.1'
            port: 仪器设备的端口号，默认为8805
            visa_address: 仪器设备的VISA地址，若提供则使用VISA连接
            vid: USB设备的供应商ID (十六进制或整数)
            pid: USB设备的产品ID (十六进制或整数)
        """
        self.host = host  # 仪器设备的IP地址
        self.port = port  # 仪器设备的端口号
        self.visa_address = visa_address  # 仪器设备的VISA地址
        
        # USB设备参数
        self.vid = vid  # USB设备的供应商ID
        self.pid = pid  # USB设备的产品ID
        
        self.sock: Optional[socket.socket] = None  # TCP连接套接字，初始为None表示未连接
        self.visa_instr = None  # VISA仪器实例，初始为None表示未连接
        self.usb_serial = None  # USB串口连接，初始为None表示未连接
        self.timeout: float = 10.0  # 连接超时时间，单位为秒
        self.connection_type: Optional[str] = None  # 连接类型 ('tcpip', 'visa' 或 'usb')

    def connect(self) -> bool:
        """
        连接到SCPI仪器设备

        根据初始化参数选择连接方式：
        - 如果提供了visa_address，则使用VISA连接
        - 如果提供了vid和pid，则使用直接USB连接
        - 否则使用TCP/IP连接

        返回:
            bool: 连接成功返回True，失败则抛出异常

        异常:
            ConnectionTimeoutError: 连接超时
            ConnectionRefusedError: 连接被拒绝
            SCPIError: 其他连接错误
        """
        # 如果提供了VISA地址，则使用VISA连接
        if self.visa_address:
            return self._connect_visa()
        # 如果提供了VID和PID，则使用直接USB连接
        elif self.vid and self.pid:
            return self._connect_usb()
        # 否则使用TCP/IP连接
        else:
            return self._connect_tcpip()

    def _connect_tcpip(self) -> bool:
        """
        使用TCP/IP连接到SCPI仪器设备

        返回:
            bool: 连接成功返回True，失败则抛出异常
        """
        try:
            # 创建TCP套接字
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置连接超时时间
            self.sock.settimeout(self.timeout)
            # 建立TCP连接
            self.sock.connect((self.host, self.port))
            self.connection_type = 'tcpip'
            logger.info(f"成功通过TCP/IP连接到仪器: {self.host}:{self.port}")
            return True
        except socket.timeout:
            logger.error(f"TCP/IP连接超时: {self.host}:{self.port}")
            raise ConnectionTimeoutError(
                "连接超时，请检查上位机IP和端口", host=self.host, port=self.port
            )
        except ConnectionRefusedError:
            logger.error(f"TCP/IP连接被拒绝: {self.host}:{self.port}")
            raise ConnectionRefusedError(
                "连接被拒绝，请确保:\n1. 上位机IP地址正确\n2. 上位机SCPI服务已启用\n3. 防火墙允许该端口连接",
                host=self.host,
                port=self.port,
            )
        except Exception as e:
            logger.error(f"TCP/IP连接错误: {str(e)}")
            raise SCPIError(f"TCP/IP连接错误: {str(e)}")

    def _connect_visa(self) -> bool:
        """
        使用VISA连接到SCPI仪器设备

        返回:
            bool: 连接成功返回True，失败则抛出异常
        """
        try:
            # 动态导入pyvisa，避免依赖问题
            import pyvisa
            # 创建VISA资源管理器
            rm = pyvisa.ResourceManager()
            # 打开VISA资源
            self.visa_instr = rm.open_resource(self.visa_address)
            # 设置超时时间
            self.visa_instr.timeout = self.timeout * 1000  # pyvisa超时单位为毫秒
            # 设置读取终止符
            self.visa_instr.read_termination = '\n'
            # 设置写入终止符
            self.visa_instr.write_termination = '\n'
            self.connection_type = 'visa'
            logger.info(f"成功通过VISA连接到仪器: {self.visa_address}")
            return True
        except pyvisa.VisaIOError as e:
            logger.error(f"VISA连接错误: {str(e)}")
            raise SCPIError(f"VISA连接错误: {str(e)}")
        except Exception as e:
            logger.error(f"VISA连接错误: {str(e)}")
            raise SCPIError(f"VISA连接错误: {str(e)}")

    def _connect_usb(self) -> bool:
        """
        通过USB连接到SCPI仪器设备
        支持直接USB设备(通过pyusb)和USB串口设备(通过pyserial)

        返回:
            bool: 连接成功返回True，失败则抛出异常
        """
        try:
            import subprocess
            import re
            
            # 将VID/PID转换为整数
            try:
                vid = int(self.vid, 16) if isinstance(self.vid, str) and self.vid.startswith('0x') else int(self.vid)
                pid = int(self.pid, 16) if isinstance(self.pid, str) and self.pid.startswith('0x') else int(self.pid)
            except ValueError:
                logger.error(f"无效的VID/PID格式: VID={self.vid}, PID={self.pid}")
                raise SCPIError(f"无效的VID/PID格式: VID={self.vid}, PID={self.pid}")
            
            # 首先使用wmic命令确认设备是否存在
            logger.info(f"使用wmic命令确认USB设备是否存在: VID=0x{vid:04X}, PID=0x{pid:04X}")
            found_via_wmic = False
            
            try:
                # 使用wmic命令获取所有即插即用设备
                cmd = "wmic path Win32_PnPEntity get DeviceID, Name"
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding='gbk')
                
                if result.returncode == 0:
                    output = result.stdout
                    lines = output.strip().split('\n')[1:]  # 跳过标题行
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # 提取DeviceID和Name
                        parts = re.split(r'\s{2,}', line)
                        if len(parts) < 2:
                            continue
                            
                        device_id = parts[0].strip()
                        device_name = ' '.join(parts[1:]).strip()
                        
                        # 检查是否为USB设备且包含目标VID和PID
                        if device_id.startswith('USB\\'):
                            vid_pid_match = re.search(r'VID_(\w+)&PID_(\w+)', device_id)
                            if vid_pid_match:
                                vendor_id_hex = vid_pid_match.group(1)
                                product_id_hex = vid_pid_match.group(2)
                                
                                # 转换为整数
                                device_vid = int(vendor_id_hex, 16)
                                device_pid = int(product_id_hex, 16)
                                
                                # 检查是否匹配目标VID和PID
                                if device_vid == vid and device_pid == pid:
                                    found_via_wmic = True
                                    logger.info(f"wmic命令确认设备存在: {device_id} - {device_name}")
                                    break
            except Exception as e:
                logger.warning(f"wmic设备检测失败: {str(e)}")
            
            # 如果wmic都检测不到设备，直接抛出错误
            if not found_via_wmic:
                logger.error(f"设备未找到: VID=0x{vid:04X}, PID=0x{pid:04X}")
                raise SCPIError(f"未找到USB设备: VID=0x{vid:04X}, PID=0x{pid:04X}", code=1000)
            
            # 1. 首先尝试使用pyusb直接连接USB设备
            usb_device = None
            try:
                import usb.core
                import usb.util
                
                logger.info(f"尝试使用pyusb连接直接USB设备: VID=0x{vid:04X}, PID=0x{pid:04X}")
                
                # 查找符合VID/PID的设备
                device = usb.core.find(idVendor=vid, idProduct=pid)
                
                if device is not None:
                    logger.info(f"找到USB设备: VID=0x{vid:04X}, PID=0x{pid:04X}")
                    
                    # 尝试获取设备描述
                    try:
                        manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "未知"
                        product = usb.util.get_string(device, device.iProduct) if device.iProduct else "未知"
                        logger.info(f"设备信息: 制造商={manufacturer}, 产品={product}")
                    except Exception as e:
                        logger.info(f"获取设备描述失败: {str(e)}")
                        pass
                    
                    # 尝试获取设备配置
                    if device.is_kernel_driver_active(0):
                        try:
                            device.detach_kernel_driver(0)
                            logger.info("已分离内核驱动")
                        except Exception as e:
                            logger.warning(f"分离内核驱动失败: {str(e)}")
                            
                    # 设置配置
                    device.set_configuration()
                    
                    # 获取端点
                    cfg = device.get_active_configuration()
                    intf = cfg[(0, 0)]
                    
                    # 查找输出端点(发送命令)
                    ep_out = usb.util.find_descriptor(
                        intf,
                        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
                    )
                    
                    # 查找输入端点(接收响应)
                    ep_in = usb.util.find_descriptor(
                        intf,
                        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
                    )
                    
                    if ep_out and ep_in:
                        logger.info(f"找到USB端点: 输出={ep_out}, 输入={ep_in}")
                        # 存储USB设备信息
                        self.usb_device = device
                        self.usb_endpoints = (ep_out, ep_in)
                        self.connection_type = 'usb'
                        logger.info(f"成功通过直接USB连接到仪器: VID=0x{vid:04X}, PID=0x{pid:04X}")
                        return True
                    else:
                        logger.warning("未找到合适的USB端点，尝试USB串口连接")
                        usb_device = device  # 保存设备信息
                else:
                    logger.info(f"pyusb未找到指定的直接USB设备: VID=0x{vid:04X}, PID=0x{pid:04X}")
                    
            except ImportError:
                logger.info("pyusb模块未安装，跳过直接USB设备连接")
            except usb.core.NoBackendError:
                logger.error("pyusb找不到后端，无法使用直接USB连接")
                logger.info("解决方案: 安装libusb-win32或libusbK驱动，并确保pyusb可以找到驱动后端。")
                logger.info("提示1: 可以尝试使用Zadig工具为设备安装兼容的libusb驱动。")
                logger.info("提示2: 将libusbK.dll复制到Python的DLLs目录或项目根目录。")
                logger.info("提示3: 确保当前使用的Python环境已安装pyusb库。")
                
                # 复制项目中的libusbK.dll到Python的DLLs目录（如果存在）
                try:
                    import shutil
                    import os
                    import sys
                    
                    # 获取Python的DLLs目录
                    python_dlls_dir = os.path.join(os.path.dirname(sys.executable), "DLLs")
                    
                    # 检查项目中的libusbK.dll是否存在
                    libusbk_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libusbK.dll")
                    if os.path.exists(libusbk_src) and os.path.exists(python_dlls_dir):
                        libusbk_dest = os.path.join(python_dlls_dir, "libusbK.dll")
                        shutil.copy2(libusbk_src, libusbk_dest)
                        logger.info(f"已将libusbK.dll复制到Python的DLLs目录: {libusbk_dest}")
                        logger.info("请重新运行程序，pyusb可能现在可以找到后端了。")
                except Exception as e:
                    logger.warning(f"无法复制libusbK.dll: {str(e)}")
            except Exception as e:
                logger.error(f"直接USB连接失败: {str(e)}")
                logger.info("详细错误信息: " + repr(e))
                logger.info("提示: 如果是权限问题，请尝试以管理员身份运行程序；如果是驱动问题，请安装正确的设备驱动。")
                logger.info("尝试USB串口连接...")
            
            # 2. 尝试使用pyserial连接USB串口设备
            try:
                import serial
                import serial.tools.list_ports
                
                logger.info(f"使用pyserial查找USB串口设备: VID=0x{vid:04X}, PID=0x{pid:04X}")
                
                # 查找所有符合VID/PID的端口
                ports = serial.tools.list_ports.comports()
                target_port = None
                
                logger.info(f"检测到的所有串口端口数量: {len(ports)}")
                
                for port in ports:
                    logger.info(f"检查端口: {port.device}, VID={port.vid}, PID={port.pid}, 名称={port.name}, 描述={port.description}")
                    
                    # 检查VID/PID是否匹配
                    if port.vid == vid and port.pid == pid:
                        target_port = port.device
                        logger.info(f"找到匹配的USB串口设备: {port.device}")
                        break
                
                if not ports:
                    logger.info("提示: 未检测到任何串口设备，可能是因为没有安装USB转串口驱动或设备未正确配置为串口模式。")
                    logger.info("解决方案: 安装设备的官方驱动程序，确保设备被识别为串口设备。")
                
                if target_port:
                    try:
                        # 打开串口连接
                        self.usb_serial = serial.Serial(
                            port=target_port,
                            baudrate=9600,  # 默认波特率，根据设备实际情况调整
                            timeout=self.timeout,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS
                        )
                        
                        self.connection_type = 'usb'
                        logger.info(f"成功通过USB串口连接到仪器: {target_port} (VID=0x{vid:04X}, PID=0x{pid:04X})")
                        return True
                    except serial.SerialException as e:
                        logger.error(f"USB串口连接错误: {str(e)}")
                        raise SCPIError(f"USB串口连接错误: {str(e)}")
                    except Exception as e:
                        logger.error(f"打开USB串口失败: {str(e)}")
                        raise SCPIError(f"打开USB串口失败: {str(e)}")
                else:
                    logger.error(f"未找到USB串口设备: VID=0x{vid:04X}, PID=0x{pid:04X}")
                    logger.info("检测到的所有USB设备:")
                    found_devices = False
                    for port in ports:
                        found_devices = True
                        vid_str = f"0x{port.vid:04X}" if port.vid is not None else "N/A"
                        pid_str = f"0x{port.pid:04X}" if port.pid is not None else "N/A"
                        logger.info(f"  端口: {port.device}, VID={vid_str}, PID={pid_str}, 名称: {port.description}")
                    if not found_devices:
                        logger.info("  没有检测到任何USB设备")
                    
                    # 如果wmic检测到设备但无法连接，提示用户
                    if found_via_wmic:
                        raise SCPIError(f"找到USB设备但无法建立连接: VID=0x{vid:04X}, PID=0x{pid:04X}。可能需要安装特定驱动或使用不同的连接方式。", code=1000)
                    else:
                        raise SCPIError(f"未找到USB设备: VID=0x{vid:04X}, PID=0x{pid:04X}", code=1000)
                        
            except ImportError:
                logger.error("pyserial模块未安装，无法使用USB串口连接")
                # 如果wmic检测到设备但pyserial不可用，提示用户
                if found_via_wmic:
                    raise SCPIError(f"找到USB设备但无法建立连接: VID=0x{vid:04X}, PID=0x{pid:04X}。pyserial模块未安装，无法使用USB串口连接。", code=1000)
                else:
                    raise SCPIError("USB连接失败: pyserial模块未安装")
                
        except ImportError as e:
            logger.error(f"USB连接失败: 模块导入错误 - {str(e)}")
            raise SCPIError(f"USB连接失败: 模块导入错误 - {str(e)}")
        except SCPIError:
            # 直接重新抛出SCPIError，避免重复添加错误代码
            raise
        except Exception as e:
            logger.error(f"USB连接错误: {str(e)}")
            # 如果wmic检测到设备，提示设备存在但无法连接
            if found_via_wmic:
                raise SCPIError(f"找到USB设备但无法建立连接: VID=0x{vid:04X}, PID=0x{pid:04X}。错误信息: {str(e)}", code=1000)
            else:
                raise SCPIError(f"USB连接错误: {str(e)}", code=1000)

    def disconnect(self) -> None:
        """
        断开与SCPI仪器设备的连接

        关闭连接并将相应属性设置为None。
        无论当前是否已连接，调用此方法都是安全的。
        """
        if self.connection_type == 'tcpip' and self.sock:
            # 断开TCP/IP连接
            try:
                self.sock.close()
                logger.info(f"成功断开与仪器的TCP/IP连接")
            except Exception as e:
                logger.error(f"断开TCP/IP连接时出错: {str(e)}")
            finally:
                self.sock = None  # 确保套接字引用被清除
                self.connection_type = None
        elif self.connection_type == 'visa' and self.visa_instr:
            # 断开VISA连接
            try:
                self.visa_instr.close()
                logger.info(f"成功断开与仪器的VISA连接")
            except Exception as e:
                logger.error(f"断开VISA连接时出错: {str(e)}")
            finally:
                self.visa_instr = None  # 确保VISA仪器引用被清除
                self.connection_type = None
        elif self.connection_type == 'usb':
            # 断开USB连接
            if hasattr(self, 'usb_serial') and self.usb_serial:
                # 断开USB串口连接
                try:
                    self.usb_serial.close()
                    logger.info(f"成功断开与仪器的USB串口连接")
                except Exception as e:
                    logger.error(f"断开USB串口连接时出错: {str(e)}")
                finally:
                    self.usb_serial = None
            
            if hasattr(self, 'usb_device') and self.usb_device:
                # 断开直接USB设备连接
                try:
                    import usb.util
                    usb.util.dispose_resources(self.usb_device)
                    logger.info(f"成功断开与仪器的直接USB连接")
                except Exception as e:
                    logger.error(f"断开直接USB连接时出错: {str(e)}")
                finally:
                    self.usb_device = None
                    self.usb_endpoints = None
            
            self.connection_type = None

    def is_connected(self) -> bool:
        """
        检查是否已与仪器设备建立连接

        返回:
            bool: 已连接返回True，未连接返回False
        """
        if self.connection_type == 'tcpip':
            return self.sock is not None
        elif self.connection_type == 'visa':
            return self.visa_instr is not None
        elif self.connection_type == 'usb':
            # 检查是否是USB串口连接
            if hasattr(self, 'usb_serial') and self.usb_serial:
                return self.usb_serial.is_open
            # 检查是否是直接USB设备连接
            if hasattr(self, 'usb_device') and self.usb_device:
                return True
            return False
        return False

    def send_command(self, command: str, timeout: float = 5.0) -> Optional[str]:
        """
        发送SCPI命令并获取响应(如果有)

        参数:
            command: SCPI命令
            timeout: 响应超时时间(秒)

        返回:
            响应内容(对于查询命令)或None
        """
        if not self.is_connected():
            raise ConnectionClosedError("未连接到上位机")

        try:
            if self.connection_type == 'tcpip':
                # 通过TCP/IP发送命令
                full_cmd = command + "\n"
                self.sock.settimeout(timeout)
                self.sock.sendall(full_cmd.encode("utf-8"))

                # 如果是查询命令，等待响应
                if command.endswith("?"):
                    response = self.sock.recv(1024)
                    if response:
                        return response.decode("utf-8").strip()
                    return None
                return None
            elif self.connection_type == 'visa':
                # 通过VISA发送命令
                self.visa_instr.timeout = timeout * 1000  # pyvisa超时单位为毫秒

                # 如果是查询命令，使用query方法
                if command.endswith("?"):
                    response = self.visa_instr.query(command)
                    return response.strip()
                # 否则使用write方法
                else:
                    self.visa_instr.write(command)
                    return None
            elif self.connection_type == 'usb':
                # 检查是直接USB设备还是USB串口设备
                if hasattr(self, 'usb_device') and self.usb_device:
                    # 通过直接USB设备发送命令
                    try:
                        ep_out, ep_in = self.usb_endpoints
                        
                        # 发送命令
                        full_cmd = command + "\n"
                        ep_out.write(full_cmd.encode("utf-8"))
                        
                        # 如果是查询命令，等待响应
                        if command.endswith("?"):
                            response = b""
                            start_time = time.time()
                            while time.time() - start_time < timeout:
                                data = ep_in.read(64, timeout=100)
                                if data:
                                    response += data
                                    if b"\n" in response:
                                        break
                            
                            if response:
                                return response.decode("utf-8").strip()
                            return None
                        return None
                    except Exception as e:
                        logger.error(f"直接USB设备发送命令失败: {str(e)}")
                        raise SCPIError(f"直接USB设备发送命令失败: {str(e)}")
                elif hasattr(self, 'usb_serial') and self.usb_serial:
                    # 通过USB串口发送命令
                    self.usb_serial.timeout = timeout
                    
                    # 发送命令
                    full_cmd = command + "\n"
                    self.usb_serial.write(full_cmd.encode("utf-8"))
                    
                    # 如果是查询命令，等待响应
                    if command.endswith("?"):
                        response = self.usb_serial.readline()
                        if response:
                            return response.decode("utf-8").strip()
                        return None
                    return None
                return None
            return None

        except socket.timeout:
            raise SCPIError(f"命令 '{command}' 超时", details={"command": command})
        except Exception as e:
            raise SCPIError(
                f"发送命令 '{command}' 时出错: {str(e)}", details={"command": command}
            )

    def send_command_sequence(
        self, commands: List[str], repeat: int = 1, interval: float = 1.0
    ) -> List[Tuple[str, Optional[str]]]:
        """
        发送命令序列

        参数:
            commands: 命令列表
            repeat: 重复次数
            interval: 命令间隔(秒)

        返回:
            包含(命令, 响应)的元组列表
        """
        results: List[Tuple[str, Optional[str]]] = []
        for loop in range(repeat):
            for cmd in commands:
                try:
                    if cmd.endswith("?"):
                        response = self.send_command(cmd)
                        results.append((cmd, response))
                    else:
                        self.send_command(cmd)
                        results.append((cmd, "OK"))
                    # 等待间隔(最后一次循环的最后一个命令后不等待)
                    if not (loop == repeat - 1 and cmd == commands[-1]):
                        time.sleep(interval)
                except SCPIError as e:
                    results.append((cmd, f"ERROR: {str(e)}"))
                    raise
        return results
