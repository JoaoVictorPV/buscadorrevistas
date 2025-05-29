"""
Adaptador para a API Unpaywall.
Realiza buscas de artigos científicos na base de dados Unpaywall para verificar acesso aberto.
"""
import logging
import requests
from datetime import datetime

from utils import normalizacao

logger = logging.getLogger(__name__)

# URLs da API
BASE_URL = "https://api.unpaywall.org/v2"

# Parâmetros comuns
API_PARAMS = {
    "email": "contato@buscadorrevistas.com"  # Obrigatório para a API
}

def buscar(termos, autor='', data_inicio=None, data_fim=None, revistas=None, limite=30):
    """
    Realiza busca na API Unpaywall.
    
    Nota: Unpaywall não suporta busca direta por termos, apenas por DOI.
    Esta função é um placeholder para compatibilidade com a interface de adaptadores.
    
    Args:
        termos (str): Termos de busca (não utilizado)
        autor (str, opcional): Nome do autor para filtrar (não utilizado)
        data_inicio (str, opcional): Data inicial (não utilizado)
        data_fim (str, opcional): Data final (não utilizado)
        revistas (list, opcional): Lista de IDs de revistas (não utilizado)
        limite (int, opcional): Número máximo de resultados (não utilizado)
    
    Returns:
        list: Lista vazia (Unpaywall não suporta busca direta)
    """
    logger.info("Unpaywall não suporta busca direta por termos, apenas por DOI")
    return []

def verificar_acesso_aberto(doi):
    """
    Verifica se um artigo está disponível em acesso aberto.
    
    Args:
        doi (str): DOI do artigo
    
    Returns:
        dict: Informações de acesso aberto ou None se não encontrado
    """
    if not doi:
        return None
    
    try:
        logger.info(f"Verificando acesso aberto para DOI: {doi}")
        
        # Normaliza o DOI
        doi = normalizacao.normalizar_doi(doi)
        
        # Prepara a URL
        url = f"{BASE_URL}/{doi}"
        
        # Realiza a requisição
        response = requests.get(url, params=API_PARAMS)
        
        # Verifica se o artigo foi encontrado
        if response.status_code == 404:
            logger.info(f"DOI não encontrado no Unpaywall: {doi}")
            return None
        
        # Verifica outros erros
        response.raise_for_status()
        
        # Processa a resposta
        data = response.json()
        
        # Extrai informações de acesso aberto
        is_oa = data.get("is_oa", False)
        
        if not is_oa:
            logger.info(f"Artigo não está em acesso aberto: {doi}")
            return {
                "is_oa": False,
                "oa_url": None,
                "oa_status": "closed"
            }
        
        # Extrai a melhor URL de acesso aberto
        best_oa_location = None
        if "best_oa_location" in data and data["best_oa_location"]:
            best_oa_location = data["best_oa_location"]
        
        # Se não tiver a melhor localização, tenta as outras
        if not best_oa_location and "oa_locations" in data and data["oa_locations"]:
            best_oa_location = data["oa_locations"][0]
        
        # Extrai URL e status
        oa_url = best_oa_location.get("url") if best_oa_location else None
        oa_status = data.get("oa_status", "unknown")
        
        logger.info(f"Artigo em acesso aberto: {doi}, status: {oa_status}")
        
        return {
            "is_oa": True,
            "oa_url": oa_url,
            "oa_status": oa_status
        }
    
    except Exception as e:
        logger.error(f"Erro ao verificar acesso aberto: {str(e)}")
        return None

def enriquecer_resultado(resultado):
    """
    Enriquece um resultado com informações de acesso aberto.
    
    Args:
        resultado (dict): Resultado a ser enriquecido
    
    Returns:
        dict: Resultado enriquecido
    """
    if not resultado or "doi" not in resultado or not resultado["doi"]:
        return resultado
    
    try:
        # Verifica acesso aberto
        oa_info = verificar_acesso_aberto(resultado["doi"])
        
        if oa_info:
            # Adiciona informações de acesso aberto
            resultado["is_oa"] = oa_info["is_oa"]
            
            # Se tiver URL de acesso aberto, atualiza a URL do resultado
            if oa_info["is_oa"] and oa_info["oa_url"]:
                resultado["oa_url"] = oa_info["oa_url"]
                
                # Se não tiver URL ou for apenas DOI, usa a URL de acesso aberto
                if not resultado.get("url") or resultado["url"].startswith("https://doi.org/"):
                    resultado["url"] = oa_info["oa_url"]
            
            resultado["oa_status"] = oa_info["oa_status"]
        
        return resultado
    
    except Exception as e:
        logger.error(f"Erro ao enriquecer resultado com acesso aberto: {str(e)}")
        return resultado
