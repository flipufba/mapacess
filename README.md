````markdown
# 🗺️ MapAcess — Mapeamento Colaborativo da Microacessibilidade Urbana

O **MapAcess** é um projeto acadêmico voltado à estruturação, representação e análise de informações geoespaciais relacionadas à **caminhabilidade e à microacessibilidade urbana**.

O repositório reúne dados, documentação, projetos SIG e scripts utilizados no desenvolvimento e na aplicação piloto de um **protocolo colaborativo de mapeamento da infraestrutura pedonal no OpenStreetMap (OSM)**.

A aplicação atualmente documentada utiliza como estudo de caso um trecho da **Avenida Centenário, em Salvador, Bahia**, com ênfase na representação de calçadas, travessias, interfaces de meio-fio e atributos associados à acessibilidade.

---

## Objetivo

O projeto busca sistematizar procedimentos para aquisição, interpretação, representação e análise de elementos de microacessibilidade urbana, considerando três dimensões principais:

- representação geométrica da infraestrutura pedonal;
- completude e consistência semântica dos atributos;
- conectividade e consistência topológica da rede pedonal.

O objetivo da aplicação piloto não é estimar globalmente a acessibilidade da Avenida Centenário, mas avaliar a aplicabilidade de um protocolo de mapeamento estruturado e reproduzível.

---

## Origem do projeto

O MapAcess foi inicialmente desenvolvido a partir de dados e procedimentos associados à pesquisa de **Danielle Marques Cazumba (UFBA, 2024)**:

> **Proposta de Metodologia para o Mapeamento Virtual da Caminhabilidade Urbana Associada à Acessibilidade por Imagens de Nível de Rua**

Os dados originais recebidos foram disponibilizados no arquivo:

```text
Dados_ICAM.zip
````

SHA256:

```text
16b2db1d70b6222fe9ebb4b1ddcb42730af53aa53dbcd61582450e65a0081c45
```

Esses materiais permanecem preservados em `data/raw/icam/`.

O desenvolvimento posterior integrou dados oficiais de Salvador, OpenStreetMap, imagens em nível de rua e procedimentos baseados no modelo de representação de acessibilidade do projeto ViaLibera.

---

## Estrutura do repositório

```text
mapacess/
├── data/
│   ├── raw/
│   │   ├── icam/
│   │   └── external/
│   │       ├── osm/
│   │       ├── sefaz/
│   │       └── prefeituras_bairro/
│   │
│   ├── study_area/
│   │   └── delimita.geojson
│   │
│   └── derived/
│       └── osm/
│           ├── exploratory/
│           └── snapshots/
│
├── scripts/
│   ├── ingestion/
│   ├── extraction/
│   └── analysis/
│
├── qgis/
│   └── projeto_qgis.qgz
│
├── results/
│   ├── exploratory/
│   ├── tables/
│   └── figures/
│
├── docs/
│   ├── assets/
│   ├── environment.md
│   ├── git_setup.md
│   └── tutorial_osm.md
│
├── references/
├── requirements.txt
├── .gitignore
└── README.md
```

### Organização dos dados

`data/raw/` contém dados recebidos ou obtidos de fontes externas e preservados como insumos do projeto.

`data/study_area/` contém a delimitação espacial utilizada na aplicação piloto. O arquivo canônico atualmente utilizado é:

```text
data/study_area/delimita.geojson
```

`data/derived/` contém dados produzidos a partir de procedimentos executados no projeto, incluindo as consultas históricas ao OpenStreetMap.

---

## Fontes de dados

As principais fontes utilizadas no projeto incluem:

**OpenStreetMap (OSM)**
Base geoespacial colaborativa utilizada para representação da infraestrutura pedonal e recuperação dos estados históricos analisados.

**Prefeitura Municipal de Salvador**
Dados cartográficos oficiais e Ortofoto 2024, utilizada como referência geométrica para a interpretação e vetorização dos elementos urbanos.

**Google Street View**
Imagens em nível de rua utilizadas de forma complementar para interpretação de características não suficientemente observáveis em vista superior.

**Dados ICAM**
Dados derivados da pesquisa de Danielle Marques Cazumba, preservados como referência metodológica e base histórica do projeto.

---

## Protocolo de mapeamento

A aplicação piloto utiliza um protocolo desenvolvido a partir da adaptação de procedimentos descritos por **Biagi et al. (2020)** no projeto ViaLibera e por **Cazumba (2024)**.

A versão utilizada como referência para a atividade colaborativa corresponde ao **Protocolo Técnico de Mapeamento da Avenida Centenário, versão 1.2**, associado ao commit:

```text
be8bccafd0b72716649a413907419fbc38028fcf
```

O escopo analisado concentra-se em:

```text
Calçadas
    highway=footway
    footway=sidewalk

Travessias
    highway=footway
    footway=crossing

Interfaces de meio-fio
    barrier=kerb

