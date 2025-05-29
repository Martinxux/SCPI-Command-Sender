import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()
        self.log_file = self._get_log_file_path()
        self._setup_file_handler()
        
    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _get_log_file_path(self):
        """获取日志文件路径(精确到秒)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.log_dir, f"SCPI_Log_{timestamp}.log")
    
    def _setup_file_handler(self):
        """设置日志文件处理器"""
        self.logger = logging.getLogger("SCPI_Logger")
        self.logger.setLevel(logging.INFO)
        
        # 设置RotatingFileHandler，限制单个文件大小为10MB，保留5个备份
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _write_log(self, level, message):
        """写入日志到文件"""
        log_method = {
            LogLevel.INFO: self.logger.info,
            LogLevel.WARNING: self.logger.warning,
            LogLevel.ERROR: self.logger.error
        }
        log_method[level](message)
    
    def info(self, message):
        """记录信息级别日志"""
        self._write_log(LogLevel.INFO, message)
    
    def warning(self, message):
        """记录警告级别日志"""
        self._write_log(LogLevel.WARNING, message)
    
    def error(self, message):
        """记录错误级别日志"""
        self._write_log(LogLevel.ERROR, message)
    
    def get_timestamp(self):
        """获取当前时间戳字符串"""
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

# 全局日志实例
logger = Logger()