# Análise Geoespacial da Área de Influência da Av. Centenário (Salvador, BA)

Este repositório documenta o processo de aquisição e filtragem de dados geoespaciais para a área de estudo definida em torno da Avenida Centenário, em Salvador, Bahia, Brasil.

O objetivo foi consolidar dados de fontes oficiais (Prefeitura de Salvador) e colaborativas (OpenStreetMap) para análises futuras.

## Ferramentas

* **QGIS:** Utilizado para consumir geosserviços (WFS), realizar análises espaciais (filtro, buffer, interseção) e exportar os dados.

## Metodologia e Processamento de Dados

O fluxo de trabalho foi dividido em duas frentes: obtenção de dados oficiais (SEFAZ e SEDUR) e dados colaborativos (OSM).

### 1. Dados Oficiais (SEFAZ e SEDUR)

Esta etapa focou na definição da área de estudo e na extração de feições da cartografia oficial do município.

#### 1.1. Fontes de Dados Oficiais

* **SEFAZ Salvador (Cartografia Base):**
    * *Descrição:* Base cartográfica oficial do município.
    * *Acesso:* Geosserviços WFS/WMS
    * *Link:* `https://cartografia.salvador.ba.gov.br/dados-geoespaciais/geoservicos/`

* **SEDUR Salvador (Logradouros):**
    * *Descrição:* Camada oficial de logradouros (ruas e avenidas).
    * *Acesso:* Geosserviço WFS
    * *Link:* `https://geo.sedur.salvador.ba.gov.br/geoserver/ows`

#### 1.2. Passos do Processamento no QGIS

1.  **Definição da Área de Estudo:**
    * A camada de logradouros da SEDUR (via WFS) foi adicionada ao QGIS.
    * Foi aplicado um filtro de atributos para selecionar apenas o logradouro referente à **"Av. Centenário"**.
    * Sobre a feição da avenida, foi aplicada uma operação de **buffer de 200 metros** para definir a área de influência direta.

2.  **Seleção de Feições (SEFAZ):**
    * As camadas da base cartográfica da SEFAZ (via WFS) foram adicionadas ao QGIS.
    * Foi realizada uma seleção espacial (interseção) para extrair apenas os objetos das classes prioritárias que **tinham interseção** com o buffer de 200m gerado.
    * As classes prioritárias da SEFAZ analisadas foram:

    * `poste_sinalizacao_p`
    * `poste_p`
    * `arvore_isolada_p`
    * `eixo_logradouro`
    * `meio_fio_l`
    * `jardim_a`
    * `edificacao_total`
    * `vegetacao_total`
    * `rampa_a`
    * `escadaria_a`
    * `ciclovia_a`
    * `acesso_a`
    * `travessia_pedestre_a`
    * `ponte_a`
    * `passagem_elevada_viaduto_a`
    * `area_de_propriedade_particular_a`
    * `trecho_arruamento_a`
    * `quadra_a`
    * `praca_a`
    * `passeio_a`
    * `estacionamento_a`
    * `canteiro_central_a`

3.  **Resultado:**
    * Os dados filtrados (feições da SEFAZ dentro do buffer de 200m) foram exportados para um único arquivo GeoPackage (`.gpkg`).
    * **Arquivo no repositório:** `sefaz.gpkg`
    * Os metadados originais estão em formato pdf na pasta metadados_sefaz.
    * Um projeto do QGIS com as configurações iniciais está no repositório para teste.

---

### 2. Dados Colaborativos (OpenStreetMap - OSM)

*(Esta seção descreverá o processo de consulta e extração de dados do OpenStreetMap utilizando o plugin QuickOSM no QGIS para a mesma área de estudo.)*
