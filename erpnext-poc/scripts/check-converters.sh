#!/usr/bin/env bash
echo "--- converters on PATH ---"
for c in pandoc libreoffice soffice; do
  p=$(command -v "$c" 2>/dev/null) && echo "  $c -> $p" || echo "  $c -> not installed"
done
echo "--- pandoc version ---"
pandoc --version 2>/dev/null | head -1 || echo "  none"
echo "--- python-docx ---"
python3 -c 'import docx, sys; print("  python-docx", docx.__version__ if hasattr(docx,"__version__") else "ok")' 2>&1 | tail -1
