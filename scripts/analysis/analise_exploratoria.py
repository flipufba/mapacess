from pathlib import Path
from collections import Counter
import csv
import json


# ============================================================
# 1. CAMINHOS DO PROJETO
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    REPO_ROOT
    / "data"
    / "derived"
    / "osm"
    / "exploratory"
    / "osm_centenario_2025-11-17.geojson"
)

RESULTS_DIR = (
    REPO_ROOT
    / "results"
    / "tables"
)

OUTPUT_GEOMETRIAS = (
    RESULTS_DIR
    / "exploratorio_geometrias.csv"
)

OUTPUT_ATRIBUTOS = (
    RESULTS_DIR
    / "exploratorio_atributos.csv"
)

OUTPUT_VALORES = (
    RESULTS_DIR
    / "exploratorio_valores_atributos.csv"
)

OUTPUT_METADADOS = (
    RESULTS_DIR
    / "exploratorio_metadados.csv"
)

OUTPUT_HIGHWAY_ATRIBUTOS = (
    RESULTS_DIR
    / "exploratorio_highway_atributos.csv"
)

OUTPUT_HIGHWAY_VALORES = (
    RESULTS_DIR
    / "exploratorio_highway_valores.csv"
)


# ============================================================
# 2. LEITURA DO GEOJSON
# ============================================================

def carregar_geojson(caminho):

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    with caminho.open(
        "r",
        encoding="utf-8",
    ) as arquivo:

        dados = json.load(arquivo)

    if dados.get("type") != "FeatureCollection":

        raise ValueError(
            "O arquivo informado não é um "
            "FeatureCollection GeoJSON válido."
        )

    return dados


# ============================================================
# 3. FUNÇÕES AUXILIARES
# ============================================================

def valor_preenchido(valor):

    if valor is None:
        return False

    if isinstance(valor, str):
        return valor.strip() != ""

    return True


def percentual(parte, total):

    if total == 0:
        return 0.0

    return round(
        (parte / total) * 100,
        1,
    )


def normalizar_valor(valor):

    if isinstance(valor, (dict, list)):

        return json.dumps(
            valor,
            ensure_ascii=False,
            sort_keys=True,
        )

    return str(valor).strip()


def salvar_csv(
    caminho,
    linhas,
    campos,
):

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with caminho.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as arquivo:

        writer = csv.DictWriter(
            arquivo,
            fieldnames=campos,
        )

        writer.writeheader()
        writer.writerows(linhas)


# ============================================================
# 4. CARREGAMENTO DOS DADOS
# ============================================================

dados = carregar_geojson(
    INPUT_PATH
)

feicoes = dados.get(
    "features",
    [],
)

total_feicoes = len(
    feicoes
)


# ============================================================
# 5. DISTRIBUIÇÃO DAS GEOMETRIAS
# ============================================================

contador_geometrias = Counter()


for feature in feicoes:

    geometria = feature.get(
        "geometry"
    )

    if geometria is None:

        tipo = "Sem geometria"

    else:

        tipo = geometria.get(
            "type",
            "Tipo desconhecido",
        )

    contador_geometrias[
        tipo
    ] += 1


linhas_geometrias = []


for tipo, quantidade in sorted(
    contador_geometrias.items(),
    key=lambda item: (
        -item[1],
        item[0],
    ),
):

    linhas_geometrias.append(
        {
            "tipo_geometria":
                tipo,
            "quantidade":
                quantidade,
            "percentual_total":
                percentual(
                    quantidade,
                    total_feicoes,
                ),
        }
    )


# ============================================================
# 6. INVENTÁRIO GERAL DOS ATRIBUTOS
# ============================================================

presenca_atributos = Counter()
presenca_metadados = Counter()

valores_atributos = {}
valores_metadados = {}


for feature in feicoes:

    propriedades = feature.get(
        "properties",
        {},
    )

    for atributo, valor in (
        propriedades.items()
    ):

        if not valor_preenchido(
            valor
        ):
            continue

        valor_normalizado = (
            normalizar_valor(
                valor
            )
        )

        # ----------------------------------------------------
        # Metadados da ohsome / OSM
        # ----------------------------------------------------

        if atributo.startswith("@"):

            presenca_metadados[
                atributo
            ] += 1

            if atributo not in valores_metadados:

                valores_metadados[
                    atributo
                ] = Counter()

            valores_metadados[
                atributo
            ][
                valor_normalizado
            ] += 1

        # ----------------------------------------------------
        # Atributos / tags OSM
        # ----------------------------------------------------

        else:

            presenca_atributos[
                atributo
            ] += 1

            if atributo not in valores_atributos:

                valores_atributos[
                    atributo
                ] = Counter()

            valores_atributos[
                atributo
            ][
                valor_normalizado
            ] += 1


