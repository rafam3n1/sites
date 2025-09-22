#!/usr/bin/env python3
"""Generate static landing pages for client demos using a JSON configuration."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import OrderedDict
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates" / "base"
OUTPUT_ROOT = ROOT / "sites"
ASSETS_DIR_NAME = "assets"


def slugify(value: str, *, default: str = "site") -> str:
    """Return a filesystem-safe slug derived from *value*."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or default


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / ASSETS_DIR_NAME).mkdir(exist_ok=True)


def read_config(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("A configuração deve ser um objeto JSON.")
    return data


def copy_logo(logo_path: Optional[str], output_dir: Path) -> Optional[str]:
    if not logo_path:
        return None

    src = (ROOT / logo_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"Logo não encontrada: {logo_path}")

    assets_dir = output_dir / ASSETS_DIR_NAME
    assets_dir.mkdir(exist_ok=True)
    destination = assets_dir / src.name
    shutil.copy2(src, destination)
    return f"{ASSETS_DIR_NAME}/{src.name}"


def html_paragraphs(text: str) -> str:
    paragraphs = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        escaped = escape(block).replace("\n", "<br>")
        paragraphs.append(f"<p>{escaped}</p>")
    return "".join(paragraphs)


def html_list(items: Iterable[str], *, cls: str = "") -> str:
    class_attr = f' class="{cls}"' if cls else ""
    escaped_items = (f"<li>{escape(item)}</li>" for item in items if str(item).strip())
    return f"<ul{class_attr}>" + "".join(escaped_items) + "</ul>"


def build_nav(sections: List[Dict[str, str]], *, site_name: str, logo: Optional[str]) -> str:
    links = "".join(
        f'<a href="#{escape(section["id"])}">{escape(section["label"])}</a>' for section in sections
    )

    logo_html = (
        f'<img src="{escape(logo)}" alt="{escape(site_name)}" class="brand-logo">'
        if logo
        else f"<span class=\"brand-name\">{escape(site_name)}</span>"
    )
    return f"""
    <nav class="top-nav">
        <div class="brand">
            {logo_html}
        </div>
        <div class="nav-links">
            {links}
        </div>
    </nav>
    """


def build_hero(data: Dict[str, Any], *, site: Dict[str, Any], logo: Optional[str]) -> str:
    headline = escape(data.get("headline", site.get("tagline", site.get("name", ""))))
    subheadline = escape(data.get("subheadline", ""))

    primary_cta = data.get("primary_cta", {}) or {}
    secondary_cta = data.get("secondary_cta", {}) or {}

    bullet_points = data.get("bullet_points") or []
    bullet_html = (
        html_list([str(item) for item in bullet_points], cls="hero-bullets") if bullet_points else ""
    )

    hero_logo = (
        f'<img src="{escape(logo)}" alt="{escape(site.get("name", ""))}" class="hero-logo">'
        if logo
        else ""
    )

    buttons = []
    if primary_cta.get("text") and primary_cta.get("link"):
        buttons.append(
            f'<a class="btn primary" href="{escape(primary_cta["link"])}" target="_blank" rel="noopener">'
            f"{escape(primary_cta['text'])}</a>"
        )
    if secondary_cta.get("text") and secondary_cta.get("link"):
        buttons.append(
            f'<a class="btn secondary" href="{escape(secondary_cta["link"])}" target="_blank" rel="noopener">'
            f"{escape(secondary_cta['text'])}</a>"
        )

    button_html = "".join(buttons)

    return f"""
    <header class="hero" id="inicio">
        <div class="hero-content">
            {hero_logo}
            <h1>{headline}</h1>
            <p class="subheadline">{subheadline}</p>
            <div class="hero-actions">{button_html}</div>
            {bullet_html}
        </div>
    </header>
    """


def build_about(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    title = escape(data.get("title", "Sobre"))
    content = data.get("content", "")
    highlights = data.get("highlights") or []

    highlights_html = (
        html_list([str(item) for item in highlights], cls="highlight-list") if highlights else ""
    )

    return f"""
    <section id="sobre" class="section about">
        <div class="section-header">
            <span class="eyebrow">Quem Somos</span>
            <h2>{title}</h2>
        </div>
        <div class="section-body">
            {html_paragraphs(content)}
            {highlights_html}
        </div>
    </section>
    """


def build_services(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    title = escape(data.get("title", "Serviços"))
    description = escape(data.get("description", ""))
    items = data.get("items") or []

    cards = []
    for item in items:
        name = escape(str(item.get("name", "")))
        summary = escape(str(item.get("description", "")))
        icon = escape(str(item.get("icon", ""))) if item.get("icon") else ""
        icon_html = f'<div class="service-icon">{icon}</div>' if icon else ""
        cards.append(
            f"""
            <article class="service-card">
                {icon_html}
                <h3>{name}</h3>
                <p>{summary}</p>
            </article>
            """
        )

    cards_html = "".join(cards)
    return f"""
    <section id="servicos" class="section services">
        <div class="section-header">
            <span class="eyebrow">O que fazemos</span>
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        <div class="service-grid">{cards_html}</div>
    </section>
    """


def build_testimonials(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    title = escape(data.get("title", "Clientes satisfeitos"))
    items = data.get("items") or []
    cards = []
    for item in items:
        quote = escape(str(item.get("quote", "")))
        name = escape(str(item.get("name", "")))
        role = escape(str(item.get("role", "")))
        cards.append(
            f"""
            <article class="testimonial">
                <p class="quote">“{quote}”</p>
                <p class="author">{name}<span>{role}</span></p>
            </article>
            """
        )
    cards_html = "".join(cards)
    return f"""
    <section id="depoimentos" class="section testimonials">
        <div class="section-header">
            <span class="eyebrow">Depoimentos</span>
            <h2>{title}</h2>
        </div>
        <div class="testimonial-grid">{cards_html}</div>
    </section>
    """


def build_cta(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    headline = escape(data.get("headline", "Pronto para começar?"))
    subheadline = escape(data.get("subheadline", "Vamos conversar sobre seu projeto."))
    button = data.get("button") or {}
    button_html = ""
    if button.get("text") and button.get("link"):
        button_html = (
            f'<a class="btn accent" href="{escape(button["link"])}" target="_blank" rel="noopener">'
            f"{escape(button['text'])}</a>"
        )
    return f"""
    <section id="cta" class="section cta">
        <div class="cta-box">
            <h2>{headline}</h2>
            <p>{subheadline}</p>
            {button_html}
        </div>
    </section>
    """


def build_faq(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    title = escape(data.get("title", "Perguntas Frequentes"))
    items = data.get("items") or []
    accordions = []
    for item in items:
        question = escape(str(item.get("question", "")))
        answer = html_paragraphs(str(item.get("answer", "")))
        accordions.append(
            f"""
            <details class="faq-item">
                <summary>{question}</summary>
                <div class="faq-answer">{answer}</div>
            </details>
            """
        )
    accordions_html = "".join(accordions)
    return f"""
    <section id="faq" class="section faq">
        <div class="section-header">
            <span class="eyebrow">Dúvidas</span>
            <h2>{title}</h2>
        </div>
        <div class="faq-list">{accordions_html}</div>
    </section>
    """


def build_contact(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    title = escape(data.get("title", "Fale Conosco"))
    description = escape(data.get("description", ""))
    phone = escape(data.get("phone", "")) if data.get("phone") else ""
    whatsapp = escape(data.get("whatsapp", "")) if data.get("whatsapp") else ""
    email = escape(data.get("email", "")) if data.get("email") else ""
    address = escape(data.get("address", "")) if data.get("address") else ""
    maps_link = data.get("maps_link")
    social = data.get("social") or []
    hours = data.get("hours") or []

    phone_html = f"<a href=\"tel:{phone}\">{phone}</a>" if phone else ""
    whatsapp_html = (
        f"<a href=\"https://wa.me/{whatsapp}\" target=\"_blank\" rel=\"noopener\">WhatsApp</a>"
        if whatsapp
        else ""
    )
    email_html = f"<a href=\"mailto:{email}\">{email}</a>" if email else ""

    contact_lines = "".join(
        f"<li><strong>{label}:</strong> {value}</li>"
        for label, value in (
            ("Telefone", phone_html),
            ("WhatsApp", whatsapp_html),
            ("E-mail", email_html),
            ("Endereço", address),
        )
        if value
    )

    hours_html = (
        "<div class=\"contact-hours\">" + html_list(hours) + "</div>" if hours else ""
    )

    social_links = []
    for item in social:
        platform = escape(str(item.get("platform", "")))
        link = item.get("url")
        if not platform or not link:
            continue
        social_links.append(
            f'<a href="{escape(link)}" target="_blank" rel="noopener">{platform}</a>'
        )
    social_html = (
        '<div class="contact-social">' + "".join(social_links) + "</div>" if social_links else ""
    )

    map_embed = (
        f'<iframe src="{escape(maps_link)}" loading="lazy" allowfullscreen '
        f'referrerpolicy="no-referrer-when-downgrade"></iframe>'
        if maps_link
        else ""
    )

    return f"""
    <section id="contato" class="section contact">
        <div class="section-header">
            <span class="eyebrow">Contato</span>
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        <div class="contact-grid">
            <div class="contact-card">
                <ul class="contact-list">{contact_lines}</ul>
                {hours_html}
                {social_html}
            </div>
            <div class="contact-map">{map_embed}</div>
        </div>
    </section>
    """


def build_footer(data: Dict[str, Any], *, site: Dict[str, Any]) -> str:
    text = data.get("text") if data else None
    default_text = f"© {escape(site.get('name', 'Sua Empresa'))}. Todos os direitos reservados."
    footer_text = escape(text) if text else default_text
    links = data.get("links") if data else []
    link_html = "".join(
        f'<a href="{escape(link.get("url", "#"))}" target="_blank" rel="noopener">{escape(link.get("label", ""))}</a>'
        for link in links or []
        if link.get("url") and link.get("label")
    )
    return f"""
    <footer class="site-footer">
        <div class="footer-text">{footer_text}</div>
        <div class="footer-links">{link_html}</div>
    </footer>
    """


def build_document(
    config: Dict[str, Any],
    *,
    generated_sections: Dict[str, str],
    nav_sections: List[Dict[str, str]],
    logo_path: Optional[str],
    footer_html: str,
) -> str:
    site = config.get("site", {})
    seo = config.get("seo", {})

    title = seo.get("title") or site.get("name") or "Site de Demonstração"
    description = seo.get("description") or config.get("tagline") or "Criação de sites profissionais."

    primary_color = site.get("primary_color", "#1b6ef3")
    secondary_color = site.get("secondary_color", "#123a9a")
    accent_color = site.get("accent_color", "#f97316")
    background_color = site.get("background_color", "#f7f9fc")
    text_color = site.get("text_color", "#1f2933")

    nav_html = build_nav(nav_sections, site_name=site.get("name", "Sua Empresa"), logo=logo_path)

    body_sections = "".join(generated_sections.values())

    style_path = "style.css"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(description)}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{style_path}">
    <style>
        :root {{
            --color-primary: {primary_color};
            --color-secondary: {secondary_color};
            --color-accent: {accent_color};
            --color-background: {background_color};
            --color-text: {text_color};
        }}
    </style>
</head>
<body>
    {nav_html}
    <main>
        {body_sections}
    </main>
    {footer_html}
</body>
</html>
"""


def generate_site(config_path: Path, *, output_dir: Path) -> Path:
    config = read_config(config_path)
    site = config.get("site", {})
    slug = config.get("slug") or site.get("slug") or slugify(site.get("name", ""))
    site_output = output_dir / slug
    ensure_output_dir(site_output)

    logo_path = copy_logo(site.get("logo"), site_output)

    sections: "OrderedDict[str, str]" = OrderedDict()
    nav_sections: List[Dict[str, str]] = [{"id": "inicio", "label": "Início"}]

    hero = build_hero(config.get("hero") or {}, site=site, logo=logo_path)
    sections["hero"] = hero

    about_html = build_about(config.get("about") or {})
    if about_html:
        sections["about"] = about_html
        nav_sections.append({"id": "sobre", "label": "Sobre"})

    services_html = build_services(config.get("services") or {})
    if services_html:
        sections["services"] = services_html
        nav_sections.append({"id": "servicos", "label": "Serviços"})

    testimonials_html = build_testimonials(config.get("testimonials") or {})
    if testimonials_html:
        sections["testimonials"] = testimonials_html
        nav_sections.append({"id": "depoimentos", "label": "Depoimentos"})

    faq_html = build_faq(config.get("faq") or {})
    if faq_html:
        sections["faq"] = faq_html
        nav_sections.append({"id": "faq", "label": "FAQ"})

    cta_html = build_cta(config.get("cta") or {})
    if cta_html:
        sections["cta"] = cta_html
        nav_sections.append({"id": "cta", "label": "Começar"})

    contact_html = build_contact(config.get("contact") or {})
    if contact_html:
        sections["contact"] = contact_html
        nav_sections.append({"id": "contato", "label": "Contato"})

    footer_html = build_footer(config.get("footer") or {}, site=site)

    document = build_document(
        config,
        generated_sections=sections,
        nav_sections=nav_sections,
        logo_path=logo_path,
        footer_html=footer_html,
    )

    index_path = site_output / "index.html"
    index_path.write_text(document, encoding="utf-8")

    css_source = TEMPLATE_DIR / "style.css"
    if css_source.exists():
        shutil.copy2(css_source, site_output / css_source.name)

    return index_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera páginas de demonstração a partir de um arquivo JSON.")
    parser.add_argument("config", type=Path, help="Caminho para o arquivo JSON com a configuração do site")
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_ROOT,
        help="Diretório onde o site será criado (padrão: sites/)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index_path = generate_site(args.config, output_dir=args.output.resolve())
    print(f"Site gerado em {index_path}")


if __name__ == "__main__":
    main()
