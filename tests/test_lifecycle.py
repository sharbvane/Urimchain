"""Installer safety tests use fake owned files and isolated configuration."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which('pwsh')


@unittest.skipUnless(PWSH, 'PowerShell 7 required for Windows lifecycle tests')
class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'installation'
        self.root.mkdir()
        self.root = self.root.resolve()
        owned = self.root / 'owned.txt'
        owned.write_text('owned', encoding='utf-8')
        self.record = {'product': 'Urimchain', 'root': str(self.root), 'files': [
            {'path': 'owned.txt', 'sha256': hashlib.sha256(owned.read_bytes()).hexdigest()}]}
        self.save_record()

    def save_record(self):
        (self.root / 'urimchain-install.json').write_text(json.dumps(self.record), encoding='utf-8')

    def invoke(self, script, *arguments, success=True):
        result = subprocess.run([PWSH, '-NoProfile', '-File', str(ROOT / 'scripts' / script),
                                 '-Root', str(self.root), *map(str, arguments)], capture_output=True, text=True,
                                encoding='utf-8', errors='replace')
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_uninstall_preserves_unowned_files(self):
        user = self.root / 'user.txt'
        user.write_text('retain')
        self.invoke('uninstall.ps1', '-Plan')
        self.assertTrue((self.root / 'owned.txt').exists())
        self.invoke('uninstall.ps1')
        self.assertFalse((self.root / 'owned.txt').exists())
        self.assertEqual(user.read_text(), 'retain')

    def test_install_plan_does_not_create_target(self):
        target = self.root.parent / 'planned installation'
        result = subprocess.run([PWSH, '-NoProfile', '-File', str(ROOT / 'scripts/install.ps1'),
                                 '-Root', str(target), '-Plan'], capture_output=True,
                                text=True, encoding='utf-8', errors='replace')
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(Path(plan['root']).resolve(), target.resolve())
        self.assertEqual(plan['globalEnvironmentChanges'], [])
        self.assertFalse(target.exists())

    def test_modified_owned_file_prevents_removal(self):
        (self.root / 'owned.txt').write_text('user modification')
        self.invoke('uninstall.ps1', success=False)
        self.assertEqual((self.root / 'owned.txt').read_text(), 'user modification')

    def test_ownership_escape_rejected(self):
        outside = self.root.parent / 'outside.txt'
        outside.write_text('retain')
        self.record['files'][0]['path'] = '../outside.txt'
        self.save_record()
        self.invoke('uninstall.ps1', success=False)
        self.assertTrue(outside.exists())

    def test_existing_mcp_not_overwritten(self):
        self.assert_existing_mcp_retained('urimchain')

    def test_existing_quoted_mcp_not_overwritten(self):
        self.assert_existing_mcp_retained('"urimchain"')

    def test_existing_literal_mcp_not_overwritten(self):
        self.assert_existing_mcp_retained("'urimchain'")

    def assert_existing_mcp_retained(self, key):
        codex = self.root.parent / 'codex'
        codex.mkdir()
        config = codex / 'config.toml'
        original = f'[mcp_servers.{key}]\r\ncommand = "existing"\r\n'.encode('utf-8')
        config.write_bytes(original)
        (self.root / 'skill').mkdir()
        (self.root / 'skill/SKILL.md').write_text('fixture skill')
        (self.root / 'toolchain.json').write_text(json.dumps({
            'node': 'node', 'rea': 'rea', 'rea_env': {'REA_TEST': 'value'}}))
        result = self.invoke('configure.ps1', '-CodexHome', codex, success=False)
        self.assertIn('Existing urimchain MCP configuration retained', result.stderr)
        self.assertEqual(config.read_bytes(), original)
        self.assertFalse((codex / 'skills/urimchain').exists())
        self.assertFalse((self.root / 'urimchain-config.json').exists())

    def test_registration_and_uninstall_preserve_other_configuration(self):
        codex = self.root.parent / 'codex'
        codex.mkdir()
        config = codex / 'config.toml'
        original = '[mcp_servers.other]\ncommand = "keep"\n'
        config.write_text(original)
        (self.root / 'skill').mkdir()
        (self.root / 'skill/SKILL.md').write_text('fixture skill')
        (self.root / 'toolchain.json').write_text(json.dumps({
            'node': 'node', 'rea': 'rea', 'rea_env': {'REA_TEST': 'value'}}))
        self.invoke('configure.ps1', '-CodexHome', codex)
        self.assertTrue(config.read_text().startswith(original))
        self.assertTrue((codex / 'skills/urimchain/SKILL.md').exists())
        user_change = '\n# User comment added later\n'
        with config.open('ab') as stream:
            stream.write(user_change.encode('utf-8'))
        self.invoke('uninstall.ps1')
        self.assertEqual(config.read_text(), original + user_change)
        self.assertFalse((codex / 'skills/urimchain/SKILL.md').exists())


if __name__ == '__main__':
    unittest.main()
