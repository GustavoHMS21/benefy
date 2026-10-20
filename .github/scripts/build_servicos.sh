#!/usr/bin/env bash
# Constrói a imagem de cada serviço em services/ e registra o resultado no resumo do job.
# Uso: bash .github/scripts/build_servicos.sh <versao>
set -euo pipefail

versao="${1:?informe a versão}"
resumo="${GITHUB_STEP_SUMMARY:-/dev/stdout}"

mapfile -t servicos < <(find services -mindepth 2 -maxdepth 2 -name Dockerfile -printf '%h\n' 2>/dev/null | sort)

{
  echo "### Imagens da versão \`${versao}\`"
  echo
} >> "$resumo"

if [ "${#servicos[@]}" -eq 0 ]; then
  echo "Nenhum serviço com Dockerfile em \`services/\`." >> "$resumo"
  exit 0
fi

{
  echo "| Serviço | Imagem |"
  echo "|---|---|"
} >> "$resumo"

for diretorio in "${servicos[@]}"; do
  nome="$(basename "$diretorio")"
  imagem="benefy/${nome}:${versao}"
  docker build --tag "$imagem" "$diretorio"
  echo "| \`${nome}\` | \`${imagem}\` |" >> "$resumo"
done
