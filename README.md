# md2cv

A small Markdown-to-HTML CV generator.

## Setup

This setup works on macOS 26.4, I cannot ensure it will work on other environments. 

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Build

```bash
python build.py
```

This generates:

- `output/cv.html`

Open `output/cv.html` in a browser, then print to PDF.

## Edit content

Update `cv.md`.

## Edit design

Update `style.css`.

## Notes

- `cv.md` is the source of truth.
- `template.html` provides the page shell.
- `build.py` converts markdown sections into the HTML structure expected by `style.css`.
