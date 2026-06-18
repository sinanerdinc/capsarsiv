"""Capsarsiv API veri modelleri."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Caps:
    """Tek bir caps kaydını temsil eder.

    Attributes:
        slug: Capsin kalıcı kimliği (URL'de kullanılır).
        title: Caps başlığı.
        image_url: Görselin tam URL'i.
        image_version: Önbellek kırma için görsel sürümü.
        description: Açıklama metni.
        type: Caps türü.
        tags: Tag listesi.
        aliases: Alternatif adlar.
        score: Toplam puan.
        source_url: Kaynak görsel URL'i (varsa).
        view_count: Görüntülenme sayısı.
        created_order: Eklenme sırası.
    """

    slug: str
    title: str
    image_url: str
    image_version: int
    description: str
    type: str
    tags: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    score: int = 0
    source_url: str | None = None
    view_count: int = 0
    created_order: int = 0

    @property
    def url(self) -> str:
        """Capsin web sayfasının URL'ini döndürür."""
        return f"https://capsarsiv.com/c/{self.slug}"

    @classmethod
    def from_dict(cls, data: dict) -> Caps:
        """API yanıtındaki dict'ten Caps nesnesi oluşturur."""
        return cls(
            slug=data["slug"],
            title=data["title"],
            image_url=data["image_url"],
            image_version=data.get("image_version", 0),
            description=data.get("description", ""),
            type=data.get("type", ""),
            tags=data.get("tags", []),
            aliases=data.get("aliases", []),
            score=data.get("score", 0),
            source_url=data.get("source_url"),
            view_count=data.get("view_count", 0),
            created_order=data.get("created_order", 0),
        )

    def to_dict(self) -> dict:
        """Caps nesnesini dict'e dönüştürür."""
        return {
            "slug": self.slug,
            "title": self.title,
            "image_url": self.image_url,
            "image_version": self.image_version,
            "description": self.description,
            "type": self.type,
            "tags": list(self.tags),
            "aliases": list(self.aliases),
            "score": self.score,
            "source_url": self.source_url,
            "view_count": self.view_count,
            "created_order": self.created_order,
            "url": self.url,
        }


@dataclass(frozen=True)
class Tag:
    """Bir tag kaydını temsil eder.

    Attributes:
        name: Tag adı.
        count: Bu tag'e sahip caps sayısı.
    """

    name: str
    count: int

    @classmethod
    def from_dict(cls, data: dict) -> Tag:
        """API yanıtındaki dict'ten Tag nesnesi oluşturur."""
        return cls(name=data["name"], count=data["count"])

    def to_dict(self) -> dict:
        """Tag nesnesini dict'e dönüştürür."""
        return {"name": self.name, "count": self.count}
