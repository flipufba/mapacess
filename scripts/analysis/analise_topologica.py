from pathlib import Path
import csv
import json

from shapely.geometry import shape, Point


# ============================================================
# 1. CAMINHOS
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[2]

SNAPSHOTS_DIR = (
    REPO_ROOT
    / "data"
    / "derived"
    / "osm"
    / "snapshots"
)

T0_PATH = (
    SNAPSHOTS_DIR
    / "osm_centenario_filt_2025-11-18.geojson"
)

T1_PATH = (
    SNAPSHOTS_DIR
    / "osm_centenario_filt_2026-03-01.geojson"
)

RESULTS_DIR = (
    REPO_ROOT
    / "results"
    / "tables"
)

OUTPUT_RESUMO = (
    RESULTS_DIR
    / "relacoes_topologicas_t0_t1.csv"
)

OUTPUT_TRAVESSIAS = (
    RESULTS_DIR
    / "topologia_travessias_t0_t1.csv"
)

OUTPUT_CALCADAS = (
    RESULTS_DIR
    / "topologia_calcadas_t0_t1.csv"
)

OUTPUT_PONTOS = (
    RESULTS_DIR
    / "topologia_pontos_t0_t1.csv"
)


# ============================================================
# 2. FUNÇÕES AUXILIARES
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
            f"Arquivo não é FeatureCollection: {caminho}"
        )

    return dados


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


def percentual(
    numerador,
    denominador,
):

    if denominador == 0:
        return ""

    return round(
        numerador
        / denominador
        * 100,
        1,
    )


def extremos(geom):

    if geom.geom_type == "LineString":

        coords = list(
            geom.coords
        )

        return (
            Point(coords[0]),
            Point(coords[-1]),
        )

    if geom.geom_type == "MultiLineString":

        partes = list(
            geom.geoms
        )

        return (
            Point(
                list(
                    partes[0].coords
                )[0]
            ),
            Point(
                list(
                    partes[-1].coords
                )[-1]
            ),
        )

    raise ValueError(
        f"Geometria linear inesperada: "
        f"{geom.geom_type}"
    )


# ============================================================
# 3. CLASSIFICAÇÃO DAS FEIÇÕES
# ============================================================

def separar_classes(dados):

    calcadas = []
    travessias = []
    kerbs = []
    nos_crossing = []

    for feature in dados["features"]:

        props = feature.get(
            "properties",
            {},
        )

        geometria_json = feature.get(
            "geometry"
        )

        if geometria_json is None:
            continue

        geom = shape(
            geometria_json
        )

        osm_id = props.get(
            "@osmId"
        )

        highway = props.get(
            "highway"
        )

        footway = props.get(
            "footway"
        )

        barrier = props.get(
            "barrier"
        )


        if (
            geom.geom_type
            in {"LineString", "MultiLineString"}
            and highway == "footway"
            and footway == "sidewalk"
        ):
            calcadas.append(
                (osm_id, geom)
            )

        elif (
            geom.geom_type
            in {"LineString", "MultiLineString"}
            and highway == "footway"
            and footway == "crossing"
        ):
            travessias.append(
                (osm_id, geom)
            )

        elif (
            geom.geom_type == "Point"
            and barrier == "kerb"
        ):
            kerbs.append(
                (osm_id, geom)
            )

        elif (
            geom.geom_type == "Point"
            and highway == "crossing"
        ):
            nos_crossing.append(
                (osm_id, geom)
            )

    return (
        calcadas,
        travessias,
        kerbs,
        nos_crossing,
    )


# ============================================================
# 4. ANÁLISE DAS TRAVESSIAS
# ============================================================

def analisar_travessias(
    estado,
    travessias,
    calcadas,
    kerbs,
    nos_crossing,
):

    linhas = []

    for osm_id, geom in travessias:

        ponta1, ponta2 = extremos(
            geom
        )

        ponta1_calcada = any(
            ponta1.intersects(
                calcada_geom
            )
            for _, calcada_geom
            in calcadas
        )

        ponta2_calcada = any(
            ponta2.intersects(
                calcada_geom
            )
            for _, calcada_geom
            in calcadas
        )

        n_extremos_conectados = sum(
            [
                ponta1_calcada,
                ponta2_calcada,
            ]
        )

        calcadas_intersectadas = sum(
            geom.intersects(
                calcada_geom
            )
            for _, calcada_geom
            in calcadas
        )

        kerbs_sobre_linha = sum(
            ponto.intersects(
                geom
            )
            for _, ponto
            in kerbs
        )

        nos_crossing_sobre_linha = sum(
            ponto.intersects(
                geom
            )
            for _, ponto
            in nos_crossing
        )

        linhas.append(
            {
                "estado":
                    estado,

                "osm_id":
                    osm_id,

                "calcadas_intersectadas":
                    calcadas_intersectadas,

                "kerbs_sobre_travessia":
                    kerbs_sobre_linha,

                "nos_crossing_sobre_travessia":
                    nos_crossing_sobre_linha,

                "extremidade_1_em_calcada":
                    ponta1_calcada,

                "extremidade_2_em_calcada":
                    ponta2_calcada,

                "extremidades_conectadas_calcadas":
                    n_extremos_conectados,
            }
        )

    return linhas


