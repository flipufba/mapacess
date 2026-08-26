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

A segunda frente de coleta focou na extração de dados colaborativos da plataforma OpenStreetMap (OSM), que é conhecida por sua riqueza em atributos semânticos (tags) detalhados, muitos dos quais são essenciais para análises de acessibilidade.

#### 2.1. Fonte de Dados e Ferramenta

* **Fonte:** OpenStreetMap (OSM)
* **Ferramenta:** QGIS (v3.xx) com o plugin **QuickOSM**.
* **Área de Extração:** Foi utilizada a mesma camada vetorial do **buffer de 200 metros** (área de influência) gerado a partir do eixo da Av. Centenário, garantindo que ambas as coletas (SEFAZ e OSM) cobrissem exatamente a mesma área de estudo.

#### 2.2. Passos do Processamento no QGIS

1.  **Definição da Consulta:**
    * Ao contrário da fonte oficial, uma consulta única ao OSM retornou poucas feições. A estratégia adotada foi realizar **múltiplas consultas isoladas** e granulares no QuickOSM.
    * Essa abordagem permitiu "varrer" a área de estudo em busca de chaves (keys) e valores (tags) específicos, garantindo uma coleta mais completa.

2.  **Camadas Prioritárias Extraídas:**
    * As consultas foram direcionadas a chaves essenciais para caminhabilidade, resultando em um conjunto detalhado de camadas (pontos, linhas e polígonos). As principais camadas obtidas foram:

    * **Vias e Passeios:**
        * `footway_l` (Caminho de pedestre - linha)
        * `sidewalk_l` (Calçada - linha)
        * `highway_res_l` (Via residencial - linha)
        * `cycleway_l` (Ciclovia - linha)
        * `highway_steps_l` / `_p` (Escadarias - linha/ponto)

    * **Acessibilidade e Barreiras:**
        * `crossing_l` / `_h_p` (Travessia de pedestre - linha/ponto)
        * `barrier_l` / `_p` (Barreiras, ex: muretas, pilaretes - linha/ponto)
        * `kerb` (Atributo de meio-fio, geralmente em nós de travessia)

    * **Atributos de Superfície (Piso):**
        * `surface_asphalt_l` / `_a` (Superfície de asfalto)
        * `surface_concrete_l` (Superfície de concreto)

    * **Mobiliário e Contexto:**
        * `bus_stop_p`, `highway_stop_p` (Paradas de ônibus - ponto)
        * `amenity_p` / `_a` (Comodidades, ex: bancos, shoppings)
        * `building_a` (Edificações - polígono)

#### 2.3. Resultado

* Todas as camadas extraídas do OSM foram salvas e consolidadas em um único arquivo GeoPackage (`osm.gpkg`) para permitir a análise comparativa direta com os dados do `sefaz.gpkg`.
* A observação inicial clave é que, embora a cobertura geométrica do OSM possa ser, em alguns casos, menos completa que o cadastro oficial da SEFAZ, ela se mostrou **excepcionalmente rica em atributos semânticos** (como `surface` e `bus_stop`), que são cruciais para a análise de acessibilidade e estão ausentes na fonte oficial.

---
### 3\. Análise Comparativa das Fontes (SEFAZ × OSM)

Após a ingestão dos dados, foi realizada uma análise comparativa focada não apenas no conteúdo, mas também na estrutura dos dados e no esforço de tratamento necessário para cada fonte.

  * **Metodologia SEFAZ:** A ingestão foi direta (1-para-1). Cada camada do `sefaz.gpkg` (ex: `passeio_a`) gerou uma tabela respectiva no banco (ex: `sefaz.passeio_a`).
  * **Metodologia OSM:** A ingestão exigiu tratamento avançado (Muitos-para-3). Dezenas de camadas do `osm.gpkg` foram unificadas em três tabelas (`osm.point`, `osm.line`, `osm.polygon`) com uma coluna `origem` para rastreabilidade, resultando em uma estrutura com muitas colunas e dados nulos.

A tabela abaixo resume as descobertas da comparação:

