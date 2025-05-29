# Buscador de Revistas Científicas

Um aplicativo web robusto para busca de artigos científicos em revistas de ortopedia, radiologia e radiologia musculoesquelética, com interface personalizável e exportação em múltiplos formatos.

## Visão Geral

Este aplicativo permite realizar buscas avançadas em múltiplas bases de dados científicas, incluindo PubMed, Crossref, Semantic Scholar, OpenAlex, Unpaywall e Thieme Connect. Ele foi projetado para ser:

- **Robusto**: Backend confiável com tratamento de erros avançado
- **Eficiente**: Implementação de cache e processamento paralelo
- **Personalizável**: Temas claro/escuro e experiência responsiva
- **Versátil**: Exportação em múltiplos formatos (HTML, PDF, Excel, TXT)
- **Avançado**: Busca com operadores booleanos e filtros poderosos

## Funcionalidades

- Busca em múltiplas APIs científicas simultaneamente
- Filtragem por revista, período, autor e termos booleanos
- Visualização de resultados em tabela interativa
- Exportação de resultados em HTML, PDF, Excel e TXT
- Interface responsiva para desktop e dispositivos móveis
- Temas claro e escuro personalizáveis
- Gerenciamento flexível da lista de revistas

## Estrutura do Projeto

```
buscador-revistas/
├── backend/           # Servidor Flask e lógica de negócio
├── frontend/          # Interface de usuário
└── dados/             # Dados locais e cache
```

## Tecnologias Utilizadas

- **Backend**: Python, Flask, aiohttp, pandas
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Integração**: APIs científicas (PubMed, Crossref, etc.)
- **Exportação**: WeasyPrint (PDF), openpyxl (Excel)

## Instalação e Uso

### Requisitos

- Python 3.11 ou superior
- Navegador web moderno

### Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/JoaoVictorPV/buscadorrevistas.git
   cd buscadorrevistas
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. Instale as dependências:
   ```
   pip install -r backend/requirements.txt
   ```

### Execução

1. Inicie o servidor:
   ```
   # Windows
   start.bat
   
   # Linux/Mac
   python backend/app.py
   ```

2. Acesse a aplicação em seu navegador:
   ```
   http://localhost:5563
   ```

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Agradecimentos

- Desenvolvido com base no projeto original de busca de revistas científicas
- Utiliza múltiplas APIs científicas para obtenção de metadados
