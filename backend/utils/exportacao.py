"""
Módulo de exportação de resultados.
Responsável por exportar resultados em diferentes formatos (HTML, PDF, Excel, TXT).
"""
import os
import json
import logging
from datetime import datetime
import pandas as pd
import weasyprint
from fpdf import FPDF

logger = logging.getLogger(__name__)

def exportar(formato, resultados, busca, diretorio):
    """
    Exporta resultados no formato especificado.
    
    Args:
        formato (str): Formato de exportação ('html', 'pdf', 'excel', 'txt')
        resultados (list): Lista de resultados a serem exportados
        busca (dict): Parâmetros da busca
        diretorio (str): Diretório para salvar o arquivo
    
    Returns:
        str: Caminho do arquivo exportado
    """
    # Garante que o diretório existe
    os.makedirs(diretorio, exist_ok=True)
    
    # Gera nome de arquivo baseado nos termos de busca
    termos = busca.get('palavras', 'busca')
    termos_formatados = termos.replace(' ', '_')[:30]
    data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    nome_arquivo = f"resultados_{termos_formatados}_{data_atual}"
    
    # Exporta no formato especificado
    if formato.lower() == 'html':
        return exportar_html(resultados, busca, diretorio, nome_arquivo)
    elif formato.lower() == 'pdf':
        return exportar_pdf(resultados, busca, diretorio, nome_arquivo)
    elif formato.lower() == 'excel':
        return exportar_excel(resultados, busca, diretorio, nome_arquivo)
    elif formato.lower() == 'txt':
        return exportar_txt(resultados, busca, diretorio, nome_arquivo)
    else:
        raise ValueError(f"Formato de exportação não suportado: {formato}")

