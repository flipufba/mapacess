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

Os dados foram inseridos em uma base de dados **PostgreSQL 14** com **extensão PostGIS** instalada.

A configuração foi realizada em uma máquina do **Laboratório de Fotogrametria e Sensoriamento Remoto (LabFSR)**, com as seguintes informações:

| Parâmetro | Valor |
|------------|--------|
| IP         | `10.131.32.26` |
| Porta      | `5432` |
| Banco de dados | `mapacess` |
| Schema     | `barra` |
| Status     | Em análise de viabilidade de acesso externo (rede local atualmente) |

---

## 🧩 Ingestão dos Dados

A ingestão dos shapefiles foi realizada com o utilitário **`shp2pgsql`**, conforme os comandos abaixo:

```bash
# Diretório dos dados ICAM
cd ~/felipe/gits/mapacess/Dados_ICAM/icam

# Importação da camada ICAM_Barra_Copia
shp2pgsql -I -s 31984 -W "UTF-8" ICAM_Barra_Copia.shp barra.icam | psql -h localhost -U user -d mapacess -W

# Diretório dos dados validados
cd ~/felipe/gits/mapacess/Dados_ICAM/barra_ok

# Importação da camada ICAM_Barra_OK
shp2pgsql -I -s 31984 -W "UTF-8" ICAM_Barra_OK.shp barra.icam_ok | psql -h localhost -U user -d mapacess -W
````

> **Nota:**
> O sistema de referência utilizado é **SIRGAS 2000 / UTM Zona 24S (EPSG:31984)** e a codificação de caracteres foi definida como **UTF-8**.

---

## 🔍 Próximas Etapas

* [ ] Tratamento dos dados e viabilidade de melhorias
* [ ] Viabilizar possibilidade de acréscimo de variáveis e dados
* [ ] Organização das análises derivadas por categoria temática
* [ ] Estruturação dos scripts SQL para automação da ingestão
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
