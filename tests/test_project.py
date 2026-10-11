"""Fast tests use generated headers, never run a target executable."""
import importlib.util
import json
from pathlib import Path
import re
import struct
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load_router():
    spec = importlib.util.spec_from_file_location('router', ROOT / 'scripts/re-tool.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pe(managed=False):
    data = bytearray(512)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 60, 128)
    data[128:132] = b'PE\0\0'
    struct.pack_into('<H', data, 132, 0x8664)
    struct.pack_into('<H', data, 148, 240)
    struct.pack_into('<H', data, 152, 0x20b)
    struct.pack_into('<I', data, 260, 16)
    if managed:
        struct.pack_into('<II', data, 376, 4096, 72)
    return bytes(data)


class Identification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = load_router()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def identify(self, content, name='target.bin'):
        path = self.root / name
        path.write_bytes(content)
        original = path.read_bytes()
        result = self.router.identify(path)
        self.assertEqual(path.read_bytes(), original)
        return result

    def test_pe_and_managed_are_distinguished_by_header(self):
        self.assertEqual(self.identify(pe(), 'spoof.apk')['kind'], 'native-pe')
        self.assertEqual(self.identify(pe(True), 'spoof.so')['kind'], 'managed-pe')

    def test_extension_does_not_choose_engine(self):
        self.assertEqual(self.identify(b'plain text', 'fake.exe')['kind'], 'unknown')

    def test_malformed_pe(self):
        for data in (b'MZ', b'MZ' + bytes(62), pe()[:270]):
            with self.subTest(length=len(data)), self.assertRaises(ValueError):
                self.identify(data)

    def test_elf_arm64(self):
        data = bytearray(64)
        data[:6] = b'\x7fELF\x02\x01'
        struct.pack_into('<H', data, 18, 183)
        result = self.identify(data)
        self.assertEqual((result['kind'], result['architecture']), ('elf', 'arm64'))

    def test_malformed_elf(self):
        for data in (b'\x7fELF', b'\x7fELF' + bytes(60)):
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.identify(data)

    def test_dex(self):
        data = bytearray(112)
        data[:8] = b'dex\n035\0'
        struct.pack_into('<III', data, 32, len(data), 112, 0x12345678)
        self.assertEqual(self.identify(data)['routes'], ['jadx'])

    def test_output_inside_target_directory_is_rejected_without_creation(self):
        (self.root / 'GameAssembly.dll').write_bytes(pe())
        (self.root / 'global-metadata.dat').write_bytes(b'\xaf\x1b\xb1\xfa')
        output = self.root / 'analysis'
        with self.assertRaises(ValueError):
            self.router.analyze(self.root, output)
        self.assertFalse(output.exists())

    def test_apk_structure_and_native_members(self):
        path = self.root / 'fixture.zip'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('AndroidManifest.xml', '<manifest/>')
            archive.writestr('lib/arm64-v8a/libexample.so', b'fixture')
        result = self.router.identify(path)
        self.assertEqual(result['kind'], 'apk')
        self.assertEqual(result['native_members'], ['lib/arm64-v8a/libexample.so'])
        self.assertIn('jadx', result['routes'])
        self.assertIn('apktool', result['routes'])

    def test_unity_metadata_has_no_removed_engine(self):
        result = self.identify(b'\xaf\x1b\xb1\xfa' + bytes(32))
        self.assertEqual(result['kind'], 'unity-metadata')
        self.assertEqual(result['routes'], [])
        self.assertEqual(result['metadata_recovery'], 'unavailable')

    def test_unity_directory_retains_native_route(self):
        (self.root / 'GameAssembly.dll').write_bytes(pe())
        (self.root / 'global-metadata.dat').write_bytes(b'\xaf\x1b\xb1\xfa')
        result = self.router.identify(self.root)
        self.assertEqual(result['kind'], 'unity-il2cpp')
        self.assertEqual(result['metadata_recovery'], 'unavailable')
        self.assertIn('ghidra-native', result['routes'])

    def test_missing_target(self):
        with self.assertRaises(FileNotFoundError):
            self.router.identify(self.root / 'absent')


class Publication(unittest.TestCase):
    def test_dependency_sources_and_versions_are_pinned(self):
        tools = json.loads((ROOT / 'dependencies.json').read_text(encoding='utf-8'))['tools']
        self.assertEqual(len({tool['id'] for tool in tools}), len(tools))
        for tool in tools:
            self.assertTrue(tool['version'])
            self.assertTrue(tool['url'].startswith('https://'))
            self.assertTrue(tool['upstream'].startswith('https://'))
            self.assertTrue(tool['license'])
            self.assertTrue(tool['license_url'].startswith('https://'))
            if tool['archive'] in ('zip', 'jar'):
                self.assertRegex(tool['sha256'], r'^[a-fA-F0-9]{64}$')
            elif tool['archive'] == 'npm':
                self.assertTrue(tool['integrity'].startswith('sha512-'))
            else:
                self.assertEqual(tool['archive'], 'dotnet')
                self.assertEqual(tool['package'], 'ilspycmd')

    def test_skill_open_format(self):
        path = ROOT / 'skill/urimchain/SKILL.md'
        text = path.read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        metadata = text.split('---', 2)[1]
        fields = dict(line.split(':', 1) for line in metadata.splitlines() if ':' in line)
        self.assertEqual(fields.get('name', '').strip(), 'urimchain')
        description = fields.get('description', '').strip()
        self.assertTrue(1 <= len(description) <= 1024)
        self.assertLessEqual(len(text.splitlines()), 500)

    def test_publication_has_no_binaries_or_local_secrets(self):
        forbidden_suffixes = {'.exe', '.dll', '.jar', '.zip', '.apk', '.dex', '.so', '.pdb'}
        forbidden_patterns = (r'[A-Za-z]:[/\\]Users[/\\]',
                              r'gh[pousr]_[A-Za-z0-9]{20,}',
                              r'github_pat_[A-Za-z0-9_]{20,}',
                              r'sk-[A-Za-z0-9_-]{20,}',
                              r'https?://[^\s/]+:[^\s/@]+@')
        locations = [ROOT / item for item in ('scripts', 'skill', 'docs', '.github', 'tests/fixtures')]
        locations += [path for path in ROOT.iterdir() if path.is_file()]
        for location in locations:
            for path in ([location] if location.is_file() else location.rglob('*')):
                if not path.is_file():
                    continue
                self.assertNotIn(path.suffix.lower(), forbidden_suffixes, str(path))
                if path.suffix in ('.py', '.ps1', '.md', '.json', '.yml', '.yaml', '.java', '.c', '.cs', '.csproj', '.xml') or not path.suffix:
                    text = path.read_text(encoding='utf-8-sig')
                    for pattern in forbidden_patterns:
                        self.assertIsNone(re.search(pattern, text), str(path))


if __name__ == '__main__':
    unittest.main()
