# Urimchain

**A reproducible Windows static reverse-engineering toolchain for AI agents.**

[![Checks](https://github.com/sharbvane/Urimchain/actions/workflows/ci.yml/badge.svg)](https://github.com/sharbvane/Urimchain/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[简体中文](README.zh-CN.md) · [Architecture](docs/architecture.md) · [Limitations](docs/limitations.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

Urimchain packages a tested combination of REA, Ghidra, JADX, Apktool and ILSpy behind a small file-type router and an independent [Agent Skill](https://agentskills.io/specification). It installs official upstream releases into a directory you choose, keeps analysis outputs separate from inputs, and gives an agent a consistent way to select and combine existing engines.

It does not recover the original source tree. Java and C# are reconstructed decompiler output; native output is pseudocode. Findings require evidence and cross-checking.

## What it analyzes

| Input | Selected engines | Useful outputs |
|---|---|---|
| Native EXE / DLL | REA + Ghidra | Functions, disassembly, pseudocode, references and REA data-flow queries |
| .NET EXE / DLL | ILSpy + REA | Reconstructed C#, CLR identity, metadata and CIL |
| APK | JADX + Apktool; REA Android bridge | Reconstructed Java, callers, Manifest, resources and Smali |
| DEX | JADX CLI | Java reconstruction and code structure |
| ELF / SO | Ghidra headless | Architecture, disassembly and pseudocode |
| Unity IL2CPP directory | Recognize container; analyze a selected native binary | Native analysis only; no metadata or C# assembly reconstruction |

Windows REA/Ghidra integration is **experimental**, with a narrower PE/local-NTFS scope than Ghidra itself. ELF uses the direct headless route. Mixed frameworks may require staged analysis. See [limitations](docs/limitations.md) before interpreting an output.

## Install

Use Windows x64 with PowerShell 7, Python 3.11+, a supported REA Node.js runtime (`^22.19.0`, `^24.11.0`, or `>=26.0.0`), npm, .NET SDK 8+ and .NET 8 runtime. The installer checks prerequisites; it does not replace system Java or install these shared runtimes. A private JDK 21 is downloaded for the Java engines.

```powershell
git clone https://github.com/sharbvane/Urimchain.git
Set-Location Urimchain
pwsh -File scripts/install.ps1 -InstallDir D:\Tools\Urimchain -Plan
pwsh -File scripts/install.ps1 -InstallDir D:\Tools\Urimchain
pwsh -File scripts/doctor.ps1 -InstallDir D:\Tools\Urimchain
```

The default installation keeps large tools, downloads and temporary work under the selected directory. Choose a non-system drive to reduce C: usage. Shared runtime and agent configuration locations may still consume small amounts of space. Downloads use pinned official URLs and available upstream integrity data in [dependencies.json](dependencies.json). Failures stop with a diagnosis rather than retry forever. Existing installations and unrelated global configuration are preserved.

## Analyze

```powershell
& D:\Tools\Urimchain\bin\urimchain.cmd identify D:\Samples\app.apk
& D:\Tools\Urimchain\bin\urimchain.cmd analyze D:\Samples\app.apk --output D:\Analysis\app-new
```

Use a new output directory. The router checks file signatures, detects CLR PE files, selects engines and records results and input hashes. It does not execute target binaries or install APKs. A successful subprocess alone is not proof that a decompiler recovered useful code: inspect the evidence and warnings.

## Use with an agent

The standalone Skill lives in [`skill/urimchain`](skill/urimchain). It contains standard `SKILL.md` frontmatter and portable instructions, without depending on a particular account or hard-coded installation directory. Agents discover tools, classify inputs, choose the route, combine code/resource/native evidence and distinguish recovered output from inference.

For Codex, configure the project-managed Skill and REA MCP entry separately:

```powershell
pwsh -File scripts/configure.ps1 -InstallDir D:\Tools\Urimchain
```

Configuration is backed up before changes. The configurator preserves other MCP entries and Skills. Reconnect Codex to load the MCP environment. For other Agent Skills-compatible agents, install the `skill/urimchain` directory in that agent's documented Skill location and expose the installation's `bin` directory through its environment. MCP registration is host-specific; the CLI route works without MCP.

Example request:

> Statically analyze `D:\Samples\app.apk` with Urimchain. Explain the key algorithm and its callers, check the Manifest and Smali against the Java output, and write evidence to `D:\Analysis\app-new`. Do not execute the sample. Separate decompiler output, inferred behavior and unresolved questions.

## Remove

```powershell
pwsh -File scripts/uninstall.ps1 -InstallDir D:\Tools\Urimchain -Plan
pwsh -File scripts/uninstall.ps1 -InstallDir D:\Tools\Urimchain
```

Uninstallation is scoped to Urimchain-owned installation files and configuration. It does not remove shared runtimes or unrelated tools. Modified owned files stop removal for review; user files and backups are retained. Keep any analysis outputs you need outside the install directory. Review the script's plan and ownership checks before removal.

## Verification

Tests use source-built harmless fixtures; this repository does not ship private targets or upstream tool binaries. Unit tests cover identification and routing. Windows checks cover installer/configuration behavior; native integration checks require actual installed engines. GitHub Actions definitions are not themselves evidence of a completed run. The release's [verification report](docs/verification.md) records the checks actually run and their gaps.

```powershell
python -m unittest discover -s tests -v
```

## License and upstream ownership

Urimchain's own code is [MIT](LICENSE). The engines remain separate upstream projects under their respective licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). REA's official Skill is not overwritten. Cpp2IL is not a dependency; no replacement Unity metadata engine is installed. IDA requires a separate lawful installation and is not bundled.
