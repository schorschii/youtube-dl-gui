"""Contains test cases for the utils.py module."""

import locale
import sys
import unittest
from pathlib import Path
from unittest import mock

PATH = Path(__file__).parent
sys.path.insert(0, str(PATH.parent))

from youtube_dl_gui import utils


class TestUtils(unittest.TestCase):
    """Test case for utils functions"""

    def test_get_config_path(self):
        config_path: str = utils.get_config_path()
        self.assertIsNot(config_path, "")
        self.assertIsInstance(config_path, str)

    def test_decode_tuple(self):
        win_size: str = "740/490"
        win_size_tuple = utils.decode_tuple(win_size)
        self.assertEqual(len(win_size_tuple), 2)
        self.assertTrue(all(isinstance(size, int) for size in win_size_tuple))

    def test_encode_tuple(self):
        win_size_tuple = (740, 490)
        win_size: str = utils.encode_tuple(win_size_tuple)
        self.assertTrue("/" in win_size)

    @mock.patch("youtube_dl_gui.utils.locale_getpreferredencoding")
    def test_get_encoding(self, mock_getpreferredencoding):
        mock_getpreferredencoding.return_value = "cp65001"
        encoding = utils.get_encoding()
        self.assertEqual(encoding, "cp65001")
        mock_getpreferredencoding.assert_called_once()

    @mock.patch("youtube_dl_gui.utils.locale_getpreferredencoding")
    def test_get_encoding_error(self, mock_getpreferredencoding):
        mock_getpreferredencoding.side_effect = locale.Error()
        encoding = utils.get_encoding()
        self.assertEqual(encoding, "utf-8")
        mock_getpreferredencoding.assert_called_once()

    def test_get_key(self):
        dictionary = {"key": "value"}
        result = utils.get_key("value", dictionary)
        self.assertEqual(result, "key")
        result = utils.get_key("value2", dictionary)
        self.assertEqual(result, "")

    def test_get_time(self):
        timestamp = 1621991858.3169
        expected = {"seconds": 38, "minutes": 17, "hours": 1, "days": 18773}
        time_dict = utils.get_time(timestamp)
        self.assertDictEqual(time_dict, expected)


class TestToBytes(unittest.TestCase):
    """Test case for the to_bytes method."""

    def test_to_bytes_bytes(self):
        self.assertEqual(utils.to_bytes("596.00B"), 596.00)
        self.assertEqual(utils.to_bytes("133.55B"), 133.55)

    def test_to_bytes_kilobytes(self):
        self.assertEqual(utils.to_bytes("1.00KiB"), 1024.00)
        self.assertEqual(utils.to_bytes("5.55KiB"), 5683.20)

    def test_to_bytes_megabytes(self):
        self.assertEqual(utils.to_bytes("13.64MiB"), 14302576.64)
        self.assertEqual(utils.to_bytes("1.00MiB"), 1048576.00)

    def test_to_bytes_gigabytes(self):
        self.assertEqual(utils.to_bytes("1.00GiB"), 1073741824.00)
        self.assertEqual(utils.to_bytes("1.55GiB"), 1664299827.20)

    def test_to_bytes_terabytes(self):
        self.assertEqual(utils.to_bytes("1.00TiB"), 1099511627776.00)


class TestFormatBytes(unittest.TestCase):
    """Test case for the format_bytes method."""

    def test_format_bytes_bytes(self):
        self.assertEqual(utils.format_bytes(518.00), "518.00B")

    def test_format_bytes_kilobytes(self):
        self.assertEqual(utils.format_bytes(1024.00), "1.00KiB")

    def test_format_bytes_megabytes(self):
        self.assertEqual(utils.format_bytes(1048576.00), "1.00MiB")

    def test_format_bytes_gigabytes(self):
        self.assertEqual(utils.format_bytes(1073741824.00), "1.00GiB")

    def test_format_bytes_terabytes(self):
        self.assertEqual(utils.format_bytes(1099511627776.00), "1.00TiB")


class TestBuildCommand(unittest.TestCase):
    """Test case for the build_command method."""

    def setUp(self):
        self.url = "https://www.youtube.com/watch?v=aaaaaaaaaaa&list=AAAAAAAAAAA"

        self.options = ["-o", None, "-f", "mp4", "--ignore-config"]

        self.result = '{{ydl_bin}} -o "{{tmpl}}" -f mp4 --ignore-config "{url}"'.format(
            url=self.url
        )

    def run_tests(self, ydl_bin, tmpl):
        """Run the main test.

        Args:
            ydl_bin (str): Name of the youtube-dl binary
            tmpl (str): Youtube-dl output template

        """
        self.options[1] = tmpl  # Plug the template in our options

        result = self.result.format(ydl_bin=ydl_bin, tmpl=tmpl)

        self.assertEqual(utils.build_command(self.options, self.url, ydl_bin), result)

    def test_build_command_with_spaces_linux(self):
        tmpl = "/home/user/downloads/%(upload_date)s/%(id)s_%(playlist_id)s - %(format)s.%(ext)s"

        self.run_tests("youtube-dl", tmpl)

    def test_build_command_without_spaces_linux(self):
        tmpl = "/home/user/downloads/%(id)s.%(ext)s"

        self.run_tests("youtube-dl", tmpl)

    def test_build_command_with_spaces_windows(self):
        tmpl = "C:\\downloads\\%(upload_date)s\\%(id)s_%(playlist_id)s - %(format)s.%(ext)s"

        self.run_tests("youtube-dl.exe", tmpl)

    def test_build_command_without_spaces_windows(self):
        tmpl = "C:\\downloads\\%(id)s.%(ext)s"

        self.run_tests("youtube-dl.exe", tmpl)


class TestGetDefaultLang(unittest.TestCase):
    """Test case for the get_default_lang function."""

    @mock.patch("youtube_dl_gui.utils.locale_getdefaultlocale")
    def run_tests(self, ret_value, result, mock_getdefaultlocale):
        """Run the main test.

        Args:
            ret_value (tuple): Return tuple of the locale.getdefaultlocale module
            result (str): Result we want to see
            mock_getdefaultlocale (MagicMock): Mock object
        """
        mock_getdefaultlocale.return_value = ret_value
        lang = utils.get_default_lang()

        mock_getdefaultlocale.assert_called_once()
        self.assertEqual(lang, result)

    def test_get_default_lang(self):
        self.run_tests(("it_IT", "UTF-8"), "it_IT")

    def test_get_default_lang_none(self):
        self.run_tests((None, None), "en_US")

    def test_get_default_lang_empty(self):
        self.run_tests(("", ""), "en_US")


def main():
    unittest.main()


if __name__ == "__main__":
    main()