# ============================================================
# 5. ANÁLISE DAS CALÇADAS
# ============================================================

def analisar_calcadas(
    estado,
    calcadas,
    travessias,
):

    linhas = []

    for osm_id, geom in calcadas:

        ponta1, ponta2 = extremos(
            geom
        )

        resultados_extremos = []

        for ponto in (
            ponta1,
            ponta2,
        ):

            toca_calcada = any(
                outro_id != osm_id
                and ponto.intersects(
                    outra_geom
                )
                for outro_id, outra_geom
                in calcadas
            )

            toca_travessia = any(
                ponto.intersects(
                    travessia_geom
                )
                for _, travessia_geom
                in travessias
            )

            conectado_rede = (
                toca_calcada
                or toca_travessia
            )

            resultados_extremos.append(
                {
                    "calcada":
                        toca_calcada,

                    "travessia":
                        toca_travessia,

                    "rede":
                        conectado_rede,
                }
            )

        n_conectados = sum(
            resultado["rede"]
            for resultado
            in resultados_extremos
        )

        linhas.append(
            {
                "estado":
                    estado,

                "osm_id":
                    osm_id,

                "extremidade_1_outra_calcada":
                    resultados_extremos[0]["calcada"],

                "extremidade_1_travessia":
                    resultados_extremos[0]["travessia"],

                "extremidade_1_rede":
                    resultados_extremos[0]["rede"],

                "extremidade_2_outra_calcada":
                    resultados_extremos[1]["calcada"],

                "extremidade_2_travessia":
                    resultados_extremos[1]["travessia"],

                "extremidade_2_rede":
                    resultados_extremos[1]["rede"],

                "extremidades_conectadas_rede":
                    n_conectados,
            }
        )

    return linhas


# ============================================================
# 6. ANÁLISE DOS PONTOS
# ============================================================

def analisar_pontos(
    estado,
    kerbs,
    nos_crossing,
    travessias,
):

    linhas = []


    for osm_id, ponto in kerbs:

        sobre_travessia = any(
            ponto.intersects(
                travessia_geom
            )
            for _, travessia_geom
            in travessias
        )

        linhas.append(
            {
                "estado":
                    estado,

                "osm_id":
                    osm_id,

                "classe":
                    "no_meio_fio",

                "sobre_travessia_linear":
                    sobre_travessia,
            }
        )


    for osm_id, ponto in nos_crossing:

        sobre_travessia = any(
            ponto.intersects(
                travessia_geom
            )
            for _, travessia_geom
            in travessias
        )

        linhas.append(
            {
                "estado":
                    estado,

                "osm_id":
                    osm_id,

                "classe":
                    "no_travessia",

                "sobre_travessia_linear":
                    sobre_travessia,
            }
        )

    return linhas


# ============================================================
# 7. RESUMO
# ============================================================

