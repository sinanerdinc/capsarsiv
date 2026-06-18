"""Capsarsiv API hata sınıfları."""


class CapsArsivError(Exception):
    """Tüm capsarsiv hatalarının temel sınıfı."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(CapsArsivError):
    """API key eksik veya geçersiz (HTTP 401)."""

    def __init__(self, message: str = "API key eksik veya geçersiz."):
        super().__init__(message, status_code=401)


class NotFoundError(CapsArsivError):
    """İstenen kaynak bulunamadı (HTTP 404)."""

    def __init__(self, message: str = "İstenen caps bulunamadı."):
        super().__init__(message, status_code=404)


class RateLimitError(CapsArsivError):
    """İstek limiti aşıldı (HTTP 429)."""

    def __init__(
        self, message: str = "İstek limiti aşıldı. Lütfen daha sonra tekrar deneyin."
    ):
        super().__init__(message, status_code=429)


class APIError(CapsArsivError):
    """Beklenmeyen API hatası."""

    def __init__(self, message: str, status_code: int):
        super().__init__(message, status_code=status_code)