| Feição de Acessibilidade | Fonte: SEFAZ (WFS Público) | Fonte: OSM (Dados Unificados) | Análise Comparativa e Observações |
| :--- | :--- | :--- | :--- |
| **Calçada / Passeio** | **Tabela(s):** `sefaz.passeio_a` (Polígono).<br>**Atributos:** Nenhum (só geometria). | **Tabela(s):** `osm.line` (onde `origem`='sidewalk\_l' ou 'footway\_l').<br>**Atributos Validados:** `surface` (preenchido às vezes), `sidewalk` (preenchido, ex: 'left', 'right', 'both'). | **Geometria:** SEFAZ (`passeio_a`) é superior (polígono oficial).<br>**Atributos:** OSM fornece dados de piso (`surface`) e posicionamento (`sidewalk`) ausentes na SEFAZ.<br>**Conclusão:** Usar geometria da SEFAZ; complementar com atributos do OSM. |
| **Travessia de Pedestre** | **Tabela(s):** `sefaz.travessia_pedestre_a` (Polígono).<br>**Atributos:** Nenhum. | **Tabela(s):** `osm.line` (`origem`='crossing\_l'), `osm.point` (`origem`='crossing\_h\_p').<br>**Atributos Validados:** `crossing` (preenchido, ex: 'uncontrolled', 'traffic\_signals'). | **Geometria:** Fontes concorrentes.<br>**Atributos:** O atributo `crossing` do OSM é a **informação semântica chave**, indicando o tipo de travessia, algo que a SEFAZ não informa.<br>**Conclusão:** Priorizar geometria da SEFAZ, mas **herdar o atributo `crossing` do OSM**. |
| **Rebaixamento de Meio-fio** | **Tabela(s):** `sefaz.rampa_a` (Polígono).<br>**Atributos:** Nenhum (só localização). | **Tabela(s):** `osm.point` (em nós de travessia).<br>**Atributos Validados:** `kerb` (preenchido: **SEMPRE NULO**). | **Geometria:** SEFAZ é a única fonte que mapeou a geometria da rampa (`rampa_a`).<br>**Atributos:** **LACUNA CRÍTICA.** Nenhuma fonte informa a *qualidade* da rampa (inclinação, etc.). A tag `kerb` do OSM, ideal para isso, está vazia na área de estudo. |
| **Acesso para Cadeira de Rodas** | **Tabela(s):** Nenhuma.<br>**Atributos:** --- | **Tabela(s):** Várias (`osm.point`, `osm.line`).<br>**Atributos Validados:** `wheelchair` (preenchido: **SEMPRE NULO**). | **Geometria:** ---<br>**Atributos:** **LACUNA CRÍTICA.** A informação mais vital para acessibilidade universal (`wheelchair=yes/no/limited`) está **totalmente ausente** em ambas as fontes para a área de estudo. |
| **Barreiras / Obstáculos** | **Tabela(s):** `sefaz.poste_p`, `sefaz.arvore_isolada_p`.<br>**Atributos:** Nenhum (só localização). | **Tabela(s):** `osm.point`/`osm.line` (onde `origem`='barrier\_p/l').<br>**Atributos Validados:** `barrier` (preenchido, ex: 'bollard', 'fence'), `access` (preenchido, ex: 'permissive'). | **Geometria:** Fontes complementares. SEFAZ tem o cadastro oficial de postes e árvores.<br>**Atributos:** OSM fornece a semântica do tipo de barreira e permissão de acesso.<br>**Conclusão:** **Unificar** as camadas no BDMapAcess. |
| **Mobiliário Urbano** | **Tabela(s):** Nenhuma.<br>**Atributos:** --- | **Tabela(s):** `osm.point` (onde `origem`='amenity\_p').<br>**Atributos Validados:** `amenity` (preenchido, ex: 'bench', 'bus\_stop'), `name` (preenchido às vezes). | **Geometria:** OSM é a *única* fonte.<br>**Atributos:** OSM fornece o tipo de mobiliário (banco, parada de ônibus), essencial para caminhabilidade.<br>**Conclusão:** Usar dados do OSM. |

#### 3.1. Principais Descobertas

A análise comparativa revela um desafio central no mapeamento da acessibilidade:

1.  **Fontes Oficiais (SEFAZ):** Possuem a melhor **precisão geométrica** (cadastro oficial, polígonos de calçadas), mas são **semanticamente pobres**, carecendo de *qualquer* atributo de acessibilidade (largura, piso, inclinação).
2.  **Fontes Colaborativas (OSM):** São **semanticamente ricas** em dados contextuais (tipo de travessia, tipo de barreira, mobiliário). No entanto, para a Av. Centenário, os atributos de acessibilidade mais críticos (`kerb` e `wheelchair`) estão **incompletos (nulos)**.
3.  **Implicação:** A descoberta de lacunas críticas em atributos como `kerb` e `wheelchair` valida as conclusões de estudos como o de Biagi et al. (2020), que apontam a **completude dos atributos** (e não apenas a sua existência) como o principal desafio do OSM para análises de acessibilidade.

