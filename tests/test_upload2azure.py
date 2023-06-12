import pytest
from freezegun import freeze_time

from src.upload2azure import getLogger, upload_data_directory, zip_dir


@pytest.fixture(scope="session")
def template_dir(tmp_path_factory):
    template_dir = tmp_path_factory.mktemp("test_dir")
    zip_dir = template_dir / "07062023"
    zip_dir.mkdir()
    (zip_dir / "test1.txt").write_text("test, line, one", "utf-8")
    (zip_dir / "test2.txt").write_text("test, line, two", "utf-8")
    return template_dir


def test_getLogger():
    assert getLogger()


def test_zip_dir(template_dir):
    assert template_dir.exists()
    assert (template_dir / "07062023").exists()
    assert (template_dir / "07062023" / "test1.txt").exists()
    assert (template_dir / "07062023" / "test2.txt").exists()
    logger = getLogger()
    zip_dir(template_dir / "07062023", logger)
    assert (template_dir / "07062023.zip").exists()


@freeze_time("2023-06-08")
def test_upload_data_directory(template_dir):
    assert template_dir.exists()
    assert (template_dir / "07062023").exists()
    assert (template_dir / "07062023" / "test1.txt").exists()
    assert (template_dir / "07062023" / "test2.txt").exists()
    logger = getLogger()
    zip_dir(template_dir / "07062023", logger)
    assert (template_dir / "07062023.zip").exists()
    assert upload_data_directory(template_dir) is None
