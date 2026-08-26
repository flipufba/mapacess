from pathlib import Path
import json
import requests


# Diretório raiz do repositório
REPO_ROOT = Path(__file__).resolve().parents[2]

# Arquivos de entrada e saída
ARQUIVO_POLIGONO = REPO_ROOT / "data" / "study_area" / "delimita.geojson"
ARQUIVO_SAIDA = (
    REPO_ROOT
    / "data"
    / "derived"
    / "osm"
    / "exploratory"
    / "osm_centenario_2025-11-17.geojson"
)

# Endpoint da ohsome API
URL = "https://api.ohsome.org/v1/elementsFullHistory/geometry"

# Filtro exploratório
FILTRO = """
(
    (type:way and highway=*)
    or
    (type:node and barrier=kerb)
    or
    (type:node and highway=crossing)
)
"""

# Carrega o polígono do trecho piloto
with ARQUIVO_POLIGONO.open("r", encoding="utf-8") as f:
    poligono = json.load(f)

# Parâmetros da consulta
dados = {
    "bpolys": json.dumps(poligono),
    "time": "2025-11-17T00:00:00Z,2025-11-17T00:00:01Z",
    "filter": FILTRO,
    "properties": "tags,metadata",
    "clipGeometry": "true",
}

# Executa a consulta
resposta = requests.post(URL, data=dados, timeout=120)

print("Status:", resposta.status_code)

if resposta.ok:
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)

    with ARQUIVO_SAIDA.open("wb") as f:
        f.write(resposta.content)

    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")
else:
    print(resposta.text)
    resposta.raise_for_status()