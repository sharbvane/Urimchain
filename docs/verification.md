# v0.1.0 verification

Local acceptance used Windows x64 on 2026-10-11/12, Node.js 24.18.0, Python 3.11, and .NET SDK 8.0.422/runtime 8.0.28. The project was prepared and installed in independent directories. Existing global REA configuration, official Skill, complementary Skill, manifest and router hashes remained unchanged.

## Engines actually exercised

| Engine | Version | Actual result |
| --- | --- | --- |
| REA | 6.4.0 | Fresh stdio MCP connection listed 170 tools; native, managed and Android queries passed |
| Temurin JDK | 21.0.12.1+1, x64 | Java invocation passed; isolated runtime selected |
| Ghidra | 12.1.4 | Native PE through REA and ARM64 ELF through direct headless analysis passed |
| JADX | 1.5.6 | APK and DEX reconstructed the arithmetic method and caller |
| Apktool | 3.0.3 | APK decoded Manifest, resources and Smali; marker resource found |
| ILSpy CLI | 9.1.0.7988 | .NET library reconstructed `KnownAlgorithm.Transform` |
| Android MCP bridge | 0.7.1 | Method source, callers and resource queries passed |

Fixtures were rebuilt from the small sources in `tests/fixtures/`: MSVC produced a PE with no C runtime, .NET produced a class library, Android build tools produced an unsigned APK/DEX, and Android NDK Clang produced an ARM64 shared object. No target program, assembly or APK was executed. All five automatic analysis routes produced the expected outputs and retained the original input SHA-256.

REA native MCP queries identified `score` at `0x140001000`, returned 14 instructions, identified its caller `entry`, and reported nine native value-flow operations. Ghidra decompiler output contained the expected branches (`x + 11` and `x * 7 + 3`); cross-reference queries succeeded. This is engine output for the fixture, not a promise of original-source recovery.

Android queries recovered `transform`, found `caller`, and decoded resource evidence. Managed analysis combined actual ILSpy C# output with REA assembly inspection. ELF export contained `score`, instructions and matching arithmetic pseudocode. Identification correctly refused a Unity metadata recovery route.

## Installation and protection

The direct archives were SHA-256 checked against pinned official release information. REA's npm package integrity was checked against the lockfile. The ILSpy package was freshly downloaded from official NuGet, its SHA-256 matched the pin, and `dotnet nuget verify` accepted its NuGet.org repository signature.

The first isolated installation exposed and fixed a PowerShell package-lock parsing issue and required bounded recovery from slow registry access. The final public installer then ran from a second empty directory without manual intervention, using checked caches for the large official archives and official npm/NuGet sources for packages. It exited successfully and its automatic scoped Doctor reported healthy. All five routes and the fresh MCP tests passed again using that installation.

Configuration was actually appended to a temporary Codex home containing an unrelated MCP entry. Python `tomllib` validated the result, and the installed Skill was present. The active user's Codex configuration was not changed. The installed CLI identified fixtures from two different working directories.

All 22 unit/lifecycle tests passed. They exercise Plan without mutation, refusal of existing bare or quoted MCP keys, changed-owned-file retention, ownership-path escape refusal, and removal that preserves an unrelated file and later configuration comments. The complete first installation was actually uninstalled: owned launchers disappeared, an added user file and the unrelated MCP entry remained, and the project Skill was removed. Skill validation followed the actual CLI decisions on harmless binaries; see [Skill validation](skill-validation.md).

## Coverage boundaries

The ordinary GitHub workflow runs parser, Skill, source-boundary and isolated lifecycle checks. The separate manual Windows workflow covers installation, Doctor and a self-built managed route. Local Ghidra and Android results above are separate from CI coverage. A workflow definition does not count as a passed run.

REA's scoped Ghidra Doctor passed. Its wider audit can report unavailable optional engines or other client registrations; those do not establish failure of the exercised routes. This release does not test arbitrary obfuscated/protected targets, a clean physical Windows machine without prerequisites, runtime debugging, or Unity metadata reconstruction. Small upstream user-profile caches may remain outside the selected installation directory.
