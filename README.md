# MD2CV

A small Markdown-to-HTML CV generator.

`md2cv` converts a structured `cv.md` file into a printable HTML CV using a fixed template and stylesheet. 
It is designed to work both as a standalone repository and as an engine embedded inside another repository via Git subtree.

## What it does

The project takes Markdown content from `cv.md` and generates a styled HTML CV using:

- `build.py` for parsing and generation,
- `template.html` for the page structure,
- `style.css` for the base design.

The generated output is written to:

```text
output/cv.html
```

You can open that file in a browser and print it to PDF.

## Repository layout

```text
md2cv
├── build.py
├── cv.md
├── output
│   └── cv.html
├── README.md
├── requirements.txt
├── style.css
└── template.html
```

### File roles

- `cv.md` — sample content and default input file.
- `build.py` — converts Markdown into the final HTML structure.
- `template.html` — provides the HTML structure.
- `style.css` — provides the default styling.
- `output/cv.html` — generated CV.

## Setup

### macOS (and possibly Linux too)

```bash
python3 -m venv .venv
source ~/venv/bin/activate
python -m pip install -r requirements.txt
```

## Build

Run:

```bash
python build.py
```

Open the generated `output/cv.html` in a browser, then print to PDF.

## Edit content

Update:

```text
cv.md
```

This is the source of truth for the generated CV when using the repo directly.

Sections are written in Markdown and rendered according to the rules in `build.py`.

## Edit design

### Change the base design

Update:

```text
style.css
```

This changes the default look of the generated CV.

### Add private overrides with `custom.css`

When `md2cv` is used inside another repository via subtree, the build script will also detect:

```text
../custom.css
```

if the parent repo contains a `cv.md`.

That file is loaded after `style.css`, so it can override the base styling without modifying the engine stylesheet directly.

## Printing to PDF

After building:

1. Open `output/cv.html` in a browser.
2. Use the browser’s print dialog.
3. Save as PDF.

Recommended print settings:

- Destination: Save as PDF
- Layout: Portrait
- Headers and footers: Off
- Background graphics: On, if your design uses background styling
- Scale: Usually 100%
- Margins: Default

The stylesheet includes print-oriented styling, so the PDF should come out close to the browser preview.

## Standalone workflow

For normal use of this repo:

1. Edit `cv.md`
2. Run `python build.py`
3. Open `output/cv.html`
4. Print to PDF

On macOS, use:

```bash
open output/cv.html
```

On Linux, use:

```bash
xdg-open output/cv.html
```

On Windows PowerShell, use:

```powershell
start output/cv.html
```

## Subtree behaviour

By default, `build.py` is subtree-aware.

If `md2cv` is embedded inside another repository and the parent folder contains a `cv.md`, the build script will prefer the parent file instead. 
In that case it will also:

- write output to the parent folder’s `output/cv.html`,
- look for `custom.css` in the parent folder,
- continue using the subtree’s own `template.html` and `style.css`.

A typical personal repo might look like this:

```text
personal-repo/
├── cv.md
├── custom.css
├── output/
└── md2cv/
    ├── build.py
    ├── template.html
    ├── style.css
    └── ...
```

In that setup, from the personal repo root you would run:

```bash
python md2cv/build.py
```

### Adding this repo as a subtree

From another repository, add `md2cv` like this:

```bash
git remote add md2cv git@github.com:insidemordecai/md2cv.git
git fetch md2cv
git subtree add --prefix=md2cv md2cv main --squash
```

If the branch is not `main`, replace it with the correct branch name.

### Updating the subtree

To pull the latest changes from this public repo into a parent repo:

```bash
git fetch md2cv
git subtree pull --prefix=md2cv md2cv main --squash
```

## Notes

- `cv.md` is the source of truth for content when using this repo directly.
- `template.html` provides the page shell.
- `build.py` converts markdown sections into the HTML structure expected by `style.css`.
- `style.css` is the base theme.
- `custom.css` is intentionally optional.
- This project aims to stay small and hackable rather than become a large CV framework.

## Back Story & Philosophy

For years, I used the [Awesome CV](https://github.com/posquit0/Awesome-CV) LaTex template by [posquit0](https://github.com/posquit0) on [Overleaf](https://www.overleaf.com/) but I soon felt like I needed some freedom.
The next logical step was to recreate my CV using HTML & CSS and so I did just that.
That was amazing, until making changes in HTML became tedious and Markdown slowly became preferable since I already use it for [my blog](https://insidemordecai.com).

This project is intentionally simple:

- Markdown for content,
- one Python build script,
- one template,
- one stylesheet,
- browser printing for PDF output.

That keeps it easy to understand, easy to modify, and easy to reuse in other repositories.
