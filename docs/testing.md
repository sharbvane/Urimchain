# Verification boundaries

`python -m unittest discover -s tests -v` runs without downloaded engines. Tests create byte headers and ZIP structures in a temporary directory. They verify routing, architecture recognition, malformed-header rejection, extension spoofing, Unity metadata limitations, input preservation, Skill metadata, and the source publication boundary. These headers are parser fixtures, not executable programs and not evidence of engine decompilation.

The normal **Fast checks** workflow also validates the install plan. It does not download the native engines or claim that Ghidra, JADX, Apktool, ILSpy, or REA analysis passed.

The manually dispatched **Windows engines** workflow installs from the pinned official download manifest, runs Doctor, compiles a harmless .NET class library, and verifies that the combined ILSpy/REA route produces the expected C# class. It never executes the generated library. A successful workflow run verifies only those explicitly performed checks; the workflow definition alone is not a test result.

Native PE, ARM64 ELF, Android APK/DEX and decoded resource tests require installed engines and trusted fixtures. The release verification report records actual local results separately. Full Android resource decoding requires a valid binary Manifest/resource table; a synthetic ZIP with textual XML tests identification only. Unity IL2CPP metadata recovery is unavailable.

PowerShell installer lifecycle tests use isolated temporary roots, preserve an unrelated user file during uninstall, and exercise configuration preservation against a temporary Codex home. They never touch the active global toolchain.

## Rebuild the harmless examples

`tests/fixtures/` contains the small original source fixtures used for local acceptance. They have arithmetic functions, caller relationships and marker strings. They do not access the network, install anything or run as part of analysis. Build into your chosen scratch directory outside the repository; generated outputs are not distributed.

For .NET, use an existing .NET 8 SDK:

```powershell
$scratch = Join-Path $env:TEMP 'urimchain-fixtures'
New-Item -ItemType Directory -Force $scratch | Out-Null
dotnet build tests/fixtures/managed/Fixture.csproj -c Release -o "$scratch/managed" -p:BaseIntermediateOutputPath="$scratch/managed-obj/"
```

For native PE, open an x64 Visual Studio Developer PowerShell with MSVC available. This deliberately small executable has a custom entry point and no C runtime. Compile it for static analysis; do not launch it:

```powershell
cl /nologo /Od /GS- /c tests/fixtures/native/native-test.c /Fo"$scratch/native-test.obj"
link /nologo /entry:entry /subsystem:console /nodefaultlib /machine:x64 /out:"$scratch/native-test.exe" "$scratch/native-test.obj"
```

For ELF, use an existing Clang installation capable of cross-compiling AArch64 with LLD. Windows compiler distributions do not all include that target/linker:

```powershell
clang --target=aarch64-linux-gnu -fuse-ld=lld -nostdlib -shared -fPIC -O0 tests/fixtures/native/native-elf.c -o "$scratch/libfixture.so"
```

For Android, use an existing JDK and Android SDK containing `javac`, D8, AAPT2, and a platform `android.jar`. Choose installed versions; the example uses SDK environment variables instead of a machine-specific path. No SDK is installed by Urimchain:

```powershell
$buildTools = Join-Path $env:ANDROID_HOME 'build-tools/YOUR_INSTALLED_VERSION'
$androidJar = Join-Path $env:ANDROID_HOME 'platforms/android-YOUR_INSTALLED_API/android.jar'
New-Item -ItemType Directory -Force "$scratch/android/classes", "$scratch/android/dex" | Out-Null
javac --release 8 -d "$scratch/android/classes" tests/fixtures/android/KnownAlgorithm.java
& "$buildTools/d8.bat" --output "$scratch/android/dex" "$scratch/android/classes/re/fixture/KnownAlgorithm.class"
& "$buildTools/aapt2.exe" compile --dir tests/fixtures/android/res -o "$scratch/android/resources.zip"
& "$buildTools/aapt2.exe" link -o "$scratch/android/fixture.apk" -I $androidJar --manifest tests/fixtures/android/AndroidManifest.xml "$scratch/android/resources.zip"
Add-Type -AssemblyName System.IO.Compression.FileSystem
$apk = [IO.Compression.ZipFile]::Open("$scratch/android/fixture.apk", 'Update')
try { [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($apk, "$scratch/android/dex/classes.dex", 'classes.dex') | Out-Null } finally { $apk.Dispose() }
```

Check each compiler command's exit status before continuing. The APK is an unsigned static-analysis fixture with no launchable Activity. It requires no signing or device installation. Analyze these outputs with `urimchain.cmd analyze TARGET --output NEW_DIRECTORY`, keeping each output separate. Expect `score`/`entry` or `caller` in native output, `KnownAlgorithm.Transform` in C#, Java `transform`/`caller`, and `fixture_marker` in decoded APK resources. Optimization, compiler versions and stripped symbols can change the exact decompiler text.