def gerar_resumo(
    estado,
    calcadas,
    travessias,
    kerbs,
    nos_crossing,
    linhas_calcadas,
    linhas_travessias,
    linhas_pontos,
):

    total_extremos_travessias = (
        len(travessias)
        * 2
    )

    extremos_travessias_conectados = sum(
        linha[
            "extremidades_conectadas_calcadas"
        ]
        for linha
        in linhas_travessias
    )

    travessias_2 = sum(
        linha[
            "extremidades_conectadas_calcadas"
        ] == 2
        for linha
        in linhas_travessias
    )

    travessias_1 = sum(
        linha[
            "extremidades_conectadas_calcadas"
        ] == 1
        for linha
        in linhas_travessias
    )

    travessias_0 = sum(
        linha[
            "extremidades_conectadas_calcadas"
        ] == 0
        for linha
        in linhas_travessias
    )


    total_extremos_calcadas = (
        len(calcadas)
        * 2
    )

    extremos_calcadas_conectados = sum(
        linha[
            "extremidades_conectadas_rede"
        ]
        for linha
        in linhas_calcadas
    )

    calcadas_2 = sum(
        linha[
            "extremidades_conectadas_rede"
        ] == 2
        for linha
        in linhas_calcadas
    )

    calcadas_1 = sum(
        linha[
            "extremidades_conectadas_rede"
        ] == 1
        for linha
        in linhas_calcadas
    )

    calcadas_0 = sum(
        linha[
            "extremidades_conectadas_rede"
        ] == 0
        for linha
        in linhas_calcadas
    )


    kerbs_sobre = sum(
        linha[
            "sobre_travessia_linear"
        ]
        for linha
        in linhas_pontos
        if linha["classe"]
        == "no_meio_fio"
    )

    crossing_sobre = sum(
        linha[
            "sobre_travessia_linear"
        ]
        for linha
        in linhas_pontos
        if linha["classe"]
        == "no_travessia"
    )


    return {
        "estado":
            estado,

        "total_calcadas":
            len(calcadas),

        "extremidades_calcadas":
            total_extremos_calcadas,

        "extremidades_calcadas_conectadas_rede":
            extremos_calcadas_conectados,

        "percentual_extremidades_calcadas_conectadas":
            percentual(
                extremos_calcadas_conectados,
                total_extremos_calcadas,
            ),

        "calcadas_2_extremidades_conectadas":
            calcadas_2,

        "calcadas_1_extremidade_conectada":
            calcadas_1,

        "calcadas_0_extremidades_conectadas":
            calcadas_0,

        "total_travessias":
            len(travessias),

        "extremidades_travessias":
            total_extremos_travessias,

        "extremidades_travessias_em_calcadas":
            extremos_travessias_conectados,

        "percentual_extremidades_travessias_em_calcadas":
            percentual(
                extremos_travessias_conectados,
                total_extremos_travessias,
            ),

        "travessias_2_extremidades_em_calcadas":
            travessias_2,

        "travessias_1_extremidade_em_calcada":
            travessias_1,

        "travessias_0_extremidades_em_calcadas":
            travessias_0,

        "total_kerbs":
            len(kerbs),

        "kerbs_sobre_travessia":
            kerbs_sobre,

        "kerbs_sem_correspondencia_travessia":
            len(kerbs)
            - kerbs_sobre,

        "percentual_kerbs_sobre_travessia":
            percentual(
                kerbs_sobre,
                len(kerbs),
            ),

        "total_nos_crossing":
            len(nos_crossing),

        "nos_crossing_sobre_travessia":
            crossing_sobre,

        "nos_crossing_sem_correspondencia_travessia":
            len(nos_crossing)
            - crossing_sobre,

        "percentual_nos_crossing_sobre_travessia":
            percentual(
                crossing_sobre,
                len(nos_crossing),
            ),
    }


# ============================================================
# 8. EXECUÇÃO POR ESTADO
# ============================================================

def analisar_estado(
    estado,
    caminho,
):

    dados = carregar_geojson(
        caminho
    )

    (
        calcadas,
        travessias,
        kerbs,
        nos_crossing,
    ) = separar_classes(
        dados
    )


    linhas_travessias = analisar_travessias(
        estado,
        travessias,
        calcadas,
        kerbs,
        nos_crossing,
    )


    linhas_calcadas = analisar_calcadas(
        estado,
        calcadas,
        travessias,
    )


    linhas_pontos = analisar_pontos(
        estado,
        kerbs,
        nos_crossing,
        travessias,
    )


    resumo = gerar_resumo(
        estado,
        calcadas,
        travessias,
        kerbs,
        nos_crossing,
        linhas_calcadas,
        linhas_travessias,
        linhas_pontos,
    )


    return (
        resumo,
        linhas_travessias,
        linhas_calcadas,
        linhas_pontos,
    )


(
    resumo_t0,
    travessias_t0,
    calcadas_t0,
    pontos_t0,
) = analisar_estado(
    "T0",
    T0_PATH,
)


(
    resumo_t1,
    travessias_t1,
    calcadas_t1,
    pontos_t1,
) = analisar_estado(
    "T1",
    T1_PATH,
)


# ============================================================
# 9. SALVAMENTO
# ============================================================

resumos = [
    resumo_t0,
    resumo_t1,
]


salvar_csv(
    OUTPUT_RESUMO,
    resumos,
    list(
        resumos[0].keys()
    ),
)


