# Urimchain

[![Checks](https://github.com/sharbvane/Urimchain/actions/workflows/ci.yml/badge.svg)](https://github.com/sharbvane/Urimchain/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**面向 AI Agent、可复现安装的 Windows 静态逆向工程工具链。**

[English](README.md) · [架构](docs/architecture.md) · [兼容边界](docs/limitations.md) · [第三方许可](THIRD_PARTY_NOTICES.md)

Urimchain 复用已经验证的 REA、Ghidra、JADX、Apktool 与 ILSpy，提供独立的 Agent Skill、自动类型识别及统一分析入口。大型工具通过官方渠道下载到用户指定目录，不随仓库分发。默认只做静态分析，原始样本与输出分离。

Java 和 C# 是反编译器重构结果，原生输出是伪代码；这些结果不等于原项目源码。Agent 应结合指令、调用关系、资源和元数据解释结论，并明确推断与无法恢复的信息。

## 分析能力

| 目标 | 自动路线 | 输出与边界 |
|---|---|---|
| 原生 EXE / DLL | REA + Ghidra | 函数、反汇编、伪代码、交叉引用及数据流查询；Windows REA/Ghidra 接入仍属实验性 |
| .NET EXE / DLL | ILSpy + REA | C# 重构、CLR 信息、元数据与 CIL |
| APK | JADX + Apktool；REA Android bridge | Java、调用关系、Manifest、资源与 Smali |
| DEX | JADX CLI | Java 重构及代码结构 |
| ELF / SO | Ghidra headless | 架构、指令与伪代码；Windows REA PE Provider 不用于 ELF |
| Unity IL2CPP 目录 | 识别并选择原生文件 | 仅原生分析，不提供 metadata 或 C# 程序集恢复 |

混合架构可以分阶段组合引擎并交叉核对。复杂混淆、加壳、拆分 APK 和 NativeAOT 有额外限制，详见[兼容边界](docs/limitations.md)。Cpp2IL 不再是依赖，也不会恢复安装。

## 安装

需要 Windows x64、PowerShell 7、Python 3.11+、npm、符合 REA 要求的 Node.js（`^22.19.0`、`^24.11.0` 或 `>=26.0.0`）、.NET SDK 8+ 与 .NET 8 runtime。安装器检查这些前置条件，不替换共享运行时；单独下载 JDK 21 给 Java 工具使用，不改变系统 Java。

```powershell
git clone https://github.com/sharbvane/Urimchain.git
Set-Location Urimchain
pwsh -File scripts/install.ps1 -InstallDir D:\Tools\Urimchain -Plan
pwsh -File scripts/install.ps1 -InstallDir D:\Tools\Urimchain
pwsh -File scripts/doctor.ps1 -InstallDir D:\Tools\Urimchain
```

工具主体、下载缓存及临时工作默认放在安装目录。选择非系统盘可减少 C 盘占用；Agent 配置和既有共享运行时仍可能占用少量 C 盘空间。安装版本、官方来源和可用校验信息固定在 [dependencies.json](dependencies.json)，下载失败会明确退出，不无限重试。既有工具和无关全局配置保留。

## CLI 与 Agent 使用

```powershell
& D:\Tools\Urimchain\bin\urimchain.cmd identify D:\Samples\app.apk
& D:\Tools\Urimchain\bin\urimchain.cmd analyze D:\Samples\app.apk --output D:\Analysis\app-new
pwsh -File scripts/configure.ps1 -InstallDir D:\Tools\Urimchain
```

输出目录应为新目录。识别依据文件签名和框架信息，而非仅凭扩展名；分析记录输入哈希，不运行 EXE/DLL/SO，不安装 APK。配置脚本单独备份并配置 Codex MCP 与互补 Skill，保留其他 MCP 和 Skill；配置后重连 Codex。

独立 Skill 位于 [`skill/urimchain`](skill/urimchain)，采用 [Agent Skills 开放规范](https://agentskills.io/specification)。其他兼容 Agent 可按自身文档安装该目录，并让 Agent 环境能访问安装目录的 `bin`。CLI 工作流不要求 MCP；不同 Agent 的 MCP 配置方式需按其官方说明设置。REA 官方 Skill 不被覆盖。

示例请求：

> 使用 Urimchain 静态分析 `D:\Samples\app.apk`，自动选择引擎，解释核心算法和调用关系，对照 Manifest、Smali 与 Java 输出；证据写入 `D:\Analysis\app-new`。不要运行样本，区分实际反编译内容、行为推断和未解决问题。

## 卸载

```powershell
pwsh -File scripts/uninstall.ps1 -InstallDir D:\Tools\Urimchain -Plan
pwsh -File scripts/uninstall.ps1 -InstallDir D:\Tools\Urimchain
```

删除限定为本项目所属安装文件和配置，不卸载共享运行时或无关工具。归属文件若已修改，卸载会停止以便检查；用户文件和备份保留。重要分析输出应保存在安装目录之外；先查看删除计划与归属检查。

## 验证与许可

测试采用从源码构建的无害样本，不提交私有目标或第三方二进制。单元测试覆盖类型识别和路由；Windows 安装、卸载和真实引擎分析需要原生环境。工作流文件存在不等于 CI 已运行，实际结果与未验证项见[验收记录](docs/verification.md)。

```powershell
python -m unittest discover -s tests -v
```

自有代码采用 [MIT](LICENSE)。上游工具各自保留许可和署名，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。IDA 不随项目安装或分发，使用需另有合法授权。
