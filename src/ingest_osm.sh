#!/bin/bash

# 🔧 CONFIGURAÇÃO DO BANCO (Usando o seu usuário atual nativamente)
DB="PG:dbname=mapacess"

# Garante que o esquema 'osm' exista no banco e que você seja o dono
psql -d mapacess -c "CREATE SCHEMA IF NOT EXISTS osm;"
psql -d mapacess -c "ALTER SCHEMA osm OWNER TO felipe;"

# 📁 ARQUIVO GPKG
GPKG="/var/gits/mapacess/dados_externos/osm.gpkg"

# 🗺️ Nomes das tabelas destino
TB_PT="osm.point"
TB_LN="osm.line"
TB_PL="osm.polygon"

# Flags para controle
FIRST_PT=true
FIRST_LN=true
FIRST_PL=true

echo "🚀 Iniciando a ingestão dos dados OSM..."

# Processa cada camada
while read -r line; do
    LAYER_NAME=$(echo "$line" | sed -E 's/^(.*) \(.*/\1/')
    GEOM_TYPE=$(echo "$line" | sed -E 's/.*\((.*)\)/\1/')
    
    echo "🧭 Processando camada: $LAYER_NAME"
    
    case "$GEOM_TYPE" in
        Point*|Multi*Point*) TARGET=$TB_PT; NLT="POINT"; FIRST=$FIRST_PT ;;
        Line*|Multi*Line*)   TARGET=$TB_LN; NLT="LINESTRING"; FIRST=$FIRST_LN ;;
        Poly*|Multi*Poly*)   TARGET=$TB_PL; NLT="POLYGON"; FIRST=$FIRST_PL ;;
        *) echo "   ⚠ Tipo desconhecido ($GEOM_TYPE), ignorando."; continue ;;
    esac

    SQL="SELECT *, '$LAYER_NAME' AS origem FROM \"$LAYER_NAME\""

    if [ "$FIRST" = true ]; then
        ogr2ogr -f "PostgreSQL" "$DB" "$GPKG" \
            -nln "$TARGET" -nlt "$NLT" \
            -lco GEOMETRY_NAME=geom -lco FID=gid -lco precision=NO \
            -sql "$SQL" -overwrite -a_srs EPSG:4326

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

echo "✅ Importação concluída com sucesso!"
