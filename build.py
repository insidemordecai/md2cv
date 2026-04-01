#!/usr/bin/env python3

from pathlib import Path
import re
import yaml
from markdown import markdown
from jinja2 import Environment, FileSystemLoader

INPUT_FILE = "cv.md"
TEMPLATE_FILE = "template.html"
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "cv.html"


def parse_markdown_file(file_path):
    content = Path(file_path).read_text(encoding="utf-8")

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        raise ValueError("No valid YAML front matter found. Make sure cv.md starts with ---")

    front_matter_raw = match.group(1)
    body = match.group(2)

    metadata = yaml.safe_load(front_matter_raw) or {}
    return metadata, body


def strip_html_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def normalize_section_key(title):
    key = title.strip().lower()
    key = key.replace("&", "and")
    key = re.sub(r"[^\w\s-]", "", key)
    key = re.sub(r"[-\s]+", "_", key)
    return key


def parse_labeled_value(line, label):
    prefix = f":{label}:"
    if line.startswith(prefix):
        return line[len(prefix):].strip()
    return None


def resolve_section_id(title, metadata):
    section_ids = metadata.get("section_ids", {}) or {}
    if title in section_ids:
        return section_ids[title]

    normalized = normalize_section_key(title)
    fallback_aliases = {
        "introduction": "intro",
        "summary": "intro",
        "profile": "intro",
        "work_experience": "experience",
        "professional_experience": "experience",
        "experience": "experience",
        "education": "education",
        "projects": "projects",
        "certifications": "certifications",
        "skills": "skills",
        "skills_and_interests": "skills",
        "skills_interests": "skills",
        "interests": "skills",
        "referees": "referees",
        "references": "referees",
        "honors": "honors",
        "honors_and_awards": "honors",
        "awards": "awards",
        "publications": "publications",
    }
    return fallback_aliases.get(normalized, normalized)


def default_section_renderers():
    return {
        "intro": "intro",
        "experience": "experience",
        "education": "experience",
        "projects": "projects",
        "certifications": "bullets",
        "skills": "skills",
        "referees": "referees",
        "honors": "bullets",
        "awards": "bullets",
        "publications": "bullets",
    }


def resolve_section_renderer(section_id, metadata):
    renderer_map = default_section_renderers()
    renderer_map.update(metadata.get("section_renderers", {}) or {})
    return renderer_map.get(section_id, "generic")


def resolve_section_visibility(section_id, metadata):
    visibility = metadata.get("section_visibility", {}) or {}

    legacy_flags = {
        "projects": metadata.get("show_projects", True),
        "certifications": metadata.get("show_certifications", True),
        "referees": metadata.get("show_referees", True),
    }

    if section_id in visibility:
        return bool(visibility[section_id])

    if section_id in legacy_flags:
        return legacy_flags[section_id]

    return True


def resolve_header_links(metadata):
    if "header_links" in metadata and metadata["header_links"]:
        return metadata["header_links"]

    links = []

    if metadata.get("phone_display") and metadata.get("phone_href"):
        links.append({
            "label": metadata["phone_display"],
            "href": metadata["phone_href"],
            "class": "contact-link"
        })

    if metadata.get("email") and metadata.get("email_href"):
        links.append({
            "label": metadata["email"],
            "href": metadata["email_href"],
            "class": "contact-link"
        })

    if metadata.get("website") and metadata.get("website_href"):
        links.append({
            "label": metadata["website"],
            "href": metadata["website_href"],
            "class": "contact-link"
        })

    if metadata.get("linkedin") and metadata.get("linkedin_href"):
        links.append({
            "label": metadata["linkedin"],
            "href": metadata["linkedin_href"],
            "class": "contact-link"
        })

    return links


def render_inline_markdown(text):
    html = markdown(text, extensions=["extra"]).strip()
    html = re.sub(r"^<p>|</p>$", "", html)
    return html


def render_bullets(bullets):
    if not bullets:
        return ""
    return '<ul class="item-bullets">\n' + "\n".join(
        f"<li>{render_inline_markdown(b)}</li>" for b in bullets
    ) + "\n</ul>"


def render_single_item(company, role="", location="", dates="", bullets=None):
    bullets = bullets or []

    item_top = f'''<div class="item-top">
    <div>
      <div class="item-company">{company}</div>
      <div class="item-role"><em>{role}</em></div>
    </div>
    <div class="item-meta">
      {f'<div class="item-location brand-location">{location}</div>' if location else ''}
      {f'<div class="item-dates">{dates}</div>' if dates else ''}
    </div>
  </div>'''

    return f'''<div class="item">
  {item_top}
  {render_bullets(bullets)}
</div>'''


