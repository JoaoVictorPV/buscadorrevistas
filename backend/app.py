"""
Configuração do ambiente e inicialização da aplicação local do Buscador de Revistas Científicas.
Este arquivo contém as configurações e inicialização do servidor Flask.
"""
import os
import sys
import json
import logging
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("buscador.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação Flask
app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')
CORS(app)  # Habilita CORS para desenvolvimento local

# Configurações da aplicação
app.config.update(
    DEBUG=True,
    SECRET_KEY=os.urandom(24),
    CACHE_DIR=os.path.abspath('../dados/cache'),
    EXPORT_DIR=os.path.abspath('../dados/exportados'),
    REVISTAS_FILE=os.path.abspath('../dados/revistas.json'),
    MAX_RESULTS_PER_API=100,
    CACHE_TIMEOUT=3600  # 1 hora
)

# Garante que os diretórios necessários existam
for directory in [app.config['CACHE_DIR'], app.config['EXPORT_DIR']]:
    os.makedirs(directory, exist_ok=True)

# Importa os módulos da aplicação
# Nota: Importações aqui para evitar problemas de dependência circular
from adaptadores import pubmed, crossref, semantic_scholar, openalex, unpaywall, thieme
from core import motor_busca, processador, cache
from utils import normalizacao, exportacao, validacao

# Rotas para servir o frontend
@app.route('/')
def index():
    """Rota principal que serve a página inicial."""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Rota para servir arquivos estáticos."""
    if os.path.exists(os.path.join('../frontend', path)):
        return send_from_directory('../frontend', path)
    return send_from_directory('../', path)

# API para obter a lista de revistas
@app.route('/api/revistas', methods=['GET'])
def get_revistas():
    """API para obter a lista de revistas."""
    try:
        with open(app.config['REVISTAS_FILE'], 'r', encoding='utf-8') as f:
            revistas = json.load(f)
        return jsonify(revistas)
    except Exception as e:
        logger.error(f"Erro ao carregar revistas: {str(e)}")
        return jsonify([])

# API para realizar busca
@app.route('/api/buscar', methods=['POST'])
def buscar():
    """API para realizar busca de artigos."""
    try:
        dados = request.json
        logger.info(f"Recebida requisição de busca: {dados}")
        
        # Validação dos dados de entrada
        if not validacao.validar_parametros_busca(dados):
            return jsonify({
                "status": "erro",
                "msg": "Parâmetros de busca inválidos."
            }), 400
        
        # Realiza a busca usando o motor de busca
        resultados = motor_busca.buscar(
            termos=dados.get('palavras', ''),
            autor=dados.get('autor', ''),
            data_inicio=dados.get('periodo_inicio'),
            data_fim=dados.get('periodo_fim'),
            revistas=dados.get('revistas', []),
            limite=dados.get('limite', 30)
        )
        
        return jsonify({
            "status": "ok",
            "msg": f"Busca realizada com sucesso. {len(resultados)} resultados encontrados.",
            "resultados": resultados
        })
    except Exception as e:
        logger.error(f"Erro na busca: {str(e)}")
        return jsonify({
            "status": "erro",
            "msg": f"Erro ao realizar a busca: {str(e)}"
        }), 500

# API para exportar resultados
@app.route('/api/exportar', methods=['POST'])
def exportar():
    """API para exportar resultados em diferentes formatos."""
    try:
        dados = request.json
        logger.info(f"Recebida requisição de exportação: {dados['formato']}")
        
        formato = dados.get('formato')
        resultados = dados.get('resultados', [])
        busca = dados.get('busca', {})
        
        if not resultados:
            return jsonify({
                "status": "erro",
                "msg": "Não há resultados para exportar."
            }), 400
        
        # Realiza a exportação usando o módulo de exportação
        arquivo = exportacao.exportar(
            formato=formato,
            resultados=resultados,
            busca=busca,
            diretorio=app.config['EXPORT_DIR']
        )
        
        # Retorna o caminho do arquivo para download
        return jsonify({
            "status": "ok",
            "msg": f"Exportação em {formato.upper()} realizada com sucesso!",
            "arquivo": arquivo
        })
    except Exception as e:
        logger.error(f"Erro na exportação: {str(e)}")
        return jsonify({
            "status": "erro",
            "msg": f"Erro ao exportar resultados: {str(e)}"
        }), 500

# Rota para download de arquivos exportados
@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """Rota para download de arquivos exportados."""
    return send_from_directory(
        app.config['EXPORT_DIR'],
        filename,
        as_attachment=True
    )

# Função para iniciar o servidor
def iniciar_servidor(host='0.0.0.0', port=5563):
    """Inicia o servidor Flask."""
    logger.info(f"Iniciando servidor em http://{host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])

# Execução direta do script
if __name__ == '__main__':
    try:
        # Verifica argumentos de linha de comando para host e porta
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        else:
            port = 5563
            
        if len(sys.argv) > 2:
            host = sys.argv[2]
        else:
            host = '0.0.0.0'
            
        iniciar_servidor(host, port)
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {str(e)}")
        sys.exit(1)
