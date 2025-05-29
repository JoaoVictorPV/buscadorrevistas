"""
Adaptador para a API Semantic Scholar.
Realiza buscas de artigos científicos na base de dados Semantic Scholar.
"""
import logging
import requests
from datetime import datetime

from utils import normalizacao

logger = logging.getLogger(__name__)

# URLs da API
BASE_URL = "https://api.semanticscholar.org/graph/v1"
PAPER_SEARCH_URL = f"{BASE_URL}/paper/search"

# Parâmetros comuns
API_PARAMS = {
    "limit": 100,
    "fields": "title,authors,venue,year,externalIds,url,abstract"
}

def buscar(termos, autor='', data_inicio=None, data_fim=None, revistas=None, limite=30):
    """
    Realiza busca na API Semantic Scholar.
    
    Args:
        termos (str): Termos de busca
        autor (str, opcional): Nome do autor para filtrar
        data_inicio (str, opcional): Data inicial no formato YYYY-MM-DD
        data_fim (str, opcional): Data final no formato YYYY-MM-DD
        revistas (list, opcional): Lista de IDs de revistas para filtrar
        limite (int, opcional): Número máximo de resultados
    
    Returns:
        list: Lista de resultados normalizados
    """
    try:
        logger.info(f"Iniciando busca no Semantic Scholar: {termos}")
        
        # Prepara a query
        query = termos
        if autor:
            query += f" author:{autor}"
        
        # Prepara parâmetros da requisição
        params = {
            **API_PARAMS,
            "query": query,
            "limit": min(limite, 100)  # Limita a 100 resultados por requisição
        }
        
        # Adiciona cabeçalhos
        headers = {
            "Accept": "application/json"
        }
        
        # Realiza a requisição
        response = requests.get(PAPER_SEARCH_URL, params=params, headers=headers)
        response.raise_for_status()
        
        # Processa a resposta
        data = response.json()
        
        # Extrai os resultados
        papers = data.get("data", [])
        
        # Normaliza os resultados
        resultados = []
        for paper in papers:
            resultado = processar_resultado(paper)
            
            # Filtra por data
            if data_inicio or data_fim:
                ano = resultado.get('ano')
                if ano:
                    ano_inicio = int(data_inicio.split('-')[0]) if data_inicio else 0
                    ano_fim = int(data_fim.split('-')[0]) if data_fim else 9999
                    
                    if ano < ano_inicio or ano > ano_fim:
                        continue
            
            # Filtra por revista
            if revistas and len(revistas) > 0:
                # Semantic Scholar não tem filtro direto por revista
                # Verificamos se a revista está na lista
                revista_id = resultado.get('revista_id', '')
                if revista_id and revista_id not in revistas:
                    continue
            
            resultados.append(resultado)
        
        logger.info(f"Busca no Semantic Scholar concluída: {len(resultados)} resultados")
        return resultados
    
    except Exception as e:
        logger.error(f"Erro na busca do Semantic Scholar: {str(e)}")
        return []

def processar_resultado(paper):
    """
    Processa um resultado da API Semantic Scholar.
    
    Args:
        paper (dict): Paper retornado pela API
    
    Returns:
        dict: Resultado normalizado
    """
    try:
        # Extrai dados básicos
        titulo = paper.get("title", "")
        
        # Extrai DOI
        external_ids = paper.get("externalIds", {})
        doi = external_ids.get("DOI", "")
        
        # Extrai ano
        ano = paper.get("year")
        
        # Cria data de publicação
        data_publicacao = f"{ano}-01-01" if ano else ""
        
        # Extrai revista
        venue = paper.get("venue", "")
        
        # Extrai autores
        autores = extrair_autores(paper.get("authors", []))
        
        # Extrai URL
        url = paper.get("url", "")
        if not url and doi:
            url = f"https://doi.org/{doi}"
        
        # Extrai resumo
        resumo = paper.get("abstract", "")
        
        # Cria ID único
        id_unico = f"semantic-{paper.get('paperId', '')}"
        
        # Cria o resultado normalizado
        resultado = {
            'id': id_unico,
            'titulo': titulo,
            'autores': autores,
            'revista': venue,
            'data_publicacao': data_publicacao,
            'doi': doi,
            'url': url,
            'resumo': resumo,
            'fonte': 'semantic_scholar',
            'ano': ano
        }
        
        return resultado
    
    except Exception as e:
        logger.error(f"Erro ao processar resultado Semantic Scholar: {str(e)}")
        return {}

def extrair_autores(autores_list):
    """
    Extrai a lista de autores do paper.
    
    Args:
        autores_list (list): Lista de autores do paper
    
    Returns:
        str: Lista de autores formatada
    """
    autores = []
    
    try:
        for autor in autores_list:
            nome = autor.get("name", "")
            if nome:
                autores.append(nome)
        
        # Limita a 10 autores
        if len(autores) > 10:
            autores = autores[:10]
            autores.append("et al.")
        
        return "; ".join(autores)
    
    except Exception as e:
        logger.error(f"Erro ao extrair autores: {str(e)}")
        return ""
