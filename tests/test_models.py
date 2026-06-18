"""Capsarsiv model testleri."""

from capsarsiv.models import Caps, Tag


SAMPLE_CAPS_DATA = {
    "slug": "test-caps",
    "title": "Test Caps",
    "image_url": "https://assets.capsarsiv.com/caps/test-caps.webp",
    "image_version": 1717000000,
    "description": "Test açıklama",
    "type": "caps",
    "tags": ["test", "örnek"],
    "aliases": ["test caps alt"],
    "score": 42,
    "source_url": "https://example.com/source.jpg",
    "view_count": 1280,
    "created_order": 137,
}

SAMPLE_CAPS_MINIMAL = {
    "slug": "minimal",
    "title": "Minimal Caps",
    "image_url": "https://assets.capsarsiv.com/caps/minimal.webp",
}

SAMPLE_TAG_DATA = {"name": "futbol", "count": 150}


class TestCaps:
    def test_from_dict_full(self):
        caps = Caps.from_dict(SAMPLE_CAPS_DATA)
        assert caps.slug == "test-caps"
        assert caps.title == "Test Caps"
        assert caps.image_url == "https://assets.capsarsiv.com/caps/test-caps.webp"
        assert caps.image_version == 1717000000
        assert caps.description == "Test açıklama"
        assert caps.type == "caps"
        assert caps.tags == ["test", "örnek"]
        assert caps.aliases == ["test caps alt"]
        assert caps.score == 42
        assert caps.source_url == "https://example.com/source.jpg"
        assert caps.view_count == 1280
        assert caps.created_order == 137

    def test_from_dict_minimal(self):
        caps = Caps.from_dict(SAMPLE_CAPS_MINIMAL)
        assert caps.slug == "minimal"
        assert caps.title == "Minimal Caps"
        assert caps.tags == []
        assert caps.aliases == []
        assert caps.score == 0
        assert caps.source_url is None
        assert caps.view_count == 0

    def test_url_property(self):
        caps = Caps.from_dict(SAMPLE_CAPS_DATA)
        assert caps.url == "https://capsarsiv.com/c/test-caps"

    def test_to_dict(self):
        caps = Caps.from_dict(SAMPLE_CAPS_DATA)
        d = caps.to_dict()
        assert d["slug"] == "test-caps"
        assert d["title"] == "Test Caps"
        assert d["url"] == "https://capsarsiv.com/c/test-caps"
        assert isinstance(d["tags"], list)

    def test_frozen(self):
        caps = Caps.from_dict(SAMPLE_CAPS_DATA)
        try:
            caps.slug = "changed"  # type: ignore[misc]
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass


class TestTag:
    def test_from_dict(self):
        tag = Tag.from_dict(SAMPLE_TAG_DATA)
        assert tag.name == "futbol"
        assert tag.count == 150

    def test_to_dict(self):
        tag = Tag.from_dict(SAMPLE_TAG_DATA)
        d = tag.to_dict()
        assert d == {"name": "futbol", "count": 150}

    def test_frozen(self):
        tag = Tag.from_dict(SAMPLE_TAG_DATA)
        try:
            tag.name = "changed"  # type: ignore[misc]
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass
