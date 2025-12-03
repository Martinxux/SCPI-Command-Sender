# SCPI相关异常类

from typing import Dict, Optional, Any
from .base import SCPIAppError


class SCPIError(SCPIAppError):
    """
    SCPI命令执行相关异常
    """

    def __init__(
        self, message: str, code: int = 1000, details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化SCPI异常

        参数:
            message: 异常信息
            code: 错误代码，默认为1000
            details: 详细错误信息
        """
        super().__init__(message, code, details)


class SCPICommandError(SCPIError):
    """
    SCPI命令格式错误
    """

    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        code: int = 1001,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化SCPI命令错误

        参数:
            message: 异常信息
            command: 错误的SCPI命令
            code: 错误代码，默认为1001
            details: 详细错误信息
        """
        if command:
            if details:
                details["command"] = command
            else:
                details = {"command": command}
        super().__init__(message, code, details)


class SCPIResponseError(SCPIError):
    """
    SCPI响应解析错误
    """

    def __init__(
        self,
        message: str,
        response: Optional[str] = None,
        code: int = 1002,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化SCPI响应错误

        参数:
            message: 异常信息
            response: 错误的SCPI响应
            code: 错误代码，默认为1002
            details: 详细错误信息
        """
        if response:
            if details:
                details["response"] = response
            else:
                details = {"response": response}
        super().__init__(message, code, details)
