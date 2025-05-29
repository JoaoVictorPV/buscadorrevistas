"""
Adaptador para a API PubMed.
Realiza buscas de artigos científicos na base de dados PubMed.
"""
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from utils import normalizacao

logger = logging.getLogger(__name__)

# URLs da API
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ESEARCH_URL = f"{BASE_URL}/esearch.fcgi"
EFETCH_URL = f"{BASE_URL}/efetch.fcgi"
ESUMMARY_URL = f"{BASE_URL}/esummary.fcgi"

# Parâmetros comuns
API_PARAMS = {
    "db": "pubmed",
    "retmode": "json",
    "retmax": 100,
    "api_key": ""  # Opcional, mas recomendado para mais requisições
}

def buscar(termos, autor='', data_inicio=None, data_fim=None, revistas=None, limite=30):
    """
    Realiza busca na API PubMed.
    
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
        logger.info(f"Iniciando busca no PubMed: {termos}")
        
        # Constrói a query para o PubMed
        query = construir_query(termos, autor, data_inicio, data_fim, revistas)
        
        # Realiza a busca para obter IDs
        ids = buscar_ids(query, limite)
        
        if not ids:
            logger.info("Nenhum resultado encontrado no PubMed")
            return []
        
        # Obtém detalhes dos artigos
        resultados = obter_detalhes_artigos(ids)
        
        logger.info(f"Busca no PubMed concluída: {len(resultados)} resultados")
        return resultados
    
    except Exception as e:
        logger.error(f"Erro na busca do PubMed: {str(e)}")
        return []

def construir_query(termos, autor, data_inicio, data_fim, revistas):
    """
    Constrói a query para a API PubMed.
    
    Args:
        termos (str): Termos de busca
        autor (str): Nome do autor
        data_inicio (str): Data inicial
        data_fim (str): Data final
        revistas (list): Lista de IDs de revistas
    
    Returns:
        str: Query formatada para o PubMed
    """
    # Inicializa a query com os termos de busca
    query_parts = [f"({termos})"]
    
    # Adiciona filtro de autor
    if autor:
        query_parts.append(f"{autor}[Author]")
    
    # Adiciona filtro de data
    if data_inicio and data_fim:
        query_parts.append(f"{data_inicio}:{data_fim}[Date - Publication]")
    
    # Adiciona filtro de revistas
    if revistas and len(revistas) > 0:
        # Mapeia IDs internos para ISSNs ou nomes de revistas do PubMed
        # Isso depende de um mapeamento específico que deve ser implementado
        # Por enquanto, usamos os IDs diretamente como exemplo
        revistas_query = " OR ".join([f"{r}[Journal]" for r in revistas])
        if revistas_query:
            query_parts.append(f"({revistas_query})")
    
    # Combina todas as partes com AND
    return " AND ".join(query_parts)

def buscar_ids(query, limite):
    """
    Busca IDs de artigos no PubMed.
    
    Args:
        query (str): Query de busca
        limite (int): Número máximo de resultados
    
    Returns:
        list: Lista de IDs de artigos
    """
    params = {
        **API_PARAMS,
        "term": query,
        "retmax": limite,
        "sort": "relevance"
    }
    
    try:
        response = requests.get(ESEARCH_URL, params=params)
        response.raise_for_status()
        
        # Processa a resposta
        data = response.json()
        
        # Extrai os IDs
        ids = data.get("esearchresult", {}).get("idlist", [])
        
        return ids
    
    except Exception as e:
        logger.error(f"Erro ao buscar IDs no PubMed: {str(e)}")
        return []

def obter_detalhes_artigos(ids):
    """
    Obtém detalhes de artigos a partir de seus IDs.
    
    Args:
        ids (list): Lista de IDs de artigos
    
    Returns:
        list: Lista de resultados normalizados
    """
    if not ids:
        return []
    
    # Limita o número de IDs por requisição
    ids_str = ",".join(ids[:200])
    
    params = {
        **API_PARAMS,
        "id": ids_str,
        "retmode": "xml"  # XML fornece mais detalhes
    }
    
    try:
        response = requests.get(EFETCH_URL, params=params)
        response.raise_for_status()
        
        # Processa o XML
        return processar_xml_resultados(response.text)
    
    except Exception as e:
        logger.error(f"Erro ao obter detalhes de artigos no PubMed: {str(e)}")
        return []

def processar_xml_resultados(xml_text):
    """
    Processa o XML de resultados do PubMed.
    
    Args:
        xml_text (str): Texto XML da resposta
    
    Returns:
        list: Lista de resultados normalizados
    """
    resultados = []
    
    try:
        # Parse do XML
        root = ET.fromstring(xml_text)
        
        # Processa cada artigo
        for article in root.findall(".//PubmedArticle"):
            try:
                # Extrai dados básicos
                pmid = article.find(".//PMID").text
                
                # Título
                titulo_elem = article.find(".//ArticleTitle")
                titulo = titulo_elem.text if titulo_elem is not None else ""
                
                # DOI
                doi_elem = article.find(".//ArticleId[@IdType='doi']")
                doi = doi_elem.text if doi_elem is not None else ""
                
                # Data de publicação
                data_elem = article.find(".//PubDate")
                data_publicacao = extrair_data_publicacao(data_elem)
                
                # Revista
                revista_elem = article.find(".//Journal/Title")
                revista = revista_elem.text if revista_elem is not None else ""
                
                # Autores
                autores = extrair_autores(article)
                
                # Resumo
                resumo_elem = article.find(".//AbstractText")
                resumo = resumo_elem.text if resumo_elem is not None else ""
                
                # URL
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                
                # Cria o resultado normalizado
                resultado = {
                    'id': f"pubmed-{pmid}",
                    'titulo': titulo,
                    'autores': autores,
                    'revista': revista,
                    'data_publicacao': data_publicacao,
                    'doi': doi,
                    'url': url,
                    'resumo': resumo,
                    'fonte': 'pubmed'
                }
                
                resultados.append(resultado)
            
            except Exception as e:
                logger.error(f"Erro ao processar artigo PubMed: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Erro ao processar XML do PubMed: {str(e)}")
    
    return resultados

def extrair_data_publicacao(data_elem):
    """
    Extrai a data de publicação do elemento XML.
    
    Args:
        data_elem: Elemento XML com a data
    
    Returns:
        str: Data no formato YYYY-MM-DD
    """
    if data_elem is None:
        return ""
    
    try:
        # Tenta extrair ano, mês e dia
        ano = data_elem.find("Year")
        ano = ano.text if ano is not None else "1900"
        
        mes = data_elem.find("Month")
        mes = mes.text if mes is not None else "01"
        
        dia = data_elem.find("Day")
        dia = dia.text if dia is not None else "01"
        
        # Converte mês textual para número
        meses = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }
        
        if mes in meses:
            mes = meses[mes]
        
        # Normaliza mês e dia para dois dígitos
        try:
            mes = mes.zfill(2) if len(mes) < 2 else mes[:2]
            dia = dia.zfill(2) if len(dia) < 2 else dia[:2]
        except:
            mes = "01"
            dia = "01"
        
        # Formata a data
        return f"{ano}-{mes}-{dia}"
    
    except Exception as e:
        logger.error(f"Erro ao extrair data de publicação: {str(e)}")
        return ""

def extrair_autores(article):
    """
    Extrai a lista de autores do artigo.
    
    Args:
        article: Elemento XML do artigo
    
    Returns:
        str: Lista de autores formatada
    """
    autores = []
    
    try:
        # Busca elementos de autor
        autor_list = article.findall(".//Author")
        
        for autor in autor_list:
            # Extrai sobrenome e nome
            sobrenome = autor.find("LastName")
            sobrenome = sobrenome.text if sobrenome is not None else ""
            
            nome = autor.find("ForeName") or autor.find("FirstName")
            nome = nome.text if nome is not None else ""
            
            # Iniciais do nome
            iniciais = autor.find("Initials")
            iniciais = iniciais.text if iniciais is not None else ""
            
            # Formata o nome do autor
            if sobrenome and (nome or iniciais):
                if nome:
                    autores.append(f"{sobrenome}, {nome}")
                else:
                    autores.append(f"{sobrenome}, {iniciais}")
            elif sobrenome:
                autores.append(sobrenome)
        
        # Limita a 10 autores
        if len(autores) > 10:
            autores = autores[:10]
            autores.append("et al.")
        
        return "; ".join(autores)
    
    except Exception as e:
        logger.error(f"Erro ao extrair autores: {str(e)}")
        return ""
