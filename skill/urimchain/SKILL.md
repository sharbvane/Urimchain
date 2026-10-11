---
name: urimchain
description: Identify and statically reverse engineer Windows native binaries, .NET assemblies, Android APK/DEX, ELF shared objects, and Unity native components with the installed Urimchain toolchain. Choose and combine Ghidra, REA, JADX, Apktool, and ILSpy by actual file headers, inspect functions and call relationships, and distinguish decompiler output from inferred pseudocode. Use when an agent needs local binary or application analysis without executing the target.
license: MIT
---

# Urimchain

Requires Windows x64, an installed Urimchain, Python 3.11+, a supported REA Node.js runtime, and engines reported ready by Doctor. MCP is optional; other Agent Skills clients can use the CLI.

## Locate the existing installation

Use `urimchain.cmd` on PATH, or the `bin/urimchain.cmd` under the user's chosen installation directory. Run the installed `scripts/doctor.ps1` to inspect readiness. If unavailable, follow the project README installation steps; do not assume a particular drive, user name, or existing global Java environment.

For Codex, the optional `urimchain` MCP server exposes REA tools. Discover the available tool names in the client; do not assume a live MCP process picked up a changed configuration. Reconnect after installation or configuration changes. The CLI remains usable independently of MCP.

## Identify before choosing an engine

Run `urimchain.cmd identify "TARGET"`. It reads headers and archive structure and hashes the input. Filename extensions alone are insufficient.

| Identified kind | Primary route | Complementary evidence |
| --- | --- | --- |
| `native-pe` | REA / Ghidra | disassembly, imports, strings, functions and references |
| `managed-pe` | ILSpy C# | REA managed metadata and IL structure |
| `apk` | JADX + Apktool | REA Android tools for targeted classes, methods and callers |
| `dex` | JADX | class and method references |
| `elf` | Ghidra headless | architecture, instructions, functions and strings |
| `unity-il2cpp` | identified native binary route | metadata is identification evidence; managed recovery unavailable |
| `unity-metadata` | no automatic analysis | report the limitation |
| `zip`, unknown, other directory | inspect identification result | choose an explicit supported member before analysis |

Windows REA native analysis is experimental and limited to supported x86/x64 PE inputs on local NTFS. ELF uses direct Ghidra headless. Check Doctor and the documented compatibility boundaries before treating a selected route as ready.

## Analyze in a new output directory

Run `urimchain.cmd analyze "TARGET" --output "NEW_OUTPUT_DIRECTORY"`. Keep output outside an input directory. The entry point writes identification, hashes, engine logs, and recovered text. It never executes the target. Existing output directories are refused.

For APKs containing `lib/*.so`, first inspect Java/Kotlin decompiler output and decoded Manifest/resources/Smali, then analyze relevant extracted native libraries separately. For Unity directories with multiple binaries, select the relevant binary explicitly. Do not claim metadata-based C# recovery.

Use targeted REA tools when broad CLI output does not answer the question: inspect native functions, disassembly, decompiler output, strings and cross references; inspect Android method bodies and callers; inspect managed assembly structure. Start with discovery or tool help if the client's names differ. Avoid runtime/debugger tools for the default static workflow.

## Cross-check and report

Trace entry points and meaningful callers to the relevant function. Verify apparent algorithms against instructions or IL/Smali, constants, strings and references. Use resources and the Manifest to validate Android code interpretation. Native export is bounded to the first 200 functions; use targeted inspection when more coverage is needed.

Label evidence precisely:

- **Decompiler output:** text actually returned by a named engine; optimization and obfuscation may make it incomplete or inaccurate.
- **Inferred pseudocode:** your interpretation, supported by addresses, instructions, IL or Smali.
- **Unavailable:** original names, comments, source layout or managed metadata that cannot be recovered by the installed engines.

Include input identity/hash, engines and versions, relevant addresses/classes/methods, output locations, conflicting evidence, and failures. Distinguish installed, callable, and successfully analyzed. Never execute APK/EXE/DLL targets, modify originals, or upload private samples without explicit authorization.
