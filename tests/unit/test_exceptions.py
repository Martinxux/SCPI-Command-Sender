# 测试exceptions模块

from scpi_app.exceptions import (
    SCPIAppError,
    SCPIError,
    SCPICommandError,
    SCPIResponseError,
    ConnectionError,
    ConnectionTimeoutError,
    ConnectionRefusedError,
    ConnectionClosedError,
    InvalidAddressError,
    ConfigError,
    ConfigNotFoundError,
    ConfigParseError,
    ConfigValidationError,
    ConfigKeyError,
)


class TestExceptions:
    """测试异常类"""

    def test_scpi_app_error(self):
        """测试基础异常类SCPIAppError"""
        # 测试基本初始化
        error = SCPIAppError("Test error")
        assert str(error) == "SCPIAppError: Test error"
        assert error.code == 0
        assert error.details == {}

        # 测试带错误代码的初始化
        error = SCPIAppError("Test error", code=1000)
        assert str(error) == "SCPIAppError: Test error (错误代码: 1000)"
        assert error.code == 1000

        # 测试带详细信息的初始化
        error = SCPIAppError("Test error", details={"key": "value"})
        assert "详细信息: {'key': 'value'}" in str(error)
        assert error.details == {"key": "value"}

    def test_scpi_error(self):
        """测试SCPIError异常类"""
        error = SCPIError("SCPI error")
        assert isinstance(error, SCPIAppError)
        assert error.code == 1000

    def test_scpi_command_error(self):
        """测试SCPICommandError异常类"""
        error = SCPICommandError("Invalid command", command="INVALID?")
        assert isinstance(error, SCPIError)
        assert error.code == 1001
        assert error.details == {"command": "INVALID?"}

    def test_scpi_response_error(self):
        """测试SCPIResponseError异常类"""
        error = SCPIResponseError("Invalid response", response="ERROR")
        assert isinstance(error, SCPIError)
        assert error.code == 1002
        assert error.details == {"response": "ERROR"}

    def test_connection_error(self):
        """测试ConnectionError异常类"""
        error = ConnectionError("Connection error")
        assert isinstance(error, SCPIAppError)
        assert error.code == 2000

    def test_connection_timeout_error(self):
        """测试ConnectionTimeoutError异常类"""
        error = ConnectionTimeoutError("Timeout", host="192.168.1.1", port=8805)
        assert isinstance(error, ConnectionError)
        assert error.code == 2001
        assert error.details == {"host": "192.168.1.1", "port": 8805}

    def test_connection_refused_error(self):
        """测试ConnectionRefusedError异常类"""
        error = ConnectionRefusedError("Refused", host="192.168.1.1", port=8805)
        assert isinstance(error, ConnectionError)
        assert error.code == 2002
        assert error.details == {"host": "192.168.1.1", "port": 8805}

    def test_connection_closed_error(self):
        """测试ConnectionClosedError异常类"""
        error = ConnectionClosedError()
        assert isinstance(error, ConnectionError)
        assert error.code == 2003
        assert "ConnectionClosedError: 连接已关闭" in str(error)

    def test_invalid_address_error(self):
        """测试InvalidAddressError异常类"""
        error = InvalidAddressError("Invalid address", address="invalid_ip")
        assert isinstance(error, ConnectionError)
        assert error.code == 2004
        assert error.details == {"address": "invalid_ip"}

    def test_config_error(self):
        """测试ConfigError异常类"""
        error = ConfigError("Config error")
        assert isinstance(error, SCPIAppError)
        assert error.code == 3000

    def test_config_not_found_error(self):
        """测试ConfigNotFoundError异常类"""
        error = ConfigNotFoundError("Config not found", file_path="config.ini")
        assert isinstance(error, ConfigError)
        assert error.code == 3001
        assert error.details == {"file_path": "config.ini"}

    def test_config_parse_error(self):
        """测试ConfigParseError异常类"""
        error = ConfigParseError("Parse error", file_path="config.ini")
        assert isinstance(error, ConfigError)
        assert error.code == 3002
        assert error.details == {"file_path": "config.ini"}

    def test_config_validation_error(self):
        """测试ConfigValidationError异常类"""
        error = ConfigValidationError(
            "Validation error", key="key", value="invalid_value"
        )
        assert isinstance(error, ConfigError)
        assert error.code == 3003
        assert error.details == {"key": "key", "value": "invalid_value"}

    def test_config_key_error(self):
        """测试ConfigKeyError异常类"""
        error = ConfigKeyError("Key not found", key="missing_key")
        assert isinstance(error, ConfigError)
        assert error.code == 3004
        assert error.details == {"key": "missing_key"}
