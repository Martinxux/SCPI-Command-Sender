# 连接相关异常类

from typing import Dict, Optional, Any
from .base import SCPIAppError


class ConnectionError(SCPIAppError):
    """
    连接相关异常
    """

    def __init__(
        self, message: str, code: int = 2000, details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化连接异常

        参数:
            message: 异常信息
            code: 错误代码，默认为2000
            details: 详细错误信息
        """
        super().__init__(message, code, details)


class ConnectionTimeoutError(ConnectionError):
    """
    连接超时异常
    """

    def __init__(
        self,
        message: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        code: int = 2001,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化连接超时异常

        参数:
            message: 异常信息
            host: 目标主机地址
            port: 目标端口
            code: 错误代码，默认为2001
            details: 详细错误信息
        """
        if host or port:
            if not details:
                details = {}
            if host:
                details["host"] = host
            if port:
                details["port"] = port
        super().__init__(message, code, details)


class ConnectionRefusedError(ConnectionError):
    """
    连接被拒绝异常
    """

    def __init__(
        self,
        message: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        code: int = 2002,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化连接被拒绝异常

        参数:
            message: 异常信息
            host: 目标主机地址
            port: 目标端口
            code: 错误代码，默认为2002
            details: 详细错误信息
        """
        if host or port:
            if not details:
                details = {}
            if host:
                details["host"] = host
            if port:
                details["port"] = port
        super().__init__(message, code, details)


class ConnectionClosedError(ConnectionError):
    """
    连接已关闭异常
    """

    def __init__(
        self,
        message: str = "连接已关闭",
        code: int = 2003,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化连接已关闭异常

        参数:
            message: 异常信息，默认为"连接已关闭"
            code: 错误代码，默认为2003
            details: 详细错误信息
        """
        super().__init__(message, code, details)


class InvalidAddressError(ConnectionError):
    """
    无效地址异常
    """

    def __init__(
        self,
        message: str,
        address: Optional[str] = None,
        code: int = 2004,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化无效地址异常

        参数:
            message: 异常信息
            address: 无效的地址
            code: 错误代码，默认为2004
            details: 详细错误信息
        """
        if address:
            if details:
                details["address"] = address
            else:
                details = {"address": address}
        super().__init__(message, code, details)
