import unittest
from nbpkg.cli.parser import parse_args
from nbpkg.cli.executor import execute_command
from nbpkg.cli.nbformat import format_results
import sys
import argparse

class TestNbqueryCommands(unittest.TestCase):
    def setUp(self):
        # Simuler parse_args pour éviter de dépendre de sys.argv
        self.original_argv = sys.argv

    def tearDown(self):
        sys.argv = self.original_argv

    def test_version_command(self):
        sys.argv = ["nbquery.py", "version"]
        args = parse_args()
        result = execute_command(args)
        output = format_results(result)
        expected = "Version: 0.2 (build 20230406, current)"
        self.assertEqual(output.strip(), expected)

    def test_about_command(self):
        sys.argv = ["nbquery.py", "about"]
        args = parse_args()
        result = execute_command(args)
        output = format_results(result)
        self.assertTrue("about:" in output)
        self.assertTrue("nbpkgquery" in output)

if __name__ == "__main__":
    unittest.main()
