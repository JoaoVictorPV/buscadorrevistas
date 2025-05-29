"""
Adaptador para a API Crossref.
Realiza buscas de artigos científicos na base de dados Crossref.
"""
import logging
import requests
from datetime import datetime

from utils import normalizacao

logger = logging.getLogger(__name__)

# URLs da API
BASE_URL = "https://api.crossref.org/works"

# Parâmetros comuns
API_PARAMS = {
    "rows": 100,
    "sort": "relevance",
    "order": "desc",
    "mailto": "contato@buscadorrevistas.com"  # Boa prática para identificação
}

def buscar(termos, autor='', data_inicio=None, data_fim=None, revistas=None, limite=30):
    """
    Realiza busca na API Crossref.
    
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
        logger.info(f"Iniciando busca no Crossref: {termos}")
        
        # Prepara parâmetros da requisição
        params = {
            **API_PARAMS,
            "query": termos,
            "rows": min(limite, 100)  # Limita a 100 resultados por requisição
        }
        
        # Adiciona filtro de autor
        if autor:
            params["query.author"] = autor
        
        # Adiciona filtro de data
        if data_inicio and data_fim:
            params["filter"] = f"from-pub-date:{data_inicio},until-pub-date:{data_fim}"
        
        # Adiciona filtro de revistas (ISSN)
        if revistas and len(revistas) > 0:
            # Mapeia IDs internos para ISSNs
            # Isso depende de um mapeamento específico que deve ser implementado
            # Por enquanto, usamos os IDs diretamente como exemplo
            issn_list = ",".join([f"issn:{r}" for r in revistas])
            if "filter" in params:
                params["filter"] += f",{issn_list}"
            else:
                params["filter"] = issn_list
        
        # Realiza a requisição
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Processa a resposta
        data = response.json()
        
        # Extrai os resultados
        items = data.get("message", {}).get("items", [])
        
        # Normaliza os resultados
        resultados = [processar_resultado(item) for item in items]
        
        # Filtra resultados inválidos
        resultados = [r for r in resultados if r.get('titulo')]
        
        logger.info(f"Busca no Crossref concluída: {len(resultados)} resultados")
        return resultados
    
    except Exception as e:
        logger.error(f"Erro na busca do Crossref: {str(e)}")
        return []

def processar_resultado(item):
    """
    Processa um resultado da API Crossref.
    
    Args:
        item (dict): Item retornado pela API
    
    Returns:
        dict: Resultado normalizado
    """
    try:
        # Extrai dados básicos
        doi = item.get("DOI", "")
        
        # Título
        titulo = ""
        if "title" in item and item["title"]:
            titulo = item["title"][0]
        
        # Data de publicação
        data_publicacao = extrair_data_publicacao(item)
        
        # Revista
        revista = ""
        if "container-title" in item and item["container-title"]:
            revista = item["container-title"][0]
        
        # Autores
        autores = extrair_autores(item)
        
        # URL
        url = item.get("URL", "")
        if not url and doi:
            url = f"https://doi.org/{doi}"
        
        # Resumo
        resumo = item.get("abstract", "")
        
        # Cria o resultado normalizado
        resultado = {
            'id': f"crossref-{doi.replace('/', '-')}",
            'titulo': titulo,
            'autores': autores,
            'revista': revista,
            'data_publicacao': data_publicacao,
            'doi': doi,
            'url': url,
            'resumo': resumo,
            'fonte': 'crossref'
        }
        
        return resultado
    
    except Exception as e:
        logger.error(f"Erro ao processar resultado Crossref: {str(e)}")
        return {}

def extrair_data_publicacao(item):
    """
    Extrai a data de publicação do item.
    
    Args:
        item (dict): Item retornado pela API
    
    Returns:
        str: Data no formato YYYY-MM-DD
    """
    try:
        # Tenta extrair da data de publicação
        if "published" in item and "date-parts" in item["published"]:
            date_parts = item["published"]["date-parts"][0]
            
            # Extrai ano, mês e dia
            ano = date_parts[0] if len(date_parts) > 0 else 1900
            mes = date_parts[1] if len(date_parts) > 1 else 1
            dia = date_parts[2] if len(date_parts) > 2 else 1
            
            # Formata a data
            return f"{ano:04d}-{mes:02d}-{dia:02d}"
        
        # Tenta extrair da data de criação
        elif "created" in item and "date-parts" in item["created"]:
            date_parts = item["created"]["date-parts"][0]
            
            # Extrai ano, mês e dia
            ano = date_parts[0] if len(date_parts) > 0 else 1900
            mes = date_parts[1] if len(date_parts) > 1 else 1
            dia = date_parts[2] if len(date_parts) > 2 else 1
            
            # Formata a data
            return f"{ano:04d}-{mes:02d}-{dia:02d}"
        
        return ""
    
    except Exception as e:
        logger.error(f"Erro ao extrair data de publicação: {str(e)}")
        return ""

def extrair_autores(item):
    """
    Extrai a lista de autores do item.
    
    Args:
        item (dict): Item retornado pela API
    
    Returns:
        str: Lista de autores formatada
    """
    autores = []
    
    try:
        # Busca lista de autores
        if "author" in item:
            for autor in item["author"]:
                # Extrai sobrenome e nome
                sobrenome = autor.get("family", "")
                nome = autor.get("given", "")
                
                # Formata o nome do autor
                if sobrenome and nome:
                    autores.append(f"{sobrenome}, {nome}")
                elif sobrenome:
                    autores.append(sobrenome)
                elif nome:
                    autores.append(nome)
        
        # Limita a 10 autores
        if len(autores) > 10:
            autores = autores[:10]
            autores.append("et al.")
        
        return "; ".join(autores)
    
    except Exception as e:
        logger.error(f"Erro ao extrair autores: {str(e)}")
        return ""
