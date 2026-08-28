from pathlib import Path
from collections import Counter, defaultdict
import csv
import json

from shapely.geometry import shape, Point


# ============================================================
# 1. CAMINHOS
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    REPO_ROOT
    / "data"
    / "derived"
    / "osm"
    / "snapshots"
    / "osm_centenario_filt_2026-03-01.geojson"
)

RESULTS_DIR = (
    REPO_ROOT
    / "results"
    / "tables"
)

OUTPUT_RESUMO = (
    RESULTS_DIR
    / "resumo_condicoes_rede_pedonal_t1.csv"
)

OUTPUT_FEICOES = (
    RESULTS_DIR
    / "condicoes_por_feicao_rede_pedonal_t1.csv"
)


# ============================================================
# 2. NÍVEIS DE EVIDÊNCIA
# ============================================================

IMPEDIMENTO = (
    "impedimento_restricao_identificada"
)

OPORTUNIDADE = (
    "condicao_critica_oportunidade_melhoria"
)

SEM_EVIDENCIA_NEGATIVA = (
    "sem_evidencia_negativa_no_criterio"
)

RECURSO_PRESENTE = (
    "recurso_acessibilidade_presente"
)

INDETERMINADO = (
    "indeterminado"
)

CARACTERIZACAO = (
    "caracterizacao_contextual"
)

QUALIDADE_DADO = (
    "qualidade_dado"
)

REQUER_INSPECAO = (
    "requer_inspecao_interpretativa"
)


# ============================================================
# 3. FUNÇÕES AUXILIARES
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

        dados = json.load(
            arquivo
        )

    if dados.get("type") != "FeatureCollection":

        raise ValueError(
            "O arquivo informado não é "
            "um FeatureCollection válido."
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
        writer.writerows(
            linhas
        )


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


def valor_preenchido(valor):

    if valor is None:
        return False

    if isinstance(valor, str):
        return valor.strip() != ""

    return True


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
        f"Geometria inesperada: "
        f"{geom.geom_type}"
    )


# ============================================================
# 4. LEITURA E SEPARAÇÃO DAS CLASSES
# ============================================================

dados = carregar_geojson(
    INPUT_PATH
)

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

    registro = {

        "osm_id":
            props.get("@osmId"),

        "props":
            props,

        "geom":
            geom,
    }

    highway = props.get(
        "highway"
    )

    footway = props.get(
        "footway"
    )

    barrier = props.get(
        "barrier"
    )


    # --------------------------------------------------------
    # Calçadas
    # --------------------------------------------------------

    if (
        geom.geom_type
        in {"LineString", "MultiLineString"}
        and highway == "footway"
        and footway == "sidewalk"
    ):

        calcadas.append(
            registro
        )


    # --------------------------------------------------------
    # Travessias lineares
    # --------------------------------------------------------

    elif (
        geom.geom_type
        in {"LineString", "MultiLineString"}
        and highway == "footway"
        and footway == "crossing"
    ):

        travessias.append(
            registro
        )


    # --------------------------------------------------------
    # Nós de meio-fio
    # --------------------------------------------------------

    elif (
        geom.geom_type == "Point"
        and barrier == "kerb"
    ):

        kerbs.append(
            registro
        )


    # --------------------------------------------------------
    # Nós de travessia
    # --------------------------------------------------------

    elif (
        geom.geom_type == "Point"
        and highway == "crossing"
    ):

        nos_crossing.append(
            registro
        )


# ============================================================
# 5. RELAÇÕES GEOMÉTRICAS
# ============================================================

# ------------------------------------------------------------
# 5.1 Nós de meio-fio × travessias lineares
# ------------------------------------------------------------

for kerb in kerbs:

    kerb[
        "sobre_travessia"
    ] = any(

        kerb["geom"].intersects(
            travessia["geom"]
        )

        for travessia
        in travessias
    )


# ------------------------------------------------------------
# 5.2 Nós de travessia × travessias lineares
# ------------------------------------------------------------

