# Documentação de APIs e Integrações

Este documento detalha as APIs científicas e integrações utilizadas no Buscador de Revistas Científicas, incluindo métodos de acesso, parâmetros e processamento de dados.

## 1. APIs Científicas Principais

### 1.1 PubMed (NCBI E-utilities)

**Descrição:** API oficial do National Center for Biotechnology Information (NCBI) que permite acesso à base de dados PubMed, uma das maiores coleções de literatura biomédica do mundo.

**Endpoints principais:**
- `esearch.fcgi`: Busca de artigos por termos
- `esummary.fcgi`: Recuperação de metadados resumidos
- `efetch.fcgi`: Recuperação de conteúdo completo

**Parâmetros de busca:**
- `db`: "pubmed" (fixo)
- `term`: Termos de busca (suporta operadores booleanos)
- `retmax`: Número máximo de resultados
- `sort`: Ordenação (relevance, pub_date)
- `datetype`: Tipo de data (pdat = data de publicação)
- `mindate`/`maxdate`: Intervalo de datas (YYYY/MM/DD)

**Exemplo de uso:**
```python
# Busca por artigos sobre "knee MRI" em revistas de radiologia
url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
params = {
    "db": "pubmed",
    "term": "knee MRI AND radiology[journal]",
    "retmax": 50,
    "sort": "pub_date",
    "retmode": "json"
}
```

**Processamento:** Os resultados são normalizados para extrair título, autores, data de publicação, DOI, resumo e outros metadados relevantes.

### 1.2 Crossref

**Descrição:** API que fornece acesso a metadados de publicações acadêmicas, incluindo DOIs, citações e referências.

**Endpoint principal:**
- `https://api.crossref.org/works`: Busca de trabalhos acadêmicos

**Parâmetros de busca:**
- `query`: Termos de busca
- `filter`: Filtros (tipo, data, ISSN)
- `rows`: Número de resultados
- `sort`: Ordenação (score, published-date)
- `order`: Direção da ordenação (asc, desc)

**Exemplo de uso:**
```python
# Busca por artigos sobre "musculoskeletal radiology" em uma revista específica
url = "https://api.crossref.org/works"
params = {
    "query": "musculoskeletal radiology",
    "filter": "issn:0364-2348,from-pub-date:2020-01-01,until-pub-date:2025-05-29",
    "rows": 30,
    "sort": "published-date",
    "order": "desc"
}
```

**Processamento:** Os resultados são normalizados para extrair título, autores, data de publicação, DOI, URL e outros metadados relevantes.

### 1.3 Semantic Scholar

**Descrição:** API que fornece acesso a artigos científicos com análise semântica e dados de citação.

**Endpoints principais:**
- `/paper/search`: Busca de artigos
- `/paper/{paper_id}`: Detalhes de artigo específico

**Parâmetros de busca:**
- `query`: Termos de busca
- `fields`: Campos a serem retornados
- `limit`: Número de resultados
- `year`: Filtro por ano de publicação

**Exemplo de uso:**
```python
# Busca por artigos sobre "orthopedic imaging"
url = "https://api.semanticscholar.org/graph/v1/paper/search"
params = {
    "query": "orthopedic imaging",
    "fields": "title,authors,year,venue,abstract,externalIds,url",
    "limit": 30
}
```

**Processamento:** Os resultados são normalizados para extrair título, autores, ano, revista, resumo, DOI e outros identificadores externos.

### 1.4 OpenAlex

**Descrição:** API que fornece acesso aberto a dados acadêmicos, incluindo trabalhos, autores, instituições e revistas.

**Endpoints principais:**
- `/works`: Busca de trabalhos acadêmicos
- `/journals`: Informações sobre revistas

**Parâmetros de busca:**
- `filter`: Filtros diversos (título, autor, data)
- `search`: Termos de busca
- `sort`: Ordenação

**Exemplo de uso:**
```python
# Busca por artigos em uma revista específica
url = "https://api.openalex.org/works"
params = {
    "filter": "journal.issn:0364-2348",
    "search": "musculoskeletal radiology",
    "sort": "publication_date:desc"
}
```

**Processamento:** Os resultados são normalizados para extrair título, autores, data de publicação, DOI, resumo e outros metadados relevantes.

### 1.5 Unpaywall

**Descrição:** API que fornece informações sobre acesso aberto a artigos científicos.

