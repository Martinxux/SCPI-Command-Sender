import socket
import time
from typing import List, Tuple, Optional


class SCPIError(Exception):
    """自定义SCPI错误类"""
    pass


class SCPIInstrument:
    def __init__(self, host: str = '127.0.0.1', port: int = 8805):
        self.host = host
        self.port = port
        self.sock = None
        self.timeout = 10

    def connect(self) -> bool:
        """连接上位机"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            return True
        except socket.timeout:
            raise SCPIError("连接超时，请检查上位机IP和端口")
        except ConnectionRefusedError:
            raise SCPIError("连接被拒绝，请确保:\n1. 上位机IP地址正确\n2. 上位机SCPI服务已启用\n3. 防火墙允许该端口连接")
        except Exception as e:
            raise SCPIError(f"连接错误: {str(e)}")

    def disconnect(self):
        """断开连接"""
        if self.sock:
            try:
                self.sock.close()
                logger.info("连接已断开")
            except Exception as e:
                logger.error(f"断开连接时出错: {str(e)}")
            finally:
                self.sock = None

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.sock is not None

    def send_command(self, command: str, timeout: float = 5.0) -> str:
        """
        发送SCPI命令并获取响应(如果有)

        参数:
            command: SCPI命令
            timeout: 响应超时时间(秒)

        返回:
            对于查询命令: 返回响应内容或空字符串(如果无响应)
            对于设置命令: 返回"OK"表示成功
        """
        if not self.is_connected():
            raise SCPIError("未连接到上位机")

        try:
            # 发送命令(添加换行符)
            full_cmd = command + '\n'
            logger.info(f"发送命令: {command}")
            self.sock.sendall(full_cmd.encode('utf-8'))

            # 如果是查询命令，等待响应
            if command.endswith('?'):
                self.sock.settimeout(timeout)
                response = self.sock.recv(1024)
                if response:
                    decoded = response.decode('utf-8').strip()
                    logger.info(f"收到响应: {decoded}")
                    return decoded
                logger.warning("查询命令但无响应")
                return ""  # 返回空字符串而不是None
            else:
                # 对于设置命令，返回确认响应
                logger.info("设置命令执行成功")
                return "OK"

        except socket.timeout:
            logger.error(f"命令 '{command}' 超时")
            raise SCPIError(f"命令 '{command}' 超时")
        except Exception as e:
            logger.error(f"发送命令 '{command}' 时出错: {str(e)}")
            raise SCPIError(f"发送命令 '{command}' 时出错: {str(e)}")

    def send_command_sequence(self, commands: List[str], repeat: int = 1, interval: float = 1.0) -> List[
        Tuple[str, Optional[str]]]:
        """
        发送命令序列

        参数:
            commands: 命令列表
            repeat: 重复次数
            interval: 命令间隔(秒)

        返回:
            包含(命令, 响应)的元组列表
        """
        results = []
        for loop in range(repeat):
            for cmd in commands:
                try:
                    response = self.send_command(cmd)
                    results.append((cmd, response))
                    # 等待间隔(最后一次循环的最后一个命令后不等待)
                    if not (loop == repeat - 1 and cmd == commands[-1]):
                        time.sleep(interval)
                except SCPIError as e:
                    results.append((cmd, f"ERROR: {str(e)}"))
                    raise
        return results