for no in nos_crossing:

    no[
        "sobre_travessia"
    ] = any(

        no["geom"].intersects(
            travessia["geom"]
        )

        for travessia
        in travessias
    )


# ------------------------------------------------------------
# 5.3 Extremidades das calçadas
# ------------------------------------------------------------

for calcada in calcadas:

    p1, p2 = extremos(
        calcada["geom"]
    )

    resultados = []

    for ponto in (
        p1,
        p2,
    ):

        toca_outra_calcada = any(

            outra["osm_id"]
            != calcada["osm_id"]

            and ponto.intersects(
                outra["geom"]
            )

            for outra
            in calcadas
        )


        toca_travessia = any(

            ponto.intersects(
                travessia["geom"]
            )

            for travessia
            in travessias
        )


        resultados.append(

            toca_outra_calcada
            or toca_travessia

        )


    calcada[
        "extremidades_conectadas"
    ] = sum(
        resultados
    )


# ------------------------------------------------------------
# 5.4 Extremidades das travessias
# ------------------------------------------------------------

for travessia in travessias:

    p1, p2 = extremos(
        travessia["geom"]
    )

    resultados = []

    for ponto in (
        p1,
        p2,
    ):

        em_calcada = any(

            ponto.intersects(
                calcada["geom"]
            )

            for calcada
            in calcadas
        )


        resultados.append(
            em_calcada
        )


    travessia[
        "extremidades_em_calcadas"
    ] = sum(
        resultados
    )


# ============================================================
# 6. REGISTRO DAS CLASSIFICAÇÕES
# ============================================================

linhas = []


def registrar(
    registro,
    elemento,
    dimensao,
    criterio,
    valor,
    nivel,
    interpretacao,
    total_universo,
):

    linhas.append(
        {

            "osm_id":
                registro["osm_id"],

            "elemento":
                elemento,

            "dimensao":
                dimensao,

            "criterio":
                criterio,

            "valor_observado":
                valor,

            "nivel_evidencia":
                nivel,

            "interpretacao":
                interpretacao,

            "total_universo_criterio":
                total_universo,

        }
    )


# ============================================================
# 7. CALÇADAS
# ============================================================

TOTAL_CALCADAS = len(
    calcadas
)


