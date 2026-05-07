# MD2CV

MD2CV is a small Markdown-to-HTML CV generator.

It converts `cv.md` into a printable HTML CV using a fixed template and stylesheet.
It works both as a standalone repository and as an engine embedded inside another repository via Git subtree.

![CV Preview](docs/preview.png?raw=true)

## Overview

The project takes Markdown content from `cv.md` and generates a styled HTML CV (`output/cv.html`) using:

- `build.py` for parsing and generation,
- `template.html` for the HTML structure,
- `style.css` for the base design.

The generated CV is written to `output/cv.html`, which you can open in a browser and print to PDF.
You can open that file in a browser and print it to PDF.

## Prerequisites

- [Python 3](https://www.python.org/downloads/) must be installed and available on your PATH (tick this option when installing Python on Windows).

To verify, run:

```bash
python3 --version
```

On Windows, you may need to use `python` instead of `python3`.

## 1. Setup

### macOS (and possibly Linux too)

```bash
python3 -m venv .venv
source ~/venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

> If script execution is disabled, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then re-run the activation command.

## 2. Edit

### Content

Update `cv.md`.
That is the exclusive source of information for the generated CV.

Sections are written in Markdown and rendered according to the rules in `build.py`.

### Design (Optional)

#### Change The Base Design

Update `style.css`.
That changes the default look of the generated CV.

#### Add Personal Overrides

The build script also detects a `custom.css` file that is loaded after `style.css`.
So it can override the base styling without modifying the engine stylesheet directly.

## 3. Build

Run:

```bash
python build.py
```

Then open the generated file:

- **macOS:** `open output/cv.html`
- **Linux:** `xdg-open output/cv.html`
- **Windows (PowerShell):** `start .\output\cv.html`

Print to PDF from the browser using the print dialog.

## 4. Printing to PDF

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

## Subtree Workflow

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

### Adding This Repo As A Subtree

From another repository, add `md2cv` like this:

```bash
git remote add md2cv git@github.com:insidemordecai/md2cv.git
git fetch md2cv
git subtree add --prefix=md2cv md2cv main --squash
```

If the branch is not `main`, replace it with the correct branch name.

### Updating The Subtree

To pull the latest changes from this public repo into a parent repo:

```bash
git fetch md2cv
git subtree pull --prefix=md2cv md2cv main --squash
```

## Back Story & Philosophy

For years, I used the [Awesome CV](https://github.com/posquit0/Awesome-CV) LaTex template by [posquit0](https://github.com/posquit0) on [Overleaf](https://www.overleaf.com/) but I soon felt like I needed some freedom.
The next logical step was to recreate my CV using HTML & CSS and so I did just that.
That was amazing, until making changes in HTML became tedious and Markdown slowly became preferable since I already use it for [my blog](https://insidemordecai.com).

This project is intentionally simple.
That keeps it easy to understand, easy to modify, and easy to reuse in other repositories.
