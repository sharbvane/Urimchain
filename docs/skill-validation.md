# Skill decision validation

On 2026-10-11, the `skill/urimchain/SKILL.md` workflow was read and followed using the repository CLI in a separate workspace. Existing harmless, self-built acceptance fixtures were identified by file contents. No target executable or APK was run. The SHA-256 of each input was compared before and after identification and remained unchanged. Identification produced JSON on stdout and did not request an analysis output directory.

| Fixture | Identified kind | Selected routes | Result |
| --- | --- | --- | --- |
| Self-built x64 PE | `native-pe` | `ghidra-native` | Pass |
| Self-built .NET library | `managed-pe` | `ilspy`, `rea-managed` | Pass |
| Self-built Android APK | `apk` | `jadx`, `apktool`, `rea-android` | Pass |
| Self-built DEX | `dex` | `jadx` | Pass |
| Self-built ARM64 shared object | `elf` | `ghidra-direct-headless` | Pass |
| Generated Unity metadata magic header | `unity-metadata` | none; metadata recovery unavailable | Pass |

The agent's decisions matched the Skill routing table. APK analysis combines code and resource evidence; managed analysis combines C# and managed metadata; ARM64 ELF selects direct Ghidra rather than the Windows REA native provider. Unity metadata alone has no supported recovery route. These results validate the identification and decision step, not engine execution, full source restoration, or arbitrary future targets.

The committed test suite separately checks a Unity directory's native route, malformed headers, extension spoofing, and refusing an output directory inside the target directory. It validates basic Agent Skills metadata without installing a YAML dependency. The local Codex `skill-creator` quick validator also passed. Compatibility information is retained in the Skill body because that older validator does not accept the open specification's optional `compatibility` frontmatter field.

The local fixtures and private installation configuration are intentionally excluded from this repository. See the release verification report for actual engine tests and their separate limits.
