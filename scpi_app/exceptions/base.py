# 基础异常类

from typing import Dict, Optional, Any


class SCPIAppError(Exception):
    """
    SCPI应用程序的基础异常类
    所有自定义异常都应该继承自这个类
    """

    def __init__(
        self, message: str, code: int = 0, details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化基础异常

        参数:
            message: 异常信息
            code: 错误代码
            details: 详细错误信息
        """
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def __str__(self):
        """
        格式化异常信息

        返回:
            格式化后的异常信息
        """
        base_msg = f"{self.__class__.__name__}: {super().__str__()}"
        if self.code:
            base_msg += f" (错误代码: {self.code})"
        if self.details:
            base_msg += f"\n详细信息: {self.details}"
        return base_msg
