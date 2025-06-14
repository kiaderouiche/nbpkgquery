import unittest
from nbpkg.cli.parser import parse_args
from nbpkg.cli.executor import execute_command
import sys

class TestNbqueryOptions(unittest.TestCase):
    def setUp(self):
        self.original_argv = sys.argv

    def tearDown(self):
        sys.argv = self.original_argv

    def test_descr_option(self):
        sys.argv = ["nbquery.py", "--DESCR", "./docs/perl-5.40.1.tgz"]
        args = parse_args()
        executor = CommandExecutor(args)
        result = executor.handle_descr()
        self.assertIn("./docs/perl-5.40.1.tgz", result)
        self.assertIn("description", result["./docs/perl-5.40.1.tgz"])

if __name__ == "__main__":
    unittest.main()