def render_experience_or_education(section_text):
    lines = [line.rstrip() for line in section_text.splitlines()]

    items = []
    current_item = None
    current_subrole = None

    def flush_subrole():
        nonlocal current_item, current_subrole
        if current_item is not None and current_subrole is not None:
            current_item["sub_roles"].append(current_subrole)
            current_subrole = None

    def flush_item():
        nonlocal current_item, current_subrole, items
        if current_item is not None:
            flush_subrole()
            items.append(current_item)
            current_item = None

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("### "):
            flush_item()
            current_item = {
                "company": line[4:].strip(),
                "location": "",
                "role": "",
                "dates": "",
                "bullets": [],
                "sub_roles": []
            }
            continue

        if current_item is None:
            continue

        if line.startswith("#### "):
            flush_subrole()
            current_subrole = {
                "role": line[5:].strip(),
                "location": "",
                "dates": "",
                "bullets": []
            }
            continue

        loc = parse_labeled_value(line, "location")
        if loc is not None:
            if current_subrole is not None:
                current_subrole["location"] = loc
            else:
                current_item["location"] = loc
            continue

        dts = parse_labeled_value(line, "dates")
        if dts is not None:
            if current_subrole is not None:
                current_subrole["dates"] = dts
            else:
                current_item["dates"] = dts
            continue

        if line.startswith("- "):
            bullet = line[2:].strip()
            if current_subrole is not None:
                current_subrole["bullets"].append(bullet)
            else:
                current_item["bullets"].append(bullet)
            continue

        if current_subrole is None and not current_item["role"]:
            current_item["role"] = line.strip("*").strip()
            continue

    flush_item()

    html_parts = []

    for item in items:
        if len(item["sub_roles"]) > 1:
            html = f'''<div class="item">
  <div class="item-top">
    <div>
      <div class="item-company">{item["company"]}</div>
    </div>
    <div class="item-meta">
      {f'<div class="item-location brand-location">{item["location"]}</div>' if item["location"] else ''}
    </div>
  </div>'''

            for sr in item["sub_roles"]:
                bullets_html = render_bullets(sr["bullets"])
                html += f'''
  <div class="sub-role">
    <div class="sub-role-header">
      <div class="item-role"><em>{sr["role"]}</em></div>
      <div class="sub-role-dates">{sr["dates"]}</div>
    </div>
    {bullets_html}
  </div>'''
            html += "\n</div>"
            html_parts.append(html)

        elif len(item["sub_roles"]) == 1:
            sr = item["sub_roles"][0]
            html_parts.append(
                render_single_item(
                    company=item["company"],
                    role=sr["role"],
                    location=sr["location"] or item["location"],
                    dates=sr["dates"] or item["dates"],
                    bullets=sr["bullets"],
                )
            )

        else:
            html_parts.append(
                render_single_item(
                    company=item["company"],
                    role=item["role"],
                    location=item["location"],
                    dates=item["dates"],
                    bullets=item["bullets"],
                )
            )

    return "\n".join(html_parts).strip()


def render_projects(section_text):
    lines = [line.rstrip() for line in section_text.splitlines()]

    items = []
    current_item = None

    def flush_item():
        nonlocal current_item, items
        if current_item is not None:
            items.append(current_item)
            current_item = None

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("### "):
            flush_item()
            current_item = {
                "company": line[4:].strip(),
                "role": "",
                "location": "",
                "dates": "",
                "bullets": []
            }
            continue

        if current_item is None:
            continue

        if line.startswith("#### "):
            current_item["role"] = line[5:].strip()
            continue

        loc = parse_labeled_value(line, "location")
        if loc is not None:
            current_item["location"] = loc
            continue

        dts = parse_labeled_value(line, "dates")
        if dts is not None:
            current_item["dates"] = dts
            continue

        if line.startswith("- "):
            current_item["bullets"].append(line[2:].strip())
            continue

    flush_item()

    html_parts = []

    for item in items:
        html_parts.append(
            render_single_item(
                company=item["company"],
                role=item["role"],
                location=item["location"],
                dates=item["dates"],
                bullets=item["bullets"],
            )
        )

    return "\n".join(html_parts).strip()


def render_simple_bullets(section_text):
    bullets = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())

    return render_bullets(bullets).strip()


