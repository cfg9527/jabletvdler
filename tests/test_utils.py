import pytest  # noqa: F401

from jabletv.utils import sanitize_filename, rotating_ua


class TestSanitizeFilename:
    def test_removes_special_chars(self) -> None:
        assert sanitize_filename("hello/world*test") == "helloworldtest"

    def test_keeps_alphanumeric_and_dashes(self) -> None:
        assert sanitize_filename("abc-123_xyz.mp4") == "abc-123_xyz.mp4"

    def test_replaces_japanese_punctuation(self) -> None:
        result = sanitize_filename("電撃復活！谷原希美？")
        assert result == "電撃復活!谷原希美?"

    def test_replaces_brackets(self) -> None:
        result = sanitize_filename("「テスト」")
        assert result == "[テスト]"

    def test_replaces_dots(self) -> None:
        result = sanitize_filename("熟女への本気—。")
        assert result == "熟女への本気—。"

    def test_truncates_to_80_chars(self) -> None:
        long_name = "a" * 100
        result = sanitize_filename(long_name)
        assert len(result) == 80

    def test_empty_returns_untitled(self) -> None:
        assert sanitize_filename("") == "untitled"

    def test_colon_preserved(self) -> None:
        result = sanitize_filename("test:file")
        assert ":" in result

    def test_keeps_japanese_chars(self) -> None:
        result = sanitize_filename("吉永塔子")
        assert result == "吉永塔子"


class TestRotatingUA:
    def test_returns_string(self) -> None:
        ua = rotating_ua()
        assert isinstance(ua, str)
        assert len(ua) > 10

    def test_returns_varied(self) -> None:
        uas = {rotating_ua() for _ in range(20)}
        assert len(uas) >= 2
