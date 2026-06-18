"""Capsarsiv CLI testleri."""

import json

from click.testing import CliRunner
import pytest

from capsarsiv.cli import main


SAMPLE_CAPS_RESPONSE = {
    "items": [
        {
            "slug": "test-caps",
            "title": "Test Caps",
            "image_url": "https://assets.capsarsiv.com/caps/test-caps.webp",
            "image_version": 1717000000,
            "description": "Test açıklama",
            "type": "caps",
            "tags": ["test"],
            "aliases": [],
            "score": 42,
            "source_url": None,
            "view_count": 1280,
            "created_order": 137,
        }
    ]
}

SAMPLE_SINGLE_CAPS = {
    "slug": "test-caps",
    "title": "Test Caps",
    "image_url": "https://assets.capsarsiv.com/caps/test-caps.webp",
    "image_version": 1717000000,
    "description": "Test açıklama",
    "type": "caps",
    "tags": ["test"],
    "aliases": [],
    "score": 42,
    "source_url": None,
    "view_count": 1280,
    "created_order": 137,
}

SAMPLE_TAGS_RESPONSE = {
    "items": [
        {"name": "futbol", "count": 150},
        {"name": "siyaset", "count": 120},
    ]
}


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def api_key():
    return "capdv_test_key_1234567890"


class TestCLIHelp:
    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Türkçe Caps Arşivi" in result.output

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "capsarsiv" in result.output

    def test_caps_help(self, runner):
        result = runner.invoke(main, ["caps", "--help"])
        assert result.exit_code == 0
        assert "--sort" in result.output
        assert "--query" in result.output

    def test_random_help(self, runner):
        result = runner.invoke(main, ["random", "--help"])
        assert result.exit_code == 0

    def test_get_help(self, runner):
        result = runner.invoke(main, ["get", "--help"])
        assert result.exit_code == 0

    def test_tags_help(self, runner):
        result = runner.invoke(main, ["tags", "--help"])
        assert result.exit_code == 0

    def test_download_help(self, runner):
        result = runner.invoke(main, ["download", "--help"])
        assert result.exit_code == 0


class TestCLICapsCommand:
    def test_caps_json(self, runner, api_key, httpx_mock):
        httpx_mock.add_response(json=SAMPLE_CAPS_RESPONSE)
        result = runner.invoke(
            main, ["--api-key", api_key, "--json", "caps", "--limit", "1"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["slug"] == "test-caps"

    def test_caps_table(self, runner, api_key, httpx_mock):
        httpx_mock.add_response(json=SAMPLE_CAPS_RESPONSE)
        result = runner.invoke(main, ["--api-key", api_key, "caps", "--limit", "1"])
        assert result.exit_code == 0
        assert "Test Caps" in result.output


class TestCLIRandomCommand:
    def test_random_json(self, runner, api_key, httpx_mock):
        httpx_mock.add_response(json=SAMPLE_SINGLE_CAPS)
        result = runner.invoke(main, ["--api-key", api_key, "--json", "random"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["slug"] == "test-caps"


class TestCLIGetCommand:
    def test_get_json(self, runner, api_key, httpx_mock):
        httpx_mock.add_response(json=SAMPLE_SINGLE_CAPS)
        result = runner.invoke(
            main, ["--api-key", api_key, "--json", "get", "test-caps"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["title"] == "Test Caps"


class TestCLITagsCommand:
    def test_tags_json(self, runner, api_key, httpx_mock):
        httpx_mock.add_response(json=SAMPLE_TAGS_RESPONSE)
        result = runner.invoke(
            main, ["--api-key", api_key, "--json", "tags", "--limit", "2"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        assert data[0]["name"] == "futbol"


class TestCLINoApiKey:
    def test_no_key_exits(self, runner, monkeypatch):
        monkeypatch.delenv("CAPSARSIV_API_KEY", raising=False)
        result = runner.invoke(main, ["caps"])
        assert result.exit_code == 1