def exportar_html(resultados, busca, diretorio, nome_arquivo):
    """
    Exporta resultados em formato HTML.
    
    Args:
        resultados (list): Lista de resultados
        busca (dict): Parâmetros da busca
        diretorio (str): Diretório para salvar o arquivo
        nome_arquivo (str): Nome base do arquivo
    
    Returns:
        str: Caminho do arquivo exportado
    """
    # Caminho completo do arquivo
    caminho = os.path.join(diretorio, f"{nome_arquivo}.html")
    
    # Informações da busca
    titulo = f"Resultados da busca: {busca.get('palavras', '')}"
    data_exportacao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    periodo = f"{busca.get('periodo_inicio', '')} a {busca.get('periodo_fim', '')}"
    
    # Cria o conteúdo HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #3a6ea8;
                border-bottom: 2px solid #3a6ea8;
                padding-bottom: 10px;
            }}
            .info {{
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px 15px;
                border: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background-color: #3a6ea8;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #e9f0f7;
            }}
            a {{
                color: #3a6ea8;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 0.9em;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <h1>{titulo}</h1>
        
        <div class="info">
            <p><strong>Data da exportação:</strong> {data_exportacao}</p>
            <p><strong>Termos de busca:</strong> {busca.get('palavras', '')}</p>
            <p><strong>Período:</strong> {periodo}</p>
            <p><strong>Total de resultados:</strong> {len(resultados)}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Título</th>
                    <th>Autores</th>
                    <th>Revista</th>
                    <th>Data</th>
                    <th>DOI</th>
                    <th>Fonte</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Adiciona cada resultado à tabela
    for resultado in resultados:
        data_formatada = formatar_data(resultado.get('data_publicacao', ''))
        html += f"""
                <tr>
                    <td><a href="{resultado.get('url', '#')}" target="_blank">{resultado.get('titulo', '')}</a></td>
                    <td>{resultado.get('autores', '')}</td>
                    <td>{resultado.get('revista', '')}</td>
                    <td>{data_formatada}</td>
                    <td><a href="https://doi.org/{resultado.get('doi', '')}" target="_blank">{resultado.get('doi', '')}</a></td>
                    <td>{resultado.get('fonte', '')}</td>
                </tr>
        """
    
    # Finaliza o HTML
    html += """
            </tbody>
        </table>
        
        <div class="footer">
            <p>Exportado pelo Buscador de Revistas Científicas</p>
        </div>
    </body>
    </html>
    """
    
    # Escreve o arquivo
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Arquivo HTML exportado: {caminho}")
    return os.path.basename(caminho)

def exportar_pdf(resultados, busca, diretorio, nome_arquivo):
    """
    Exporta resultados em formato PDF.
    
    Args:
        resultados (list): Lista de resultados
        busca (dict): Parâmetros da busca
        diretorio (str): Diretório para salvar o arquivo
        nome_arquivo (str): Nome base do arquivo
    
    Returns:
        str: Caminho do arquivo exportado
    """
    # Caminho completo do arquivo
    caminho = os.path.join(diretorio, f"{nome_arquivo}.pdf")
    
    # Primeiro gera um HTML temporário
    html_temp = os.path.join(diretorio, f"{nome_arquivo}_temp.html")
    exportar_html(resultados, busca, diretorio, f"{nome_arquivo}_temp")
    
    try:
        # Converte HTML para PDF usando WeasyPrint
        html = weasyprint.HTML(html_temp)
        html.write_pdf(caminho)
        
        # Remove o arquivo HTML temporário
        os.remove(html_temp)
        
        logger.info(f"Arquivo PDF exportado: {caminho}")
        return os.path.basename(caminho)
    
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}")
        
        # Fallback para FPDF se WeasyPrint falhar
        try:
            exportar_pdf_fpdf(resultados, busca, caminho)
            return os.path.basename(caminho)
        except Exception as e2:
            logger.error(f"Erro no fallback para FPDF: {str(e2)}")
            raise

def exportar_pdf_fpdf(resultados, busca, caminho):
    """
    Exporta resultados em formato PDF usando FPDF (fallback).
    
    Args:
        resultados (list): Lista de resultados
        busca (dict): Parâmetros da busca
        caminho (str): Caminho completo do arquivo
    """
    # Cria um novo PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Adiciona fonte para suporte a caracteres especiais
    pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 10)
    
    # Título
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 10, f"Resultados da busca: {busca.get('palavras', '')}", 0, 1, 'C')
    pdf.ln(5)
    
    # Informações da busca
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(0, 8, f"Data da exportação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1)
    pdf.cell(0, 8, f"Termos de busca: {busca.get('palavras', '')}", 0, 1)
    pdf.cell(0, 8, f"Período: {busca.get('periodo_inicio', '')} a {busca.get('periodo_fim', '')}", 0, 1)
    pdf.cell(0, 8, f"Total de resultados: {len(resultados)}", 0, 1)
    pdf.ln(5)
    
    # Cabeçalho da tabela
    pdf.set_fill_color(58, 110, 168)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 10, "Título", 1, 0, 'C', True)
    pdf.cell(40, 10, "Autores", 1, 0, 'C', True)
    pdf.cell(30, 10, "Revista", 1, 0, 'C', True)
    pdf.cell(20, 10, "Data", 1, 0, 'C', True)
    pdf.cell(20, 10, "Fonte", 1, 1, 'C', True)
    
    # Conteúdo da tabela
    pdf.set_text_color(0, 0, 0)
    for resultado in resultados:
        # Ajusta o título para caber na célula
        titulo = resultado.get('titulo', '')
        if len(titulo) > 60:
            titulo = titulo[:57] + "..."
        
        # Ajusta autores
        autores = resultado.get('autores', '')
        if len(autores) > 30:
            autores = autores[:27] + "..."
        
        # Ajusta revista
        revista = resultado.get('revista', '')
        if len(revista) > 20:
            revista = revista[:17] + "..."
        
        # Data formatada
        data = formatar_data(resultado.get('data_publicacao', ''))
        
        # Fonte
        fonte = resultado.get('fonte', '')
        
        # Adiciona linha à tabela
        pdf.cell(80, 10, titulo, 1, 0)
        pdf.cell(40, 10, autores, 1, 0)
        pdf.cell(30, 10, revista, 1, 0)
        pdf.cell(20, 10, data, 1, 0)
        pdf.cell(20, 10, fonte, 1, 1)
    
    # Rodapé
    pdf.ln(10)
    pdf.cell(0, 10, "Exportado pelo Buscador de Revistas Científicas", 0, 1, 'C')
    
    # Salva o PDF
    pdf.output(caminho)
    
    logger.info(f"Arquivo PDF exportado via FPDF: {caminho}")

