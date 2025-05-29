"""
Motor de busca do Buscador de Revistas Científicas.
Coordena as buscas em múltiplas APIs e processa os resultados.
"""
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Importa os adaptadores de APIs
from adaptadores import pubmed, crossref, semantic_scholar, openalex, unpaywall, thieme
from core import processador, cache
from utils import normalizacao

logger = logging.getLogger(__name__)

# Mapeamento de adaptadores disponíveis
ADAPTADORES = {
    'pubmed': pubmed,
    'crossref': crossref,
    'semantic_scholar': semantic_scholar,
    'openalex': openalex,
    'unpaywall': unpaywall,
    'thieme': thieme
}

def buscar(termos, autor='', data_inicio=None, data_fim=None, revistas=None, limite=30, apis=None):
    """
    Realiza busca em múltiplas APIs científicas e retorna resultados processados.
    
    Args:
        termos (str): Termos de busca (suporta operadores booleanos)
        autor (str, opcional): Nome do autor para filtrar
        data_inicio (str, opcional): Data inicial no formato YYYY-MM-DD
        data_fim (str, opcional): Data final no formato YYYY-MM-DD
        revistas (list, opcional): Lista de IDs de revistas para filtrar
        limite (int, opcional): Número máximo de resultados por API
        apis (list, opcional): Lista de APIs a serem consultadas (se None, usa todas)
    
    Returns:
        list: Lista de resultados processados e normalizados
    """
    logger.info(f"Iniciando busca: termos='{termos}', autor='{autor}', período={data_inicio} a {data_fim}, revistas={revistas}")
    
    # Normaliza datas
    if not data_inicio:
        data_inicio = (datetime.now().replace(year=datetime.now().year - 1)).strftime('%Y-%m-%d')
    if not data_fim:
        data_fim = datetime.now().strftime('%Y-%m-%d')
    
    # Normaliza revistas
    if revistas is None:
        revistas = []
    
    # Define quais APIs serão consultadas
    if apis is None:
        apis = list(ADAPTADORES.keys())
    
    # Verifica se há resultados em cache
    chave_cache = cache.gerar_chave_cache(termos, autor, data_inicio, data_fim, revistas, apis)
    resultados_cache = cache.obter_cache(chave_cache)
    
    if resultados_cache:
        logger.info(f"Resultados encontrados em cache para: {chave_cache}")
        return resultados_cache
    
    # Prepara parâmetros de busca normalizados
    parametros = {
        'termos': normalizacao.normalizar_termos_busca(termos),
        'autor': normalizacao.normalizar_autor(autor),
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'revistas': revistas,
        'limite': limite
    }
    
    # Inicia o tempo de execução
    tempo_inicio = time.time()
    
    # Executa buscas em paralelo
    resultados = executar_buscas_paralelas(parametros, apis)
    
    # Processa e normaliza resultados
    resultados_processados = processador.processar_resultados(resultados, parametros)
    
    # Limita ao número máximo de resultados
    if len(resultados_processados) > limite:
        resultados_processados = resultados_processados[:limite]
    
    # Registra tempo total de execução
    tempo_total = time.time() - tempo_inicio
    logger.info(f"Busca concluída em {tempo_total:.2f}s. Total de resultados: {len(resultados_processados)}")
    
    # Armazena em cache
    cache.armazenar_cache(chave_cache, resultados_processados)
    
    return resultados_processados

def executar_buscas_paralelas(parametros, apis):
    """
    Executa buscas em múltiplas APIs em paralelo.
    
    Args:
        parametros (dict): Parâmetros de busca
        apis (list): Lista de APIs a serem consultadas
    
    Returns:
        list: Lista de resultados de todas as APIs
    """
    resultados = []
    
    # Cria tarefas para cada API
    tarefas = []
    for api in apis:
        if api in ADAPTADORES:
            tarefas.append((api, parametros))
    
    # Executa tarefas em paralelo usando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(tarefas)) as executor:
        futures = {executor.submit(executar_busca_api, api, params): api 
                  for api, params in tarefas}
        
        for future in futures:
            try:
                api_resultados = future.result()
                if api_resultados:
                    resultados.extend(api_resultados)
            except Exception as e:
                api = futures[future]
                logger.error(f"Erro na busca da API {api}: {str(e)}")
    
    return resultados

def executar_busca_api(api, parametros):
    """
    Executa busca em uma API específica.
    
    Args:
        api (str): Nome da API
        parametros (dict): Parâmetros de busca
    
    Returns:
        list: Lista de resultados da API
    """
    try:
        logger.info(f"Iniciando busca na API: {api}")
        adaptador = ADAPTADORES[api]
        
        # Executa a busca no adaptador
        resultados = adaptador.buscar(
            termos=parametros['termos'],
            autor=parametros['autor'],
            data_inicio=parametros['data_inicio'],
            data_fim=parametros['data_fim'],
            revistas=parametros['revistas'],
            limite=parametros['limite']
        )
        
        logger.info(f"API {api}: {len(resultados)} resultados encontrados")
        
        # Adiciona a fonte aos resultados
        for resultado in resultados:
            resultado['fonte'] = api
        
        return resultados
    except Exception as e:
        logger.error(f"Erro ao buscar na API {api}: {str(e)}")
        return []
