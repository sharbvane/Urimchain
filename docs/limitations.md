# Compatibility and limits

| Capability | Status | Boundary |
|---|---|---|
| Windows x64 CLI installation | Supported target | Requires user-provided Node, Python and .NET prerequisites and official download access |
| APK / DEX via JADX | Supported static route | Decompiler errors, obfuscation and missing dependencies can produce incomplete Java |
| APK via Apktool | Supported static route | Framework/vendor resources, split APKs and unusual packaging may need manual handling |
| CLR PE via ILSpy | Supported static route | NativeAOT and mixed native/CLR files need additional native analysis |
| Native PE via REA/Ghidra | Experimental upstream Windows support | Local NTFS, upstream P0 scope; not equivalent to every Ghidra feature/platform |
| ELF / SO via direct Ghidra headless | Supported static route | ARM64 was validated locally; other architectures remain dependent on Ghidra and require their own checks |
| Unity IL2CPP recognition | Detection and native route | One native candidate can be selected automatically; ambiguous directories need an explicit target |
| Unity metadata / managed assembly recovery | Unavailable | No Cpp2IL dependency or replacement tool |
| IDA integration | Not installed by Urimchain | Any use requires a separate lawful installation and upstream support |
| Dynamic analysis / execution | Outside default workflow | Unknown binaries and APKs are not run |
| Non-Windows installation | Not supported in v0.1.0 | The Skill format is portable; installer and launchers target Windows |

Native export is bounded by the router's function limit (currently 200). A small export can omit relevant functions; use targeted REA/Ghidra queries for deeper work. Packed, encrypted or strongly protected code may be unreadable without additional evidence. Static analysis cannot prove runtime behavior, server-side logic or dynamically loaded content.

Reproducibility means pinned downloads and repeatable orchestration, not guaranteed identical decompilation across all targets. npm/NuGet resolve transitive components according to their package metadata; review generated lock/package metadata when updating dependencies. Upstream download outages produce an explicit failure. Do not disable digest checks or replace official downloads with arbitrary proxies.

A Skill-compatible agent can follow the same CLI workflow. This does not imply every host supports the same MCP transport or installation path. Restart/reconnect a host after MCP environment changes. Configuration backups can contain local data and must remain outside public source archives.

CI unit checks, source fixture builds, an installed tool's version response, and a real decompilation are separate levels of evidence. See the release verification report for actual results. New hardware, fresh user profiles, protected samples and frameworks not listed in that report require independent verification.
