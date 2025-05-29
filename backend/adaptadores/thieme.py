"""
Adaptador para a API Thieme Connect.
Realiza buscas de artigos científicos na base de dados Thieme Connect.
"""
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from utils import normalizacao

logger = logging.getLogger(__name__)

# URLs da API
BASE_URL = "https://www.thieme-connect.com/products/ejournals/search"

# Parâmetros comuns
API_PARAMS = {
    "journal": "10.1055/s-00000070",
    "sortOrder": "relevance",
    "resultsPerPage": 50
}

def buscar(termos, autor='', data_inicio=None, data_fim=None, revistas=None, limite=30):
    """
    Realiza busca na API Thieme Connect.
    
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
        logger.info(f"Iniciando busca no Thieme Connect: {termos}")
        
        # Prepara parâmetros da requisição
        params = {
            **API_PARAMS,
            "searchTerm": termos,
            "resultsPerPage": min(limite, 50)  # Limita a 50 resultados por requisição
        }
        
        # Adiciona filtro de autor
        if autor:
            params["author"] = autor
        
        # Adiciona filtro de data
        if data_inicio and data_fim:
            params["startDate"] = data_inicio
            params["endDate"] = data_fim
        
        # Adiciona filtro de revistas
        if revistas and len(revistas) > 0:
            # Thieme Connect usa seu próprio sistema de IDs
            # Aqui precisaríamos mapear os IDs internos para os IDs da Thieme
            # Por enquanto, mantemos o ID padrão
            pass
        
        # Realiza a requisição
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Processa a resposta HTML
        resultados = extrair_resultados_html(response.text, limite)
        
        logger.info(f"Busca no Thieme Connect concluída: {len(resultados)} resultados")
        return resultados
    
    except Exception as e:
        logger.error(f"Erro na busca do Thieme Connect: {str(e)}")
        return []

def extrair_resultados_html(html, limite):
    """
    Extrai resultados do HTML da página de busca do Thieme Connect.
    
    Args:
        html (str): Conteúdo HTML da página
        limite (int): Número máximo de resultados
    
    Returns:
        list: Lista de resultados normalizados
    """
    resultados = []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Encontra os elementos de resultado
        artigos = soup.select('.searchResultItem')
        
        for artigo in artigos[:limite]:
            try:
                # Extrai título
                titulo_elem = artigo.select_one('.articleTitle')
                titulo = titulo_elem.text.strip() if titulo_elem else ""
                
                # Extrai link
                link_elem = titulo_elem.find('a') if titulo_elem else None
                url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                
                # Extrai DOI
                doi = ""
                if url and "doi" in url:
                    doi = url.split("doi/")[-1]
                
                # Extrai autores
                autores_elem = artigo.select_one('.authors')
                autores = autores_elem.text.strip() if autores_elem else ""
                
                # Extrai revista
                revista_elem = artigo.select_one('.journalName')
                revista = revista_elem.text.strip() if revista_elem else "Thieme Connect"
                
                # Extrai data
                data_elem = artigo.select_one('.pubDate')
                data_publicacao = extrair_data_publicacao(data_elem.text.strip() if data_elem else "")
                
                # Extrai resumo
                resumo_elem = artigo.select_one('.abstract')
                resumo = resumo_elem.text.strip() if resumo_elem else ""
                
                # Cria ID único
                id_unico = f"thieme-{doi.replace('/', '-')}" if doi else f"thieme-{len(resultados)}"
                
                # Cria o resultado normalizado
                resultado = {
                    'id': id_unico,
                    'titulo': titulo,
                    'autores': autores,
                    'revista': revista,
                    'data_publicacao': data_publicacao,
                    'doi': doi,
                    'url': url,
                    'resumo': resumo,
                    'fonte': 'thieme'
                }
                
                resultados.append(resultado)
            
            except Exception as e:
                logger.error(f"Erro ao processar artigo Thieme: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Erro ao extrair resultados do HTML Thieme: {str(e)}")
    
    return resultados

def extrair_data_publicacao(data_texto):
    """
    Extrai a data de publicação do texto.
    
    Args:
        data_texto (str): Texto contendo a data
    
    Returns:
        str: Data no formato YYYY-MM-DD
    """
    try:
        # Formatos comuns no Thieme Connect
        formatos = [
            "%B %Y",           # January 2023
            "%d %B %Y",        # 15 January 2023
            "%Y-%m-%d",        # 2023-01-15
            "%Y/%m/%d",        # 2023/01/15
            "%d.%m.%Y",        # 15.01.2023
            "%m/%d/%Y"         # 01/15/2023
        ]
        
        for formato in formatos:
            try:
                data = datetime.strptime(data_texto, formato)
                return data.strftime("%Y-%m-%d")
            except:
                continue
        
        # Se não conseguir extrair, tenta extrair apenas o ano
        import re
        ano_match = re.search(r'\b(19|20)\d{2}\b', data_texto)
        if ano_match:
            return f"{ano_match.group(0)}-01-01"
        
        return ""
    
    except Exception as e:
        logger.error(f"Erro ao extrair data de publicação: {str(e)}")
        return ""