def exportar_excel(resultados, busca, diretorio, nome_arquivo):
    """
    Exporta resultados em formato Excel.
    
    Args:
        resultados (list): Lista de resultados
        busca (dict): Parâmetros da busca
        diretorio (str): Diretório para salvar o arquivo
        nome_arquivo (str): Nome base do arquivo
    
    Returns:
        str: Caminho do arquivo exportado
    """
    # Caminho completo do arquivo
    caminho = os.path.join(diretorio, f"{nome_arquivo}.xlsx")
    
    # Cria um DataFrame com os resultados
    df = pd.DataFrame(resultados)
    
    # Seleciona e renomeia colunas
    colunas = {
        'titulo': 'Título',
        'autores': 'Autores',
        'revista': 'Revista',
        'data_publicacao': 'Data de Publicação',
        'doi': 'DOI',
        'url': 'URL',
        'fonte': 'Fonte'
    }
    
    # Filtra colunas existentes
    colunas_existentes = {k: v for k, v in colunas.items() if k in df.columns}
    
    # Se não houver colunas, cria um DataFrame vazio com as colunas padrão
    if not colunas_existentes:
        df = pd.DataFrame(columns=list(colunas.values()))
    else:
        # Seleciona e renomeia colunas
        df = df[list(colunas_existentes.keys())].rename(columns=colunas_existentes)
    
    # Adiciona informações da busca em uma nova planilha
    with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
        # Planilha de resultados
        df.to_excel(writer, sheet_name='Resultados', index=False)
        
        # Planilha de informações
        info_data = {
            'Informação': [
                'Data da Exportação',
                'Termos de Busca',
                'Período',
                'Total de Resultados'
            ],
            'Valor': [
                datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                busca.get('palavras', ''),
                f"{busca.get('periodo_inicio', '')} a {busca.get('periodo_fim', '')}",
                len(resultados)
            ]
        }
        pd.DataFrame(info_data).to_excel(writer, sheet_name='Informações', index=False)
    
    logger.info(f"Arquivo Excel exportado: {caminho}")
    return os.path.basename(caminho)

def exportar_txt(resultados, busca, diretorio, nome_arquivo):
    """
    Exporta resultados em formato TXT.
    
    Args:
        resultados (list): Lista de resultados
        busca (dict): Parâmetros da busca
        diretorio (str): Diretório para salvar o arquivo
        nome_arquivo (str): Nome base do arquivo
    
    Returns:
        str: Caminho do arquivo exportado
    """
    # Caminho completo do arquivo
    caminho = os.path.join(diretorio, f"{nome_arquivo}.txt")
    
    # Informações da busca
    titulo = f"Resultados da busca: {busca.get('palavras', '')}"
    data_exportacao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    periodo = f"{busca.get('periodo_inicio', '')} a {busca.get('periodo_fim', '')}"
    
    # Cria o conteúdo de texto
    texto = f"{titulo}\n"
    texto += "=" * len(titulo) + "\n\n"
    texto += f"Data da exportação: {data_exportacao}\n"
    texto += f"Termos de busca: {busca.get('palavras', '')}\n"
    texto += f"Período: {periodo}\n"
    texto += f"Total de resultados: {len(resultados)}\n\n"
    texto += "=" * 80 + "\n\n"
    
    # Adiciona cada resultado
    for i, resultado in enumerate(resultados, 1):
        texto += f"[{i}] {resultado.get('titulo', '')}\n"
        texto += f"Autores: {resultado.get('autores', '')}\n"
        texto += f"Revista: {resultado.get('revista', '')}\n"
        texto += f"Data: {formatar_data(resultado.get('data_publicacao', ''))}\n"
        texto += f"DOI: {resultado.get('doi', '')}\n"
        texto += f"URL: {resultado.get('url', '')}\n"
        texto += f"Fonte: {resultado.get('fonte', '')}\n"
        texto += f"\n{'-' * 80}\n\n"
    
    # Adiciona rodapé
    texto += "\nExportado pelo Buscador de Revistas Científicas\n"
    
    # Escreve o arquivo
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(texto)
    
    logger.info(f"Arquivo TXT exportado: {caminho}")
    return os.path.basename(caminho)

def formatar_data(data_str):
    """
    Formata uma data para exibição.
    
    Args:
        data_str (str): Data no formato YYYY-MM-DD
    
    Returns:
        str: Data formatada para exibição
    """
    if not data_str:
        return ""
    
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except:
        return data_str