for registro in calcadas:

    props = registro[
        "props"
    ]


    # --------------------------------------------------------
    # 7.1 Mobilidade física — smoothness
    # --------------------------------------------------------

    smoothness = props.get(
        "smoothness"
    )


    if not valor_preenchido(
        smoothness
    ):

        registrar(

            registro,
            "calcada",
            "mobilidade_fisica",
            "smoothness",
            "",
            INDETERMINADO,

            (
                "Condição aparente do pavimento "
                "não determinada."
            ),

            TOTAL_CALCADAS,
        )


    elif smoothness == "bad":

        registrar(

            registro,
            "calcada",
            "mobilidade_fisica",
            "smoothness",
            smoothness,
            IMPEDIMENTO,

            (
                "Condição ruim do pavimento, "
                "capaz de dificultar o deslocamento "
                "de usuários com mobilidade reduzida."
            ),

            TOTAL_CALCADAS,
        )


    elif smoothness == "intermediate":

        registrar(

            registro,
            "calcada",
            "mobilidade_fisica",
            "smoothness",
            smoothness,
            OPORTUNIDADE,

            (
                "Condição intermediária do pavimento; "
                "recomenda-se avaliação ou inspeção "
                "mais detalhada."
            ),

            TOTAL_CALCADAS,
        )


    elif smoothness in {
        "good",
        "excellent",
    }:

        registrar(

            registro,
            "calcada",
            "mobilidade_fisica",
            "smoothness",
            smoothness,
            SEM_EVIDENCIA_NEGATIVA,

            (
                "Não foi identificada condição "
                "desfavorável neste critério."
            ),

            TOTAL_CALCADAS,
        )


    else:

        registrar(

            registro,
            "calcada",
            "mobilidade_fisica",
            "smoothness",
            smoothness,
            CARACTERIZACAO,

            (
                "Valor registrado para caracterização, "
                "sem classificação automática "
                "de impedimento."
            ),

            TOTAL_CALCADAS,
        )


    # --------------------------------------------------------
    # 7.2 Característica da superfície
    # --------------------------------------------------------

    surface = props.get(
        "surface"
    )


    if not valor_preenchido(
        surface
    ):

        registrar(

            registro,
            "calcada",
            "superficie",
            "surface",
            "",
            INDETERMINADO,

            (
                "Material da superfície "
                "não informado."
            ),

            TOTAL_CALCADAS,
        )


    elif surface in {
        "paving_stones",
        "sett",
    }:

        registrar(

            registro,
            "calcada",
            "superficie",
            "surface",
            surface,
            OPORTUNIDADE,

            (
                "Material que pode demandar inspeção "
                "quanto à regularidade e trepidação. "
                "O material isoladamente não determina "
                "uma barreira."
            ),

            TOTAL_CALCADAS,
        )


    elif surface in {
        "concreto",
        "concre",
    }:

        registrar(

            registro,
            "calcada",
            "qualidade_informacional",
            "surface",
            surface,
            QUALIDADE_DADO,

            (
                "Valor não padronizado em relação "
                "à etiquetagem utilizada no conjunto "
                "analisado; recomenda-se normalização."
            ),

            TOTAL_CALCADAS,
        )


    else:

        registrar(

            registro,
            "calcada",
            "superficie",
            "surface",
            surface,
            CARACTERIZACAO,

            (
                "Material da superfície registrado "
                "para caracterização física do trecho."
            ),

            TOTAL_CALCADAS,
        )


    # --------------------------------------------------------
    # 7.3 Orientação visual/sensorial
    # --------------------------------------------------------

    tactile = props.get(
        "tactile_paving"
    )


    if not valor_preenchido(
        tactile
    ):

        registrar(

            registro,
            "calcada",
            "orientacao_visual_sensorial",
            "tactile_paving",
            "",
            INDETERMINADO,

            (
                "Não há informação suficiente para "
                "determinar a presença de orientação "
                "tátil no trecho."
            ),

            TOTAL_CALCADAS,
        )


    elif tactile == "no":

        registrar(

            registro,
            "calcada",
            "orientacao_visual_sensorial",
            "tactile_paving",
            tactile,
            IMPEDIMENTO,

            (
                "Ausência explicitamente registrada "
                "de piso tátil, interpretada no estudo "
                "como restrição à orientação sensorial."
            ),

            TOTAL_CALCADAS,
        )


    elif tactile == "yes":

        registrar(

            registro,
            "calcada",
            "orientacao_visual_sensorial",
            "tactile_paving",
            tactile,
            RECURSO_PRESENTE,

            (
                "Presença registrada de recurso "
                "de orientação tátil."
            ),

            TOTAL_CALCADAS,
        )


    else:

        registrar(

            registro,
            "calcada",
            "orientacao_visual_sensorial",
            "tactile_paving",
            tactile,
            CARACTERIZACAO,

            (
                "Valor registrado para caracterização "
                "do recurso tátil."
            ),

            TOTAL_CALCADAS,
        )


    # --------------------------------------------------------
    # 7.4 Continuidade da rede
    # --------------------------------------------------------

    conectadas = registro[
        "extremidades_conectadas"
    ]


    if conectadas == 2:

        registrar(

            registro,
            "calcada",
            "continuidade_rede",
            "extremidades_conectadas_rede",
            "2_de_2",
            SEM_EVIDENCIA_NEGATIVA,

            (
                "As duas extremidades apresentam "
                "correspondência geométrica com outra "
                "calçada ou travessia."
            ),

            TOTAL_CALCADAS,
        )


    else:

        registrar(

            registro,
            "calcada",
            "continuidade_rede",
            "extremidades_conectadas_rede",
            f"{conectadas}_de_2",
            REQUER_INSPECAO,

            (
                "Uma ou mais extremidades não apresentam "
                "correspondência geométrica no conjunto "
                "analisado. A situação não é tratada "
                "automaticamente como erro."
            ),

            TOTAL_CALCADAS,
        )


