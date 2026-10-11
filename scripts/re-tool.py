"""Global static routing. Never load or execute target code."""
import argparse, hashlib, json, os, pathlib, struct, subprocess, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def identify(path):
    path = pathlib.Path(path).resolve(strict=True)
    result = {'path':str(path), 'routes':[], 'architecture':None}
    if path.is_dir():
        binaries = list(path.glob('**/GameAssembly.dll')) + list(path.glob('**/libil2cpp.so'))
        metadata = list(path.glob('**/global-metadata.dat'))
        result.update(kind='unity-il2cpp' if binaries and metadata else 'directory',
                      binaries=[str(x) for x in binaries], metadata=[str(x) for x in metadata],
                      input_hashes={str(x):digest(x) for x in binaries+metadata})
        if binaries and metadata:
            result['routes'] = sorted({route for binary in binaries for route in identify(binary)['routes']})
            result['metadata_recovery'] = 'unavailable'
        return result
    with path.open('rb') as stream:
        result['sha256'] = hashlib.file_digest(stream,'sha256').hexdigest()
        stream.seek(0)
        data = stream.read(1024*1024)
    if data.startswith(b'MZ'):
        if len(data) < 64:
            raise ValueError('Truncated DOS header')
        pe = struct.unpack_from('<I', data, 60)[0]
        if pe + 26 > len(data) or data[pe:pe+4] != b'PE\0\0':
            raise ValueError('Invalid PE header')
        machine, = struct.unpack_from('<H', data, pe+4)
        result['architecture'] = {0x14c:'x86',0x8664:'x64',0xaa64:'arm64'}.get(machine, hex(machine))
        magic, = struct.unpack_from('<H', data, pe+24)
        if magic not in (0x10b, 0x20b):
            raise ValueError('Unsupported PE optional header')
        optional_size, = struct.unpack_from('<H', data, pe+20)
        directory = pe+24+(112 if magic == 0x20b else 96)
        count_offset = pe+24+(108 if magic == 0x20b else 92)
        if pe+24+optional_size > len(data) or count_offset+4 > pe+24+optional_size:
            raise ValueError('Truncated PE optional header')
        count, = struct.unpack_from('<I', data, count_offset)
        managed = count > 14 and directory+120 <= pe+24+optional_size and struct.unpack_from('<I',data,directory+112)[0] != 0
        result.update(kind='managed-pe' if managed else 'native-pe', routes=['ilspy','rea-managed'] if managed else ['ghidra-native'])
        if path.name.lower() == 'gameassembly.dll':
            result['unity_candidate'] = True
    elif data.startswith(b'\x7fELF'):
        if len(data) < 20 or data[4] not in (1,2) or data[5] not in (1,2):
            raise ValueError('Invalid ELF header')
        if len(data) < (64 if data[4] == 2 else 52):
            raise ValueError('Truncated ELF header')
        machine, = struct.unpack_from('<H' if data[5] == 1 else '>H', data, 18)
        result.update(kind='elf', architecture={3:'x86',62:'x64',40:'arm',183:'arm64'}.get(machine,str(machine)), routes=['ghidra-direct-headless'])
        result['rea_windows_native_supported'] = False
    elif data.startswith(b'dex\n'):
        if len(data) < 112 or not data[4:7].isdigit() or data[7] != 0:
            raise ValueError('Invalid DEX header')
        result.update(kind='dex', routes=['jadx'])
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
        apk = 'AndroidManifest.xml' in names
        result.update(kind='apk' if apk else 'zip', routes=['jadx','apktool','rea-android'] if apk else ['rea-archive'])
        result['native_members'] = [n for n in names if n.startswith('lib/') and n.endswith('.so')]
        result['unity_metadata_members'] = [n for n in names if n.endswith('global-metadata.dat')]
    elif data[:4] == b'\xaf\x1b\xb1\xfa':
        result.update(kind='unity-metadata', routes=[], metadata_recovery='unavailable')
    else:
        result.update(kind='unknown', routes=[])
    return result

def run(command, output, env=None):
    with output.open('wb') as log:
        proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT)
        try:
            code = proc.wait(timeout=600)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill.exe','/PID',str(proc.pid),'/T','/F'],stdout=log,stderr=subprocess.STDOUT)
            raise
    if code:
        raise RuntimeError(f'Tool exited {code}; see {output}')

def analyze(target, output):
    output = pathlib.Path(output).resolve()
    info = identify(target)
    source = pathlib.Path(info['path'])
    if source.is_dir() and (output == source or source in output.parents):
        raise ValueError('Output must be outside the input directory')
    output.mkdir(parents=True, exist_ok=False)
    (output/'identity.json').write_text(json.dumps(info,indent=2), encoding='utf-8')
    config = json.loads((ROOT/'toolchain.json').read_text(encoding='utf-8-sig'))
    env = dict(os.environ, **config['rea_env'])
    analysis = info
    if info['kind'] == 'unity-il2cpp':
        if len(info['binaries']) != 1:
            raise ValueError('Select one native binary from the Unity directory')
        analysis = identify(info['binaries'][0])
    path = analysis['path']
    java = str(pathlib.Path(config['jdk'])/'bin/java.exe')
    if analysis['kind'] in ('apk','dex'):
        run([java,'-cp',config['jadx_jar'],'jadx.cli.JadxCLI','-d',str(output/'jadx'),path], output/'jadx.log', env)
        if analysis['kind'] == 'apk':
            run([java,'-jar',config['apktool'],'d','-o',str(output/'apktool'),'-p',str(output/'framework'),path],output/'apktool.log',env)
    elif analysis['kind'] == 'managed-pe':
        run([config['ilspy'],'-o',str(output/'ilspy'),path],output/'ilspy.log',env)
        run([config['node'],config['rea'],'inspect-managed-artifact',path,'--format','json'],output/'rea-managed.json',env)
    elif analysis['kind'] == 'native-pe':
        run([config['node'],config['rea'],'inspect',path,'--provider','ghidra','--format','json'],output/'rea-native.json',env)
    elif analysis['kind'] == 'elf':
        arguments = [str(pathlib.Path(config['ghidra'])/'support/analyzeHeadless.bat'),str(output),'native','-import',path,'-readOnly','-deleteProject','-scriptPath',str(ROOT/'scripts'),'-postScript','ExportStatic.java',str(output/'native-code.txt')]
        if any(any(c in arg for c in '%!\r\n"') for arg in arguments):
            raise ValueError('Unsupported characters in Windows batch path')
        run('cmd.exe /d /s /c "'+' '.join('"'+arg+'"' for arg in arguments)+'"',output/'ghidra.log',env)
        exported = output/'native-code.txt'
        if not exported.exists() or not exported.stat().st_size:
            raise RuntimeError('Ghidra did not export functions; inspect ghidra.log')
    else:
        raise ValueError(f'No automatic analysis for {info["kind"]}; identification retained')
    if identify(target) != info:
        raise RuntimeError('Target changed during analysis')
    return info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['identify','analyze'])
    parser.add_argument('target')
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.action == 'analyze' and not args.output:
        parser.error('analyze requires a new --output directory')
    print(json.dumps(identify(args.target) if args.action == 'identify' else analyze(args.target,args.output), indent=2))
