"""
Script de instalação e configuração do Buscador de Revistas Científicas.
Este script configura o ambiente virtual e instala as dependências necessárias.
"""
import os
import sys
import subprocess
import platform
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("setup")

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent

def verificar_python():
    """Verifica se a versão do Python é compatível."""
    versao_minima = (3, 7)
    versao_atual = sys.version_info
    
    if versao_atual < versao_minima:
        logger.error(f"Versão do Python incompatível. Necessário Python {versao_minima[0]}.{versao_minima[1]} ou superior.")
        sys.exit(1)
    
    logger.info(f"Versão do Python compatível: {sys.version}")

def criar_ambiente_virtual():
    """Cria o ambiente virtual Python."""
    venv_dir = ROOT_DIR / "venv"
    
    if venv_dir.exists():
        logger.info("Ambiente virtual já existe.")
        return venv_dir
    
    logger.info("Criando ambiente virtual...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        logger.info("Ambiente virtual criado com sucesso.")
        return venv_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao criar ambiente virtual: {e}")
        sys.exit(1)

def instalar_dependencias(venv_dir):
    """Instala as dependências do projeto."""
    logger.info("Instalando dependências...")
    
    # Determina o executável pip
    if platform.system() == "Windows":
        pip = venv_dir / "Scripts" / "pip"
    else:
        pip = venv_dir / "bin" / "pip"
    
    # Atualiza pip
    try:
        subprocess.run([str(pip), "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao atualizar pip: {e}")
        sys.exit(1)
    
    # Instala dependências do requirements.txt
    requirements = ROOT_DIR / "backend" / "requirements.txt"
    try:
        subprocess.run([str(pip), "install", "-r", str(requirements)], check=True)
        logger.info("Dependências instaladas com sucesso.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao instalar dependências: {e}")
        sys.exit(1)

def criar_script_inicializacao():
    """Cria scripts de inicialização para diferentes sistemas operacionais."""
    logger.info("Criando scripts de inicialização...")
    
    # Script para Windows (batch)
    if platform.system() == "Windows":
        with open(ROOT_DIR / "iniciar.bat", "w") as f:
            f.write('@echo off\n')
            f.write('echo Iniciando Buscador de Revistas Cientificas...\n')
            f.write('cd %~dp0\n')
            f.write('call venv\\Scripts\\activate\n')
            f.write('cd backend\n')
            f.write('python app.py\n')
            f.write('pause\n')
        logger.info("Script de inicialização para Windows criado: iniciar.bat")
    
    # Script para Linux/Mac (shell)
    else:
        with open(ROOT_DIR / "iniciar.sh", "w") as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Iniciando Buscador de Revistas Científicas..."\n')
            f.write('cd "$(dirname "$0")"\n')
            f.write('source venv/bin/activate\n')
            f.write('cd backend\n')
            f.write('python app.py\n')
        
        # Torna o script executável
        os.chmod(ROOT_DIR / "iniciar.sh", 0o755)
        logger.info("Script de inicialização para Linux/Mac criado: iniciar.sh")

def main():
    """Função principal de instalação."""
    logger.info("Iniciando configuração do Buscador de Revistas Científicas...")
    
    # Verifica versão do Python
    verificar_python()
    
    # Cria ambiente virtual
    venv_dir = criar_ambiente_virtual()
    
    # Instala dependências
    instalar_dependencias(venv_dir)
    
    # Cria scripts de inicialização
    criar_script_inicializacao()
    
    logger.info("Configuração concluída com sucesso!")
    logger.info("Para iniciar o aplicativo:")
    
    if platform.system() == "Windows":
        logger.info("  Execute o arquivo 'iniciar.bat'")
    else:
        logger.info("  Execute o comando: ./iniciar.sh")
    
    logger.info("Após iniciar, acesse o aplicativo em: http://localhost:5563")

if __name__ == "__main__":
    main()
