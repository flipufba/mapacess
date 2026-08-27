from pathlib import Path
from collections import Counter
import csv
import json


# ============================================================
# CAMINHOS DO PROJETO
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[2]

SNAPSHOTS_DIR = (
    REPO_ROOT
    / "data"
    / "derived"
    / "osm"
    / "snapshots"
)

T0_PATH = SNAPSHOTS_DIR / "osm_centenario_filt_2025-11-18.geojson"
T1_PATH = SNAPSHOTS_DIR / "osm_centenario_filt_2026-03-01.geojson"

OUTPUT_PATH = (
    REPO_ROOT
    / "results"
    / "tables"
    / "contagem_geometrica_t0_t1.csv"
)


# ============================================================
# LEITURA DOS DADOS
# ============================================================

def carregar_geojson(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if dados.get("type") != "FeatureCollection":
        raise ValueError(
            f"O arquivo não é um FeatureCollection válido: {caminho}"
        )

    return dados


# ============================================================
# CLASSIFICAÇÃO DAS FEIÇÕES
# ============================================================

def classificar_feicao(feature):
    propriedades = feature.get("properties", {})
    geometria = feature.get("geometry") or {}

    tipo_geometria = geometria.get("type")

    highway = propriedades.get("highway")
    footway = propriedades.get("footway")
    barrier = propriedades.get("barrier")

    # Calçadas representadas como vias independentes
    if (
        tipo_geometria in {"LineString", "MultiLineString"}
        and highway == "footway"
        and footway == "sidewalk"
    ):
        return "calcada"

    # Travessias representadas como vias lineares
    if (
        tipo_geometria in {"LineString", "MultiLineString"}
        and highway == "footway"
        and footway == "crossing"
    ):
        return "travessia_linear"

    # Nós de interface de meio-fio
    if (
        tipo_geometria == "Point"
        and barrier == "kerb"
    ):
        return "no_meio_fio"

    # Nós de travessia compartilhados com a via
    if (
        tipo_geometria == "Point"
        and highway == "crossing"
    ):
        return "no_travessia"

    return "outros"


def contar_classes(dados):
    return Counter(
        classificar_feicao(feature)
        for feature in dados["features"]
    )


# ============================================================
# PROCESSAMENTO
# ============================================================

t0 = carregar_geojson(T0_PATH)
t1 = carregar_geojson(T1_PATH)

contagem_t0 = contar_classes(t0)
contagem_t1 = contar_classes(t1)


# Verificação de segurança:
# o filtro analítico deve retornar apenas as quatro classes
# previstas pelo protocolo.

if contagem_t0["outros"] > 0:
    raise RuntimeError(
        f"T0 contém {contagem_t0['outros']} feição(ões) "
        "fora das classes analíticas previstas."
    )

if contagem_t1["outros"] > 0:
    raise RuntimeError(
        f"T1 contém {contagem_t1['outros']} feição(ões) "
        "fora das classes analíticas previstas."
    )


classes = [
    ("calcada", "Calçadas"),
    ("travessia_linear", "Travessias lineares"),
    ("no_meio_fio", "Nós de meio-fio"),
    ("no_travessia", "Nós de travessia"),
]


# ============================================================
# GERAÇÃO DA TABELA
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

with OUTPUT_PATH.open(
    "w",
    newline="",
    encoding="utf-8",
) as arquivo:

    writer = csv.writer(arquivo)

    writer.writerow(
        [
            "classe",
            "t0",
            "t1",
            "variacao_absoluta",
        ]
    )

    for codigo, nome in classes:
        valor_t0 = contagem_t0[codigo]
        valor_t1 = contagem_t1[codigo]

        writer.writerow(
            [
                nome,
                valor_t0,
                valor_t1,
                valor_t1 - valor_t0,
            ]
        )

    total_t0 = len(t0["features"])
    total_t1 = len(t1["features"])

    writer.writerow(
        [
            "Total",
            total_t0,
            total_t1,
            total_t1 - total_t0,
        ]
    )


# ============================================================
# RESULTADO NO TERMINAL
# ============================================================

print()
print("ANÁLISE DA REPRESENTAÇÃO GEOMÉTRICA — T0 × T1")
print("=" * 68)

for codigo, nome in classes:
    valor_t0 = contagem_t0[codigo]
    valor_t1 = contagem_t1[codigo]
    diferenca = valor_t1 - valor_t0

    print(
        f"{nome:<25}"
        f"T0 = {valor_t0:>3}   "
        f"T1 = {valor_t1:>3}   "
        f"Δ = {diferenca:+4}"
    )

print("-" * 68)

total_t0 = len(t0["features"])
total_t1 = len(t1["features"])

print(
    f"{'Total':<25}"
    f"T0 = {total_t0:>3}   "
    f"T1 = {total_t1:>3}   "
    f"Δ = {total_t1 - total_t0:+4}"
)

print("=" * 68)

print()
print(f"Tabela salva em:")
print(OUTPUT_PATH)
print()