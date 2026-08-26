# 📘 Protocolo Técnico de Mapeamento: Av. Centenário (MapAcess)

**Versão:** 1.2 
**Estratégia:** Aquisição de geometria via Ortofoto PMS 2024 (7,5cm) + Atributos via Street View.

-----

## 1\. Objetivo

Realizar o mapeamento colaborativo e o preenchimento sistemático de atributos semânticos (tags) dos elementos de acessibilidade na região da Avenida Centenário e entorno.
O trabalho utiliza uma adaptação das metodologias de Biagi et al. (2020) e Cazumba (2024) com a finalidade de produzir subsídios robustos e reprodutíveis para análise de acessibilidade e caminhabilidade em contexto urbano.

-----

## 2\. Configuração do Ambiente (iD Editor)

Para garantir a precisão geométrica exigida, não utilize o mapa padrão.

1.  **Fundo (Background):** Selecione "Custom" e insira:
    `https://geo.salvador.ba.gov.br/imageserver/services/Ortofotos/2024/ImageServer/WMSServer?service=WMS&request=GetMap&version=1.1.1&layers=2024&styles=&format=image/png&srs={proj}&bbox={bbox}&width={width}&height={height}`
2.  **Visualização:** Utilize duas abas/telas: uma com o editor e outra com o Google Street View (GSV) para verificação de atributos.

-----

## 3\. Esquema Topológico de Referência (Geometria)

Para o mapeamento das travessias e conexões, adotamos rigorosamente o modelo topológico do projeto **ViaLibera**.

![ViaLibera?! Tagging Schema](ref/800px-ViaLiberaSchema.jpg)

> **Legenda e Topologia:**
>
>   * **Vias 1 e 3 (Vermelho):** Calçadas (`highway=footway` + `footway=sidewalk`).
>   * **Via 2 (Azul):** Eixo da rua (Veículos).
>   * **Via 4 (Verde):** Linha da Travessia (`footway=crossing`). Conecta as calçadas.
>   * **Pontos B e D:** Nós de Meio-Fio (`barrier=kerb`). Interface Calçada/Rua.
>   * **Ponto C:** Nó Central (`highway=crossing`). Interface Travessia/Rua.
>
> *Fonte: Projeto ViaLibera (Biagi et al., 2020). CC-BY 4.0.*

-----

## 4\. Tabelas de Etiquetagem (Tagging)

### 4.1. Calçadas (Sidewalks) - Vias 1 e 3

*Objeto: Linha separada da rua.*

| Elemento | Chave (Key) | Valor (Value) | Critério Visual (GSV / Ortofoto) |
| :--- | :--- | :--- | :--- |
| **Identificação** | `highway` | `footway` | Obrigatório. |
| **Subtipo** | `footway` | `sidewalk` | Obrigatório. |
| **Superfície** | `surface` | `concrete` | Cimento, placas de concreto. |
| | | `paving_stones` | Pedras portuguesas, blocos intertravados. |
| | | `asphalt` | Asfalto. |
| **Condição** | `smoothness` | `excellent` | Novo, sem falhas. |
| | | `good` | Estável, poucas emendas. |
| | | `bad` | Buracos, raízes expostas. |
| **Acessibilidade** | `tactile_paving` | `yes` / `no` | Se visível nas fotos. |
| **Uso** | `bicycle` | `no` | (Opcional) Explícito se não for ciclovia. |

### 4.2. Linha da Travessia - Via 4

*Objeto: Linha que conecta as duas calçadas.*

| Elemento | Chave (Key) | Valor (Value) | Critério Visual |
| :--- | :--- | :--- | :--- |
| **Identificação** | `highway` | `footway` | Obrigatório. |
| | `footway` | `crossing` | Obrigatório. |
| **Pintura** | `crossing` | `marked` | Se houver pintura. |
| **Tipo de Faixa** | `crossing:markings` | `zebra` | Faixa listrada (Zebra). |
| | | `lines` | Linhas paralelas. |
| **Meio-fio** | `kerb` | `yes` | Indica presença de desnível na rota. |
| **Acessibilidade** | `wheelchair` | `yes` | Se plana e segura. |
| | | `no` | Se perigosa/inadequada. |

### 4.3. Nó Central da Travessia - Ponto C

*Objeto: Ponto (Node) onde a travessia cruza o eixo da rua.*

| Elemento | Chave (Key) | Valor (Value) | Critério Visual |
| :--- | :--- | :--- | :--- |
| **Identificação** | `highway` | `crossing` | Obrigatório no nó. |
| | `footway` | `crossing` | (Reforço de identificação). |
| **Controle** | `crossing` | `traffic_signals` | Semáforo. |
| | | `uncontrolled` | Faixa sem semáforo. |
| **Pintura** | `crossing:markings` | `zebra` | Confirmar tipo de pintura. |

### 4.4. Meios-Fios e Rampas (Kerbs) - Pontos B e D

*Objeto: Ponto (Node) exato da transição Calçada/Rua.*

