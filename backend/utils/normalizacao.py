"""
Módulo de utilidades para normalização de dados.
Contém funções para normalizar textos, datas, DOIs e outros campos.
"""
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def normalizar_texto(texto):
    """
    Normaliza um texto, removendo caracteres especiais e espaços extras.
    
    Args:
        texto (str): Texto a ser normalizado
    
    Returns:
        str: Texto normalizado
    """
    if not texto:
        return ""
    
    # Remove espaços extras
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    # Remove caracteres HTML
    texto = re.sub(r'<[^>]+>', '', texto)
    
    return texto

def normalizar_doi(doi):
    """
    Normaliza um DOI, removendo prefixos e espaços.
    
    Args:
        doi (str): DOI a ser normalizado
    
    Returns:
        str: DOI normalizado
    """
    if not doi:
        return ""
    
    # Remove espaços
    doi = doi.strip()
    
    # Remove prefixos comuns
    prefixos = ["doi:", "DOI:", "https://doi.org/", "http://doi.org/", "doi.org/"]
    for prefixo in prefixos:
        if doi.startswith(prefixo):
            doi = doi[len(prefixo):]
    
    return doi.strip()

def normalizar_data(data_str):
    """
    Normaliza uma data para o formato YYYY-MM-DD.
    
    Args:
        data_str (str): Data em formato string
    
    Returns:
        str: Data normalizada no formato YYYY-MM-DD
    """
    if not data_str:
        return ""
    
    # Formatos comuns de data
    formatos = [
        "%Y-%m-%d",        # 2023-01-15
        "%Y/%m/%d",        # 2023/01/15
        "%d/%m/%Y",        # 15/01/2023
        "%m/%d/%Y",        # 01/15/2023
        "%d-%m-%Y",        # 15-01-2023
        "%d.%m.%Y",        # 15.01.2023
        "%B %d, %Y",       # January 15, 2023
        "%d %B %Y",        # 15 January 2023
        "%Y-%m",           # 2023-01
        "%Y"               # 2023
    ]
    
    # Tenta converter a data
    for formato in formatos:
        try:
            data = datetime.strptime(data_str, formato)
            return data.strftime("%Y-%m-%d")
        except:
            continue
    
    # Se não conseguir converter, tenta extrair o ano
    try:
        match = re.search(r'\b(19|20)\d{2}\b', data_str)
        if match:
            ano = match.group(0)
            return f"{ano}-01-01"
    except:
        pass
    
    logger.warning(f"Não foi possível normalizar a data: {data_str}")
    return ""

def normalizar_autores(autores_str):
    """
    Normaliza uma string de autores.
    
    Args:
        autores_str (str): String de autores
    
    Returns:
        str: Autores normalizados
    """
    if not autores_str:
        return ""
    
    # Remove espaços extras
    autores_str = re.sub(r'\s+', ' ', autores_str).strip()
    
    # Normaliza separadores
    separadores = [', and ', ' and ', ', & ', ' & ', '; ']
    for sep in separadores:
        autores_str = autores_str.replace(sep, '; ')
    
    # Normaliza formato
    autores = []
    for autor in autores_str.split(';'):
        autor = autor.strip()
        if autor:
            # Verifica se está no formato "Sobrenome, Nome"
            if ',' in autor:
                partes = autor.split(',', 1)
                sobrenome = partes[0].strip()
                nome = partes[1].strip() if len(partes) > 1 else ""
                autores.append(f"{sobrenome}, {nome}" if nome else sobrenome)
            else:
                # Tenta extrair sobrenome e nome
                partes = autor.split()
                if len(partes) > 1:
                    sobrenome = partes[-1]
                    nome = ' '.join(partes[:-1])
                    autores.append(f"{sobrenome}, {nome}")
                else:
                    autores.append(autor)
    
    return '; '.join(autores)

def normalizar_termos_busca(termos):
    """
    Normaliza termos de busca, preservando operadores booleanos.
    
    Args:
        termos (str): Termos de busca
    
    Returns:
        str: Termos normalizados
    """
    if not termos:
        return ""
    
    # Remove espaços extras
    termos = re.sub(r'\s+', ' ', termos).strip()
    
    # Preserva operadores booleanos
    operadores = ['AND', 'OR', 'NOT']
    for op in operadores:
        # Substitui por placeholder
        termos = termos.replace(f" {op} ", f" __{op}__ ")
    
    # Normaliza o texto
    termos = normalizar_texto(termos)
    
    # Restaura operadores
    for op in operadores:
        termos = termos.replace(f"__{op}__", op)
    
    return termos

def normalizar_autor(autor):
    """
    Normaliza um nome de autor para busca.
    
    Args:
        autor (str): Nome do autor
    
    Returns:
        str: Nome normalizado
    """
    if not autor:
        return ""
    
    # Remove espaços extras
    autor = re.sub(r'\s+', ' ', autor).strip()
    
    # Verifica se está no formato "Sobrenome, Nome"
    if ',' in autor:
        return autor
    
    # Tenta extrair sobrenome e nome
    partes = autor.split()
    if len(partes) > 1:
        sobrenome = partes[-1]
        nome = ' '.join(partes[:-1])
        return f"{sobrenome}, {nome}"
    
    return autor
