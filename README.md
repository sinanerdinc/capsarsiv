# capsarsiv

Türkçe Caps Arşivi Python SDK ve CLI aracı.

[![PyPI](https://img.shields.io/pypi/v/capsarsiv)](https://pypi.org/project/capsarsiv/)
[![Python](https://img.shields.io/pypi/pyversions/capsarsiv)](https://pypi.org/project/capsarsiv/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Türkçe Caps Arşivi](https://capsarsiv.com) API'sine erişmek için Python SDK ve komut satırı aracı.

## Kurulum

```bash
pip install capsarsiv
```

## API Key

API key almak için:

1. [capsarsiv.com/uyelik](https://capsarsiv.com/uyelik) sayfasından giriş yapın.
2. Hesap altındaki **developer API** bölümünde **API key oluştur**'a tıklayın.
3. Key yalnızca oluşturulduğu anda bir kez gösterilir; güvenli bir yerde saklayın.

Key'inizi ortam değişkeni olarak ayarlayın:

```bash
export CAPSARSIV_API_KEY="senin_api_keyin"
```

## Python SDK

```python
from capsarsiv import CapsArsiv

# Context manager ile kullanım (önerilir)
with CapsArsiv() as client:
    # Capsleri listele
    caps_list = client.caps(sort="popular", limit=10)
    for c in caps_list:
        print(f"{c.title} — puan: {c.score}")

    # Arama yap
    results = client.caps(q="futbol", sort="popular")

    # Tag ile filtrele
    spor_caps = client.caps(tag="spor", limit=5)

    # Rastgele caps getir
    rastgele = client.random()
    print(f"Rastgele: {rastgele.title}")

    # Slug ile detay getir
    caps = client.get("ornek-caps")
    print(caps.image_url)

    # Tagleri listele
    tags = client.tags(limit=20)
    for t in tags:
        print(f"#{t.name} ({t.count} caps)")

    # Caps görselini indir
    filepath = client.download("ornek-caps", directory="./caps")
    print(f"İndirildi: {filepath}")
```

### API Key'i parametre olarak verme

```python
client = CapsArsiv(api_key="senin_api_keyin")
```

## CLI Kullanımı

```bash
# Capsleri listele
capsarsiv caps
capsarsiv caps --sort popular --limit 10
capsarsiv caps --query futbol
capsarsiv caps --tag spor

# Rastgele caps
capsarsiv random

# Caps detayı
capsarsiv get ornek-caps

# Tagleri listele
capsarsiv tags
capsarsiv tags --limit 20

# Caps görselini indir
capsarsiv download ornek-caps
capsarsiv download ornek-caps -o ./caps/

# JSON çıktı
capsarsiv --json caps --limit 5
capsarsiv --json random

# Yardım
capsarsiv --help
capsarsiv caps --help
```

### CLI ile API Key

```bash
# Ortam değişkeni (önerilir)
export CAPSARSIV_API_KEY="senin_api_keyin"
capsarsiv caps

# Parametre olarak
capsarsiv --api-key "senin_api_keyin" caps
```

## Hata Yönetimi

```python
from capsarsiv import CapsArsiv, NotFoundError, RateLimitError, AuthenticationError

with CapsArsiv() as client:
    try:
        caps = client.get("olmayan-caps")
    except NotFoundError:
        print("Caps bulunamadı!")
    except RateLimitError:
        print("İstek limiti aşıldı, lütfen bekleyin.")
    except AuthenticationError:
        print("API key geçersiz!")
```

## API Limitleri

- Dakikada en fazla **60** istek
- Aylık **1000** istek (key başına)

## Lisans

MIT — detaylar için [LICENSE](LICENSE) dosyasına bakın.
