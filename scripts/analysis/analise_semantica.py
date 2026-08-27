from pathlib import Path
from collections import Counter
import csv
import json


# ============================================================
# 1. CAMINHOS DO PROJETO
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

OUTPUT_PREENCHIMENTO = (
    RESULTS_DIR
    / "preenchimento_semantico_t0_t1.csv"
)

OUTPUT_VALORES = (
    RESULTS_DIR
    / "frequencia_valores_semanticos_t0_t1.csv"
)

OUTPUT_NAO_CONFORMIDADES = (
    RESULTS_DIR
    / "nao_conformidades_protocolo_t0_t1.csv"
)

OUTPUT_KERB_WHEELCHAIR = (
    RESULTS_DIR
    / "conformidade_kerb_raised_wheelchair_t0_t1.csv"
)


# ============================================================
# 2. CLASSES E ATRIBUTOS ANALISADOS
# ============================================================

ATRIBUTOS_POR_CLASSE = {
    "calcada": [
        "surface",
        "smoothness",
        "tactile_paving",
    ],

    "travessia_linear": [
        "crossing",
        "crossing:markings",
        "wheelchair",
    ],

    "no_meio_fio": [
        "kerb",
        "tactile_paving",
    ],

    "no_travessia": [
        "crossing",
        "crossing:markings",
    ],
}


NOMES_CLASSES = {
    "calcada": "Calçadas",
    "travessia_linear": "Travessias lineares",
    "no_meio_fio": "Nós de meio-fio",
    "no_travessia": "Nós de travessia",
}


# ============================================================
# 3. VOCABULÁRIOS ADOTADOS PELO PROTOCOLO
# ============================================================

# Estes vocabulários são deliberadamente específicos
# por classe.
#
# Um valor fora destas listas não é necessariamente inválido
# no OpenStreetMap. Ele representa uma não conformidade
# em relação ao vocabulário adotado no protocolo do estudo.

VOCABULARIO_POR_CLASSE = {

    "calcada": {
        "smoothness": {
            "excellent",
            "good",
            "bad",
        },
    },

    "no_meio_fio": {
        "kerb": {
            "lowered",
            "flush",
            "raised",
        },
    },
}


# ============================================================
# 4. LEITURA DOS DADOS
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
            f"O arquivo não é um FeatureCollection válido: "
            f"{caminho}"
        )

    return dados


# ============================================================
# 5. CLASSIFICAÇÃO DAS FEIÇÕES
# ============================================================

def classificar_feicao(feature):

    propriedades = feature.get(
        "properties",
        {},
    )

    geometria = (
        feature.get("geometry")
        or {}
    )

    tipo_geometria = geometria.get(
        "type"
    )

    highway = propriedades.get(
        "highway"
    )

    footway = propriedades.get(
        "footway"
    )

    barrier = propriedades.get(
        "barrier"
    )


    # Calçadas
    if (
        tipo_geometria
        in {"LineString", "MultiLineString"}
        and highway == "footway"
        and footway == "sidewalk"
    ):

        return "calcada"


    # Travessias lineares
    if (
        tipo_geometria
        in {"LineString", "MultiLineString"}
        and highway == "footway"
        and footway == "crossing"
    ):

        return "travessia_linear"


    # Nós de meio-fio
    if (
        tipo_geometria == "Point"
        and barrier == "kerb"
    ):

        return "no_meio_fio"


    # Nós de travessia
    if (
        tipo_geometria == "Point"
        and highway == "crossing"
    ):

        return "no_travessia"


    return "outros"


# ============================================================
# 6. FUNÇÕES AUXILIARES
# ============================================================

def valor_preenchido(valor):

    if valor is None:
        return False

    if isinstance(valor, str):
        return valor.strip() != ""

    return True


def obter_osm_id(feature):

    return (
        feature
        .get("properties", {})
        .get("@osmId", "")
    )


def percentual(
    numerador,
    denominador,
):

    if denominador == 0:
        return ""

    return round(
        (numerador / denominador) * 100,
        1,
    )


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
# 7. PREENCHIMENTO SEMÂNTICO
# ============================================================

