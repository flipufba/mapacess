#!/bin/bash
# ============================================================
# Importa todas as camadas de um GeoPackage para o PostGIS,
# criando uma tabela para cada camada no schema 'sefaz'.
# ============================================================

# 🔧 CONFIGURAÇÃO DO BANCO
DB="PG:host=10.131.32.26 dbname=mapacess user=user password=user"

# 📁 ARQUIVO GPKG
GPKG="/home/labfsr/felipe/gits/mapacess/dados_externos/sefaz.gpkg"

# Schema destino
SCHEMA="sefaz"

# ============================================================
# Processa cada camada
while read -r line; do
    # Extrai o nome e o tipo de geometria entre parênteses
    LAYER_NAME=$(echo "$line" | sed -E 's/^(.*) \(.*/\1/')
    GEOM_TYPE=$(echo "$line" | sed -E 's/.*\((.*)\)/\1/')
    
    echo "🧭 Processando camada: $LAYER_NAME"

    # Normaliza o tipo geométrico para o ogr2ogr
    case "$GEOM_TYPE" in
        Point*|Multi*Point*) NLT="POINT" ;;
        Line*|Multi*Line*)   NLT="LINESTRING" ;;
        Poly*|Multi*Poly*)   NLT="POLYGON" ;;
        *) echo "   ⚠ Tipo desconhecido ($GEOM_TYPE), ignorando."; continue ;;
    esac

    echo "   ➤ Tipo: $GEOM_TYPE → tabela destino: $SCHEMA.$LAYER_NAME"

    # SQL opcional (adiciona campo origem)
    SQL="SELECT *, '$LAYER_NAME' AS origem FROM \"$LAYER_NAME\""

    # Executa a importação (overwrite se já existir)
    ogr2ogr -f "PostgreSQL" "$DB" "$GPKG" \
        -nln "$SCHEMA.$LAYER_NAME" -nlt "$NLT" \
        -lco GEOMETRY_NAME=geom -lco FID=gid -lco precision=NO \
        -sql "$SQL" -overwrite -a_srs EPSG:4326

done < <(ogrinfo -ro -so "$GPKG" | grep -E "^[[:space:]]*[0-9]+:" | sed -E 's/^[[:space:]]*[0-9]+:[[:space:]]*//')

echo "✅ Importação concluída!"

