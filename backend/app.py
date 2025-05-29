"""
Módulo principal da aplicação Flask para o Buscador de Revistas Científicas.
"""
import os
import signal
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_caching import Cache

# Configuração da aplicação
app = Flask(__name__, static_folder='../frontend/static')
CORS(app)

# Configuração do cache
cache_config = {
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DIR': '../dados/cache',
    'CACHE_DEFAULT_TIMEOUT': 3600
}
cache = Cache(app, config=cache_config)

# Constantes
REVISTAS_PATH = '../dados/revistas.json'
EXPORTADOS_PATH = '../dados/exportados'

# Função para garantir que os diretórios existam
def ensure_directories():
    """Garante que os diretórios necessários existam."""
    os.makedirs(os.path.dirname(REVISTAS_PATH), exist_ok=True)
    os.makedirs(EXPORTADOS_PATH, exist_ok=True)

# Carregar revistas
def load_revistas():
    """Carrega o catálogo de revistas do arquivo JSON."""
    ensure_directories()
    try:
        with open(REVISTAS_PATH, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver vazio/inválido, retorna lista vazia
        return []

# Salvar revistas
def save_revistas(data):
    """Salva o catálogo de revistas no arquivo JSON."""
    ensure_directories()
    with open(REVISTAS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Rota principal que serve a página inicial."""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Rota para servir arquivos estáticos."""
    return send_from_directory('../frontend', path)

@app.route('/api/revistas', methods=['GET'])
def get_revistas():
    """API para obter a lista de revistas."""
    return jsonify(load_revistas())

@app.route('/api/revistas', methods=['POST'])
def add_revista():
    """API para adicionar uma nova revista."""
    data = request.json
    revistas = load_revistas()
    
    # Verifica se a revista já existe
    for revista in revistas:
        if revista.get('id') == data.get('id'):
            return jsonify({"status": "erro", "msg": "Revista com este ID já existe."}), 400
    
    revistas.append(data)
    save_revistas(revistas)
    return jsonify({"status": "ok", "msg": "Revista adicionada com sucesso."})

@app.route('/api/buscar', methods=['POST'])
def buscar():
    """API para realizar busca de artigos."""
    # Este é apenas um placeholder. A implementação completa será feita posteriormente.
    return jsonify({
        "status": "ok", 
        "msg": "Funcionalidade de busca em desenvolvimento.",
        "resultados": []
    })

@app.route('/api/exportar', methods=['POST'])
def exportar():
    """API para exportar resultados em diferentes formatos."""
    # Este é apenas um placeholder. A implementação completa será feita posteriormente.
    return jsonify({
        "status": "ok", 
        "msg": "Funcionalidade de exportação em desenvolvimento."
    })

if __name__ == '__main__':
    ensure_directories()
    app.run(host='0.0.0.0', port=5563, debug=True)
