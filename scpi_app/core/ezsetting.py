import configparser
import os
import time
from typing import Dict, List
from scpi_app.core.scpi import SCPIInstrument


class DCAConfigurator:
    def __init__(self):
        self.configurations: Dict[str, List[str]] = {}

    def load_configurations(self, config_path: str = 'dcasetting.ini') -> Dict[str, List[str]]:
        """
        从配置文件加载预定义的配置
        
        参数:
            config_path: 配置文件路径
        
        返回:
            配置字典，格式为 {配置名称: [命令列表]}
        """
        config = configparser.ConfigParser()
        config.optionxform = str  # 保持键的大小写不变

        # 检查配置文件是否存在
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"找不到配置文件: {config_path}")

        try:
            config.read(config_path, encoding='utf-8')
            configurations = {}

            # 遍历所有section
            for section in config.sections():
                # 只处理包含commands键的配置
                if config.has_option(section, 'commands'):
                    # 获取命令字符串
                    cmd_str = config[section]['commands']
                    # 分割命令为列表
                    commands = cmd_str.split('\n')
                    # 过滤空行和注释行
                    commands = [cmd.strip() for cmd in commands if cmd.strip() and not cmd.strip().startswith(';')]
                    configurations[section] = commands
                else:
                    # 对于没有commands键的配置，记录警告
                    print(f"警告: 配置 '{section}' 缺少 'commands' 键，将被忽略")

            self.configurations = configurations
            return configurations

        except Exception as e:
            raise Exception(f"读取配置文件失败: {str(e)}")

    def apply_configuration(self, instrument: SCPIInstrument, config_name: str) -> None:
        """
        应用选定的配置
        
        参数:
            instrument: SCPIInstrument 实例
            config_name: 配置名称
        """
        if not instrument.is_connected():
            raise Exception("请先连接仪器")

        if not config_name:
            raise Exception("请先选择一个配置")

        if config_name not in self.configurations:
            raise Exception(f"配置 '{config_name}' 不存在")

        commands = self.configurations[config_name]
        if not commands:
            raise Exception(f"配置 '{config_name}' 没有命令")

        try:
            for cmd in commands:
                instrument.send_command(cmd)
                time.sleep(0.1)  # 避免发送过快

        except Exception as e:
            raise Exception(f"应用配置时出错: {str(e)}")