**Endpoint principal:**
- `https://api.unpaywall.org/v2/{doi}`: Informações de acesso aberto por DOI

**Parâmetros:**
- `email`: Email para identificação (obrigatório)

**Exemplo de uso:**
```python
# Verificar status de acesso aberto de um artigo
doi = "10.1007/s00256-020-03401-3"
url = f"https://api.unpaywall.org/v2/{doi}"
params = {
    "email": "user@example.com"
}
```

**Processamento:** Os resultados são utilizados para enriquecer os metadados dos artigos com informações sobre acesso aberto, incluindo links para versões de acesso aberto quando disponíveis.

### 1.6 Thieme Connect (Nova)

**Descrição:** Integração com a plataforma Thieme Connect, que abrange diversas revistas científicas de radiologia e ortopedia.

**Método de acesso:** Combinação de API (quando disponível) e web scraping respeitoso.

**Parâmetros de busca:**
- Termos de busca
- Filtros de data
- Filtros de tipo de conteúdo

**Processamento:** Os resultados são normalizados para extrair título, autores, data de publicação, DOI, resumo e outros metadados relevantes, seguindo o mesmo padrão das outras APIs.

## 2. Integração com OpenAI API

**Descrição:** Integração com a API da OpenAI para melhorar a experiência do usuário e a qualidade dos resultados.

**Usos principais:**
- Refinamento de consultas de busca
- Sugestões de termos relacionados
- Resumo de artigos longos
- Tradução de termos técnicos

**Endpoint principal:**
- `https://api.openai.com/v1/chat/completions`

**Modelo utilizado:**
- GPT-4 ou equivalente

**Exemplo de uso:**
```python
# Refinar uma consulta de busca
from openai import OpenAI

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Você é um assistente especializado em pesquisa médica."},
        {"role": "user", "content": "Refine esta consulta para busca em bases científicas: 'dor no joelho imagem'"}
    ]
)
```

**Processamento:** As respostas da API são utilizadas para melhorar a experiência do usuário e a qualidade dos resultados, sem substituir as funcionalidades principais do aplicativo.

## 3. Revistas Incluídas

O aplicativo inclui um catálogo inicial de revistas científicas relevantes para ortopedia, radiologia e radiologia musculoesquelética, incluindo:

1. **Thieme Connect** - Plataforma que abrange diversas revistas científicas
2. **American Journal of Roentgenology (AJR)** - Revista líder em radiologia diagnóstica
3. **RadioGraphics** - Revista educacional da RSNA
4. **Radiology** - Revista científica da RSNA
5. **The Journal of Bone and Joint Surgery** - Revista respeitada em ortopedia
6. **Clinical Orthopaedics and Related Research** - Focada em pesquisa ortopédica
7. **Journal of Magnetic Resonance Imaging** - Especializada em ressonância magnética
8. **Skeletal Radiology** - Dedicada à radiologia musculoesquelética
9. **European Journal of Radiology** - Revista europeia de radiologia
10. **British Journal of Radiology** - Publicada pelo British Institute of Radiology
11. **Journal of Computer Assisted Tomography** - Focada em técnicas de imagem avançadas
12. **Acta Orthopaedica** - Revista internacional de ortopedia
13. **Journal of Orthopaedic Research** - Revista oficial da Orthopaedic Research Society
14. **American Journal of Sports Medicine** - Líder em medicina esportiva
15. **Journal of Ultrasound in Medicine** - Revista oficial da American Institute of Ultrasound in Medicine

O catálogo pode ser facilmente expandido pelo usuário através da interface do aplicativo.

## 4. Fluxo de Integração

O aplicativo segue um fluxo de integração que maximiza a cobertura e a qualidade dos resultados:

1. **Recebimento da consulta** do usuário com termos de busca, filtros e seleção de revistas
2. **Distribuição da consulta** para múltiplas APIs em paralelo
3. **Normalização dos resultados** de cada API para um formato comum
4. **Deduplicação** baseada em DOI e similaridade de título
5. **Enriquecimento** com dados adicionais (acesso aberto, links, etc.)
6. **Ordenação e filtragem** conforme preferências do usuário
7. **Apresentação dos resultados** na interface
8. **Exportação** nos formatos selecionados pelo usuário

Este fluxo garante resultados abrangentes, precisos e úteis para o usuário final.
