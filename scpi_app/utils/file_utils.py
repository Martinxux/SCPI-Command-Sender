# 文件处理工具函数

import os
import json
import configparser
from typing import List, Any, Optional


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    读取文件内容

    参数:
        file_path: 文件路径
        encoding: 文件编码

    返回:
        文件内容字符串

    异常:
        FileNotFoundError: 文件不存在
        IOError: 读取文件时发生错误
    """
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """
    写入文件内容

    参数:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 文件编码

    异常:
        IOError: 写入文件时发生错误
    """
    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)


def append_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """
    追加内容到文件

    参数:
        file_path: 文件路径
        content: 要追加的内容
        encoding: 文件编码

    异常:
        IOError: 写入文件时发生错误
    """
    with open(file_path, "a", encoding=encoding) as f:
        f.write(content)


def read_json(file_path: str, encoding: str = "utf-8") -> Any:
    """
    读取JSON文件

    参数:
        file_path: 文件路径
        encoding: 文件编码

    返回:
        JSON解析后的数据

    异常:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON格式错误
        IOError: 读取文件时发生错误
    """
    with open(file_path, "r", encoding=encoding) as f:
        return json.load(f)


def write_json(
    file_path: str, data: Any, indent: int = 4, encoding: str = "utf-8"
) -> None:
    """
    写入JSON文件

    参数:
        file_path: 文件路径
        data: 要写入的数据
        indent: 缩进空格数
        encoding: 文件编码

    异常:
        IOError: 写入文件时发生错误
        TypeError: 数据类型不支持JSON序列化
    """
    with open(file_path, "w", encoding=encoding) as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_ini(file_path: str) -> configparser.ConfigParser:
    """
    读取INI文件

    参数:
        file_path: 文件路径

    返回:
        ConfigParser对象

    异常:
        FileNotFoundError: 文件不存在
        configparser.Error: INI格式错误
        IOError: 读取文件时发生错误
    """
    config = configparser.ConfigParser()
    config.read(file_path, encoding="utf-8")
    return config


def write_ini(file_path: str, config: configparser.ConfigParser) -> None:
    """
    写入INI文件

    参数:
        file_path: 文件路径
        config: ConfigParser对象

    异常:
        IOError: 写入文件时发生错误
    """
    with open(file_path, "w", encoding="utf-8") as f:
        config.write(f)


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名

    参数:
        file_path: 文件路径

    返回:
        文件扩展名（不包含点号）
    """
    return os.path.splitext(file_path)[1][1:].lower()


def get_file_name(file_path: str) -> str:
    """
    获取文件名（不包含路径）

    参数:
        file_path: 文件路径

    返回:
        文件名
    """
    return os.path.basename(file_path)


def get_file_name_without_extension(file_path: str) -> str:
    """
    获取文件名（不包含路径和扩展名）

    参数:
        file_path: 文件路径

    返回:
        不带扩展名的文件名
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def ensure_dir_exists(dir_path: str) -> None:
    """
    确保目录存在，如果不存在则创建

    参数:
        dir_path: 目录路径

    异常:
        OSError: 创建目录时发生错误
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def list_files(dir_path: str, extension: Optional[str] = None) -> List[str]:
    """
    列出目录中的文件

    参数:
        dir_path: 目录路径
        extension: 可选，文件扩展名过滤

    返回:
        文件路径列表

    异常:
        FileNotFoundError: 目录不存在
    """
    files = []
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)

        if os.path.isfile(file_path):
            if not extension or get_file_extension(file_path) == extension:
                files.append(file_path)
    return files


def get_relative_path(base_path: str, target_path: str) -> str:
    """
    获取相对路径

    参数:
        base_path: 基准路径
        target_path: 目标路径

    返回:
        相对路径字符串
    """
    return os.path.relpath(target_path, base_path)


def get_absolute_path(relative_path: str) -> str:
    """
    获取绝对路径

    参数:
        relative_path: 相对路径

    返回:
        绝对路径字符串
    """
    return os.path.abspath(relative_path)