salvar_csv(
    OUTPUT_TRAVESSIAS,
    travessias_t0
    + travessias_t1,
    [
        "estado",
        "osm_id",
        "calcadas_intersectadas",
        "kerbs_sobre_travessia",
        "nos_crossing_sobre_travessia",
        "extremidade_1_em_calcada",
        "extremidade_2_em_calcada",
        "extremidades_conectadas_calcadas",
    ],
)


salvar_csv(
    OUTPUT_CALCADAS,
    calcadas_t0
    + calcadas_t1,
    [
        "estado",
        "osm_id",
        "extremidade_1_outra_calcada",
        "extremidade_1_travessia",
        "extremidade_1_rede",
        "extremidade_2_outra_calcada",
        "extremidade_2_travessia",
        "extremidade_2_rede",
        "extremidades_conectadas_rede",
    ],
)


salvar_csv(
    OUTPUT_PONTOS,
    pontos_t0
    + pontos_t1,
    [
        "estado",
        "osm_id",
        "classe",
        "sobre_travessia_linear",
    ],
)


# ============================================================
# 10. RESULTADOS NO TERMINAL
# ============================================================

print()

print(
    "ANÁLISE DAS RELAÇÕES "
    "GEOMÉTRICO-TOPOLÓGICAS — T0 × T1"
)

print("=" * 80)


for resumo in resumos:

    estado = resumo[
        "estado"
    ]

    print()
    print(estado)
    print("-" * 80)

    print(
        "Calçadas:",
        resumo[
            "total_calcadas"
        ],
    )

    print(
        "Extremidades de calçadas conectadas à rede:",
        f"{resumo['extremidades_calcadas_conectadas_rede']}/"
        f"{resumo['extremidades_calcadas']}",
        (
            "n/a"
            if resumo[
                "percentual_extremidades_calcadas_conectadas"
            ] == ""
            else
            f"({resumo['percentual_extremidades_calcadas_conectadas']:.1f}%)"
        ),
    )

    print(
        "Calçadas com 2 / 1 / 0 extremidades conectadas:",
        resumo[
            "calcadas_2_extremidades_conectadas"
        ],
        "/",
        resumo[
            "calcadas_1_extremidade_conectada"
        ],
        "/",
        resumo[
            "calcadas_0_extremidades_conectadas"
        ],
    )

    print()

    print(
        "Travessias:",
        resumo[
            "total_travessias"
        ],
    )

    print(
        "Extremidades de travessias em calçadas:",
        f"{resumo['extremidades_travessias_em_calcadas']}/"
        f"{resumo['extremidades_travessias']}",
        (
            "n/a"
            if resumo[
                "percentual_extremidades_travessias_em_calcadas"
            ] == ""
            else
            f"({resumo['percentual_extremidades_travessias_em_calcadas']:.1f}%)"
        ),
    )

    print(
        "Travessias com 2 / 1 / 0 extremidades em calçadas:",
        resumo[
            "travessias_2_extremidades_em_calcadas"
        ],
        "/",
        resumo[
            "travessias_1_extremidade_em_calcada"
        ],
        "/",
        resumo[
            "travessias_0_extremidades_em_calcadas"
        ],
    )

    print()

    print(
        "Nós de meio-fio sobre travessia:",
        f"{resumo['kerbs_sobre_travessia']}/"
        f"{resumo['total_kerbs']}",
        (
            "n/a"
            if resumo[
                "percentual_kerbs_sobre_travessia"
            ] == ""
            else
            f"({resumo['percentual_kerbs_sobre_travessia']:.1f}%)"
        ),
    )

    print(
        "Nós de meio-fio sem correspondência:",
        resumo[
            "kerbs_sem_correspondencia_travessia"
        ],
    )

    print()

    print(
        "Nós highway=crossing sobre travessia:",
        f"{resumo['nos_crossing_sobre_travessia']}/"
        f"{resumo['total_nos_crossing']}",
        (
            "n/a"
            if resumo[
                "percentual_nos_crossing_sobre_travessia"
            ] == ""
            else
            f"({resumo['percentual_nos_crossing_sobre_travessia']:.1f}%)"
        ),
    )

    print(
        "Nós highway=crossing sem correspondência:",
        resumo[
            "nos_crossing_sem_correspondencia_travessia"
        ],
    )


print()
print("=" * 80)

print("Arquivos gerados:")
print(OUTPUT_RESUMO)
print(OUTPUT_TRAVESSIAS)
print(OUTPUT_CALCADAS)
print(OUTPUT_PONTOS)

print()