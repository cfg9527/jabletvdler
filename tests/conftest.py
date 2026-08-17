from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def roe505_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "roe-505.html").read_text(encoding="utf-8")


@pytest.fixture
def master_m3u8(fixtures_dir: Path) -> str:
    return (fixtures_dir / "master.m3u8").read_text(encoding="utf-8")


@pytest.fixture
def unencrypted_m3u8(fixtures_dir: Path) -> str:
    return (fixtures_dir / "variant_unencrypted.m3u8").read_text(encoding="utf-8")


@pytest.fixture
def encrypted_m3u8(fixtures_dir: Path) -> str:
    return (fixtures_dir / "variant_encrypted.m3u8").read_text(encoding="utf-8")
