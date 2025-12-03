# SCPI Command Sender

一个专业的SCPI命令发送工具，用于测试和控制仪器设备。

## 项目简介

SCPI Command Sender是一个基于Python和PySide6开发的GUI应用程序，用于发送SCPI命令到仪器设备并接收响应。它提供了友好的用户界面，支持命令预设、批量发送、日志记录等功能，适用于各种需要SCPI通信的测试场景。

## 功能特性

- ✅ 可视化SCPI命令发送和响应接收
- ✅ 支持命令预设和批量发送
- ✅ 实时日志记录
- ✅ 连接状态监控
- ✅ 响应超时设置
- ✅ 命令历史记录
- ✅ 支持多种仪器设备
- ✅ 跨平台支持（Windows、Linux、macOS）
- ✅ 可扩展的架构设计

## 技术栈

- **编程语言**: Python 3.13
- **GUI框架**: PySide6
- **网络通信**: Socket
- **日志系统**: logging
- **打包工具**: PyInstaller
- **测试框架**: pytest

## 安装说明

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/scpi-command-sender.git
cd scpi-command-sender
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行应用

```bash
python main.py
```

## 使用方法

### 1. 连接设备

1. 点击"连接"按钮
2. 在弹出的对话框中输入设备的IP地址和端口
3. 点击"连接"按钮建立连接

### 2. 发送命令

1. 在命令输入框中输入SCPI命令
2. 点击"发送"按钮发送命令
3. 在响应区域查看设备返回的响应

### 3. 使用预设命令

1. 点击"预设"下拉菜单选择预设命令
2. 预设命令会自动填充到命令输入框
3. 点击"发送"按钮发送命令

### 4. 批量发送命令

1. 点击"批量发送"按钮
2. 在弹出的对话框中输入多个命令，每行一个
3. 设置命令间隔和重复次数
4. 点击"开始"按钮开始批量发送

### 5. 查看日志

日志文件会保存在`logs`目录下，按日期命名，包含所有操作记录和设备响应。

## 项目结构

```
SCPI_Test/
├── scpi_app/                  # 主应用包
│   ├── __init__.py           # 包初始化文件
│   ├── core/                 # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── ezsetting.py      # DCA配置工具
│   │   └── scpi.py           # SCPI客户端实现
│   ├── gui/                  # GUI相关代码
│   │   ├── __init__.py
│   │   ├── scpi_gui.py       # 主窗口
│   │   ├── components/       # UI组件
│   │   │   ├── __init__.py
│   │   │   └── components.py # 通用组件
│   │   ├── dialogs/          # 对话框
│   │   │   ├── __init__.py
│   │   │   └── connection_dialog.py # 连接对话框
│   │   └── styles/           # 样式定义
│   │       ├── __init__.py
│   │       └── styles.py     # 主样式
│   ├── logger/               # 日志模块
│   │   ├── __init__.py
│   │   └── logger.py         # 日志配置和管理
│   └── utils/                # 工具函数
│       └── __init__.py
├── config/                   # 配置文件目录
│   ├── dcasetting.ini
│   └── presets.json
├── docs/                     # 文档目录
├── ico/                      # 图标资源
│   └── logo.ico
├── logs/                     # 日志文件目录
├── output/                   # 输出目录
├── tests/                    # 测试目录
├── main.py                   # 应用入口
├── PROJECT_STRUCTURE.md      # 项目结构文档
├── requirements.txt          # 依赖声明
└── README.md                 # 项目说明文档
```

## 开发指南

### 代码风格

- 遵循PEP 8代码风格指南
- 使用类型注解
- 添加详细的文档字符串
- 保持代码简洁、清晰

### 提交规范

- 使用语义化提交信息
- 每次提交只包含一个功能或修复
- 添加详细的提交说明

### 分支管理

- `main`: 主分支，用于发布稳定版本
- `develop`: 开发分支，用于集成新功能
- `feature/*`: 特性分支，用于开发新功能
- `bugfix/*`: 修复分支，用于修复bug

## 测试指南

### 运行单元测试

```bash
python -m pytest tests/ -v
```

### 运行集成测试

```bash
python -m pytest tests/integration/ -v
```

### 查看测试覆盖率

```bash
python -m pytest tests/ --cov=scpi_app --cov-report=html
```

## 打包指南

### 生成可执行文件

```bash
pyinstaller --onefile --windowed --icon=ico/logo.ico --name="SCPI Command Sender" main.py
```

### 打包配置

- 单文件模式: `--onefile`
- 窗口模式: `--windowed`
- 图标设置: `--icon=ico/logo.ico`
- 应用名称: `--name="SCPI Command Sender"`

## 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 版本历史

### v1.0.0 (2025-12-03)

- 初始版本发布
- 支持基本的SCPI命令发送和接收
- 支持命令预设和批量发送
- 支持日志记录

## 联系方式

- 作者: Your Name
- 邮箱: your.email@example.com
- GitHub: [yourusername](https://github.com/yourusername)

## 致谢

感谢所有为这个项目做出贡献的人！

## 开源协议

[MIT](LICENSE)
