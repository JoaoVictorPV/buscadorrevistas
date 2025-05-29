"""
Processador de resultados do Buscador de Revistas Científicas.
Responsável por normalizar, enriquecer e deduplica resultados.
"""
import logging
from datetime import datetime
from difflib import SequenceMatcher

from utils import normalizacao

logger = logging.getLogger(__name__)

def processar_resultados(resultados, parametros):
    """
    Processa os resultados de múltiplas APIs, normalizando, enriquecendo e deduplicando.
    
    Args:
        resultados (list): Lista de resultados de todas as APIs
        parametros (dict): Parâmetros de busca originais
    
    Returns:
        list: Lista de resultados processados
    """
    logger.info(f"Processando {len(resultados)} resultados brutos")
    
    # Normaliza os resultados
    resultados_normalizados = [normalizar_resultado(r) for r in resultados]
    
    # Remove resultados inválidos
    resultados_validos = [r for r in resultados_normalizados if validar_resultado(r)]
    
    # Deduplica resultados
    resultados_unicos = deduplica_resultados(resultados_validos)
    
    # Filtra por critérios adicionais
    resultados_filtrados = filtrar_resultados(resultados_unicos, parametros)
    
    # Ordena resultados (padrão: por data, mais recentes primeiro)
    resultados_ordenados = ordenar_resultados(resultados_filtrados)
    
    logger.info(f"Processamento concluído: {len(resultados_ordenados)} resultados finais")
    
    return resultados_ordenados

def normalizar_resultado(resultado):
    """
    Normaliza um resultado para o formato padrão da aplicação.
    
    Args:
        resultado (dict): Resultado bruto de uma API
    
    Returns:
        dict: Resultado normalizado
    """
    # Cria um resultado normalizado com campos padrão
    normalizado = {
        'id': resultado.get('id', ''),
        'titulo': normalizacao.normalizar_texto(resultado.get('titulo', '')),
        'autores': normalizacao.normalizar_autores(resultado.get('autores', '')),
        'revista': normalizacao.normalizar_texto(resultado.get('revista', '')),
        'data_publicacao': normalizacao.normalizar_data(resultado.get('data_publicacao', '')),
        'doi': normalizacao.normalizar_doi(resultado.get('doi', '')),
        'url': resultado.get('url', ''),
        'resumo': normalizacao.normalizar_texto(resultado.get('resumo', '')),
        'fonte': resultado.get('fonte', '')
    }
    
    # Gera URL a partir do DOI se não existir
    if not normalizado['url'] and normalizado['doi']:
        normalizado['url'] = f"https://doi.org/{normalizado['doi']}"
    
    # Gera ID único se não existir
    if not normalizado['id']:
        normalizado['id'] = gerar_id_resultado(normalizado)
    
    return normalizado

def validar_resultado(resultado):
    """
    Valida se um resultado contém os campos mínimos necessários.
    
    Args:
        resultado (dict): Resultado normalizado
    
    Returns:
        bool: True se o resultado é válido, False caso contrário
    """
    # Verifica campos obrigatórios
    if not resultado.get('titulo'):
        return False
    
    if not resultado.get('data_publicacao'):
        return False
    
    # Verifica se tem DOI ou URL
    if not resultado.get('doi') and not resultado.get('url'):
        return False
    
    return True

def deduplica_resultados(resultados):
    """
    Remove resultados duplicados baseado em DOI e similaridade de título.
    
    Args:
        resultados (list): Lista de resultados normalizados
    
    Returns:
        list: Lista de resultados sem duplicatas
    """
    # Primeiro agrupa por DOI
    resultados_por_doi = {}
    resultados_sem_doi = []
    
    for resultado in resultados:
        doi = resultado.get('doi')
        if doi:
            if doi not in resultados_por_doi:
                resultados_por_doi[doi] = resultado
            else:
                # Se já existe, mantém o mais completo
                resultados_por_doi[doi] = escolher_resultado_mais_completo(
                    resultados_por_doi[doi], resultado
                )
        else:
            resultados_sem_doi.append(resultado)
    
    # Resultados com DOI já estão deduplicados
    resultados_deduplicados = list(resultados_por_doi.values())
    
    # Para resultados sem DOI, verifica similaridade de título
    for resultado in resultados_sem_doi:
        duplicado = False
        for idx, res_existente in enumerate(resultados_deduplicados):
            if similaridade_titulo(resultado, res_existente) > 0.85:
                # Encontrou duplicata, mantém o mais completo
                resultados_deduplicados[idx] = escolher_resultado_mais_completo(
                    res_existente, resultado
                )
                duplicado = True
                break
        
        if not duplicado:
            resultados_deduplicados.append(resultado)
    
    return resultados_deduplicados