# ============================================================
# 8. TRAVESSIAS LINEARES
# ============================================================

TOTAL_TRAVESSIAS = len(
    travessias
)


for registro in travessias:

    props = registro[
        "props"
    ]


    # --------------------------------------------------------
    # 8.1 Mobilidade física — wheelchair
    # --------------------------------------------------------

    wheelchair = props.get(
        "wheelchair"
    )


    if not valor_preenchido(
        wheelchair
    ):

        registrar(

            registro,
            "travessia_linear",
            "mobilidade_fisica",
            "wheelchair",
            "",
            INDETERMINADO,

            (
                "A condição de utilização por cadeira "
                "de rodas não foi determinada."
            ),

            TOTAL_TRAVESSIAS,
        )


    elif wheelchair in {
        "no",
        "limited",
    }:

        registrar(

            registro,
            "travessia_linear",
            "mobilidade_fisica",
            "wheelchair",
            wheelchair,
            IMPEDIMENTO,

            (
                "Restrição de mobilidade registrada "
                "para usuários de cadeira de rodas."
            ),

            TOTAL_TRAVESSIAS,
        )


    elif wheelchair == "yes":

        registrar(

            registro,
            "travessia_linear",
            "mobilidade_fisica",
            "wheelchair",
            wheelchair,
            SEM_EVIDENCIA_NEGATIVA,

            (
                "Não foi registrada restrição "
                "para cadeira de rodas neste critério."
            ),

            TOTAL_TRAVESSIAS,
        )


    else:

        registrar(

            registro,
            "travessia_linear",
            "mobilidade_fisica",
            "wheelchair",
            wheelchair,
            CARACTERIZACAO,

            (
                "Valor registrado sem interpretação "
                "automática de acessibilidade."
            ),

            TOTAL_TRAVESSIAS,
        )


    # --------------------------------------------------------
    # 8.2 Tipo de travessia
    # --------------------------------------------------------

    crossing = props.get(
        "crossing"
    )


    if not valor_preenchido(
        crossing
    ):

        registrar(

            registro,
            "travessia_linear",
            "travessia_seguranca",
            "crossing",
            "",
            INDETERMINADO,

            (
                "Tipo de travessia não informado."
            ),

            TOTAL_TRAVESSIAS,
        )


    elif crossing == "unmarked":

        registrar(

            registro,
            "travessia_linear",
            "travessia_seguranca",
            "crossing",
            crossing,
            OPORTUNIDADE,

            (
                "Travessia explicitamente registrada "
                "como não demarcada."
            ),

            TOTAL_TRAVESSIAS,
        )


    else:

        registrar(

            registro,
            "travessia_linear",
            "travessia_seguranca",
            "crossing",
            crossing,
            CARACTERIZACAO,

            (
                "Tipo de travessia registrado "
                "para caracterização da infraestrutura."
            ),

            TOTAL_TRAVESSIAS,
        )


    # --------------------------------------------------------
    # 8.3 Demarcação da travessia
    # --------------------------------------------------------

    markings = props.get(
        "crossing:markings"
    )


    if not valor_preenchido(
        markings
    ):

        registrar(

            registro,
            "travessia_linear",
            "travessia_seguranca",
            "crossing:markings",
            "",
            INDETERMINADO,

            (
                "Informação de demarcação "
                "da travessia ausente."
            ),

            TOTAL_TRAVESSIAS,
        )


    elif markings == "no":

        registrar(

            registro,
            "travessia_linear",
            "travessia_seguranca",
            "crossing:markings",
            markings,
            OPORTUNIDADE,

            (
                "Ausência explícita de demarcação "
                "da travessia."
            ),

            TOTAL_TRAVESSIAS,
        )


    else:

        registrar(

            registro,
            "travessia_linear",
            "travessia_seguranca",
            "crossing:markings",
            markings,
            CARACTERIZACAO,

            (
                "Demarcação da travessia registrada."
            ),

            TOTAL_TRAVESSIAS,
        )


    # --------------------------------------------------------
    # 8.4 Continuidade com as calçadas
    # --------------------------------------------------------

    conectadas = registro[
        "extremidades_em_calcadas"
    ]


    if conectadas == 2:

        registrar(

            registro,
            "travessia_linear",
            "continuidade_rede",
            "extremidades_em_calcadas",
            "2_de_2",
            SEM_EVIDENCIA_NEGATIVA,

            (
                "As duas extremidades apresentam "
                "correspondência geométrica com calçadas."
            ),

            TOTAL_TRAVESSIAS,
        )


    else:

        registrar(

            registro,
            "travessia_linear",
            "continuidade_rede",
            "extremidades_em_calcadas",
            f"{conectadas}_de_2",
            REQUER_INSPECAO,

            (
                "Uma ou mais extremidades não apresentam "
                "correspondência geométrica com calçada. "
                "A situação requer interpretação."
            ),

            TOTAL_TRAVESSIAS,
        )


