import json
from pathlib import Path

from jabletv.metadata_store import (
    load_all_metadata,
    save_metadata,
    search_metadata,
)
from jabletv.scraper import VideoInfo


class TestSaveMetadata:
    def test_saves_json_file(self, tmp_path: Path) -> None:
        v = VideoInfo(code="ABC-123", title="Test", tags=["tag1"], actresses=["A"])
        path = save_metadata(v, str(tmp_path))
        assert path.exists()
        assert path.name == "ABC-123.json"

    def test_contains_version(self, tmp_path: Path) -> None:
        v = VideoInfo(code="ABC-123")
        path = save_metadata(v, str(tmp_path))
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["_version"] == 1

    def test_contains_video_fields(self, tmp_path: Path) -> None:
        v = VideoInfo(code="X-001", title="Hello", views=42, tags=["a", "b"])
        path = save_metadata(v, str(tmp_path))
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["code"] == "X-001"
        assert data["title"] == "Hello"
        assert data["views"] == 42
        assert data["tags"] == ["a", "b"]

    def test_creates_jable_db_dir(self, tmp_path: Path) -> None:
        v = VideoInfo(code="ABC-123")
        path = save_metadata(v, str(tmp_path))
        assert path.parent.name == "jable_db"

    def test_overwrites_existing(self, tmp_path: Path) -> None:
        v1 = VideoInfo(code="ABC-123", title="First")
        save_metadata(v1, str(tmp_path))
        v2 = VideoInfo(code="ABC-123", title="Second")
        save_metadata(v2, str(tmp_path))
        entries = load_all_metadata(str(tmp_path))
        assert len(entries) == 1
        assert entries[0]["title"] == "Second"


class TestLoadAllMetadata:
    def test_returns_empty_when_no_db_dir(self, tmp_path: Path) -> None:
        assert load_all_metadata(str(tmp_path)) == []

    def test_returns_empty_when_db_dir_empty(self, tmp_path: Path) -> None:
        (tmp_path / "jable_db").mkdir()
        assert load_all_metadata(str(tmp_path)) == []

    def test_loads_single_entry(self, tmp_path: Path) -> None:
        v = VideoInfo(code="ABC-123", title="Test")
        save_metadata(v, str(tmp_path))
        entries = load_all_metadata(str(tmp_path))
        assert len(entries) == 1
        assert entries[0]["code"] == "ABC-123"
        assert entries[0]["title"] == "Test"

    def test_loads_multiple_entries(self, tmp_path: Path) -> None:
        save_metadata(VideoInfo(code="A", title="One"), str(tmp_path))
        save_metadata(VideoInfo(code="B", title="Two"), str(tmp_path))
        entries = load_all_metadata(str(tmp_path))
        assert len(entries) == 2

    def test_strips_version_field(self, tmp_path: Path) -> None:
        save_metadata(VideoInfo(code="XYZ"), str(tmp_path))
        entries = load_all_metadata(str(tmp_path))
        assert "_version" not in entries[0]

    def test_skips_corrupt_json(self, tmp_path: Path) -> None:
        db_dir = tmp_path / "jable_db"
        db_dir.mkdir()
        (db_dir / "good.json").write_text(json.dumps({"code": "OK"}), encoding="utf-8")
        (db_dir / "bad.json").write_text("not json", encoding="utf-8")
        entries = load_all_metadata(str(tmp_path))
        assert len(entries) == 1
        assert entries[0]["code"] == "OK"


class TestSearchMetadata:
    def test_empty_query_returns_all(self) -> None:
        entries = [{"code": "A"}, {"code": "B"}]
        assert search_metadata(entries, "") == entries

    def test_search_by_code(self) -> None:
        entries = [{"code": "ABC-123"}, {"code": "XYZ-456"}]
        result = search_metadata(entries, "abc")
        assert len(result) == 1
        assert result[0]["code"] == "ABC-123"

    def test_search_by_title(self) -> None:
        entries = [{"code": "A", "title": "Hello World"}, {"code": "B", "title": "Goodbye"}]
        result = search_metadata(entries, "hello")
        assert len(result) == 1
        assert result[0]["code"] == "A"

    def test_search_by_tag(self) -> None:
        entries = [
            {"code": "A", "tags": ["jav", "hd"]},
            {"code": "B", "tags": ["vr"]},
        ]
        result = search_metadata(entries, "hd")
        assert len(result) == 1
        assert result[0]["code"] == "A"

    def test_search_by_actress(self) -> None:
        entries = [
            {"code": "A", "actresses": ["佐佐波", "小野"]},
            {"code": "B", "actresses": ["涼森"]},
        ]
        result = search_metadata(entries, "小野")
        assert len(result) == 1
        assert result[0]["code"] == "A"

    def test_search_by_category(self) -> None:
        entries = [
            {"code": "A", "category": "高清"},
            {"code": "B", "category": "普通"},
        ]
        result = search_metadata(entries, "高清")
        assert len(result) == 1
        assert result[0]["code"] == "A"

    def test_search_case_insensitive(self) -> None:
        entries = [{"code": "ABC-123"}]
        assert len(search_metadata(entries, "abc")) == 1
        assert len(search_metadata(entries, "ABC")) == 1


class TestTolerantReader:
    def test_ignores_unknown_keys(self, tmp_path: Path) -> None:
        db_dir = tmp_path / "jable_db"
        db_dir.mkdir()
        (db_dir / "test.json").write_text(
            json.dumps({"code": "X", "unknown_field": "should be ignored", "_version": 1}),
            encoding="utf-8",
        )
        entries = load_all_metadata(str(tmp_path))
        assert len(entries) == 1
        assert entries[0]["code"] == "X"
