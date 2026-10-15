"""Security regressions use only disposable files, fake tokens and fake HTTP services."""
import ast
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import inference_bridge as bridge
import refresh_security_metadata as metadata

BENCHMARKS = [
    ROOT / 'results/2026-09-04/local-llm-coding-benchmark/benchmark.py',
    ROOT / 'results/2026-09-06/local-llm-humaneval-benchmark/benchmark.py',
]


class FakeWhich:
    """Stands in for shutil so the static policy test runs where bubblewrap isn't installed."""
    def __init__(self, found):
        self.found = found

    def which(self, name):
        return f'/usr/bin/{name}' if self.found else None


def sandbox_function(path, which=shutil):
    """Load just the pure sandbox builder, not benchmark imports or entry points."""
    tree = ast.parse(path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'sandbox_command')
    scope = {'Path': Path, 'shutil': which, 'sys': sys}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), scope)
    return scope['sandbox_command']


class SandboxTests(unittest.TestCase):
    def test_commands_clear_secrets_and_omit_etc(self):
        for path in BENCHMARKS:
            with self.subTest(path=path.name):
                cmd = sandbox_function(path, FakeWhich(True))(Path('/tmp/fake-work'))
                self.assertIn('--clearenv', cmd)
                self.assertNotIn('/etc', cmd)

    def test_missing_bubblewrap_refuses_instead_of_running_unsandboxed(self):
        for path in BENCHMARKS:
            with self.subTest(path=path.name), self.assertRaises(RuntimeError):
                sandbox_function(path, FakeWhich(False))(Path('/tmp/fake-work'))

    @unittest.skipUnless(shutil.which('bwrap'), 'bubblewrap unavailable')
    def test_real_sandbox_has_no_fake_secret_host_etc_or_host_network(self):
        with ThreadingHTTPServer(('127.0.0.1', 0), BaseHTTPRequestHandler) as host:
            # Merely listening suffices: the sandbox must be unable to connect.
            for path in BENCHMARKS:
                with self.subTest(path=str(path)), tempfile.TemporaryDirectory() as tmp:
                    work = Path(tmp)
                    program = f'''import json,os,socket
try:
    socket.create_connection(("127.0.0.1", {host.server_port}), .2).close()
    host_network = True
except OSError:
    host_network = False
print(json.dumps({{"secret":os.environ.get("AUDIT_SENTINEL"), "etc":os.path.exists("/etc/hostname"), "host_network":host_network}}))
'''
                    for name in ('runner.py', 'test_runner.py'):
                        (work / name).write_text(program)
                    p = subprocess.run(sandbox_function(path)(work), capture_output=True, text=True,
                                       env={'PATH': '/usr/bin:/bin', 'AUDIT_SENTINEL': 'fake-test-only'}, timeout=10)
                    if p.returncode and ('Operation not permitted' in p.stderr or 'No permissions' in p.stderr):
                        self.skipTest('runner disallows user namespaces; static policy test still applies')
                    self.assertEqual(p.returncode, 0, p.stderr)
                    self.assertEqual(json.loads(p.stdout), {'secret': None, 'etc': False, 'host_network': False})