def analisar_preenchimento(
    estado,
    dados,
):

    resultados = []

    for classe, atributos in (
        ATRIBUTOS_POR_CLASSE.items()
    ):

        feicoes_classe = [
            feature
            for feature in dados["features"]
            if classificar_feicao(feature) == classe
        ]

        total_classe = len(
            feicoes_classe
        )


        for atributo in atributos:

            preenchidos = sum(

                valor_preenchido(
                    feature
                    .get("properties", {})
                    .get(atributo)
                )

                for feature
                in feicoes_classe
            )

            ausentes = (
                total_classe
                - preenchidos
            )

            resultados.append(
                {
                    "estado":
                        estado,

                    "classe":
                        NOMES_CLASSES[classe],

                    "atributo":
                        atributo,

                    "total_feicoes":
                        total_classe,

                    "preenchidos":
                        preenchidos,

                    "ausentes":
                        ausentes,

                    "percentual_preenchimento":
                        percentual(
                            preenchidos,
                            total_classe,
                        ),
                }
            )

    return resultados


# ============================================================
# 8. FREQUÊNCIA DOS VALORES
# ============================================================

def analisar_frequencias(
    estado,
    dados,
):

    resultados = []

    for classe, atributos in (
        ATRIBUTOS_POR_CLASSE.items()
    ):

        feicoes_classe = [
            feature
            for feature in dados["features"]
            if classificar_feicao(feature) == classe
        ]


        for atributo in atributos:

            contador = Counter()

            for feature in feicoes_classe:

                valor = (
                    feature
                    .get("properties", {})
                    .get(atributo)
                )

                if valor_preenchido(valor):

                    contador[
                        str(valor).strip()
                    ] += 1


            total_preenchidos = sum(
                contador.values()
            )


            for valor, quantidade in sorted(
                contador.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            ):

                resultados.append(
                    {
                        "estado":
                            estado,

                        "classe":
                            NOMES_CLASSES[classe],

                        "atributo":
                            atributo,

                        "valor":
                            valor,

                        "quantidade":
                            quantidade,

                        "total_preenchidos":
                            total_preenchidos,

                        "percentual_dentro_atributo":
                            percentual(
                                quantidade,
                                total_preenchidos,
                            ),
                    }
                )

    return resultados


# ============================================================
# 9. NÃO CONFORMIDADES EM RELAÇÃO AO PROTOCOLO
# ============================================================

def analisar_nao_conformidades(
    estado,
    dados,
):

    resultados = []


    for feature in dados["features"]:

        classe = classificar_feicao(
            feature
        )

        if classe == "outros":
            continue


        propriedades = feature.get(
            "properties",
            {},
        )

        osm_id = obter_osm_id(
            feature
        )


        # ----------------------------------------------------
        # 9.1 Valores fora do vocabulário adotado
        # ----------------------------------------------------

        regras_classe = (
            VOCABULARIO_POR_CLASSE
            .get(
                classe,
                {},
            )
        )


        for atributo, valores_validos in (
            regras_classe.items()
        ):

            valor = propriedades.get(
                atributo
            )

            # Ausência não é tratada aqui como erro.
            # Ela é contabilizada no preenchimento.
            if not valor_preenchido(valor):
                continue


            valor = str(
                valor
            ).strip()


            if valor not in valores_validos:

                resultados.append(
                    {
                        "estado":
                            estado,

                        "osm_id":
                            osm_id,

                        "classe":
                            NOMES_CLASSES[classe],

                        "atributo":
                            atributo,

                        "valor":
                            valor,

                        "tipo_nao_conformidade":
                            "fora_vocabulario_protocolo",

                        "descricao":
                            (
                                "Valor não previsto no "
                                "vocabulário adotado pelo "
                                "protocolo para esta classe. "
                                "Isso não implica que o valor "
                                "seja inválido no OpenStreetMap."
                            ),
                    }
                )


        # ----------------------------------------------------
        # 9.2 Regra condicional:
        #     kerb=raised -> wheelchair=no
        # ----------------------------------------------------

        if classe == "no_meio_fio":

            kerb = propriedades.get(
                "kerb"
            )

            wheelchair = propriedades.get(
                "wheelchair"
            )


            if kerb == "raised":

                if not valor_preenchido(
                    wheelchair
                ):

                    resultados.append(
                        {
                            "estado":
                                estado,

                            "osm_id":
                                osm_id,

                            "classe":
                                NOMES_CLASSES[classe],

                            "atributo":
                                "wheelchair",

                            "valor":
                                "",

                            "tipo_nao_conformidade":
                                "atributo_condicional_ausente",

                            "descricao":
                                (
                                    "O protocolo prescreve "
                                    "wheelchair=no para nós "
                                    "de meio-fio classificados "
                                    "como kerb=raised."
                                ),
                        }
                    )


                elif (
                    str(wheelchair).strip()
                    != "no"
                ):

                    resultados.append(
                        {
                            "estado":
                                estado,

                            "osm_id":
                                osm_id,

                            "classe":
                                NOMES_CLASSES[classe],

                            "atributo":
                                "wheelchair",

                            "valor":
                                str(
                                    wheelchair
                                ).strip(),

                            "tipo_nao_conformidade":
                                "valor_condicional_divergente",

                            "descricao":
                                (
                                    "O protocolo prescreve "
                                    "wheelchair=no para nós "
                                    "de meio-fio classificados "
                                    "como kerb=raised."
                                ),
                        }
                    )

    return resultados


