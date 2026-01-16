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

    用于与支持SCPI协议的仪器设备进行通信，支持TCP/IP和VISA连接。

    属性:
        host: 仪器设备的IP地址
        port: 仪器设备的端口号
        visa_address: 仪器设备的VISA地址
        sock: TCP连接套接字
        visa_instr: VISA仪器实例
        timeout: 连接超时时间(秒)
        connection_type: 连接类型 ('tcpip' 或 'visa')

    参数:
        host: 仪器设备的IP地址，默认为'127.0.0.1'
        port: 仪器设备的端口号，默认为8805
        visa_address: 仪器设备的VISA地址，若提供则使用VISA连接
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8805, visa_address: Optional[str] = None):
        """
        初始化SCPIInstrument实例

        参数:
            host: 仪器设备的IP地址，默认为'127.0.0.1'
            port: 仪器设备的端口号，默认为8805
            visa_address: 仪器设备的VISA地址，若提供则使用VISA连接
        """
        self.host = host  # 仪器设备的IP地址
        self.port = port  # 仪器设备的端口号
        self.visa_address = visa_address  # 仪器设备的VISA地址
        
        self.sock: Optional[socket.socket] = None  # TCP连接套接字，初始为None表示未连接
        self.visa_instr = None  # VISA仪器实例，初始为None表示未连接
        self.timeout: float = 10.0  # 连接超时时间，单位为秒
        self.connection_type: Optional[str] = None  # 连接类型 ('tcpip' 或 'visa')

    def connect(self) -> bool:
        """
        连接到SCPI仪器设备

        根据初始化参数选择连接方式：
        - 如果提供了visa_address，则使用VISA连接
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