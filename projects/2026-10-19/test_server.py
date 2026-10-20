"""Regression checks for the encoding issue discovered by actual Firefox navigation."""
import threading
import unittest
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from serve import Handler


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = Path(__file__).resolve().parent / 'airline-delay-intervention-screen/outputs'
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(directory)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = 'http://127.0.0.1:' + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_text_routes_explicitly_declare_utf8(self):
        for filename in ['app.html', 'app.js', 'executive_memo.md', 'policy_evaluation.csv']:
            with self.subTest(filename=filename), urllib.request.urlopen(self.origin + '/' + filename) as response:
                self.assertEqual(response.status, 200)
                self.assertIn('charset=utf-8', response.headers['Content-Type'])
                self.assertTrue(response.read().decode('utf-8'))

    def test_optional_favicon_has_no_missing_resource_error(self):
        with urllib.request.urlopen(self.origin + '/favicon.ico') as response:
            self.assertEqual(response.status, 204)


if __name__ == '__main__':
    unittest.main()
