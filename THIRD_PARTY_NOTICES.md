# Third-party software

Urimchain's own orchestration code, scripts, fixtures and Skill are MIT licensed. The project installs upstream tools separately; its source archive does not include their large binaries. Installing a tool does not change its license. Keep the license, NOTICE and component notices included with each upstream distribution.

| Project / pinned version | Maintainer attribution | License / upstream license source |
|---|---|---|
| [REA 6.4.0](https://github.com/morluto/rea/tree/rea-agents-6.4.0) | Copyright 2026 morluto and contributors | [MIT](https://github.com/morluto/rea/blob/rea-agents-6.4.0/LICENSE) |
| [Ghidra 12.1.4](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build) | National Security Agency and Ghidra contributors | [Apache-2.0](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.4_build/LICENSE); bundled component notices remain in the distribution |
| [JADX 1.5.6](https://github.com/skylot/jadx/releases/tag/v1.5.6) | skylot and JADX contributors | [Apache-2.0](https://github.com/skylot/jadx/blob/v1.5.6/LICENSE) |
| [Apktool 3.0.3](https://github.com/iBotPeaches/Apktool/releases/tag/v3.0.3) | Connor Tumbleson, Ryszard Wiśniewski and contributors | [Apache-2.0](https://github.com/iBotPeaches/Apktool/blob/v3.0.3/LICENSE.md) |
| [jadx-headless-mcp 0.7.1](https://github.com/1013503897/jadx-headless-mcp/releases/tag/v0.7.1) | Copyright 2026 jadx-headless-mcp authors | [Apache-2.0](https://github.com/1013503897/jadx-headless-mcp/blob/v0.7.1/LICENSE); separate download, not vendored source |
| [ILSpy / ilspycmd 9.1.0.7988](https://www.nuget.org/packages/ilspycmd/9.1.0.7988) | ILSpy contributors / SharpDevelop team | [MIT](https://github.com/icsharpcode/ILSpy/blob/v9.1/LICENSE); dependent packages retain their own notices |
| [Eclipse Temurin JDK 21.0.12.1+1](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1) | Eclipse Adoptium, OpenJDK and their contributors | [GPL-2.0 with Classpath Exception](https://github.com/openjdk/jdk21u/blob/master/LICENSE); see installed `legal/` for exceptions and separately licensed components |

The REA npm package LICENSE was checked as MIT, as was npm package metadata. GitHub's automated license classifier reports NOASSERTION for the Android bridge, but its actual v0.7.1 LICENSE contains Apache License 2.0. License text takes precedence over the classifier.

The dependency manifest records official URLs, pinned versions and SHA-256 release digests for GitHub downloads. npm uses package integrity. The pinned ILSpy SHA-256 was independently computed from the official NuGet flat-container package and matched the tested package; `dotnet nuget verify` validated its NuGet.org repository signature. This is not advertised as a separately published upstream SHA-256 checksum. No third-party checksum should be replaced with an unverified mirror's checksum.

Node.js, Python and .NET are external prerequisites, not bundled or re-licensed by this repository. Their distributions and transitive packages have independent licenses. Cpp2IL is absent from the dependency manifest and installer. IDA is not installed or distributed.
