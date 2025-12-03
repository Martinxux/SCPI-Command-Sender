# 测试utils模块

import os
import tempfile
import configparser
from scpi_app.utils.file_utils import (
    read_file,
    write_file,
    append_file,
    read_json,
    write_json,
    read_ini,
    write_ini,
    get_file_extension,
    get_file_name,
    get_file_name_without_extension,
    ensure_dir_exists,
    list_files,
    get_relative_path,
    get_absolute_path,
)
from scpi_app.utils.string_utils import (
    remove_whitespace,
    normalize_whitespace,
    truncate_string,
    is_valid_ip,
    is_valid_port,
    format_scpi_command,
    parse_scpi_response,
    extract_numbers,
    to_camel_case,
    to_snake_case,
    remove_prefix,
    remove_suffix,
    center_string,
    ljust_string,
    rjust_string,
    is_empty,
    split_lines,
    join_lines,
)


class TestFileUtils:
    """测试文件处理工具函数"""

    def setup_method(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        # 创建临时文件
        self.temp_file = os.path.join(self.temp_dir, "test.txt")
        write_file(self.temp_file, "Hello, World!")

    def teardown_method(self):
        """测试后的清理工作"""
        # 删除临时目录中的所有文件和子目录
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    def test_read_file(self):
        """测试读取文件内容"""
        content = read_file(self.temp_file)
        assert content == "Hello, World!"

    def test_write_file(self):
        """测试写入文件内容"""
        write_file(self.temp_file, "Test content")
        content = read_file(self.temp_file)
        assert content == "Test content"

    def test_append_file(self):
        """测试追加内容到文件"""
        append_file(self.temp_file, "\nAppended content")
        content = read_file(self.temp_file)
        assert content == "Hello, World!\nAppended content"

    def test_read_write_json(self):
        """测试读写JSON文件"""
        json_file = os.path.join(self.temp_dir, "test.json")
        data = {"name": "Test", "value": 123}
        write_json(json_file, data)
        read_data = read_json(json_file)
        assert read_data == data

    def test_read_write_ini(self):
        """测试读写INI文件"""
        ini_file = os.path.join(self.temp_dir, "test.ini")
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"ServerAliveInterval": "45", "Compression": "yes"}
        write_ini(ini_file, config)
        read_config = read_ini(ini_file)
        assert read_config["DEFAULT"]["ServerAliveInterval"] == "45"

    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        assert get_file_extension("test.txt") == "txt"
        assert get_file_extension("document.pdf") == "pdf"
        assert get_file_extension("image.png") == "png"

    def test_get_file_name(self):
        """测试获取文件名"""
        assert get_file_name("/path/to/file.txt") == "file.txt"
        assert get_file_name("file.txt") == "file.txt"

    def test_get_file_name_without_extension(self):
        """测试获取不带扩展名的文件名"""
        assert get_file_name_without_extension("file.txt") == "file"
        assert get_file_name_without_extension("/path/to/document.pdf") == "document"

    def test_ensure_dir_exists(self):
        """测试确保目录存在"""
        new_dir = os.path.join(self.temp_dir, "new_dir")
        ensure_dir_exists(new_dir)
        assert os.path.exists(new_dir)

    def test_list_files(self):
        """测试列出目录中的文件"""
        # 创建多个临时文件
        file1 = os.path.join(self.temp_dir, "file1.txt")
        file2 = os.path.join(self.temp_dir, "file2.txt")
        file3 = os.path.join(self.temp_dir, "file3.json")
        write_file(file1, "test1")
        write_file(file2, "test2")
        write_file(file3, "{}")

        # 列出所有文件
        files = list_files(self.temp_dir)
        assert len(files) == 4  # 包括之前创建的test.txt和新创建的3个文件

        # 按扩展名过滤
        txt_files = list_files(self.temp_dir, "txt")
        assert len(txt_files) == 3

        # 清理
        for f in [file1, file2, file3]:
            os.remove(f)

    def test_get_relative_path(self):
        """测试获取相对路径"""
        base_path = "/path/to"
        target_path = "/path/to/file.txt"
        assert get_relative_path(base_path, target_path) == "file.txt"

    def test_get_absolute_path(self):
        """测试获取绝对路径"""
        relative_path = "file.txt"
        absolute_path = get_absolute_path(relative_path)
        assert os.path.isabs(absolute_path)


