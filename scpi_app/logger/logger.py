# -*- coding: utf-8 -*-
"""
日志管理模块

该模块提供了一个简单易用的日志管理功能，支持日志分级记录、文件轮转等特性。
主要用于SCPI Command Sender应用程序的日志记录，方便调试和问题追踪。

主要功能:
- 支持INFO、WARNING、ERROR三个日志级别
- 自动按日期创建日志文件
- 支持日志文件大小限制和自动轮转
- 提供全局日志实例，方便在应用程序的任何地方使用

典型使用示例:
```python
from scpi_app.logger import logger

# 记录信息日志
logger.info("应用程序启动")

# 记录警告日志
logger.warning("配置文件不存在，使用默认配置")

# 记录错误日志
logger.error("连接仪器失败: 连接超时")
```
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """
    日志级别枚举类

    定义了支持的日志级别:
    - INFO: 信息级别，用于记录普通操作信息
    - WARNING: 警告级别，用于记录可能的问题
    - ERROR: 错误级别，用于记录严重错误
    """

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Logger:
    """
    日志管理类

    用于管理应用程序的日志记录，支持日志分级、文件轮转等功能。

    属性:
        log_dir: 日志文件存储目录
        log_file: 日志文件路径
        logger: 内部使用的logging.Logger实例

    参数:
        log_dir: 日志文件存储目录，默认为"logs"
    """

    def __init__(self, log_dir="logs"):
        """
        初始化Logger实例

        参数:
            log_dir: 日志文件存储目录，默认为"logs"
        """
        self.log_dir = log_dir  # 日志文件存储目录
        self._ensure_log_dir()  # 确保日志目录存在
        self.log_file = self._get_log_file_path()  # 获取日志文件路径
        self._setup_file_handler()  # 设置日志文件处理器

    def _ensure_log_dir(self):
        """
        确保日志目录存在

        如果日志目录不存在，则创建该目录。
        """
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"创建日志目录: {self.log_dir}")

    def _get_log_file_path(self) -> str:
        """
        获取日志文件路径

        生成按日期命名的日志文件路径，格式为"SCPI_Log_YYYYMMDD.log"。

        返回:
            str: 日志文件的完整路径
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.log_dir, f"SCPI_Log_{timestamp}.log")

    def _setup_file_handler(self):
        """
        设置日志文件处理器

        配置logging模块，使用RotatingFileHandler来处理日志记录，
        支持日志文件大小限制(10MB)和自动轮转，保留最近5个备份文件。
        """
        # 创建或获取名为"SCPI_Logger"的logger实例
        self.logger = logging.getLogger("SCPI_Logger")
        # 设置日志级别为INFO，低于该级别的日志将被忽略
        self.logger.setLevel(logging.INFO)

        # 设置RotatingFileHandler，限制单个文件大小为10MB，保留5个备份
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 单个日志文件最大大小为10MB
            backupCount=5,  # 保留5个备份文件
            encoding="utf-8",  # 使用UTF-8编码
        )

        # 设置日志格式
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",  # 日期格式
        )
        handler.setFormatter(formatter)

        # 添加处理器到logger实例
        self.logger.addHandler(handler)

    def _write_log(self, level: LogLevel, message: str):
        """
        写入日志到文件

        根据指定的日志级别，将日志信息写入到日志文件中。

        参数:
            level: 日志级别，必须是LogLevel枚举值
            message: 日志信息
        """
        # 日志级别映射，将自定义的LogLevel枚举映射到logging模块的方法
        log_method = {
            LogLevel.INFO: self.logger.info,
            LogLevel.WARNING: self.logger.warning,
            LogLevel.ERROR: self.logger.error,
        }
        # 调用对应的日志方法写入日志
        log_method[level](message)

    def info(self, message: str):
        """
        记录信息级别日志

        参数:
            message: 要记录的信息日志内容
        """
        self._write_log(LogLevel.INFO, message)

    def warning(self, message: str):
        """
        记录警告级别日志

        参数:
            message: 要记录的警告日志内容
        """
        self._write_log(LogLevel.WARNING, message)

    def error(self, message: str):
        """
        记录错误级别日志

        参数:
            message: 要记录的错误日志内容
        """
        self._write_log(LogLevel.ERROR, message)

    def get_timestamp(self) -> str:
        """
        获取当前时间戳字符串

        返回:
            str: 格式化的时间戳字符串，格式为"[YYYY-MM-DD HH:MM:SS]"
        """
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


# 全局日志实例
# 应用程序中可以直接导入并使用此实例记录日志
logger = Logger()
