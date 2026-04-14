#!/usr/bin/env bash
# Converte DOCX para PDF usando LibreOffice headless.
#
# Uso:
#   ./docx_para_pdf.sh relatorio.docx [saida.pdf]
#
# Se o segundo argumento for omitido, o PDF fica com o mesmo nome do DOCX.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "uso: $0 <arquivo.docx> [saida.pdf]" >&2
  exit 1
fi

if ! command -v libreoffice >/dev/null 2>&1; then
  echo "[erro] libreoffice não encontrado." >&2
  echo "instale com: sudo apt install -y libreoffice-core libreoffice-writer --no-install-recommends" >&2
  exit 2
fi

input_docx="$1"
if [[ ! -f "$input_docx" ]]; then
  echo "[erro] arquivo não encontrado: $input_docx" >&2
  exit 1
fi

output_dir="$(dirname "$input_docx")"
base_name="$(basename "${input_docx%.*}")"
default_pdf="${output_dir}/${base_name}.pdf"

libreoffice --headless --convert-to pdf "$input_docx" --outdir "$output_dir" >/dev/null

if [[ $# -ge 2 ]]; then
  target="$2"
  if [[ "$default_pdf" != "$target" ]]; then
    mv "$default_pdf" "$target"
  fi
  echo "PDF gerado: $target"
else
  echo "PDF gerado: $default_pdf"
fi