class TestStringUtils:
    """测试字符串处理工具函数"""

    def test_remove_whitespace(self):
        """测试移除空白字符"""
        assert remove_whitespace("  Hello  World  ") == "HelloWorld"
        assert remove_whitespace("Hello\nWorld\t") == "HelloWorld"

    def test_normalize_whitespace(self):
        """测试规范化空白字符"""
        assert normalize_whitespace("  Hello  \n  World  ") == "Hello World"
        assert normalize_whitespace("Hello\t\tWorld") == "Hello World"

    def test_truncate_string(self):
        """测试截断字符串"""
        assert truncate_string("Hello World", 5) == "He..."
        assert truncate_string("Short", 10) == "Short"
        assert truncate_string("Hello World", 5, "...") == "He..."

    def test_is_valid_ip(self):
        """测试IP地址验证"""
        assert is_valid_ip("192.168.1.1")
        assert is_valid_ip("10.0.0.1")
        assert is_valid_ip("255.255.255.255")
        assert not is_valid_ip("256.0.0.1")
        assert not is_valid_ip("192.168.1")
        assert not is_valid_ip("invalid_ip")

    def test_is_valid_port(self):
        """测试端口号验证"""
        assert is_valid_port("80")
        assert is_valid_port("443")
        assert is_valid_port("65535")
        assert is_valid_port("0")
        assert not is_valid_port("65536")
        assert not is_valid_port("invalid_port")

    def test_format_scpi_command(self):
        """测试格式化SCPI命令"""
        assert format_scpi_command("*IDN?") == "*IDN?\n"
        assert format_scpi_command("*IDN?\n") == "*IDN?\n"
        assert format_scpi_command("SYST:ERR?") == "SYST:ERR?\n"

    def test_parse_scpi_response(self):
        """测试解析SCPI响应"""
        assert parse_scpi_response("Hello\n") == "Hello"
        assert parse_scpi_response("  123.45  ") == "123.45"

    def test_extract_numbers(self):
        """测试从字符串中提取数字"""
        assert extract_numbers("There are 123 apples and 456 oranges") == [123.0, 456.0]
        assert extract_numbers("The temperature is -23.45°C") == [-23.45]
        assert extract_numbers("No numbers here") == []

    def test_to_camel_case(self):
        """测试转换为驼峰命名"""
        assert to_camel_case("hello_world") == "helloWorld"
        assert to_camel_case("scpi_command") == "scpiCommand"

    def test_to_snake_case(self):
        """测试转换为下划线命名"""
        assert to_snake_case("helloWorld") == "hello_world"
        assert to_snake_case("SCPICommand") == "scpi_command"

    def test_remove_prefix(self):
        """测试移除前缀"""
        assert remove_prefix("prefix_test", "prefix_") == "test"
        assert remove_prefix("no_prefix", "prefix_") == "no_prefix"

    def test_remove_suffix(self):
        """测试移除后缀"""
        assert remove_suffix("test_suffix", "_suffix") == "test"
        assert remove_suffix("no_suffix", "_suffix") == "no"
        assert remove_suffix("no_suffix", "_nonexistent") == "no_suffix"

    def test_center_string(self):
        """测试字符串居中对齐"""
        assert center_string("test", 10) == "   test   "
        assert center_string("test", 10, "=") == "===test==="

    def test_ljust_string(self):
        """测试字符串左对齐"""
        assert ljust_string("test", 10) == "test      "
        assert ljust_string("test", 10, "=") == "test======"

    def test_rjust_string(self):
        """测试字符串右对齐"""
        assert rjust_string("test", 10) == "      test"
        assert rjust_string("test", 10, "=") == "======test"

    def test_is_empty(self):
        """测试字符串是否为空"""
        assert is_empty(None)
        assert is_empty("")
        assert is_empty("   ")
        assert not is_empty("test")

    def test_split_lines(self):
        """测试按行分割字符串"""
        assert split_lines("Line 1\nLine 2\nLine 3") == ["Line 1", "Line 2", "Line 3"]
        assert split_lines("Single line") == ["Single line"]

    def test_join_lines(self):
        """测试将行列表连接为字符串"""
        assert join_lines(["Line 1", "Line 2", "Line 3"]) == "Line 1\nLine 2\nLine 3"
        assert join_lines(["Single line"]) == "Single line"
