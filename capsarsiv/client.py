"""Capsarsiv API istemcisi."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from capsarsiv.exceptions import (
    APIError,
    AuthenticationError,
    CapsArsivError,
    NotFoundError,
    RateLimitError,
)
from capsarsiv.models import Caps, Tag

if TYPE_CHECKING:
    pass

_BASE_URL = "https://capsarsiv.com"
_API_PREFIX = "/developer/v1"


class CapsArsiv:
    """Türkçe Caps Arşivi API istemcisi.

    Args:
        api_key: API anahtarı.  Verilmezse ``CAPSARSIV_API_KEY``
            ortam değişkeninden okunur.
        base_url: API temel URL'i (test amaçlı değiştirilebilir).
        timeout: HTTP istek zaman aşımı (saniye).

    Raises:
        CapsArsivError: API key bulunamazsa.

    Example::

        from capsarsiv import CapsArsiv

        with CapsArsiv() as client:
            caps_list = client.caps(q="futbol", sort="popular", limit=5)
            for c in caps_list:
                print(c.title, c.score)
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = _BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("CAPSARSIV_API_KEY")
        if not self._api_key:
            raise CapsArsivError(
                "API key gerekli. api_key parametresi ile verin "
                "veya CAPSARSIV_API_KEY ortam değişkenini ayarlayın."
            )

        from capsarsiv import __version__

        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "x-api-key": self._api_key,
                "User-Agent": f"capsarsiv-python/{__version__}",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    # -- Context manager --------------------------------------------------

    def __enter__(self) -> CapsArsiv:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def __repr__(self) -> str:
        masked = self._api_key[:8] + "…" if self._api_key else "None"
        return f"CapsArsiv(api_key='{masked}')"

    # -- Public API --------------------------------------------------------

    def caps(
        self,
        *,
        sort: str = "newest",
        q: str | None = None,
        tag: str | None = None,
        limit: int = 50,
    ) -> list[Caps]:
        """Capsleri listeler ve arar.

        Args:
            sort: Sıralama. ``newest``, ``popular``, ``trend`` veya ``random``.
            q: Arama metni (başlık, açıklama, tag, alternatif adlarda arar).
            tag: Tek bir tag'e göre filtrele.
            limit: Sonuç sayısı (1–100, varsayılan 50).

        Returns:
            Caps nesnelerinin listesi.
        """
        params: dict = {"sort": sort, "limit": min(max(limit, 1), 100)}
        if q:
            params["q"] = q
        if tag:
            params["tag"] = tag

        data = self._get(f"{_API_PREFIX}/caps", params=params)
        items = data.get("items", data) if isinstance(data, dict) else data
        return [Caps.from_dict(item) for item in items]

    def random(self, *, exclude: list[str] | None = None) -> Caps:
        """Rastgele tek bir caps döndürür.

        Args:
            exclude: Hariç tutulacak slug listesi.

        Returns:
            Rastgele bir Caps nesnesi.
        """
        params: dict = {}
        if exclude:
            params["exclude"] = ",".join(exclude)

        data = self._get(f"{_API_PREFIX}/caps/random", params=params)
        return Caps.from_dict(data)

    def get(self, slug: str) -> Caps:
        """Slug ile tek bir capsin detayını getirir.

        Args:
            slug: Capsin kalıcı kimliği.

        Returns:
            Caps nesnesi.

        Raises:
            NotFoundError: Caps bulunamazsa.
        """
        data = self._get(f"{_API_PREFIX}/caps/{slug}")
        return Caps.from_dict(data)

    def tags(self, *, limit: int = 40) -> list[Tag]:
        """En çok kullanılan tagleri listeler.

        Args:
            limit: Sonuç sayısı (1–200, varsayılan 40).

        Returns:
            Tag nesnelerinin listesi.
        """
        params: dict = {"limit": min(max(limit, 1), 200)}
        data = self._get(f"{_API_PREFIX}/tags", params=params)
        items = data.get("items", data) if isinstance(data, dict) else data
        return [Tag.from_dict(item) for item in items]

    def download(self, slug: str, *, directory: str | Path = ".") -> Path:
        """Bir capsin görselini indirir.

        Args:
            slug: Capsin slug'ı.
            directory: İndirilecek dizin (varsayılan: mevcut dizin).

        Returns:
            İndirilen dosyanın yolu.

        Raises:
            NotFoundError: Caps bulunamazsa.
        """
        caps = self.get(slug)
        image_url = caps.image_url

        response = httpx.get(image_url, follow_redirects=True, timeout=60.0)
        response.raise_for_status()

        # Dosya adını URL'den çıkar
        ext = Path(image_url).suffix or ".webp"
        filename = f"{caps.slug}{ext}"

        dest = Path(directory)
        dest.mkdir(parents=True, exist_ok=True)
        filepath = dest / filename

        filepath.write_bytes(response.content)
        return filepath

    def close(self) -> None:
        """HTTP bağlantısını kapatır."""
        self._client.close()

    # -- Private -----------------------------------------------------------

    def _get(self, path: str, *, params: dict | None = None) -> dict | list:
        """GET isteği gönderir ve yanıtı ayrıştırır."""
        try:
            response = self._client.get(path, params=params)
        except httpx.HTTPError as exc:
            raise CapsArsivError(f"HTTP isteği başarısız: {exc}") from exc

        if response.status_code == 401:
            raise AuthenticationError()
        if response.status_code == 404:
            raise NotFoundError()
        if response.status_code == 429:
            raise RateLimitError()
        if response.status_code >= 400:
            raise APIError(
                f"API hatası: {response.status_code} — {response.text}",
                status_code=response.status_code,
            )

        return response.json()
