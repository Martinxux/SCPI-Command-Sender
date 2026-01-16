# -*- coding: utf-8 -*-
"""
SCPI命令执行后台工作线程模块

该模块提供了SCPIWorker类，用于在后台执行SCPI命令，避免阻塞GUI主线程。

主要功能:
- 在独立线程中执行SCPI命令
- 支持命令批量发送
- 支持重复执行
- 支持命令间隔设置
- 提供命令执行进度更新
- 完善的错误处理机制

典型使用示例:
```python
from scpi_app.core.worker import SCPIWorker
from scpi_app.core.scpi import SCPIInstrument

# 创建SCPI仪器实例
instrument = SCPIInstrument(host='192.168.1.100', port=5025)

# 创建工作线程
worker = SCPIWorker(instrument, ['*IDN?', ':VOLTage 10.0'], repeat=1, interval=1.0)

# 连接信号槽
worker.command_sent.connect(lambda cmd, response, loop: print(f"命令: {cmd}, 响应: {response}, 循环: {loop}"))
worker.progress_updated.connect(lambda current, total: print(f"进度: {current}/{total}"))
worker.finished.connect(lambda: print("执行完成"))
worker.error_occurred.connect(lambda error: print(f"错误: {error}"))

# 启动工作线程
worker.start()
```
"""

import time
from PySide6.QtCore import QThread, Signal
from scpi_app.logger import logger
from scpi_app.exceptions import SCPIError


class SCPIWorker(QThread):
    """用于在后台执行SCPI命令的工作线程"""

    command_sent = Signal(str, str, int)  # 信号：命令发送、响应和循环次数
    progress_updated = Signal(int, int)  # 信号：当前进度和总命令数
    finished = Signal()  # 信号：任务完成
    error_occurred = Signal(str)  # 信号：错误发生

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
        # 请求线程终止
        self.quit()
        # 等待线程安全退出（最多等待2秒）
        self.wait(2000)

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
                        return  # 直接返回，不发送finished信号

                    try:
                        # 为*OPC?命令设置更长的超时时间
                        timeout = 30.0 if cmd.strip() == "*OPC?" else 5.0
                        response = self.instrument.send_command(cmd, timeout)
                        if cmd.endswith("?"):
                            self.command_sent.emit(
                                cmd,
                                str(response) if response else "No response",
                                loop_num,
                            )
                        else:
                            self.command_sent.emit(cmd, "", loop_num)
                        commands_executed += 1
                        self.progress_updated.emit(commands_executed, total_commands)

                        # 等待间隔(最后一次循环的最后一个命令后不等待)
                        if not (loop == self.repeat - 1 and cmd == self.commands[-1]):
                            # 分段等待，以便能够响应停止请求
                            wait_time = self.interval
                            while wait_time > 0 and self._is_running:
                                # 每次等待0.1秒，以便快速响应停止请求
                                sleep_time = min(0.1, wait_time)
                                time.sleep(sleep_time)
                                wait_time -= sleep_time

                    except SCPIError as e:
                        self.error_occurred.emit(str(e))
                        return

            # 只有在正常完成所有命令时才发送finished信号
            # 再次检查_is_running状态，确保用户没有在最后时刻停止执行
            if self._is_running:
                self.finished.emit()
            else:
                # 如果用户停止了执行，不发送finished信号
                return
        except Exception as e:
            self.error_occurred.emit(f"意外错误: {str(e)}")