# ============================================================
# 9. NÓS DE MEIO-FIO
# ============================================================

TOTAL_KERBS = len(
    kerbs
)


for registro in kerbs:

    props = registro[
        "props"
    ]


    # --------------------------------------------------------
    # 9.1 Tipo de meio-fio
    # --------------------------------------------------------

    kerb = props.get(
        "kerb"
    )


    if not valor_preenchido(
        kerb
    ):

        registrar(

            registro,
            "no_meio_fio",
            "mobilidade_fisica",
            "kerb",
            "",
            INDETERMINADO,

            (
                "Tipo de interface de meio-fio "
                "não determinado."
            ),

            TOTAL_KERBS,
        )


    elif kerb == "raised":

        registrar(

            registro,
            "no_meio_fio",
            "mobilidade_fisica",
            "kerb",
            kerb,
            IMPEDIMENTO,

            (
                "Meio-fio elevado, representando "
                "desnível na transição entre "
                "calçada e via."
            ),

            TOTAL_KERBS,
        )


    elif kerb in {
        "lowered",
        "flush",
    }:

        registrar(

            registro,
            "no_meio_fio",
            "mobilidade_fisica",
            "kerb",
            kerb,
            SEM_EVIDENCIA_NEGATIVA,

            (
                "Não foi identificado desnível "
                "elevado neste critério."
            ),

            TOTAL_KERBS,
        )


    else:

        registrar(

            registro,
            "no_meio_fio",
            "mobilidade_fisica",
            "kerb",
            kerb,
            CARACTERIZACAO,

            (
                "Valor registrado para "
                "caracterização do meio-fio."
            ),

            TOTAL_KERBS,
        )


    # --------------------------------------------------------
    # 9.2 Mobilidade física — wheelchair
    # --------------------------------------------------------

    wheelchair = props.get(
        "wheelchair"
    )


    if not valor_preenchido(
        wheelchair
    ):

        registrar(

            registro,
            "no_meio_fio",
            "mobilidade_fisica",
            "wheelchair",
            "",
            INDETERMINADO,

            (
                "Condição de utilização por cadeira "
                "de rodas não determinada."
            ),

            TOTAL_KERBS,
        )


    elif wheelchair in {
        "no",
        "limited",
    }:

        registrar(

            registro,
            "no_meio_fio",
            "mobilidade_fisica",
            "wheelchair",
            wheelchair,
            IMPEDIMENTO,

            (
                "Restrição de mobilidade registrada "
                "para usuários de cadeira de rodas."
            ),

            TOTAL_KERBS,
        )


    elif wheelchair == "yes":

        registrar(

            registro,
            "no_meio_fio",
            "mobilidade_fisica",
            "wheelchair",
            wheelchair,
            SEM_EVIDENCIA_NEGATIVA,

            (
                "Não foi registrada restrição "
                "para cadeira de rodas neste critério."
            ),

            TOTAL_KERBS,
        )


    else:

        registrar(

            registro,
            "no_meio_fio",
            "mobilidade_fisica",
            "wheelchair",
            wheelchair,
            CARACTERIZACAO,

            (
                "Valor registrado sem interpretação "
                "automática de acessibilidade."
            ),

            TOTAL_KERBS,
        )


    # --------------------------------------------------------
    # 9.3 Orientação visual/sensorial
    # --------------------------------------------------------

    tactile = props.get(
        "tactile_paving"
    )


    if not valor_preenchido(
        tactile
    ):

        registrar(

            registro,
            "no_meio_fio",
            "orientacao_visual_sensorial",
            "tactile_paving",
            "",
            INDETERMINADO,

            (
                "Não há informação suficiente para "
                "determinar a presença de sinalização "
                "tátil na interface."
            ),

            TOTAL_KERBS,
        )


    elif tactile == "no":

        registrar(

            registro,
            "no_meio_fio",
            "orientacao_visual_sensorial",
            "tactile_paving",
            tactile,
            IMPEDIMENTO,

            (
                "Ausência explicitamente registrada "
                "de sinalização tátil na interface "
                "de meio-fio."
            ),

            TOTAL_KERBS,
        )


    elif tactile == "yes":

        registrar(

            registro,
            "no_meio_fio",
            "orientacao_visual_sensorial",
            "tactile_paving",
            tactile,
            RECURSO_PRESENTE,

            (
                "Presença registrada de "
                "sinalização tátil."
            ),

            TOTAL_KERBS,
        )


    else:

        registrar(

            registro,
            "no_meio_fio",
            "orientacao_visual_sensorial",
            "tactile_paving",
            tactile,
            CARACTERIZACAO,

            (
                "Valor registrado para "
                "caracterização tátil."
            ),

            TOTAL_KERBS,
        )


