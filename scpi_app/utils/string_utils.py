# 字符串处理工具函数

import re
from typing import List, Optional


def remove_whitespace(s: str) -> str:
    """
    移除字符串中的所有空白字符

    参数:
        s: 输入字符串

    返回:
        移除空白字符后的字符串
    """
    return "".join(s.split())


def normalize_whitespace(s: str) -> str:
    """
    规范化字符串中的空白字符，将连续的空白字符替换为单个空格

    参数:
        s: 输入字符串

    返回:
        规范化后的字符串
    """
    return " ".join(s.split())


def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串到指定长度

    参数:
        s: 输入字符串
        max_length: 最大长度
        suffix: 截断后缀

    返回:
        截断后的字符串
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def is_valid_ip(ip: str) -> bool:
    """
    验证IP地址格式是否有效

    参数:
        ip: IP地址字符串

    返回:
        IP地址格式是否有效
    """
    pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    if not re.match(pattern, ip):
        return False

    parts = ip.split(".")
    for part in parts:
        if not 0 <= int(part) <= 255:
            return False

    return True


def is_valid_port(port: str) -> bool:
    """
    验证端口号格式是否有效

    参数:
        port: 端口号字符串

    返回:
        端口号格式是否有效
    """
    if not port.isdigit():
        return False

    port_num = int(port)
    return 0 <= port_num <= 65535


def format_scpi_command(cmd: str) -> str:
    """
    格式化SCPI命令

    参数:
        cmd: SCPI命令字符串

    返回:
        格式化后的SCPI命令
    """
    # 移除前后空白字符
    cmd = cmd.strip()

    # 如果命令已经以换行符结尾，不需要添加
    if cmd.endswith("\n"):
        return cmd

    # 确保命令以换行符结尾
    return cmd + "\n"


def parse_scpi_response(response: str) -> str:
    """
    解析SCPI响应

    参数:
        response: SCPI响应字符串

    返回:
        解析后的响应
    """
    # 移除前后空白字符和换行符
    return response.strip()


def extract_numbers(s: str) -> List[float]:
    """
    从字符串中提取所有数字

    参数:
        s: 输入字符串

    返回:
        提取的数字列表
    """
    # 使用捕获组，但只提取完整的数字匹配
    pattern = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
    matches = re.findall(pattern, s)
    return [float(match) for match in matches]


def to_camel_case(s: str) -> str:
    """
    将下划线命名转换为驼峰命名

    参数:
        s: 下划线命名的字符串

    返回:
        驼峰命名的字符串
    """
    parts = s.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def to_snake_case(s: str) -> str:
    """
    将驼峰命名转换为下划线命名

    参数:
        s: 驼峰命名的字符串

    返回:
        下划线命名的字符串
    """
    # 处理首字母大写和连续大写的情况
    # 1. 在小写字母后接大写字母处添加下划线
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", s)
    # 2. 在连续大写字母序列中，除了最后一个大写字母外，在前面添加下划线
    s = re.sub(r"([A-Z])(?=[A-Z][a-z])", r"\1_", s)
    return s.lower()


def remove_prefix(s: str, prefix: str) -> str:
    """
    移除字符串前缀

    参数:
        s: 输入字符串
        prefix: 要移除的前缀

    返回:
        移除前缀后的字符串
    """
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def remove_suffix(s: str, suffix: str) -> str:
    """
    移除字符串后缀

    参数:
        s: 输入字符串
        suffix: 要移除的后缀

    返回:
        移除后缀后的字符串
    """
    # 直接使用Python 3.9+的内置方法，或者手动实现
    if suffix and s.endswith(suffix):
        return s[: len(s) - len(suffix)]
    return s


def center_string(s: str, width: int, fillchar: str = " ") -> str:
    """
    将字符串居中对齐

    参数:
        s: 输入字符串
        width: 总宽度
        fillchar: 填充字符

    返回:
        居中对齐后的字符串
    """
    return s.center(width, fillchar)


def ljust_string(s: str, width: int, fillchar: str = " ") -> str:
    """
    将字符串左对齐

    参数:
        s: 输入字符串
        width: 总宽度
        fillchar: 填充字符

    返回:
        左对齐后的字符串
    """
    return s.ljust(width, fillchar)


def rjust_string(s: str, width: int, fillchar: str = " ") -> str:
    """
    将字符串右对齐

    参数:
        s: 输入字符串
        width: 总宽度
        fillchar: 填充字符

    返回:
        右对齐后的字符串
    """
    return s.rjust(width, fillchar)


def is_empty(s: Optional[str]) -> bool:
    """
    检查字符串是否为空或None

    参数:
        s: 输入字符串

    返回:
        字符串是否为空或None
    """
    return s is None or s.strip() == ""


def split_lines(s: str) -> List[str]:
    """
    按行分割字符串

    参数:
        s: 输入字符串

    返回:
        行列表
    """
    return s.splitlines()


def join_lines(lines: List[str]) -> str:
    """
    将行列表连接为字符串

    参数:
        lines: 行列表

    返回:
        连接后的字符串
    """
    return "\n".join(lines)
