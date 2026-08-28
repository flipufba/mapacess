from pathlib import Path
import json
from shapely.geometry import shape, mapping


# ============================================================
# CAMINHOS
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

OUTPUT_PATH = (
    REPO_ROOT
    / "results"
    / "layers"
    / "residuos_topologicos_t1.geojson"
)


# ============================================================
# LEITURA
# ============================================================

with INPUT_PATH.open("r", encoding="utf-8") as f:
    dados = json.load(f)


# ============================================================
# COLETA DAS TRAVESSIAS LINEARES
# ============================================================

travessias = []

for feat in dados["features"]:
    props = feat.get("properties", {})
    geom = shape(feat["geometry"])

    if (
        geom.geom_type in {"LineString", "MultiLineString"}
        and props.get("highway") == "footway"
        and props.get("footway") == "crossing"
    ):
        travessias.append(geom)


# ============================================================
# IDENTIFICAÇÃO DOS RESÍDUOS TOPOLOGICOS
# ============================================================

residuos = []

for feat in dados["features"]:
    props = feat.get("properties", {})
    geom = shape(feat["geometry"])

    # --------------------------------------------------------
    # 1. Kerbs fora de travessia
    # --------------------------------------------------------
    if (
        geom.geom_type == "Point"
        and props.get("barrier") == "kerb"
        and not any(geom.intersects(l) for l in travessias)
    ):
        residuos.append(
            {
                "type": "Feature",
                "geometry": mapping(geom),
                "properties": {
                    "tipo_residuo": "kerb_fora_travessia",
                    "classe_analitica": "no_meio_fio",
                    "osm_id": props.get("@osmId"),
                    "kerb": props.get("kerb"),
                    "wheelchair": props.get("wheelchair"),
                    "crossing": None,
                    "crossing_markings": None,
                    "descricao": (
                        "Nó barrier=kerb sem interseção geométrica "
                        "com travessia linear footway=crossing"
                    ),
                },
            }
        )

    # --------------------------------------------------------
    # 2. Nós highway=crossing fora de travessia
    # --------------------------------------------------------
    elif (
        geom.geom_type == "Point"
        and props.get("highway") == "crossing"
        and not any(geom.intersects(l) for l in travessias)
    ):
        residuos.append(
            {
                "type": "Feature",
                "geometry": mapping(geom),
                "properties": {
                    "tipo_residuo": "no_crossing_fora_travessia",
                    "classe_analitica": "no_travessia",
                    "osm_id": props.get("@osmId"),
                    "kerb": None,
                    "wheelchair": props.get("wheelchair"),
                    "crossing": props.get("crossing"),
                    "crossing_markings": props.get("crossing:markings"),
                    "descricao": (
                        "Nó highway=crossing sem interseção geométrica "
                        "com travessia linear footway=crossing"
                    ),
                },
            }
        )


# ============================================================
# SALVAMENTO
# ============================================================

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

saida = {
    "type": "FeatureCollection",
    "features": residuos,
}

with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(saida, f, ensure_ascii=False, indent=2)


# ============================================================
# RESUMO
# ============================================================

n_kerb = sum(
    1 for feat in residuos
    if feat["properties"]["tipo_residuo"] == "kerb_fora_travessia"
)

n_crossing = sum(
    1 for feat in residuos
    if feat["properties"]["tipo_residuo"] == "no_crossing_fora_travessia"
)

print("Camada gerada com sucesso.")
print(f"Total de resíduos: {len(residuos)}")
print(f" - kerb_fora_travessia: {n_kerb}")
print(f" - no_crossing_fora_travessia: {n_crossing}")
print(f"Arquivo salvo em: {OUTPUT_PATH}")