# ============================================================
# 10. REBAIXAMENTO SEM TRAVESSIA LINEAR
# ============================================================

kerbs_rebaixados = [

    registro
    for registro in kerbs

    if registro[
        "props"
    ].get(
        "kerb"
    )
    in {
        "lowered",
        "flush",
    }

]

TOTAL_REBAIXADOS = len(
    kerbs_rebaixados
)


for registro in kerbs_rebaixados:

    if registro[
        "sobre_travessia"
    ]:

        registrar(

            registro,
            "no_meio_fio",
            "configuracao_infraestrutura",
            "rebaixamento_com_travessia_linear",
            "sim",
            SEM_EVIDENCIA_NEGATIVA,

            (
                "O rebaixamento apresenta "
                "correspondência geométrica "
                "com travessia linear."
            ),

            TOTAL_REBAIXADOS,
        )


    else:

        registrar(

            registro,
            "no_meio_fio",
            "configuracao_infraestrutura",
            "rebaixamento_com_travessia_linear",
            "nao",
            OPORTUNIDADE,

            (
                "Rebaixamento corretamente mapeado "
                "sem travessia linear correspondente; "
                "o caso pode representar oportunidade "
                "de melhoria da infraestrutura real."
            ),

            TOTAL_REBAIXADOS,
        )


# ============================================================
# 11. NÓS DE TRAVESSIA
# ============================================================

TOTAL_NOS_CROSSING = len(
    nos_crossing
)


