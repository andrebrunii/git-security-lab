import unittest
from unittest.mock import patch

from app.report import render_report


class ReportTests(unittest.TestCase):
    def test_normal_name(self):
        self.assertEqual(render_report("Andrea"), "Report per: Andrea")

    def test_empty_name(self):
        self.assertEqual(render_report(""), "Report per: ")

    def test_special_characters_remain_text(self):
        # Impedisce di lanciare processi anche eseguendo il test sulla versione vulnerabile.
        with patch("subprocess.run", side_effect=AssertionError("Processi non ammessi")):
            self.assertEqual(render_report("Andrea & Co"), "Report per: Andrea & Co")

    def test_unicode(self):
        self.assertEqual(render_report("Niccolò"), "Report per: Niccolò")


if __name__ == "__main__":
    unittest.main()
