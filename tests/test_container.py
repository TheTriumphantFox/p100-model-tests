"""Opt-in real rootless-Podman smoke test; no GPU or live endpoint is used."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]


class FakeRouter(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"data":[]}')


@unittest.skipUnless(os.environ.get('P100_TEST_CONTAINER') == '1', 'opt-in Podman smoke test')
class RealContainerTests(unittest.TestCase):
    def test_network_none_and_restricted_inference_bridge(self):
        with tempfile.TemporaryDirectory(prefix='p100-container-test-') as tmp:
            temp = Path(tmp)
            for name in ('tools/aider', 'tools/polyglot-benchmark'):
                (temp / name).mkdir(parents=True)
            output = temp / 'output'
            with ThreadingHTTPServer(('127.0.0.1', 0), FakeRouter) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                probe = f'''import json,os,socket,urllib.request,urllib.error,pathlib
results={{}}
results['secret_absent']=os.environ.get('AUDIT_SENTINEL') is None
results['proxy_secret_absent']=not os.environ.get('HTTP_PROXY') and not os.environ.get('http_proxy')
for label,address in [('host_network',('127.0.0.1',{server.server_port})),('outbound_network',('1.1.1.1',443))]:
    try:
        socket.create_connection(address,.5).close();results[label]=True
    except OSError:
        results[label]=False
results['models']=json.load(urllib.request.urlopen('http://127.0.0.1:8081/v1/models',timeout=10))
try:
    urllib.request.urlopen('http://127.0.0.1:8081/models',timeout=10)
    results['management_blocked']=False
except urllib.error.HTTPError as exc:
    results['management_blocked']=exc.code==403
for label,path in [('root_readonly','/etc/p100-fake-probe'),('sources_readonly','/aider/p100-fake-probe')]:
    try:
        pathlib.Path(path).write_text('fake');results[label]=False
    except OSError:
        results[label]=True
pathlib.Path('/run/probe.json').write_text(json.dumps(results))
print(json.dumps(results))
'''
                env = {**os.environ, 'P100_RUN_DIR': str(output), 'P100_TEST_WORKSPACE': str(temp),
                       'P100_INFERENCE_URL': f'http://127.0.0.1:{server.server_port}',
                       'AUDIT_SENTINEL': 'fake-test-only', 'HTTP_PROXY': 'http://fake-test-only.invalid:9999'}
                try:
                    p = subprocess.run(['bash', str(ROOT / 'scripts/secure_polyglot.sh'), 'python3', '-c', probe],
                                       env=env, capture_output=True, text=True, timeout=90)
                    self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                    result = json.loads((output / 'probe.json').read_text())
                    self.assertEqual(result, {'secret_absent': True, 'proxy_secret_absent': True,
                                             'host_network': False, 'outbound_network': False,
                                             'models': {'data': []}, 'management_blocked': True,
                                             'root_readonly': True, 'sources_readonly': True})
                finally:
                    server.shutdown()
                    thread.join(timeout=2)


if __name__ == '__main__':
    unittest.main()