for registro in nos_crossing:

    props = registro[
        "props"
    ]


    # --------------------------------------------------------
    # 11.1 Tipo de travessia
    # --------------------------------------------------------

    crossing = props.get(
        "crossing"
    )


    if not valor_preenchido(
        crossing
    ):

        registrar(

            registro,
            "no_travessia",
            "travessia_seguranca",
            "crossing",
            "",
            INDETERMINADO,

            (
                "Tipo de travessia não informado."
            ),

            TOTAL_NOS_CROSSING,
        )


    elif crossing == "unmarked":

        registrar(

            registro,
            "no_travessia",
            "travessia_seguranca",
            "crossing",
            crossing,
            OPORTUNIDADE,

            (
                "Travessia registrada como "
                "não demarcada."
            ),

            TOTAL_NOS_CROSSING,
        )


    else:

        registrar(

            registro,
            "no_travessia",
            "travessia_seguranca",
            "crossing",
            crossing,
            CARACTERIZACAO,

            (
                "Tipo de travessia registrado."
            ),

            TOTAL_NOS_CROSSING,
        )


    # --------------------------------------------------------
    # 11.2 Demarcação
    # --------------------------------------------------------

    markings = props.get(
        "crossing:markings"
    )


    if not valor_preenchido(
        markings
    ):

        registrar(

            registro,
            "no_travessia",
            "travessia_seguranca",
            "crossing:markings",
            "",
            INDETERMINADO,

            (
                "Informação sobre demarcação "
                "da travessia ausente."
            ),

            TOTAL_NOS_CROSSING,
        )


    elif markings == "no":

        registrar(

            registro,
            "no_travessia",
            "travessia_seguranca",
            "crossing:markings",
            markings,
            OPORTUNIDADE,

            (
                "Ausência explícita de "
                "demarcação da travessia."
            ),

            TOTAL_NOS_CROSSING,
        )


    else:

        registrar(

            registro,
            "no_travessia",
            "travessia_seguranca",
            "crossing:markings",
            markings,
            CARACTERIZACAO,

            (
                "Demarcação da travessia registrada."
            ),

            TOTAL_NOS_CROSSING,
        )


    # --------------------------------------------------------
    # 11.3 Correspondência com travessia linear
    # --------------------------------------------------------

    if registro[
        "sobre_travessia"
    ]:

        registrar(

            registro,
            "no_travessia",
            "continuidade_rede",
            "correspondencia_travessia_linear",
            "sim",
            SEM_EVIDENCIA_NEGATIVA,

            (
                "O nó apresenta correspondência "
                "geométrica com travessia linear."
            ),

            TOTAL_NOS_CROSSING,
        )


    else:

        registrar(

            registro,
            "no_travessia",
            "continuidade_rede",
            "correspondencia_travessia_linear",
            "nao",
            REQUER_INSPECAO,

            (
                "O nó não apresenta correspondência "
                "geométrica com travessia linear. "
                "A situação requer interpretação "
                "e não é classificada automaticamente "
                "como erro."
            ),

            TOTAL_NOS_CROSSING,
        )


# ============================================================
# 12. RESUMO POR CRITÉRIO E NÍVEL DE EVIDÊNCIA
# ============================================================

agrupamento = defaultdict(
    list
)


for linha in linhas:

    chave = (

        linha["dimensao"],
        linha["elemento"],
        linha["criterio"],
        linha["nivel_evidencia"],
        linha["interpretacao"],
        linha["total_universo_criterio"],

    )

    agrupamento[
        chave
    ].append(
        linha
    )


resumo = []


for chave, grupo in agrupamento.items():

    (
        dimensao,
        elemento,
        criterio,
        nivel,
        interpretacao,
        total_universo,
    ) = chave


    quantidade = len(
        grupo
    )


    valores = Counter(

        linha["valor_observado"]

        if linha["valor_observado"] != ""

        else "<ausente>"

        for linha in grupo

    )


    resumo.append(
        {

            "dimensao":
                dimensao,

            "elemento":
                elemento,

            "criterio":
                criterio,

            "nivel_evidencia":
                nivel,

            "quantidade":
                quantidade,

            "total_universo":
                total_universo,

            "percentual_universo":
                percentual(
                    quantidade,
                    total_universo,
                ),

            "valores_observados":
                " | ".join(

                    f"{valor}:{n}"

                    for valor, n
                    in sorted(
                        valores.items()
                    )

                ),

            "interpretacao":
                interpretacao,

        }
    )


resumo.sort(

    key=lambda linha: (

        linha["dimensao"],
        linha["elemento"],
        linha["criterio"],
        linha["nivel_evidencia"],

    )

)