# ============================================================
# 7. PRESENÇA DOS ATRIBUTOS OSM
# ============================================================

linhas_atributos = []


for atributo, quantidade in sorted(
    presenca_atributos.items(),
    key=lambda item: (
        -item[1],
        item[0],
    ),
):

    valores_distintos = len(
        valores_atributos.get(
            atributo,
            {},
        )
    )

    linhas_atributos.append(
        {
            "atributo":
                atributo,
            "objetos_com_atributo":
                quantidade,
            "total_objetos":
                total_feicoes,
            "percentual_presenca":
                percentual(
                    quantidade,
                    total_feicoes,
                ),
            "valores_distintos":
                valores_distintos,
        }
    )


# ============================================================
# 8. FREQUÊNCIA DOS VALORES DOS ATRIBUTOS
# ============================================================

linhas_valores = []


for atributo in sorted(
    valores_atributos
):

    contador = valores_atributos[
        atributo
    ]

    total_com_atributo = sum(
        contador.values()
    )

    for valor, quantidade in sorted(
        contador.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    ):

        linhas_valores.append(
            {
                "atributo":
                    atributo,
                "valor":
                    valor,
                "quantidade":
                    quantidade,
                "total_com_atributo":
                    total_com_atributo,
                "percentual_dentro_atributo":
                    percentual(
                        quantidade,
                        total_com_atributo,
                    ),
            }
        )


# ============================================================
# 9. INVENTÁRIO DOS METADADOS
# ============================================================

linhas_metadados = []


for atributo, quantidade in sorted(
    presenca_metadados.items(),
    key=lambda item: (
        -item[1],
        item[0],
    ),
):

    linhas_metadados.append(
        {
            "metadado":
                atributo,
            "objetos_com_metadado":
                quantidade,
            "total_objetos":
                total_feicoes,
            "percentual_presenca":
                percentual(
                    quantidade,
                    total_feicoes,
                ),
            "valores_distintos":
                len(
                    valores_metadados.get(
                        atributo,
                        {},
                    )
                ),
        }
    )


# ============================================================
# 10. ATRIBUTOS POR CLASSE HIGHWAY
# ============================================================

total_por_highway = Counter()

atributos_por_highway = {}

valores_por_highway = {}


for feature in feicoes:

    propriedades = feature.get(
        "properties",
        {},
    )

    highway = propriedades.get(
        "highway"
    )

    if not valor_preenchido(
        highway
    ):
        continue

    highway = str(
        highway
    ).strip()

    total_por_highway[
        highway
    ] += 1

    if highway not in atributos_por_highway:

        atributos_por_highway[
            highway
        ] = Counter()

    if highway not in valores_por_highway:

        valores_por_highway[
            highway
        ] = {}


    for atributo, valor in (
        propriedades.items()
    ):

        # Metadados da ohsome
        if atributo.startswith("@"):
            continue

        # highway é utilizado como variável
        # de agrupamento e não como atributo
        if atributo == "highway":
            continue

        if not valor_preenchido(
            valor
        ):
            continue

        valor_normalizado = (
            normalizar_valor(
                valor
            )
        )

        # Presença do atributo dentro
        # da classe highway
        atributos_por_highway[
            highway
        ][
            atributo
        ] += 1

        # Valores observados
        if atributo not in valores_por_highway[
            highway
        ]:

            valores_por_highway[
                highway
            ][
                atributo
            ] = Counter()

        valores_por_highway[
            highway
        ][
            atributo
        ][
            valor_normalizado
        ] += 1


# ============================================================
# 11. TABELA HIGHWAY × ATRIBUTOS
# ============================================================

linhas_highway_atributos = []


for highway, total_classe in sorted(
    total_por_highway.items(),
    key=lambda item: (
        -item[1],
        item[0],
    ),
):

    contador_atributos = (
        atributos_por_highway[
            highway
        ]
    )

    for atributo, quantidade in sorted(
        contador_atributos.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    ):

        linhas_highway_atributos.append(
            {
                "highway":
                    highway,
                "total_classe":
                    total_classe,
                "atributo":
                    atributo,
                "objetos_com_atributo":
                    quantidade,
                "percentual_na_classe":
                    percentual(
                        quantidade,
                        total_classe,
                    ),
            }
        )


# ============================================================
# 12. TABELA HIGHWAY × ATRIBUTOS × VALORES
# ============================================================

linhas_highway_valores = []


