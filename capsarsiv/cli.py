"""Capsarsiv CLI — Türkçe Caps Arşivi komut satırı aracı."""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from capsarsiv import __version__
from capsarsiv.client import CapsArsiv
from capsarsiv.exceptions import CapsArsivError

console = Console()
err_console = Console(stderr=True)


def _get_client(api_key: str | None) -> CapsArsiv:
    """API istemcisi oluşturur, hata durumunda anlaşılır mesaj verir."""
    try:
        return CapsArsiv(api_key=api_key)
    except CapsArsivError as exc:
        err_console.print(f"[bold red]Hata:[/] {exc}")
        err_console.print(
            "\n[dim]API key'inizi şu yollardan biriyle sağlayın:[/]\n"
            "  1. [cyan]--api-key[/] parametresi\n"
            "  2. [cyan]CAPSARSIV_API_KEY[/] ortam değişkeni\n"
            "  3. Proje dizinindeki [cyan].env[/] dosyası"
        )
        raise SystemExit(1) from exc


def _print_caps_table(caps_list: list, title: str = "Capsler") -> None:
    """Caps listesini zengin tablo olarak yazdırır."""
    table = Table(title=title, show_lines=True, title_style="bold magenta")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Başlık", style="bold cyan", max_width=30)
    table.add_column("Slug", style="green", max_width=25)
    table.add_column("Tür", style="yellow", width=8)
    table.add_column("Puan", style="bold", justify="right", width=6)
    table.add_column("Görüntülenme", justify="right", width=12)
    table.add_column("Tagler", style="dim", max_width=30)

    for i, c in enumerate(caps_list, 1):
        tags_str = ", ".join(c.tags[:5])
        if len(c.tags) > 5:
            tags_str += f" (+{len(c.tags) - 5})"
        table.add_row(
            str(i),
            c.title,
            c.slug,
            c.type,
            str(c.score),
            f"{c.view_count:,}",
            tags_str,
        )

    console.print(table)


def _print_caps_detail(c) -> None:
    """Tek bir caps detayını panel olarak yazdırır."""
    tags_str = ", ".join(c.tags) if c.tags else "—"
    aliases_str = ", ".join(c.aliases) if c.aliases else "—"

    content = Text()
    content.append("Başlık:        ", style="bold")
    content.append(f"{c.title}\n")
    content.append("Slug:          ", style="bold")
    content.append(f"{c.slug}\n")
    content.append("Tür:           ", style="bold")
    content.append(f"{c.type}\n")
    content.append("Açıklama:      ", style="bold")
    content.append(f"{c.description or '—'}\n")
    content.append("Puan:          ", style="bold")
    content.append(f"{c.score}\n")
    content.append("Görüntülenme:  ", style="bold")
    content.append(f"{c.view_count:,}\n")
    content.append("Tagler:        ", style="bold")
    content.append(f"{tags_str}\n")
    content.append("Alternatifler: ", style="bold")
    content.append(f"{aliases_str}\n")
    content.append("Görsel:        ", style="bold")
    content.append(f"{c.image_url}\n", style="underline blue")
    content.append("Web:           ", style="bold")
    content.append(f"{c.url}\n", style="underline blue")
    if c.source_url:
        content.append("Kaynak:        ", style="bold")
        content.append(f"{c.source_url}\n", style="underline blue")

    console.print(Panel(content, title=f"[bold magenta]{c.title}[/]", border_style="cyan"))


def _print_tags_table(tags_list: list) -> None:
    """Tag listesini tablo olarak yazdırır."""
    table = Table(title="Tagler", show_lines=False, title_style="bold magenta")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Tag", style="bold cyan", min_width=20)
    table.add_column("Caps Sayısı", style="green", justify="right", width=12)

    for i, t in enumerate(tags_list, 1):
        table.add_row(str(i), t.name, f"{t.count:,}")

    console.print(table)


# -- CLI Grubu ------------------------------------------------------------


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-v", "--version", prog_name="capsarsiv")
@click.option(
    "--api-key",
    envvar="CAPSARSIV_API_KEY",
    help="API anahtarı (veya CAPSARSIV_API_KEY ortam değişkeni).",
)
@click.option("--json", "output_json", is_flag=True, help="Çıktıyı JSON olarak ver.")
@click.pass_context
def main(ctx: click.Context, api_key: str | None, output_json: bool) -> None:
    """Türkçe Caps Arşivi CLI aracı.

    Capsleri listele, ara, rastgele getir ve indir.
    """
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["json"] = output_json


