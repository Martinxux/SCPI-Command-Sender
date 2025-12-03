# 配置相关异常类

from .base import SCPIAppError


class ConfigError(SCPIAppError):
    """
    配置相关异常
    """

    def __init__(self, message: str, code: int = 3000, details: dict = None):
        """
        初始化配置异常

        参数:
            message: 异常信息
            code: 错误代码，默认为3000
            details: 详细错误信息
        """
        super().__init__(message, code, details)


class ConfigNotFoundError(ConfigError):
    """
    配置文件未找到异常
    """

    def __init__(
        self,
        message: str,
        file_path: str = None,
        code: int = 3001,
        details: dict = None,
    ):
        """
        初始化配置文件未找到异常

        参数:
            message: 异常信息
            file_path: 配置文件路径
            code: 错误代码，默认为3001
            details: 详细错误信息
        """
        if file_path:
            if details:
                details["file_path"] = file_path
            else:
                details = {"file_path": file_path}
        super().__init__(message, code, details)


class ConfigParseError(ConfigError):
    """
    配置解析错误
    """

    def __init__(
        self,
        message: str,
        file_path: str = None,
        code: int = 3002,
        details: dict = None,
    ):
        """
        初始化配置解析错误

        参数:
            message: 异常信息
            file_path: 配置文件路径
            code: 错误代码，默认为3002
            details: 详细错误信息
        """
        if file_path:
            if details:
                details["file_path"] = file_path
            else:
                details = {"file_path": file_path}
        super().__init__(message, code, details)


class ConfigValidationError(ConfigError):
    """
    配置验证错误
    """

    def __init__(
        self,
        message: str,
        key: str = None,
        value: str = None,
        code: int = 3003,
        details: dict = None,
    ):
        """
        初始化配置验证错误

        参数:
            message: 异常信息
            key: 错误的配置键
            value: 错误的配置值
            code: 错误代码，默认为3003
            details: 详细错误信息
        """
        if key or value:
            if not details:
                details = {}
            if key:
                details["key"] = key
            if value:
                details["value"] = value
        super().__init__(message, code, details)


class ConfigKeyError(ConfigError):
    """
    配置键不存在异常
    """

    def __init__(
        self, message: str, key: str = None, code: int = 3004, details: dict = None
    ):
        """
        初始化配置键不存在异常

        参数:
            message: 异常信息
            key: 不存在的配置键
            code: 错误代码，默认为3004
            details: 详细错误信息
        """
        if key:
            if details:
                details["key"] = key
            else:
                details = {"key": key}
        super().__init__(message, code, details)
