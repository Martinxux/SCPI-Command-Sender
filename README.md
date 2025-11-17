# SCPI Command Sender

## 项目概述
SCPI Command Sender 是一个基于 Pyside6 的图形界面工具，用于通过 TCP/IP 连接发送 SCPI 命令到测试仪器。它支持以下功能：
- 单条命令发送
- 命令序列发送
- 预定义配置管理
- 实时响应显示
- 自动化测试
  
## 使用说明
1. **连接仪器**：
   - 输入仪器的 IP 地址和端口号（默认端口：8805）。
   - 点击“连接”按钮建立连接。
2. **发送命令**：
   - 在输入框中输入 SCPI 命令（如 `*IDN?`）。
   - 点击“发送”按钮执行命令。
3. **发送预设命令序列**：
   - 在 `preset.json` 中定义命令序列。
   - 点击“发送预设命令序列”按钮循环执行命令序列。
3. **配置管理**：
   - 通过修改 `config` 文件夹中的配置文件（`.ini` 或 `.json` 文件）可以管理预设命令序列和 DCA 设置配置。

## 配置文件格式
### JSON 配置文件
JSON 文件用于存储命令序列和配置信息。格式要求如下：
- 必须是一个有效的 JSON 文件。
- 支持嵌套结构和自定义字段。

**示例**：
```json
{
    "presets": {
        "Clear and Run": {
            "description": "清除并运行采集 -- clean and run",
            "commands": [
                "*CLS",
                ":ACQuire:CDISplay",
                ":ACQ:RUN",
                "*OPC?"
            ],
            "repeat": 1,
            "interval": 1.0
        },
        "Measurement Setup": {
            "description": "测量设置 -- measurement setup",
            "commands": [
                ":MEASure:SOURce CH1",
                ":MEASure:VPP?",
                ":MEASure:VRMS?",
                ":MEASure:FREQuency?"
            ],
            "repeat": 3,
            "interval": 0.8
        }
    }
}
```

### INI 配置文件
INI 文件用于存储 DCA 设置。格式要求如下：
- 每个配置块以 `[basic_commands1]` 开头。
- `commands` 键是必须的，用于定义命令列表。
- 命令之间用换行符分隔。

**示例**：
```ini
[basic_commands1]
commands = 
  *IDN?
  SYST:ERR?
  MEAS:VOLT?

[basic_commands2]
commands = 
  *IDN?
  SYST:ERR?
  MEAS:VOLT?
```
## TODO: 
- 支持USB-TCP 连接
- ~~连接模块放到导航栏中，GUI重新设计~~
- 支持SCPI命令历史记录
- 支持SCPI命令自动补全
- 支持命令序列自动化测试
## 许可证
MIT License