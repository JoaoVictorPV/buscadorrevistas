"""
Sistema de cache para o Buscador de Revistas Científicas.
Gerencia o armazenamento e recuperação de resultados em cache.
"""
import os
import json
import time
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Diretório de cache padrão
CACHE_DIR = os.path.abspath('../dados/cache')

# Tempo de expiração padrão (1 hora)
CACHE_TIMEOUT = 3600

def gerar_chave_cache(termos, autor, data_inicio, data_fim, revistas, apis):
    """
    Gera uma chave única para o cache baseada nos parâmetros de busca.
    
    Args:
        termos (str): Termos de busca
        autor (str): Nome do autor
        data_inicio (str): Data inicial
        data_fim (str): Data final
        revistas (list): Lista de IDs de revistas
        apis (list): Lista de APIs consultadas
    
    Returns:
        str: Chave de cache
    """
    # Normaliza parâmetros para gerar chave consistente
    termos_norm = termos.lower().strip()
    autor_norm = autor.lower().strip() if autor else ""
    revistas_norm = sorted(revistas) if revistas else []
    apis_norm = sorted(apis) if apis else []
    
    # Cria string para hash
    params_str = f"{termos_norm}|{autor_norm}|{data_inicio}|{data_fim}|{','.join(revistas_norm)}|{','.join(apis_norm)}"
    
    # Gera hash MD5
    hash_obj = hashlib.md5(params_str.encode('utf-8'))
    return hash_obj.hexdigest()

def obter_caminho_cache(chave):
    """
    Obtém o caminho completo do arquivo de cache para uma chave.
    
    Args:
        chave (str): Chave de cache
    
    Returns:
        str: Caminho completo do arquivo
    """
    # Garante que o diretório de cache existe
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Retorna caminho do arquivo
    return os.path.join(CACHE_DIR, f"{chave}.json")

def obter_cache(chave):
    """
    Recupera resultados do cache se existirem e não estiverem expirados.
    
    Args:
        chave (str): Chave de cache
    
    Returns:
        list: Resultados em cache ou None se não existir ou estiver expirado
    """
    caminho = obter_caminho_cache(chave)
    
    # Verifica se o arquivo existe
    if not os.path.exists(caminho):
        return None
    
    try:
        # Lê o arquivo de cache
        with open(caminho, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Verifica se o cache expirou
        timestamp = cache_data.get('timestamp', 0)
        if time.time() - timestamp > CACHE_TIMEOUT:
            logger.info(f"Cache expirado para chave: {chave}")
            return None
        
        # Retorna os resultados
        logger.info(f"Cache encontrado para chave: {chave}")
        return cache_data.get('resultados', [])
    
    except Exception as e:
        logger.error(f"Erro ao ler cache: {str(e)}")
        return None

def armazenar_cache(chave, resultados):
    """
    Armazena resultados em cache.
    
    Args:
        chave (str): Chave de cache
        resultados (list): Resultados a serem armazenados
    
    Returns:
        bool: True se o cache foi armazenado com sucesso, False caso contrário
    """
    caminho = obter_caminho_cache(chave)
    
    try:
        # Cria estrutura de dados para o cache
        cache_data = {
            'timestamp': time.time(),
            'data': datetime.now().isoformat(),
            'resultados': resultados
        }
        
        # Escreve no arquivo
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Cache armazenado para chave: {chave}")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao armazenar cache: {str(e)}")
        return False

def limpar_cache_expirado():
    """
    Remove arquivos de cache expirados.
    
    Returns:
        int: Número de arquivos removidos
    """
    if not os.path.exists(CACHE_DIR):
        return 0
    
    removidos = 0
    agora = time.time()
    
    for arquivo in os.listdir(CACHE_DIR):
        if not arquivo.endswith('.json'):
            continue
        
        caminho = os.path.join(CACHE_DIR, arquivo)
        
        try:
            # Lê o timestamp do arquivo
            with open(caminho, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            timestamp = cache_data.get('timestamp', 0)
            
            # Remove se expirado
            if agora - timestamp > CACHE_TIMEOUT:
                os.remove(caminho)
                removidos += 1
        
        except Exception as e:
            logger.error(f"Erro ao verificar cache expirado: {str(e)}")
    
    logger.info(f"Limpeza de cache: {removidos} arquivos removidos")
    return removidos
