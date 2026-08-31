from pathlib import Path
from collections import Counter
import csv
import json

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform


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
    / "analise_geometrica_t0_t1.csv"
)


# ============================================================
# SISTEMAS DE REFERÊNCIA
# ============================================================

# Os arquivos GeoJSON utilizam coordenadas geográficas WGS 84.
# Para o cálculo das extensões, as geometrias lineares são
# transformadas para SIRGAS 2000 / UTM zona 24S,
# adequado à área de Salvador-BA.

transformador = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:31984",
    always_xy=True,
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


# ============================================================
# CONTAGEM DAS CLASSES
# ============================================================

def contar_classes(dados):
    return Counter(
        classificar_feicao(feature)
        for feature in dados["features"]
    )


# ============================================================
# CÁLCULO DE EXTENSÃO
# ============================================================

def calcular_extensao_classe(dados, classe_alvo):
    """
    Calcula a extensão total, em metros, das feições pertencentes
    a uma determinada classe linear.

    As geometrias são transformadas de EPSG:4326 para EPSG:31984
    antes do cálculo do comprimento.
    """

    extensao_total = 0.0

    for feature in dados["features"]:

        if classificar_feicao(feature) != classe_alvo:
            continue

        geometria_geojson = feature.get("geometry")

        if not geometria_geojson:
            continue

        geometria = shape(geometria_geojson)

        if geometria.geom_type not in {
            "LineString",
            "MultiLineString",
        }:
            continue

        geometria_metrica = transform(
            transformador.transform,
            geometria,
        )

        extensao_total += geometria_metrica.length

    return extensao_total


# ============================================================
# PROCESSAMENTO
# ============================================================

t0 = carregar_geojson(T0_PATH)
t1 = carregar_geojson(T1_PATH)

contagem_t0 = contar_classes(t0)
contagem_t1 = contar_classes(t1)


# ============================================================
# VERIFICAÇÃO DE SEGURANÇA
# ============================================================

# O filtro analítico utilizado nos snapshots deve retornar
# somente as quatro classes previstas na análise.

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


# ============================================================
# DEFINIÇÃO DAS CLASSES
# ============================================================

classes = [
    ("calcada", "Calçadas", True),
    ("travessia_linear", "Travessias lineares", True),
    ("no_meio_fio", "Nós de meio-fio", False),
    ("no_travessia", "Nós de travessia", False),
]


# ============================================================
# CÁLCULO DAS EXTENSÕES DAS CLASSES LINEARES
# ============================================================

extensoes_t0 = {}
extensoes_t1 = {}

for codigo, nome, classe_linear in classes:

    if classe_linear:
        extensoes_t0[codigo] = calcular_extensao_classe(
            t0,
            codigo,
        )

        extensoes_t1[codigo] = calcular_extensao_classe(
            t1,
            codigo,
        )


# ============================================================
# TOTAIS
# ============================================================

total_objetos_t0 = len(t0["features"])
total_objetos_t1 = len(t1["features"])

total_extensao_t0 = sum(extensoes_t0.values())
total_extensao_t1 = sum(extensoes_t1.values())


# ============================================================
# GERAÇÃO DA TABELA CONSOLIDADA
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
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
            "t0_n",
            "t1_n",
            "variacao_n",
            "t0_m",
            "t1_m",
            "variacao_m",
        ]
    )

    for codigo, nome, classe_linear in classes:

        valor_t0 = contagem_t0[codigo]
        valor_t1 = contagem_t1[codigo]

        if classe_linear:

            extensao_t0 = extensoes_t0[codigo]
            extensao_t1 = extensoes_t1[codigo]

            writer.writerow(
                [
                    nome,
                    valor_t0,
                    valor_t1,
                    valor_t1 - valor_t0,
                    round(extensao_t0, 2),
                    round(extensao_t1, 2),
                    round(
                        extensao_t1 - extensao_t0,
                        2,
                    ),
                ]
            )

        else:

            # Para feições pontuais, extensão linear não se aplica.
            writer.writerow(
                [
                    nome,
                    valor_t0,
                    valor_t1,
                    valor_t1 - valor_t0,
                    "—",
                    "—",
                    "—",
                ]
            )

    writer.writerow(
        [
            "Total",
            total_objetos_t0,
            total_objetos_t1,
            total_objetos_t1 - total_objetos_t0,
            round(total_extensao_t0, 2),
            round(total_extensao_t1, 2),
            round(
                total_extensao_t1 - total_extensao_t0,
                2,
            ),
        ]
    )


# ============================================================
# RESULTADO NO TERMINAL
# ============================================================

print()
print("ANÁLISE GEOMÉTRICA — T0 × T1")
print("=" * 96)

print(
    f"{'Classe':<25}"
    f"{'T0 (n)':>8}"
    f"{'T1 (n)':>8}"
    f"{'Δ (n)':>8}"
    f"{'T0 (m)':>14}"
    f"{'T1 (m)':>14}"
    f"{'Δ (m)':>14}"
)

print("-" * 96)

for codigo, nome, classe_linear in classes:

    valor_t0 = contagem_t0[codigo]
    valor_t1 = contagem_t1[codigo]
    diferenca_n = valor_t1 - valor_t0

    if classe_linear:

        extensao_t0 = extensoes_t0[codigo]
        extensao_t1 = extensoes_t1[codigo]
        diferenca_m = extensao_t1 - extensao_t0

        print(
            f"{nome:<25}"
            f"{valor_t0:>8}"
            f"{valor_t1:>8}"
            f"{diferenca_n:>+8}"
            f"{extensao_t0:>14.2f}"
            f"{extensao_t1:>14.2f}"
            f"{diferenca_m:>+14.2f}"
        )

    else:

        print(
            f"{nome:<25}"
            f"{valor_t0:>8}"
            f"{valor_t1:>8}"
            f"{diferenca_n:>+8}"
            f"{'—':>14}"
            f"{'—':>14}"
            f"{'—':>14}"
        )

print("-" * 96)

print(
    f"{'Total':<25}"
    f"{total_objetos_t0:>8}"
    f"{total_objetos_t1:>8}"
    f"{total_objetos_t1 - total_objetos_t0:>+8}"
    f"{total_extensao_t0:>14.2f}"
    f"{total_extensao_t1:>14.2f}"
    f"{total_extensao_t1 - total_extensao_t0:>+14.2f}"
)

print("=" * 96)

print()
print(
    "Nota: as extensões são calculadas somente para "
    "as classes lineares."
)

print(
    "Sistema métrico utilizado: "
    "SIRGAS 2000 / UTM zona 24S (EPSG:31984)."
)

print()
print("Tabela salva em:")
print(OUTPUT_PATH)