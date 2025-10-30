#!/bin/bash
# ============================================================
# Importa todas as camadas de um GeoPackage para o PostGIS,
# separando por tipo de geometria (ponto, linha, polígono).
# Cria/atualiza tabelas únicas para cada tipo:
#   - osm.point
#   - osm.line
#   - osm.polygon
# ============================================================

# 🔧 CONFIGURAÇÃO DO BANCO
DB="PG:host=10.131.32.26 dbname=mapacess user=user password=user"

# 📁 ARQUIVO GPKG
GPKG="/home/labfsr/felipe/gits/mapacess/dados_externos/osm.gpkg"

# 🗺️ Nomes das tabelas destino
TB_PT="osm.point"
TB_LN="osm.line"
TB_PL="osm.polygon"

# Flags para saber se as tabelas já foram criadas
FIRST_PT=true
FIRST_LN=true
FIRST_PL=true

# ============================================================
# Processa cada camada
while read -r line; do
    # Extrai o nome e o tipo de geometria entre parênteses
    LAYER_NAME=$(echo "$line" | sed -E 's/^(.*) \(.*/\1/')
    GEOM_TYPE=$(echo "$line" | sed -E 's/.*\((.*)\)/\1/')
    
    echo "🧭 Processando camada: $LAYER_NAME"
    
    # Normaliza o tipo geométrico
    case "$GEOM_TYPE" in
        Point*|Multi*Point*) TARGET=$TB_PT; NLT="POINT"; FIRST=$FIRST_PT ;;
        Line*|Multi*Line*)   TARGET=$TB_LN; NLT="LINESTRING"; FIRST=$FIRST_LN ;;
        Poly*|Multi*Poly*)   TARGET=$TB_PL; NLT="POLYGON"; FIRST=$FIRST_PL ;;
        *) echo "   ⚠ Tipo desconhecido ($GEOM_TYPE), ignorando."; continue ;;
    esac

    echo "   ➤ Tipo: $GEOM_TYPE → Tabela destino: $TARGET"

    # Cria campo com nome da camada original
    SQL="SELECT *, '$LAYER_NAME' AS origem FROM \"$LAYER_NAME\""

    # Executa a importação
    if [ "$FIRST" = true ]; then
        ogr2ogr -f "PostgreSQL" "$DB" "$GPKG" \
            -nln "$TARGET" -nlt "$NLT" \
            -lco GEOMETRY_NAME=geom -lco FID=gid -lco precision=NO \
            -sql "$SQL" -overwrite -a_srs EPSG:4326

        # Atualiza flag
        case "$TARGET" in
            $TB_PT) FIRST_PT=false ;;
            $TB_LN) FIRST_LN=false ;;
            $TB_PL) FIRST_PL=false ;;
        esac
    else
        ogr2ogr -f "PostgreSQL" "$DB" "$GPKG" \
            -nln "$TARGET" -nlt "$NLT" \
            -lco GEOMETRY_NAME=geom -lco FID=gid -lco precision=NO \
            -sql "$SQL" -append -addfields -a_srs EPSG:4326
    fi
done < <(ogrinfo -ro -so "$GPKG" | grep -E "^[[:space:]]*[0-9]+:" | sed -E 's/^[[:space:]]*[0-9]+:[[:space:]]*//')

echo "✅ Importação concluída!"
echo "Tabelas criadas/atualizadas:"
echo "  → $TB_PT"
echo "  → $TB_LN"
echo "  → $TB_PL"
