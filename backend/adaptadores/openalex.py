"""
Adaptador para a API OpenAlex.
Realiza buscas de artigos científicos na base de dados OpenAlex.
"""
import logging
import requests
from datetime import datetime

from utils import normalizacao

logger = logging.getLogger(__name__)

# URLs da API
BASE_URL = "https://api.openalex.org/works"

# Parâmetros comuns
API_PARAMS = {
    "per_page": 50,
    "sort": "relevance_score:desc",
    "mailto": "contato@buscadorrevistas.com"  # Boa prática para identificação
}

def buscar(termos, autor='', data_inicio=None, data_fim=None, revistas=None, limite=30):
    """
    Realiza busca na API OpenAlex.
    
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
        logger.info(f"Iniciando busca no OpenAlex: {termos}")
        
        # Prepara filtros
        filtros = []
        
        # Adiciona filtro de data
        if data_inicio or data_fim:
            inicio = data_inicio or "1900-01-01"
            fim = data_fim or datetime.now().strftime("%Y-%m-%d")
            filtros.append(f"publication_date:{inicio}:{fim}")
        
        # Adiciona filtro de autor
        if autor:
            filtros.append(f"author.display_name:\"{autor}\"")
        
        # Adiciona filtro de revistas
        if revistas and len(revistas) > 0:
            # OpenAlex usa ISSNs para revistas
            # Isso depende de um mapeamento específico que deve ser implementado
            # Por enquanto, não aplicamos filtro de revista
            pass
        
        # Prepara parâmetros da requisição
        params = {
            **API_PARAMS,
            "search": termos,
            "per_page": min(limite, 50)  # Limita a 50 resultados por requisição
        }
        
        # Adiciona filtros
        if filtros:
            params["filter"] = ",".join(filtros)
        
        # Realiza a requisição
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Processa a resposta
        data = response.json()
        
        # Extrai os resultados
        works = data.get("results", [])
        
        # Normaliza os resultados
        resultados = [processar_resultado(work) for work in works]
        
        # Filtra resultados inválidos
        resultados = [r for r in resultados if r.get('titulo')]
        
        logger.info(f"Busca no OpenAlex concluída: {len(resultados)} resultados")
        return resultados
    
    except Exception as e:
        logger.error(f"Erro na busca do OpenAlex: {str(e)}")
        return []

def processar_resultado(work):
    """
    Processa um resultado da API OpenAlex.
    
    Args:
        work (dict): Work retornado pela API
    
    Returns:
        dict: Resultado normalizado
    """
    try:
        # Extrai dados básicos
        titulo = work.get("title", "")
        
        # Extrai DOI
        doi = work.get("doi", "")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")
        
        # Extrai data de publicação
        data_publicacao = extrair_data_publicacao(work)
        
        # Extrai revista
        revista = ""
        if "primary_location" in work and work["primary_location"]:
            source = work["primary_location"].get("source")
            if source:
                revista = source.get("display_name", "")
        
        # Extrai autores
        autores = extrair_autores(work.get("authorships", []))
        
        # Extrai URL
        url = work.get("doi", "")
        if not url and doi:
            url = f"https://doi.org/{doi}"
        
        # Extrai resumo
        resumo = work.get("abstract_inverted_index", "")
        if resumo:
            # OpenAlex usa um formato especial para resumos
            # Aqui precisaríamos converter o índice invertido para texto
            # Por simplicidade, deixamos em branco
            resumo = ""
        
        # Cria o resultado normalizado
        resultado = {
            'id': f"openalex-{work.get('id', '').split('/')[-1]}",
            'titulo': titulo,
            'autores': autores,
            'revista': revista,
            'data_publicacao': data_publicacao,
            'doi': doi,
            'url': url,
            'resumo': resumo,
            'fonte': 'openalex'
        }
        
        return resultado
    
    except Exception as e:
        logger.error(f"Erro ao processar resultado OpenAlex: {str(e)}")
        return {}

def extrair_data_publicacao(work):
    """
    Extrai a data de publicação do work.
    
    Args:
        work (dict): Work retornado pela API
    
    Returns:
        str: Data no formato YYYY-MM-DD
    """
    try:
        # Tenta extrair da data de publicação
        data = work.get("publication_date")
        if data:
            return data
        
        # Se não tiver data completa, tenta extrair o ano
        ano = work.get("publication_year")
        if ano:
            return f"{ano}-01-01"
        
        return ""
    
    except Exception as e:
        logger.error(f"Erro ao extrair data de publicação: {str(e)}")
        return ""

def extrair_autores(authorships):
    """
    Extrai a lista de autores do work.
    
    Args:
        authorships (list): Lista de authorships do work
    
    Returns:
        str: Lista de autores formatada
    """
    autores = []
    
    try:
        for authorship in authorships:
            autor = authorship.get("author", {})
            nome = autor.get("display_name", "")
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
