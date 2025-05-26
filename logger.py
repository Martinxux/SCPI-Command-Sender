import os
import time
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
        
    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _get_log_file_path(self):
        """获取当天日志文件路径"""
        today = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.log_dir, f"SCPI_Log_{today}.log")
    
    def _write_log(self, level, message):
        """写入日志到文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.value}] {message}\n"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to write log: {str(e)}")
    
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