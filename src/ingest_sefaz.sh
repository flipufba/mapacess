#!/bin/bash
# ============================================================
# Importa camadas do GeoPackage SEFAZ para o PostGIS
# ============================================================

# 🔧 CONFIGURAÇÃO DO BANCO (Usando a conexão nativa do usuário felipe)
DB="PG:dbname=mapacess"

# 📁 ARQUIVO GPKG
GPKG="/var/gits/mapacess/dados_externos/sefaz.gpkg"

# Schema destino
SCHEMA="sefaz"

# 🛠️ GARANTE QUE O SCHEMA EXISTE E PERTENCE AO FELIPE
psql -d mapacess -c "CREATE SCHEMA IF NOT EXISTS $SCHEMA;"
psql -d mapacess -c "ALTER SCHEMA $SCHEMA OWNER TO felipe;"

echo "🚀 Iniciando a ingestão dos dados SEFAZ..."

# ============================================================
# Processa cada camada
while read -r line; do
    LAYER_NAME=$(echo "$line" | sed -E 's/^(.*) \(.*/\1/')
    GEOM_TYPE=$(echo "$line" | sed -E 's/.*\((.*)\)/\1/')

    echo "🧭 Processando camada: $LAYER_NAME"

    case "$GEOM_TYPE" in
        Point*|Multi*Point*) NLT="POINT" ;;
        Line*|Multi*Line*)   NLT="LINESTRING" ;;
        Poly*|Multi*Poly*)   NLT="PROMOTE_TO_MULTI" ;; # Melhor para dados fiscais/lotes
        *) echo "   ⚠ Tipo desconhecido ($GEOM_TYPE), ignorando."; continue ;;
    esac

    echo "   ➤ Tipo: $GEOM_TYPE → tabela destino: $SCHEMA.$LAYER_NAME"

    SQL="SELECT *, '$LAYER_NAME' AS origem FROM \"$LAYER_NAME\""

    # Executa a importação
    ogr2ogr -f "PostgreSQL" "$DB" "$GPKG" \
        -nln "$SCHEMA.$LAYER_NAME" -nlt "$NLT" \
        -lco GEOMETRY_NAME=geom -lco FID=gid -lco precision=NO \
        -sql "$SQL" -overwrite -a_srs EPSG:31984

done < <(ogrinfo -ro -so "$GPKG" | grep -E "^[[:space:]]*[0-9]+:" | sed -E 's/^[[:space:]]*[0-9]+:[[:space:]]*//')

echo "✅ Importação da SEFAZ concluída!"