# -- caps komutu -----------------------------------------------------------


@main.command()
@click.option(
    "-s", "--sort",
    type=click.Choice(["newest", "popular", "trend", "random"], case_sensitive=False),
    default="newest",
    help="Sıralama (varsayılan: newest).",
)
@click.option("-q", "--query", default=None, help="Arama metni.")
@click.option("-t", "--tag", default=None, help="Tag filtresi.")
@click.option(
    "-l", "--limit",
    type=click.IntRange(1, 100),
    default=50,
    help="Sonuç sayısı (1–100, varsayılan: 50).",
)
@click.pass_context
def caps(ctx: click.Context, sort: str, query: str | None, tag: str | None, limit: int) -> None:
    """Capsleri listele ve ara."""
    client = _get_client(ctx.obj["api_key"])
    try:
        result = client.caps(sort=sort, q=query, tag=tag, limit=limit)

        if not result:
            console.print("[yellow]Sonuç bulunamadı.[/]")
            return

        if ctx.obj["json"]:
            click.echo(json.dumps([c.to_dict() for c in result], ensure_ascii=False, indent=2))
        else:
            title = "Capsler"
            if query:
                title += f" — arama: '{query}'"
            if tag:
                title += f" — tag: #{tag}"
            _print_caps_table(result, title=title)
    except CapsArsivError as exc:
        err_console.print(f"[bold red]Hata:[/] {exc}")
        raise SystemExit(1) from exc
    finally:
        client.close()


# -- random komutu ---------------------------------------------------------


@main.command()
@click.option(
    "-e", "--exclude",
    default=None,
    help="Hariç tutulacak slug'lar (virgülle ayır).",
)
@click.pass_context
def random(ctx: click.Context, exclude: str | None) -> None:
    """Rastgele bir caps getir."""
    client = _get_client(ctx.obj["api_key"])
    try:
        exclude_list = [s.strip() for s in exclude.split(",")] if exclude else None
        result = client.random(exclude=exclude_list)

        if ctx.obj["json"]:
            click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            _print_caps_detail(result)
    except CapsArsivError as exc:
        err_console.print(f"[bold red]Hata:[/] {exc}")
        raise SystemExit(1) from exc
    finally:
        client.close()


# -- get komutu ------------------------------------------------------------


@main.command()
@click.argument("slug")
@click.pass_context
def get(ctx: click.Context, slug: str) -> None:
    """Slug ile caps detayı getir."""
    client = _get_client(ctx.obj["api_key"])
    try:
        result = client.get(slug)

        if ctx.obj["json"]:
            click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            _print_caps_detail(result)
    except CapsArsivError as exc:
        err_console.print(f"[bold red]Hata:[/] {exc}")
        raise SystemExit(1) from exc
    finally:
        client.close()


# -- tags komutu -----------------------------------------------------------


@main.command()
@click.option(
    "-l", "--limit",
    type=click.IntRange(1, 200),
    default=40,
    help="Sonuç sayısı (1–200, varsayılan: 40).",
)
@click.pass_context
def tags(ctx: click.Context, limit: int) -> None:
    """Tagleri listele."""
    client = _get_client(ctx.obj["api_key"])
    try:
        result = client.tags(limit=limit)

        if not result:
            console.print("[yellow]Tag bulunamadı.[/]")
            return

        if ctx.obj["json"]:
            click.echo(json.dumps([t.to_dict() for t in result], ensure_ascii=False, indent=2))
        else:
            _print_tags_table(result)
    except CapsArsivError as exc:
        err_console.print(f"[bold red]Hata:[/] {exc}")
        raise SystemExit(1) from exc
    finally:
        client.close()


# -- download komutu -------------------------------------------------------


@main.command()
@click.argument("slug")
@click.option(
    "-o", "--output",
    type=click.Path(),
    default=".",
    help="İndirilecek dizin (varsayılan: mevcut dizin).",
)
@click.pass_context
def download(ctx: click.Context, slug: str, output: str) -> None:
    """Caps görselini indir."""
    client = _get_client(ctx.obj["api_key"])
    try:
        filepath = client.download(slug, directory=output)

        if ctx.obj["json"]:
            click.echo(json.dumps({"path": str(filepath)}, ensure_ascii=False))
        else:
            console.print(f"[bold green]✓[/] İndirildi: [cyan]{filepath}[/]")
    except CapsArsivError as exc:
        err_console.print(f"[bold red]Hata:[/] {exc}")
        raise SystemExit(1) from exc
    finally:
        client.close()


if __name__ == "__main__":
    main()
