---
title: Installation
nav_order: 2
---

# Installation

Every method below installs the same package. Pick whichever fits your workflow — then don't skip the Playwright browser step at the end.

## Binary releases

Download a pre-built binary from the [latest release](https://github.com/twardoch/brosh/releases/latest). No Python required.

### Linux / macOS

```bash
# Linux
wget https://github.com/twardoch/brosh/releases/latest/download/brosh-linux-x86_64
# macOS Intel
wget https://github.com/twardoch/brosh/releases/latest/download/brosh-macos-x86_64
# macOS Apple Silicon
wget https://github.com/twardoch/brosh/releases/latest/download/brosh-macos-arm64

chmod +x brosh-*
sudo mv brosh-* /usr/local/bin/brosh
brosh --version
```

### Windows

```powershell
Invoke-WebRequest -Uri "https://github.com/twardoch/brosh/releases/latest/download/brosh-windows-x86_64.exe" -OutFile "brosh.exe"
Move-Item brosh.exe C:\Windows\System32\brosh.exe
brosh --version
```

Binaries bundle all Python dependencies but still need Playwright's browser binaries — see below.

## Using uv/uvx (recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# run without installing
uvx brosh shot "https://example.com"

# or install globally
uv tool install brosh
uv tool install "brosh[all]"   # with dev/test/docs extras
```

## Using pip

```bash
python -m pip install brosh
python -m pip install "brosh[all]"
```

## Using pipx

[pipx](https://pipx.pypa.io/) installs Python applications in isolated environments.

```bash
python -m pip install --user pipx
python -m pipx ensurepath
pipx install brosh
```

## From source

```bash
git clone https://github.com/twardoch/brosh.git
cd brosh
python -m pip install -e ".[all]"
```

## Install Playwright browsers

After installing the `brosh` package itself, install the browser binaries Playwright drives:

```bash
playwright install
# or just one browser
playwright install chromium
```

This downloads Chromium, Firefox, and WebKit. Brosh targets Chrome and Edge (Chromium-based) and Safari (WebKit-based) — Firefox isn't supported.