-----

### 4\. Lista de Feições Recomendadas para o BDMapAcess

Com base na análise, o **BDMapAcess** deverá ser um **modelo de dados híbrido**. Ele não irá apenas "consumir" os dados, mas sim **estruturá-los para preenchimento futuro**.

O banco de dados (schema `public` ou `mapacess`) deverá conter as seguintes camadas prioritárias, que herdarão a geometria da fonte mais precisa (SEFAZ) e terão colunas criadas para os atributos de ambas as fontes (OSM e lacunas):

1.  **`calcadas` (Polígono):**

      * **Geometria:** `sefaz.passeio_a`.
      * **Atributos (Colunas):**
          * `id_calcada` (Chave Primária)
          * `largura_media` (Tipo: `numeric` - **NULO**, prioridade de levantamento)
          * `tipo_piso` (Tipo: `text` - *Preenchível via `osm.line` onde `surface` não é nulo*)
          * `tem_piso_tatil` (Tipo: `boolean` - **NULO**, prioridade de levantamento)
          * `qualidade_piso` (Tipo: `text` - **NULO**, prioridade de levantamento)

2.  **`travessias` (Linha ou Polígono):**

      * **Geometria:** `sefaz.travessia_pedestre_a` (convertido para linha) ou `osm.line` (onde `origem`='crossing\_l').
      * **Atributos (Colunas):**
          * `tipo_travessia` (Tipo: `text` - *Preenchível via `osm.point` onde `crossing` não é nulo*)
          * `tem_semaforo` (Tipo: `boolean` - *Derivado do `crossing`='traffic\_signals'*)
          * `rampa_inicio_id` (Chave Estrangeira para `rampas`)
          * `rampa_fim_id` (Chave Estrangeira para `rampas`)

3.  **`rampas` (Ponto):**

      * **Geometria:** Centroide de `sefaz.rampa_a`.
      * **Atributos (Colunas):**
          * `tipo_meiofio` (Tipo: `text` - *Preenchível via `osm.point` onde `kerb` não é nulo* - **LACUNA IDENTIFICADA**)
          * `acessivel_pcr` (Tipo: `boolean` - *Preenchível via `osm.point` onde `wheelchair` não é nulo* - **LACUNA IDENTIFICADA**)
          * `inclinacao_ok` (Tipo: `boolean` - **NULO**, prioridade de levantamento)

4.  **`obstaculos_mobiliarios` (Ponto):**

      * **Geometria:** Geometrias unificadas de `sefaz.poste_p`, `sefaz.arvore_isolada_p`, `osm.point` (onde `origem`='barrier\_p' ou 'amenity\_p' ou 'bus\_stop\_p').
      * **Atributos (Colunas):**
          * `tipo` (Tipo: `text` - Preenchido com 'poste', 'arvore', 'banco', 'parada\_onibus', 'barreira', etc.)
          * `subtipo` (Tipo: `text` - Preenchido com a tag original, ex: `barrier=gate`)
          * `nome` (Tipo: `text` - Preenchido via `name` do OSM)

-----
### 5. Próximos Passos: Modelagem e Consolidação

Com os dados das fontes oficiais (SEFAZ) e colaborativas (OSM) ingeridos e suas lacunas críticas identificadas, a próxima etapa foca na estruturação formal do banco de dados para criar um modelo conceitual e lógico.

O objetivo é consolidar a estrutura proposta na Seção 4 (Lista de Feições Recomendadas) para compor uma modelagem inicial robusta para o **BDMapAcess**.

As próximas tarefas incluem:

* **Análise de Dados em SQL:** Realizar o **confronto e a validação** dos dados diretamente no ambiente SQL (PostgreSQL/PostGIS). Esta etapa utilizará ferramentas de consulta como **DBeaver** e o próprio **QGIS** para analisar sobreposições espaciais, atributos nulos e inconsistências semânticas entre as tabelas `sefaz.*` e `osm.*`.
* **Desenho do Modelo de Dados:** Utilizar o software **OMT-g Designer**, baseado na metodologia de Clodoveu Davis Jr. e Luis Lizardo, para desenhar o modelo geo-conceitual (diagrama) do **BDMapAcess**.
* **Implementação do Modelo Físico:** Criar fisicamente as tabelas prioritárias (ex: `calcadas`, `travessias`, `obstaculos_mobiliarios`) no banco de dados, prontas para receber os dados tratados e, futuramente, os dados de levantamentos de campo.
-----
