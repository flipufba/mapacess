# 🗺️ Mapeamento de Informações Geoespaciais Remotas e Colaborativas da Acessibilidade Universal Urbana

Este repositório reúne dados e scripts relacionados ao **mapeamento geoespacial da acessibilidade urbana**, com base em dados obtidos a partir da pesquisa de **Danielle Cazumba (UFBA, 2024)**.

---

## 📚 Referência da Pesquisa

Os dados utilizados foram originalmente disponibilizados em formato `.zip` com o nome:

```

Dados_ICAM.zip

```

Hash SHA256 de verificação:

```

16b2db1d70b6222fe9ebb4b1ddcb42730af53aa53dbcd61582450e65a0081c45

```

Os dados são oriundos da tese intitulada:

> **“Proposta de Metodologia para o Mapeamento Virtual da Caminhabilidade Urbana Associada à Acessibilidade por Imagens de Nível de Rua”**  
> Autora: *Danielle Marques Cazumba*  
> Ano: 2024  
> Disponível no repositório da UFBA:  
> [https://repositorio.ufba.br/handle/ri/22482/simple-search?filterquery=Cazumba%2C+Danielle+Marques&filtername=author&filtertype=equals](https://repositorio.ufba.br/handle/ri/22482/simple-search?filterquery=Cazumba%2C+Danielle+Marques&filtername=author&filtertype=equals)

---

## 📂 Estrutura do Diretório

Os dados extraídos estão armazenados na pasta:

```

Dados_ICAM/

```

Essa pasta contém **duas subpastas** e **três arquivos principais**:

```

├── Dados_ICAM/
│   ├── icam/
│   │   ├── ICAM_Barra_Copia.shp
│   │   ├── ICAM_Barra_Copia.dbf
│   │   ├── ...
│   ├── barra_ok/
│   │   ├── ICAM_Barra_OK.shp
│   │   ├── ICAM_Barra_OK.dbf
│   │   ├── ...
│   ├── planilha caminhabilidade.xlsx
│   ├── ...

````

As subpastas `icam/` e `barra_ok/` contêm os arquivos vetoriais no formato **Shapefile (.shp)** e seus respectivos arquivos auxiliares (`.dbf`, `.prj`, `.shx`), com as **geometrias** e **análises espaciais** realizadas pela autora da pesquisa.

Os arquivos complementares (como planilhas) contêm dados tabulares e análises derivadas dos shapefiles.

---

## 🗃️ Base de Dados

Todos os dados do projeto estão centralizados em uma base de dados **PostgreSQL 14** com **extensão PostGIS** instalada, hospedada no **Laboratório de Fotogrametria e Sensoriamento Remoto (LabFSR)**.

| Parâmetro | Valor |
|------------|--------|
| IP         | `10.131.32.48` |
| Porta      | `5432` |
| Banco de dados | `mapacess` |

### Estrutura de Schemas

O banco está organizado nos seguintes schemas, de acordo com a origem dos dados:

* **`barra`:** Contém os dados originais e processados da pesquisa de **Danielle Cazumba (2024)**, focados na área da Barra (ex: `barra.icam`, `barra.icam_ok`).
* **`sefaz`:** Contém os dados cartográficos oficiais da Prefeitura de Salvador (SEFAZ/SEDUR) para as áreas de estudo (ex: `sefaz.passeio_a`, `sefaz.rampa_a`). Os dados são ingeridos em tabelas separadas por camada.
* **`osm`:** Contém os dados colaborativos do OpenStreetMap. Devido à sua natureza granular, os dados são ingeridos e unificados em três tabelas principais baseadas em geometria: `osm.point`, `osm.line` e `osm.polygon`, com uma coluna `origem` para rastreabilidade.


---

## 🧩 Ingestão dos Dados

A ingestão de dados no banco `mapacess` é realizada por diferentes métodos, dependendo da fonte e da sua complexidade.

### 1\. Dados da Pesquisa Original (Schema `barra`)

A ingestão inicial dos shapefiles da pesquisa de Danielle Cazumba (dados `ICAM_Barra_Copia` e `ICAM_Barra_OK`) foi realizada com o utilitário **`shp2pgsql`**, conforme os comandos abaixo:

```bash
# Diretório dos dados ICAM
cd /var/gits/mapacess/Dados_ICAM/icam

# Importação da camada ICAM_Barra_Copia usando ogr2ogr
sudo -u postgres ogr2ogr -f "PostgreSQL" PG:"dbname=mapacess" ICAM_Barra_Copia.shp \
  -nln barra.icam \
  -a_srs EPSG:31984 \
  --config SHAPE_ENCODING "UTF-8" \
  -lco SPATIAL_INDEX=GIST \
  -overwrite

# Diretório dos dados validados
cd /var/gits/mapacess/Dados_ICAM/barra_ok

# Importação da camada ICAM_Barra_OK usando ogr2ogr
sudo -u postgres ogr2ogr -f "PostgreSQL" PG:"dbname=mapacess" ICAM_Barra_OK.shp \
  -nln barra.icam_ok \
  -a_srs EPSG:31984 \
  --config SHAPE_ENCODING "UTF-8" \
  -lco SPATIAL_INDEX=GIST \
  -overwrite
```

> **Nota:** O sistema de referência utilizado é **SIRGAS 2000 / UTM Zona 24S (EPSG:31984)** e a codificação de caracteres foi definida como **UTF-8**.

### 2\. Dados Externos (Schemas `sefaz` e `osm`)

Para a ingestão de fontes de dados externas (como os GeoPackages da SEFAZ e OSM), foram desenvolvidos scripts de automação para garantir um tratamento consistente, reprodutível e adaptado à estrutura de cada fonte.

  * **Localização:** Todos os scripts de ingestão estão localizados na pasta [`src/`](./src/) do repositório.
  * **Tecnologia:** São scripts `bash` que utilizam a ferramenta `ogr2ogr` (parte da biblioteca GDAL) para processar os arquivos `.gpkg` e carregá-los no PostGIS.
  * **Metodologias de Ingestão:**
      * **SEFAZ (`src/import_sefaz.sh`):** Utiliza uma abordagem **1-para-1**, onde cada camada do GeoPackage de origem é importada como uma tabela individual no schema `sefaz` (ex: `sefaz.passeio_a`).
      * **OSM (`src/import_osm.sh`):** Utiliza uma abordagem de **unificação (Muitos-para-3)**. Todas as dezenas de camadas granulares extraídas do QuickOSM são consolidadas em apenas três tabelas (`osm.point`, `osm.line`, `osm.polygon`), com uma coluna `origem` adicionada para rastrear a camada-fonte de cada feição.


---

## 🔍 Próximas Etapas

* [ ] Tratamento dos dados e viabilidade de melhorias
* [x] Viabilizar possibilidade de acréscimo de variáveis e dados
* [x] Organização das análises derivadas por categoria temática
* [x] Estruturação dos scripts SQL para automação da ingestão
* [ ] Integração com ambientes SIG (QGIS / GeoServer)
* [ ] Possibilidade de criação de plugin QGIS para divulgação do método
* [ ] Documentação técnica dos metadados espaciais

---

## 🧠 Créditos

* **Autoria dos dados originais:** Danielle Marques Cazumba
* **Tratamento e ingestão em base de dados:** Felipe Reis da Cruz
* **Instituição:** Universidade Federal da Bahia  — Escola Politécnica da UFBA — Laboratório de Fotogrametria e Sensoriamento Remoto

---

> 💡 *Este repositório tem caráter técnico e acadêmico, voltado à documentação e reprodutibilidade do processo de ingestão, tratamento e análise de dados geoespaciais da acessibilidade urbana.*
```