# ============================================================
# 10. CONFORMIDADE DA REGRA
#     kerb=raised -> wheelchair=no
# ============================================================

def analisar_regra_kerb_wheelchair(
    estado,
    dados,
):

    kerbs = [
        feature
        for feature in dados["features"]
        if classificar_feicao(feature)
        == "no_meio_fio"
    ]


    raised = [
        feature
        for feature in kerbs
        if (
            feature
            .get("properties", {})
            .get("kerb")
            == "raised"
        )
    ]


    total_kerbs = len(
        kerbs
    )

    total_raised = len(
        raised
    )


    conformes = 0
    wheelchair_ausente = 0
    wheelchair_divergente = 0


    for feature in raised:

        wheelchair = (
            feature
            .get("properties", {})
            .get("wheelchair")
        )


        if not valor_preenchido(
            wheelchair
        ):

            wheelchair_ausente += 1


        elif (
            str(wheelchair).strip()
            == "no"
        ):

            conformes += 1


        else:

            wheelchair_divergente += 1


    nao_conformes = (
        wheelchair_ausente
        + wheelchair_divergente
    )


    return {
        "estado":
            estado,

        "total_nos_kerb":
            total_kerbs,

        "total_kerb_raised":
            total_raised,

        "wheelchair_no":
            conformes,

        "wheelchair_ausente":
            wheelchair_ausente,

        "wheelchair_valor_divergente":
            wheelchair_divergente,

        "total_nao_conformes":
            nao_conformes,

        "percentual_conforme":
            percentual(
                conformes,
                total_raised,
            ),

        "percentual_nao_conforme":
            percentual(
                nao_conformes,
                total_raised,
            ),
    }


# ============================================================
# 11. EXECUÇÃO
# ============================================================

t0 = carregar_geojson(
    T0_PATH
)

t1 = carregar_geojson(
    T1_PATH
)


preenchimento = (
    analisar_preenchimento(
        "T0",
        t0,
    )
    +
    analisar_preenchimento(
        "T1",
        t1,
    )
)


frequencias = (
    analisar_frequencias(
        "T0",
        t0,
    )
    +
    analisar_frequencias(
        "T1",
        t1,
    )
)


nao_conformidades = (
    analisar_nao_conformidades(
        "T0",
        t0,
    )
    +
    analisar_nao_conformidades(
        "T1",
        t1,
    )
)


conformidade_kerb = [
    analisar_regra_kerb_wheelchair(
        "T0",
        t0,
    ),

    analisar_regra_kerb_wheelchair(
        "T1",
        t1,
    ),
]


# ============================================================
# 12. SALVAMENTO DOS RESULTADOS
# ============================================================

salvar_csv(
    OUTPUT_PREENCHIMENTO,
    preenchimento,
    [
        "estado",
        "classe",
        "atributo",
        "total_feicoes",
        "preenchidos",
        "ausentes",
        "percentual_preenchimento",
    ],
)