def render_skills(section_text):
    html_parts = []

    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue

        content = line[2:].strip()
        m = re.match(r"^\*\*(.+?)\*\*\s*:\s*(.+)$", content)

        if m:
            label = m.group(1).strip()
            value = m.group(2).strip()
            html_parts.append(f'<p><span class="label">{label}:</span> {value}</p>')
        else:
            fallback = render_inline_markdown(content)
            html_parts.append(f"<p>{fallback}</p>")

    return "\n".join(html_parts).strip()


def render_referees(section_text):
    blocks = [b.strip() for b in re.split(r"\n\s*\n", section_text.strip()) if b.strip()]
    referees = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        name = lines[0].replace("### ", "").strip()
        role = lines[1] if len(lines) > 1 else ""

        phone = ""
        email = ""

        for line in lines[2:]:
            phone_match = re.search(r'\[([^\]]+)\]\((tel:[^)]+)\)', line)
            email_match = re.search(r'\[([^\]]+)\]\((mailto:[^)]+)\)', line)

            if phone_match:
                phone = f'<a class="ref-phone" href="{phone_match.group(2)}">{phone_match.group(1)}</a>'
            if email_match:
                email = f'<a class="ref-email" href="{email_match.group(2)}">{email_match.group(1)}</a>'

        referees.append({
            "name": name,
            "role": role,
            "phone": phone,
            "email": email
        })

    if not referees:
        return ""

    if len(referees) == 1:
        return f'''<div class="skills-grid">
  <div>
    <p class="label">{referees[0]["name"]}</p>
    <p>{referees[0]["role"]}</p>
    <p>{referees[0]["phone"]}</p>
    <p>{referees[0]["email"]}</p>
  </div>
</div>'''.strip()

    html = '''<div class="skills-grid">'''
    for ref in referees[:2]:
        html += f'''
  <div>
    <p class="label">{ref["name"]}</p>
    <p>{ref["role"]}</p>
    <p>{ref["phone"]}</p>
    <p>{ref["email"]}</p>
  </div>'''
    html += '\n</div>'

    if len(referees) > 2:
        ref = referees[2]
        html += f'''
<div class="referee-extra">
  <p class="label">{ref["name"]}</p>
  <p>{ref["role"]}</p>
  <p>{ref["phone"]}</p>
  <p>{ref["email"]}</p>
</div>'''

    return html.strip()


def parse_sections(body, metadata):
    section_list = []

    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        body = "\n".join(lines[1:]).lstrip()

    parts = re.split(r"^##\s+(.+?)\s*$", body, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        raw_title = parts[i].strip()
        raw_content = parts[i + 1].strip()

        if not raw_content:
            continue

        section_id = resolve_section_id(raw_title, metadata)
        renderer = resolve_section_renderer(section_id, metadata)

        if renderer == "experience":
            html = render_experience_or_education(raw_content)
        elif renderer == "projects":
            html = render_projects(raw_content)
        elif renderer == "bullets":
            html = render_simple_bullets(raw_content)
        elif renderer == "skills":
            html = render_skills(raw_content)
        elif renderer == "referees":
            html = render_referees(raw_content)
        elif renderer == "intro":
            html = f'<p class="intro">{render_inline_markdown(raw_content)}</p>'
        else:
            html = markdown(raw_content, extensions=["extra", "sane_lists"]).strip()

        section_list.append({
            "id": section_id,
            "title": raw_title,
            "renderer": renderer,
            "html": html,
            "classes": f"section section-{section_id} renderer-{renderer}",
        })

    return section_list


def build():
    OUTPUT_DIR.mkdir(exist_ok=True)

    metadata, body = parse_markdown_file(INPUT_FILE)

    strip_comments = metadata.get("build", {}).get("strip_comments", True)
    if strip_comments:
        body = strip_html_comments(body)

    sections = parse_sections(body, metadata)
    header_links = resolve_header_links(metadata)

    name = metadata.get("name", "")

    filtered_sections = [
        section for section in sections
        if resolve_section_visibility(section["id"], metadata)
    ]

    env = Environment(loader=FileSystemLoader("."), autoescape=False)
    template = env.get_template(TEMPLATE_FILE)

    rendered = template.render(
        name=name,
        header_links=header_links,
        sections=filtered_sections,
        stylesheet_path=metadata.get("stylesheet", "../style.css"),
    )

    OUTPUT_FILE.write_text(rendered, encoding="utf-8")

    print(f"Generated: {OUTPUT_FILE}")
    print("Open output/cv.html in a browser and print to PDF.")


if __name__ == "__main__":
    build()