# ============================================================
# 13. SALVAMENTO DOS CSV
# ============================================================

salvar_csv(

    OUTPUT_FEICOES,

    linhas,

    [
        "osm_id",
        "elemento",
        "dimensao",
        "criterio",
        "valor_observado",
        "nivel_evidencia",
        "interpretacao",
        "total_universo_criterio",
    ],

)


salvar_csv(

    OUTPUT_RESUMO,

    resumo,

    [
        "dimensao",
        "elemento",
        "criterio",
        "nivel_evidencia",
        "quantidade",
        "total_universo",
        "percentual_universo",
        "valores_observados",
        "interpretacao",
    ],

)


# ============================================================
# 14. RESUMO NO TERMINAL
# ============================================================

print()

print(
    "CARACTERIZAÇÃO DE CONDIÇÕES "
    "DA REDE PEDONAL — T1"
)

print("=" * 88)


NIVEIS_PRIORITARIOS = {

    IMPEDIMENTO,
    OPORTUNIDADE,
    REQUER_INSPECAO,
    QUALIDADE_DADO,

}


print()

print(
    "CONDIÇÕES QUE INDICAM RESTRIÇÃO, "
    "OPORTUNIDADE DE MELHORIA OU INSPEÇÃO"
)

print("-" * 88)


for linha in resumo:

    if (
        linha[
            "nivel_evidencia"
        ]
        not in NIVEIS_PRIORITARIOS
    ):
        continue


    print(

        f"{linha['dimensao']:<32}"
        f"{linha['elemento']:<20}"
        f"{linha['criterio']:<36}"
        f"{linha['quantidade']:>3}/"
        f"{linha['total_universo']:<3} "
        f"({linha['percentual_universo']:>5.1f}%) "
        f"{linha['nivel_evidencia']} "
        f"[{linha['valores_observados']}]"

    )


# ============================================================
# 15. FEIÇÕES ÚNICAS COM CONDIÇÕES PRIORITÁRIAS
# ============================================================

feicoes_prioritarias = {

    linha["osm_id"]

    for linha in linhas

    if linha[
        "nivel_evidencia"
    ]
    in NIVEIS_PRIORITARIOS

}


feicoes_impedimento = {

    linha["osm_id"]

    for linha in linhas

    if linha[
        "nivel_evidencia"
    ]
    == IMPEDIMENTO

}


print()
print("=" * 88)


print(

    "Feições únicas com ao menos uma "
    "condição prioritária:",

    len(
        feicoes_prioritarias
    ),

)


print(

    "Feições únicas com ao menos um "
    "impedimento/restrição identificado:",

    len(
        feicoes_impedimento
    ),

)


# ============================================================
# 16. INFORMAÇÃO INDETERMINADA
# ============================================================

indeterminados = [

    linha

    for linha in resumo

    if linha[
        "nivel_evidencia"
    ]
    == INDETERMINADO

]


print()
print("=" * 88)


print(
    "CRITÉRIOS COM INFORMAÇÃO INDETERMINADA"
)

print("-" * 88)


for linha in indeterminados:

    print(

        f"{linha['dimensao']:<32}"
        f"{linha['elemento']:<20}"
        f"{linha['criterio']:<36}"
        f"{linha['quantidade']:>3}/"
        f"{linha['total_universo']:<3} "
        f"({linha['percentual_universo']:>5.1f}%)"

    )


# ============================================================
# 17. OBSERVAÇÕES FINAIS
# ============================================================

print()
print("=" * 88)


print(
    "Observação: as classificações não são "
    "mutuamente exclusivas entre critérios."
)


print(
    "Uma mesma feição pode apresentar "
    "condições associadas a mais de uma dimensão."
)


print(
    "A ausência de evidência negativa em um "
    "critério não é interpretada como comprovação "
    "de acessibilidade integral."
)


print()
print(
    "Arquivos gerados:"
)

print(
    OUTPUT_RESUMO
)

print(
    OUTPUT_FEICOES
)

print()