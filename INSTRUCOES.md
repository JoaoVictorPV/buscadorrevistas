# Instruções de Uso - Buscador de Revistas Científicas

## Visão Geral

O Buscador de Revistas Científicas é uma aplicação local que permite realizar buscas avançadas em múltiplas bases de dados científicas, incluindo PubMed, Crossref, Semantic Scholar, OpenAlex, e Thieme Connect. A aplicação oferece uma interface intuitiva, suporte a operadores booleanos, e exportação de resultados em diversos formatos.

## Requisitos do Sistema

- Python 3.7 ou superior
- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Conexão com a internet para busca em APIs externas
- Aproximadamente 200MB de espaço em disco

## Instalação

### Windows

1. Descompacte o arquivo ZIP em uma pasta de sua preferência
2. Execute o arquivo `setup.py` clicando duas vezes ou via linha de comando:
   ```
   python setup.py
   ```
3. Aguarde a conclusão da instalação (criação do ambiente virtual e instalação de dependências)
4. Execute o arquivo `iniciar.bat` para iniciar a aplicação

### macOS / Linux

1. Descompacte o arquivo ZIP em uma pasta de sua preferência
2. Abra o terminal na pasta do projeto
3. Execute o script de instalação:
   ```
   python3 setup.py
   ```
4. Aguarde a conclusão da instalação
5. Execute o script de inicialização:
   ```
   ./iniciar.sh
   ```

## Uso da Aplicação

Após iniciar a aplicação, acesse-a através do navegador no endereço:
```
http://localhost:5563
```

### Realizando Buscas

1. **Termos de Busca**: Digite os termos desejados no campo principal
   - Use operadores booleanos: AND, OR, NOT (ex: "fratura AND joelho NOT pediátrico")
   - Use aspas para frases exatas: "ressonância magnética"

2. **Filtros**:
   - **Autor**: Especifique um autor para filtrar resultados
   - **Período**: Defina um intervalo de datas para a busca
   - **Revistas**: Selecione as revistas específicas na lista lateral

3. **Opções Avançadas**:
   - **Limite de Resultados**: Defina o número máximo de resultados (10-200)
   - **APIs**: Selecione quais bases de dados serão consultadas

4. Clique em "Buscar" para iniciar a pesquisa

### Visualizando Resultados

- Os resultados são exibidos em uma tabela interativa
- Clique nos cabeçalhos para ordenar por diferentes colunas
- Links diretos para artigos e DOIs estão disponíveis
- Indicadores visuais mostram artigos em acesso aberto

### Exportando Resultados

1. Selecione o formato desejado:
   - **HTML**: Tabela formatada com estilos e links
   - **PDF**: Documento profissional para impressão
   - **Excel**: Planilha com todos os metadados
   - **TXT**: Formato de texto simples para compatibilidade

2. Clique em "Exportar" para gerar o arquivo
3. Os arquivos exportados são salvos na pasta `dados/exportacao`

## Personalização

### Temas

- Alterne entre os temas claro e escuro usando o botão no canto superior direito
- As preferências de tema são salvas localmente no navegador

### Revistas

Para adicionar novas revistas ao catálogo:
1. Edite o arquivo `dados/revistas.json`
2. Adicione uma nova entrada seguindo o formato existente
3. Reinicie a aplicação para aplicar as alterações

## Solução de Problemas

### A aplicação não inicia

- Verifique se o Python 3.7+ está instalado e no PATH do sistema
- Verifique se todas as dependências foram instaladas corretamente
- Consulte o arquivo `setup.log` para detalhes sobre erros de instalação

### Erros durante a busca

- Verifique sua conexão com a internet
- Algumas APIs podem ter limites de requisição; tente novamente mais tarde
- Consulte os logs em `dados/logs` para informações detalhadas

## Suporte

Para suporte ou relatar problemas, abra uma issue no repositório GitHub:
https://github.com/JoaoVictorPV/buscadorrevistas

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.
