"""Capsarsiv client testleri."""

import os

import httpx
import pytest

from capsarsiv.client import CapsArsiv
from capsarsiv.exceptions import (
    AuthenticationError,
    CapsArsivError,
    NotFoundError,
    RateLimitError,
)
from capsarsiv.models import Caps, Tag


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
def api_key():
    return "capdv_test_key_1234567890"


@pytest.fixture()
def client(api_key, httpx_mock):
    """Test client oluşturur."""
    c = CapsArsiv(api_key=api_key)
    yield c
    c.close()


class TestClientInit:
    def test_init_with_api_key(self, api_key):
        c = CapsArsiv(api_key=api_key)
        assert c._api_key == api_key
        c.close()

    def test_init_from_env(self, monkeypatch, api_key):
        monkeypatch.setenv("CAPSARSIV_API_KEY", api_key)
        c = CapsArsiv()
        assert c._api_key == api_key
        c.close()

    def test_init_no_key_raises(self, monkeypatch):
        monkeypatch.delenv("CAPSARSIV_API_KEY", raising=False)
        with pytest.raises(CapsArsivError, match="API key gerekli"):
            CapsArsiv()

    def test_context_manager(self, api_key):
        with CapsArsiv(api_key=api_key) as c:
            assert c._api_key == api_key

    def test_repr(self, api_key):
        c = CapsArsiv(api_key=api_key)
        assert "capdv_te…" in repr(c)
        c.close()


class TestCapsEndpoint:
    def test_list_caps(self, client, httpx_mock):
        httpx_mock.add_response(
            url=httpx.URL("https://capsarsiv.com/developer/v1/caps?sort=newest&limit=50"),
            json=SAMPLE_CAPS_RESPONSE,
        )
        result = client.caps()
        assert len(result) == 1
        assert isinstance(result[0], Caps)
        assert result[0].slug == "test-caps"

    def test_search_caps(self, client, httpx_mock):
        httpx_mock.add_response(
            url=httpx.URL("https://capsarsiv.com/developer/v1/caps?sort=newest&limit=50&q=futbol"),
            json=SAMPLE_CAPS_RESPONSE,
        )
        result = client.caps(q="futbol")
        assert len(result) == 1

    def test_caps_with_tag(self, client, httpx_mock):
        httpx_mock.add_response(
            url=httpx.URL("https://capsarsiv.com/developer/v1/caps?sort=popular&limit=10&tag=spor"),
            json=SAMPLE_CAPS_RESPONSE,
        )
        result = client.caps(sort="popular", tag="spor", limit=10)
        assert len(result) == 1

    def test_limit_clamped(self, client, httpx_mock):
        httpx_mock.add_response(json=SAMPLE_CAPS_RESPONSE)
        # limit > 100 should be clamped to 100
        client.caps(limit=999)
        request = httpx_mock.get_request()
        assert request.url.params["limit"] == "100"


class TestRandomEndpoint:
    def test_random(self, client, httpx_mock):
        httpx_mock.add_response(
            url=httpx.URL("https://capsarsiv.com/developer/v1/caps/random"),
            json=SAMPLE_SINGLE_CAPS,
        )
        result = client.random()
        assert isinstance(result, Caps)
        assert result.slug == "test-caps"

    def test_random_with_exclude(self, client, httpx_mock):
        httpx_mock.add_response(json=SAMPLE_SINGLE_CAPS)
        client.random(exclude=["caps-1", "caps-2"])
        request = httpx_mock.get_request()
        assert request.url.params["exclude"] == "caps-1,caps-2"


class TestGetEndpoint:
    def test_get_caps(self, client, httpx_mock):
        httpx_mock.add_response(
            url=httpx.URL("https://capsarsiv.com/developer/v1/caps/test-caps"),
            json=SAMPLE_SINGLE_CAPS,
        )
        result = client.get("test-caps")
        assert isinstance(result, Caps)
        assert result.title == "Test Caps"


class TestTagsEndpoint:
    def test_list_tags(self, client, httpx_mock):
        httpx_mock.add_response(
            url=httpx.URL("https://capsarsiv.com/developer/v1/tags?limit=40"),
            json=SAMPLE_TAGS_RESPONSE,
        )
        result = client.tags()
        assert len(result) == 2
        assert isinstance(result[0], Tag)
        assert result[0].name == "futbol"


class TestErrorHandling:
    def test_401_raises_auth_error(self, client, httpx_mock):
        httpx_mock.add_response(status_code=401)
        with pytest.raises(AuthenticationError):
            client.caps()

    def test_404_raises_not_found(self, client, httpx_mock):
        httpx_mock.add_response(status_code=404)
        with pytest.raises(NotFoundError):
            client.get("olmayan-caps")

    def test_429_raises_rate_limit(self, client, httpx_mock):
        httpx_mock.add_response(status_code=429)
        with pytest.raises(RateLimitError):
            client.caps()

    def test_500_raises_api_error(self, client, httpx_mock):
        httpx_mock.add_response(status_code=500, text="Internal Server Error")
        from capsarsiv.exceptions import APIError

        with pytest.raises(APIError) as exc_info:
            client.caps()
        assert exc_info.value.status_code == 500