class MetadataTests(unittest.TestCase):
    def test_policy_is_idempotent_and_hash_changes_with_script(self):
        text = '<html><head><meta charset="utf-8"></head><body><script>const a=1;</script></body></html>'
        secure = metadata.secure_html(text)
        self.assertEqual(metadata.secure_html(secure), secure)
        self.assertIn("script-src-attr 'none'", secure)
        self.assertNotEqual(metadata.secure_html(text.replace('a=1', 'a=2')), secure)
        self.assertLess(secure.index('Content-Security-Policy'), secure.index('<script>'))

    def test_published_html_has_current_policies(self):
        paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '*.html']).decode().splitlines()
        for name in paths:
            with self.subTest(path=name):
                text = (ROOT / name).read_text()
                self.assertEqual(text, metadata.secure_html(text))

    def test_archived_shell_guards_precede_actions(self):
        paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', 'results/*.sh', 'rig/drive.sh', 'scripts/build_llama_cuda12.sh.bak-*']).decode().splitlines()
        for name in paths:
            if name in metadata.SAFE_LAUNCHERS:
                continue
            with self.subTest(path=name):
                self.assertTrue((ROOT / name).read_text().split('\n', 1)[1].startswith(metadata.ARCHIVE_GUARD))

    def test_old_drivers_and_setters_refuse_before_side_effects(self):
        names = ['results/2026-09-18/devstral-p100-tuning/ctx-sweep.sh',
                 'results/2026-10-05/max-context/run.sh',
                 'results/2026-10-05/max-context/set_ctx.py',
                 'results/2026-10-05/qwen38-27b-spill/set_preset.py']
        with tempfile.TemporaryDirectory() as tmp:
            for name in names:
                with self.subTest(path=name):
                    command = ['bash' if name.endswith('.sh') else sys.executable, str(ROOT / name)]
                    p = subprocess.run(command, env={'PATH': '/usr/bin:/bin', 'HOME': tmp},
                                       capture_output=True, text=True, timeout=5)
                    self.assertNotEqual(p.returncode, 0)
                    self.assertIn('Refusing archived', p.stderr)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_staged_metadata_checks_index_not_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / 'scripts').mkdir()
            shutil.copy(ROOT / 'scripts/refresh_security_metadata.py', repo / 'scripts/')
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            page = repo / 'index.html'
            valid = metadata.secure_html('<html><head></head><script>const a=1;</script></html>')
            page.write_text(valid)
            subprocess.run(['git', '-C', str(repo), 'add', 'index.html'], check=True)
            page.write_text('<html><head></head><script>const a=2;</script></html>')
            command = [sys.executable, str(repo / 'scripts/refresh_security_metadata.py'), '--staged']
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            subprocess.run(['git', '-C', str(repo), 'add', 'index.html'], check=True)
            page.write_text(valid)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)

    def test_mutable_build_pin_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = subprocess.run(['bash', str(ROOT / 'scripts/build_llama_cuda12.sh')],
                               env={'PATH': '/usr/bin:/bin', 'HOME': tmp, 'LLAMA_COMMIT': 'main'},
                               capture_output=True, text=True, timeout=5)
            self.assertEqual(p.returncode, 2)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_container_launcher_has_no_host_network_or_shared_writable_cache(self):
        text = (ROOT / 'scripts/secure_polyglot.sh').read_text()
        for flag in ('--network none', '--http-proxy=false', '--read-only', '--cap-drop=ALL',
                     '--security-opt=no-new-privileges', '--pids-limit=256', '--pull=never'):
            self.assertIn(flag, text)
        self.assertNotIn('--network host', text)
        self.assertIn(':/seed/$cache:ro', text)
        self.assertIn('Output directory must be empty', text)


class FakeUpstream(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.server.requests.append((self.command, self.path, dict(self.headers), None))
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"data":[]}')

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.requests.append((self.command, self.path, dict(self.headers), body))
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream' if body.get('stream') else 'application/json')
        self.end_headers()
        self.wfile.write(b'data: {"choices":[]}\n\ndata: [DONE]\n\n' if body.get('stream') else b'{"choices":[]}')


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.socket = Path(self.tmp.name) / 'router.sock'
        self.upstream = ThreadingHTTPServer(('127.0.0.1', 0), FakeUpstream)
        self.upstream.requests = []
        self.host = bridge.host_server(self.socket, f'http://127.0.0.1:{self.upstream.server_port}')
        self.threads = []
        for server in (self.upstream, self.host):
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.threads.append(thread)

    def tearDown(self):
        for server in (self.host, self.upstream):
            server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join(timeout=2)
        self.tmp.cleanup()

    def request(self, method, path, body=None, headers=None):
        c = bridge.UnixConnection(self.socket)
        c.request(method, path, body=json.dumps(body) if body is not None else None, headers=headers or {})
        r = c.getresponse()
        result = (r.status, r.read())
        c.close()
        return result

    def test_allowed_inference_works_but_credentials_are_not_forwarded(self):
        status, body = self.request('POST', '/v1/chat/completions', {'model': 'fake', 'messages': []},
                                    {'Authorization': 'Bearer fake-only', 'Cookie': 'fake-only'})
        self.assertEqual(status, 200)
        request = self.upstream.requests[-1]
        self.assertNotIn('Authorization', request[2])
        self.assertNotIn('Cookie', request[2])
        self.assertEqual(request[3]['max_tokens'], 16384)
        self.assertFalse(request[3]['cache_prompt'])
        self.assertEqual(self.request('GET', '/v1/models')[0], 200)

    def test_streaming_preserved(self):
        status, body = self.request('POST', '/v1/chat/completions', {'model': 'fake', 'messages': [], 'stream': True})
        self.assertEqual(status, 200)
        self.assertIn(b'data: [DONE]', body)

    def test_management_and_arbitrary_paths_never_reach_upstream(self):
        for path in ('/models', '/v1/models?secret=1', '/models/fake/unload', '/../../etc/passwd', 'http://example.com/'):
            with self.subTest(path=path):
                self.assertEqual(self.request('POST', path, {})[0], 403)
        self.assertEqual(self.upstream.requests, [])

    def test_invalid_chat_and_oversized_budget_are_blocked(self):
        for body in ([], {'model': 'fake', 'messages': [], 'max_tokens': -1},
                     {'model': 'fake', 'messages': [], 'max_tokens': True},
                     {'model': 'fake', 'messages': [], 'max_tokens': 16385}):
            self.assertIn(self.request('POST', '/v1/chat/completions', body)[0], (400, 502))
        self.assertEqual(self.upstream.requests, [])

    def test_ambiguous_framing_rejected(self):
        with socket.socket(socket.AF_UNIX) as c:
            c.connect(str(self.socket))
            c.sendall(b'POST /v1/chat/completions HTTP/1.0\r\nContent-Length: 0\r\nContent-Length: 1\r\n\r\n')
            self.assertIn(b'400', c.recv(4096))
        self.assertEqual(self.upstream.requests, [])

    def test_non_loopback_destinations_and_credentials_refused(self):
        for url in ('http://example.com:8081', 'http://localhost:8081', 'http://user:pass@127.0.0.1:8081',
                    'http://127.0.0.1:8081/arbitrary', 'https://127.0.0.1:8081'):
            with self.assertRaises(ValueError):
                bridge.host_server(Path(self.tmp.name) / 'bad.sock', url)


if __name__ == '__main__':
    unittest.main()
