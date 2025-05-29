"""
Módulo de validação de parâmetros.
Contém funções para validar parâmetros de busca e outros dados.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def validar_parametros_busca(parametros):
    """
    Valida os parâmetros de busca.
    
    Args:
        parametros (dict): Parâmetros de busca
    
    Returns:
        bool: True se os parâmetros são válidos, False caso contrário
    """
    # Verifica se há termos de busca
    if 'palavras' not in parametros or not parametros['palavras'].strip():
        logger.warning("Parâmetros de busca inválidos: palavras não informadas")
        return False
    
    # Valida datas
    if 'periodo_inicio' in parametros and parametros['periodo_inicio']:
        if not validar_data(parametros['periodo_inicio']):
            logger.warning(f"Data inicial inválida: {parametros['periodo_inicio']}")
            return False
    
    if 'periodo_fim' in parametros and parametros['periodo_fim']:
        if not validar_data(parametros['periodo_fim']):
            logger.warning(f"Data final inválida: {parametros['periodo_fim']}")
            return False
    
    # Valida limite de resultados
    if 'limite' in parametros:
        try:
            limite = int(parametros['limite'])
            if limite <= 0 or limite > 500:
                logger.warning(f"Limite de resultados inválido: {limite}")
                return False
        except:
            logger.warning(f"Limite de resultados não é um número: {parametros['limite']}")
            return False
    
    # Valida revistas
    if 'revistas' in parametros and parametros['revistas']:
        if not isinstance(parametros['revistas'], list):
            logger.warning(f"Lista de revistas inválida: {parametros['revistas']}")
            return False
    
    return True

def validar_data(data_str):
    """
    Valida se uma string representa uma data válida no formato YYYY-MM-DD.
    
    Args:
        data_str (str): String de data
    
    Returns:
        bool: True se a data é válida, False caso contrário
    """
    try:
        datetime.strptime(data_str, '%Y-%m-%d')
        return True
    except:
        return False