| Elemento | Chave (Key) | Valor (Value) | Critério Visual | Status Acessibilidade |
| :--- | :--- | :--- | :--- | :--- |
| **Barreira** | `barrier` | `kerb` | Obrigatório. | - |
| **Tipo** | `kerb` | `lowered` | Rampa/Rebaixado. | **Acessível** |
| | | `raised` | Degrau alto. | **Inacessível** |
| | | `flush` | Nivelado. | **Acessível** |
| **Acessibilidade** | `wheelchair` | `no` | Se `kerb=raised`. | - |
| **Detalhes** | `tactile_paving` | `yes`/`no` | Se sinaliza a travesia. | - |

### 4.5. Atração e Fachadas

*Objeto: Pontos (`Node`) ou Polígonos das edificações.*

| Elemento | Chave (Key) | Valor (Value) | Critério Visual |
| :--- | :--- | :--- | :--- |
| **Entrada** | `entrance` | `main` | Porta principal aberta. |
| **Uso** | `shop` | `bakery`, `clothes`... | Vitrines visíveis. |
| | `amenity` | `restaurant`, `bank`... | Serviços visíveis. |
| **Altura** | `building:levels`| `<número>` | Contagem de andares. |

-----

## 5\. Passo a Passo: Aquisição Geométrica e Topológica

Esta seção detalha a sequência de cliques para desenhar a rede de pedestres com a precisão necessária para roteamento.

### Passo 1: Preparar a Base (Ortofoto)
Antes de desenhar, garanta que você está vendo a imagem correta.
1.  Vá em **Configurações de Fundo** (Atalho `B`).
2.  Cole a URL WMS da PMS 2024.
3.  Ajuste o brilho se necessário para distinguir o meio-fio.

> ![Adiciona ortofoto](ref/gif1.gif)
> Procedimento de configuração de geosserviço da ortofoto de Salvador

---

### Passo 2: Vetorizar a Calçada (Vias 1 e 3)
O primeiro passo é criar o caminho longitudinal.
1.  Selecione a ferramenta **Linha** (Atalho `2`).
2.  Clique no início e vá traçando a linha exatamente no **centro** da calçada visível na Ortofoto.
3.  Ao terminar, selecione o tipo **"Caminho de Pedestre"** no menu esquerdo.
4.  **Tags Automáticas:** Certifique-se de que `highway=footway` e `footway=sidewalk` estão preenchidos.

> ![Vetoriza Calçada](ref/gif2.gif)
> Vetorização da calçada seguindo o meio visível da feição na ortofoto.

---

### Passo 3: Criar a Conexão da Travessia (Via 4)
Aqui criamos a ponte entre os dois lados da rua.
1.  Comece a linha clicando na **Linha da Calçada** que você acabou de desenhar (o nó deve "grudar" ou fazer *snap* na linha).
2.  Atravesse a rua clicando nas mudanças entre calça, meio-fio e rua para criar os nós os quais serão *taggeados* e finalize com um clique na **Calçada do outro lado**.
3.  Selecione a *Feature Type* altere para **"Marked Crossing"**.
4.  **Tags:** `footway=crossing`.

> ![Vetoriza travessia](ref/gif3.gif)
> Vetorização de travessia criando nós conforme *taggeamento* proposto no ViaLibera?!

---

### Passo 4: Definir os Nós Críticos (Topologia)
Agora vamos transformar os nós de junção em elementos de acessibilidade.

**A. O Meio-Fio (Nós B e D):**
1.  Selecione o nó onde a travessia toca a calçada.
2.  No campo de busca de etiquetas, digite **"Kerb"** ou **"Meio-fio"**.
3.  Preencha o valor (ex: `lowered` para rebaixado, `flush` para nivelado e `raised` para desnível elevado ).

> ![Caracteriza o meio fio](ref/gif4.gif)
> Caracterização dos nós que representam *kerb* ou meio fio ou desnível na rota de travessia.

**B. O Eixo da Rua (Nó C):**
1.  Dê um duplo clique onde a linha da travessia cruza a linha da rua (linha azul). Isso cria um novo nó.
2.  Etiquete este nó como **"Travessia"** (`highway=crossing`).
3.  Defina se tem semáforo ou é faixa simples.

> ![Caracteriza o nó central de travessia](ref/gif5.gif)
> Caracterização de nó central da travessia de pedestre.

---

## 5. Referência Visual de Tags (Exemplos)

### Exemplo: Calçada Padrão (Concreto)
> ![Tags da calçada](ref/print24.png)
> Exemplos de Tags da calçada preenchidas.

### Exemplo: Meio-Fio Inacessível
> ![Tags do meio-fio](ref/print25.png)
> Exemplos de Tags do meio-fio(kerb) preenchidas.

### Exemplo: Travessia Completa
> ![Tags da travessia](ref/print26.png)
> Exemplos de Tags da travessia preenchidas.

-----

## 6\. Fluxo de Trabalho e Boas Práticas

1.  **Priorize a Geometria:** Use a Ortofoto 2024 para desenhar as linhas com precisão.
2.  **Topologia é Vital:** Garanta que a Linha da Travessia (4) esteja conectada fisicamente à Calçada (1/3) através dos Nós de Meio-fio (B/D) e à Rua (2) através do Nó Central (C).
3.  **Regra da Incerteza:** Ao verificar atributos no Street View, confira a data da imagem. Se for antiga (\<2022) ou estiver obstruída, **não preencha a tag**. Deixe o valor em branco para validação futura em campo.