def similaridade_titulo(resultado1, resultado2):
    """
    Calcula a similaridade entre títulos de dois resultados.
    
    Args:
        resultado1 (dict): Primeiro resultado
        resultado2 (dict): Segundo resultado
    
    Returns:
        float: Valor de similaridade entre 0 e 1
    """
    titulo1 = resultado1.get('titulo', '').lower()
    titulo2 = resultado2.get('titulo', '').lower()
    
    return SequenceMatcher(None, titulo1, titulo2).ratio()

def escolher_resultado_mais_completo(resultado1, resultado2):
    """
    Escolhe o resultado mais completo entre dois resultados duplicados.
    
    Args:
        resultado1 (dict): Primeiro resultado
        resultado2 (dict): Segundo resultado
    
    Returns:
        dict: O resultado mais completo
    """
    # Critérios de completude (campos não vazios)
    campos = ['resumo', 'autores', 'revista', 'url']
    pontos1 = sum(1 for campo in campos if resultado1.get(campo))
    pontos2 = sum(1 for campo in campos if resultado2.get(campo))
    
    # Prefere o resultado com mais informações
    if pontos1 >= pontos2:
        # Mantém resultado1, mas pega campos extras de resultado2 se estiverem vazios
        for campo in campos:
            if not resultado1.get(campo) and resultado2.get(campo):
                resultado1[campo] = resultado2[campo]
        return resultado1
    else:
        # Mantém resultado2, mas pega campos extras de resultado1 se estiverem vazios
        for campo in campos:
            if not resultado2.get(campo) and resultado1.get(campo):
                resultado2[campo] = resultado1[campo]
        return resultado2

def filtrar_resultados(resultados, parametros):
    """
    Filtra resultados com base nos parâmetros de busca.
    
    Args:
        resultados (list): Lista de resultados normalizados
        parametros (dict): Parâmetros de busca
    
    Returns:
        list: Lista de resultados filtrados
    """
    resultados_filtrados = resultados
    
    # Filtra por data
    if parametros.get('data_inicio') or parametros.get('data_fim'):
        data_inicio = datetime.strptime(parametros.get('data_inicio', '1900-01-01'), '%Y-%m-%d')
        data_fim = datetime.strptime(parametros.get('data_fim', '2100-12-31'), '%Y-%m-%d')
        
        resultados_filtrados = [
            r for r in resultados_filtrados 
            if data_esta_no_intervalo(r.get('data_publicacao', ''), data_inicio, data_fim)
        ]
    
    # Filtra por revista
    if parametros.get('revistas'):
        revistas = parametros.get('revistas', [])
        if revistas:
            resultados_filtrados = [
                r for r in resultados_filtrados 
                if r.get('revista_id') in revistas
            ]
    
    return resultados_filtrados

def data_esta_no_intervalo(data_str, data_inicio, data_fim):
    """
    Verifica se uma data está dentro de um intervalo.
    
    Args:
        data_str (str): Data em formato string (YYYY-MM-DD)
        data_inicio (datetime): Data inicial do intervalo
        data_fim (datetime): Data final do intervalo
    
    Returns:
        bool: True se a data está no intervalo, False caso contrário
    """
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        return data_inicio <= data <= data_fim
    except:
        return False

def ordenar_resultados(resultados):
    """
    Ordena resultados por data de publicação (mais recentes primeiro).
    
    Args:
        resultados (list): Lista de resultados
    
    Returns:
        list: Lista de resultados ordenados
    """
    return sorted(
        resultados,
        key=lambda r: r.get('data_publicacao', '1900-01-01'),
        reverse=True
    )

def gerar_id_resultado(resultado):
    """
    Gera um ID único para um resultado.
    
    Args:
        resultado (dict): Resultado normalizado
    
    Returns:
        str: ID único
    """
    # Usa DOI se disponível
    if resultado.get('doi'):
        return f"doi-{resultado['doi'].replace('/', '-')}"
    
    # Caso contrário, gera um hash baseado no título e autores
    titulo = resultado.get('titulo', '')
    autores = resultado.get('autores', '')
    fonte = resultado.get('fonte', '')
    
    import hashlib
    texto = f"{titulo}|{autores}|{fonte}".encode('utf-8')
    return f"hash-{hashlib.md5(texto).hexdigest()[:12]}"