Nós de travessia
    highway=crossing
```

Entre os atributos analisados encontram-se `surface`, `smoothness`, `tactile_paving`, `kerb`, `wheelchair`, `crossing` e `crossing:markings`.

O tutorial utilizado durante a atividade de mapeamento encontra-se em:

```text
docs/tutorial_osm.md
```

---

## Extração histórica do OpenStreetMap

A recuperação histórica dos dados é realizada por meio da **ohsome API v1**, utilizando scripts Python.

Os scripts encontram-se em:

```text
scripts/extraction/
├── extrai_pt1.py
├── extrai_pt2.py
└── extrai_pt3.py
```

### Diagnóstico exploratório

`extrai_pt1.py` recupera um estado anterior à intervenção utilizando um filtro abrangente sobre a infraestrutura viária e pedonal.

Saída:

```text
data/derived/osm/exploratory/
└── osm_centenario_2025-11-17.geojson
```

### Estado T0

`extrai_pt2.py` reconstrói o estado imediatamente anterior à primeira edição incluída na aplicação analisada.

Intervalo utilizado:

```text
2025-11-18T14:28:09Z
2025-11-18T14:28:10Z
```

Saída:

```text
data/derived/osm/snapshots/
└── osm_centenario_filt_2025-11-18.geojson
```

### Estado T1

`extrai_pt3.py` reconstrói o estado imediatamente posterior à última edição considerada na aplicação.

Intervalo utilizado:

```text
2026-03-01T18:21:38Z
2026-03-01T18:21:39Z
```

Saída:

```text
data/derived/osm/snapshots/
└── osm_centenario_filt_2026-03-01.geojson
```

O mesmo polígono espacial e o mesmo filtro analítico são utilizados em T0 e T1.

---

## Reprodução das extrações

Recomenda-se utilizar um ambiente virtual Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Na raiz do repositório, as extrações podem ser reproduzidas com:

```bash
python3 scripts/extraction/extrai_pt1.py
python3 scripts/extraction/extrai_pt2.py
python3 scripts/extraction/extrai_pt3.py
```

Os scripts identificam automaticamente a raiz do repositório e utilizam:

```text
data/study_area/delimita.geojson
```

como recorte espacial.

---

## Ambiente computacional

O ambiente utilizado na etapa atual é documentado em:

```text
docs/environment.md
```

Principais componentes:

| Ferramenta         |  Versão |
| ------------------ | ------: |
| QGIS               |  3.44.3 |
| Python             |  3.12.3 |
| requests           |  2.31.0 |
| Visual Studio Code | 1.134.0 |
| ohsome API         |      v1 |

As dependências Python estão registradas em `requirements.txt`.

---

## Projeto QGIS

O projeto SIG principal está disponível em:

```text
qgis/projeto_qgis.qgz
```

As fontes de dados armazenadas no próprio repositório utilizam caminhos relativos, permitindo que o projeto seja aberto após a clonagem sem dependência dos diretórios locais utilizados durante seu desenvolvimento.

O projeto reúne dados de apoio, delimitação da área piloto e os estados históricos do OSM utilizados no estudo.

---

## Ingestão histórica em PostGIS

As primeiras etapas do MapAcess também envolveram a integração de dados provenientes do OSM e de fontes oficiais de Salvador em PostgreSQL/PostGIS.

Os scripts utilizados nessa etapa foram preservados em:

```text
scripts/ingestion/
├── ingest_osm.sh
└── ingest_sefaz.sh
```

Essa estrutura corresponde a uma etapa anterior do desenvolvimento do projeto e é mantida no repositório para documentação e rastreabilidade metodológica.

---

## Resultados

Os resultados exploratórios anteriores estão armazenados em:

```text
results/exploratory/
```

As próximas análises do estudo serão organizadas em:

```text
results/tables/
results/figures/
```

e os respectivos códigos serão desenvolvidos em:

```text
scripts/analysis/
```

A análise principal será baseada na comparação entre os estados T0 e T1, contemplando representação geométrica, completude semântica e consistência topológica.

---

## Referências e documentação

Materiais bibliográficos utilizados no desenvolvimento do projeto encontram-se em:

```text
references/
```

Documentação operacional, materiais do protocolo e informações sobre o ambiente computacional encontram-se em:

```text
docs/
```

---

## Créditos

**Dados e metodologia de referência:** Danielle Marques Cazumba
**Desenvolvimento, processamento geoespacial e automação:** Felipe Reis da Cruz
**Instituição:** Universidade Federal da Bahia — Escola Politécnica — Laboratório de Fotogrametria e Sensoriamento Remoto

---

## Status do projeto

O projeto encontra-se em desenvolvimento.

A estrutura de aquisição dos dados históricos e os estados T0 e T1 estão consolidados. As etapas seguintes compreendem a análise quantitativa e espacial dos dados, produção das tabelas e figuras e consolidação dos resultados do estudo científico.

```