for highway, total_classe in sorted(
    total_por_highway.items(),
    key=lambda item: (
        -item[1],
        item[0],
    ),
):

    atributos = valores_por_highway[
        highway
    ]

    for atributo in sorted(
        atributos
    ):

        contador_valores = atributos[
            atributo
        ]

        total_com_atributo = sum(
            contador_valores.values()
        )

        for valor, quantidade in sorted(
            contador_valores.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        ):

            linhas_highway_valores.append(
                {
                    "highway":
                        highway,
                    "total_classe":
                        total_classe,
                    "atributo":
                        atributo,
                    "valor":
                        valor,
                    "quantidade":
                        quantidade,
                    "total_com_atributo":
                        total_com_atributo,
                    "percentual_dentro_atributo":
                        percentual(
                            quantidade,
                            total_com_atributo,
                        ),
                }
            )


# ============================================================
# 13. GRAVAÇÃO DOS RESULTADOS
# ============================================================

salvar_csv(
    OUTPUT_GEOMETRIAS,
    linhas_geometrias,
    [
        "tipo_geometria",
        "quantidade",
        "percentual_total",
    ],
)


salvar_csv(
    OUTPUT_ATRIBUTOS,
    linhas_atributos,
    [
        "atributo",
        "objetos_com_atributo",
        "total_objetos",
        "percentual_presenca",
        "valores_distintos",
    ],
)


salvar_csv(
    OUTPUT_VALORES,
    linhas_valores,
    [
        "atributo",
        "valor",
        "quantidade",
        "total_com_atributo",
        "percentual_dentro_atributo",
    ],
)


salvar_csv(
    OUTPUT_METADADOS,
    linhas_metadados,
    [
        "metadado",
        "objetos_com_metadado",
        "total_objetos",
        "percentual_presenca",
        "valores_distintos",
    ],
)


salvar_csv(
    OUTPUT_HIGHWAY_ATRIBUTOS,
    linhas_highway_atributos,
    [
        "highway",
        "total_classe",
        "atributo",
        "objetos_com_atributo",
        "percentual_na_classe",
    ],
)


salvar_csv(
    OUTPUT_HIGHWAY_VALORES,
    linhas_highway_valores,
    [
        "highway",
        "total_classe",
        "atributo",
        "valor",
        "quantidade",
        "total_com_atributo",
        "percentual_dentro_atributo",
    ],
)


# ============================================================
# 14. RESULTADOS NO TERMINAL
# ============================================================

print()
print(
    "ANÁLISE EXPLORATÓRIA GERAL "
    "DA BASE OSM"
)

print("=" * 80)

print()
print(
    f"Total de objetos recuperados: "
    f"{total_feicoes}"
)


# ------------------------------------------------------------
# Geometrias
# ------------------------------------------------------------

print()
print("GEOMETRIAS")
print("-" * 80)


for linha in linhas_geometrias:

    print(
        f"{linha['tipo_geometria']:<25}"
        f"{linha['quantidade']:>5} "
        f"({linha['percentual_total']:>5.1f}%)"
    )


# ------------------------------------------------------------
# Atributos gerais
# ------------------------------------------------------------

print()
print("ATRIBUTOS OSM ENCONTRADOS")
print("-" * 80)


for linha in linhas_atributos:

    print(
        f"{linha['atributo']:<32}"
        f"{linha['objetos_com_atributo']:>5}/"
        f"{linha['total_objetos']:<5} "
        f"({linha['percentual_presenca']:>5.1f}%) "
        f"valores distintos: "
        f"{linha['valores_distintos']}"
    )


# ------------------------------------------------------------
# Classes highway
# ------------------------------------------------------------

print()
print("CLASSES highway=*")
print("-" * 80)


for highway, quantidade in sorted(
    total_por_highway.items(),
    key=lambda item: (
        -item[1],
        item[0],
    ),
):

    print(
        f"{highway:<30}"
        f"{quantidade:>5} "
        f"({percentual(quantidade, total_feicoes):>5.1f}%)"
    )


# ------------------------------------------------------------
# Metadados
# ------------------------------------------------------------

print()
print("METADADOS")
print("-" * 80)


for linha in linhas_metadados:

    print(
        f"{linha['metadado']:<32}"
        f"{linha['objetos_com_metadado']:>5}/"
        f"{linha['total_objetos']:<5} "
        f"({linha['percentual_presenca']:>5.1f}%)"
    )


# ------------------------------------------------------------
# Arquivos gerados
# ------------------------------------------------------------

print()
print("=" * 80)

print("Arquivos gerados:")

print(OUTPUT_GEOMETRIAS)
print(OUTPUT_ATRIBUTOS)
print(OUTPUT_VALORES)
print(OUTPUT_METADADOS)
print(OUTPUT_HIGHWAY_ATRIBUTOS)
print(OUTPUT_HIGHWAY_VALORES)

print()