salvar_csv(
    OUTPUT_VALORES,
    frequencias,
    [
        "estado",
        "classe",
        "atributo",
        "valor",
        "quantidade",
        "total_preenchidos",
        "percentual_dentro_atributo",
    ],
)


salvar_csv(
    OUTPUT_NAO_CONFORMIDADES,
    nao_conformidades,
    [
        "estado",
        "osm_id",
        "classe",
        "atributo",
        "valor",
        "tipo_nao_conformidade",
        "descricao",
    ],
)


salvar_csv(
    OUTPUT_KERB_WHEELCHAIR,
    conformidade_kerb,
    [
        "estado",
        "total_nos_kerb",
        "total_kerb_raised",
        "wheelchair_no",
        "wheelchair_ausente",
        "wheelchair_valor_divergente",
        "total_nao_conformes",
        "percentual_conforme",
        "percentual_nao_conforme",
    ],
)


# ============================================================
# 13. RESULTADOS NO TERMINAL
# ============================================================

print()

print(
    "ANÁLISE DE PREENCHIMENTO E "
    "CONFORMIDADE SEMÂNTICA — T0 × T1"
)

print("=" * 78)


# ------------------------------------------------------------
# Preenchimento
# ------------------------------------------------------------

for estado in (
    "T0",
    "T1",
):

    print()
    print(
        estado
    )

    print("-" * 78)


    linhas_estado = [
        linha
        for linha in preenchimento
        if linha["estado"]
        == estado
    ]


    for linha in linhas_estado:

        valor_percentual = (
            linha[
                "percentual_preenchimento"
            ]
        )


        if valor_percentual == "":

            percentual_texto = (
                "n/a"
            )

        else:

            percentual_texto = (
                f"{valor_percentual:.1f}%"
            )


        print(
            f"{linha['classe']:<23}"
            f"{linha['atributo']:<20}"
            f"{linha['preenchidos']:>3}/"
            f"{linha['total_feicoes']:<3} "
            f"{percentual_texto:>7}"
        )


# ------------------------------------------------------------
# Não conformidades
# ------------------------------------------------------------

print()
print("=" * 78)

print(
    "NÃO CONFORMIDADES EM RELAÇÃO "
    "AO PROTOCOLO"
)

print("-" * 78)


if not nao_conformidades:

    print(
        "Nenhuma não conformidade identificada."
    )

else:

    contador_tipos = Counter(
        linha[
            "tipo_nao_conformidade"
        ]
        for linha
        in nao_conformidades
    )


    for tipo, quantidade in (
        contador_tipos.most_common()
    ):

        print(
            f"{tipo:<45}"
            f"{quantidade:>5}"
        )


print()

print(
    f"Total de não conformidades: "
    f"{len(nao_conformidades)}"
)


# ------------------------------------------------------------
# Regra kerb=raised -> wheelchair=no
# ------------------------------------------------------------

print()
print("=" * 78)

print(
    "CONFORMIDADE DA REGRA "
    "kerb=raised → wheelchair=no"
)

print("-" * 78)


for linha in conformidade_kerb:

    if linha["total_kerb_raised"] == 0:

        percentual_conforme = "n/a"
        percentual_nao = "n/a"

    else:

        percentual_conforme = (
            f"{linha['percentual_conforme']:.1f}%"
        )

        percentual_nao = (
            f"{linha['percentual_nao_conforme']:.1f}%"
        )


    print(
        f"{linha['estado']}: "
        f"raised={linha['total_kerb_raised']} | "
        f"wheelchair=no={linha['wheelchair_no']} | "
        f"ausente={linha['wheelchair_ausente']} | "
        f"divergente="
        f"{linha['wheelchair_valor_divergente']} | "
        f"conforme={percentual_conforme} | "
        f"não conforme={percentual_nao}"
    )


# ------------------------------------------------------------
# Arquivos
# ------------------------------------------------------------

print()
print("=" * 78)

print(
    "Arquivos gerados:"
)

print(
    OUTPUT_PREENCHIMENTO
)

print(
    OUTPUT_VALORES
)

print(
    OUTPUT_NAO_CONFORMIDADES
)

print(
    OUTPUT_KERB_WHEELCHAIR
)

print()