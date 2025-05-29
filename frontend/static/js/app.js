/**
 * Aplicativo principal do Buscador de Revistas Científicas
 * Gerencia a inicialização e coordenação dos módulos
 */

// Configurações globais
const CONFIG = {
  apiUrl: '/api',
  maxResultados: 120,
  tempoCache: 3600, // segundos
  formatosExportacao: ['html', 'pdf', 'excel', 'txt']
};

// Estado global da aplicação
const ESTADO = {
  revistas: [],
  resultados: [],
  ultimaBusca: null,
  carregando: false,
  temaAtual: 'escuro'
};

document.addEventListener('DOMContentLoaded', function() {
  // Inicialização dos módulos
  inicializarFormulario();
  carregarRevistas();
  configurarEventos();
  
  // Verifica se há parâmetros na URL para busca automática
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('q')) {
    const termoBusca = urlParams.get('q');
    document.getElementById('palavras').value = termoBusca;
    // Executa busca automática após carregar revistas
    setTimeout(() => {
      document.getElementById('btn-buscar').click();
    }, 1000);
  }
});

/**
 * Inicializa o formulário com valores padrão
 */
function inicializarFormulario() {
  // Define data atual como data final
  const hoje = new Date();
  const dataFim = hoje.toISOString().split('T')[0];
  document.getElementById('periodo_fim').value = dataFim;
  
  // Define data inicial como 1 ano atrás
  const umAnoAtras = new Date();
  umAnoAtras.setFullYear(umAnoAtras.getFullYear() - 1);
  const dataInicio = umAnoAtras.toISOString().split('T')[0];
  document.getElementById('periodo_inicio').value = dataInicio;
  
  // Configura o limite de resultados personalizado
  const inputLimitePersonalizado = document.getElementById('input-limite-personalizado');
  const radioLimitePersonalizado = document.querySelector('input[name="limite_resultados"][value="personalizado"]');
  
  radioLimitePersonalizado.addEventListener('change', function() {
    inputLimitePersonalizado.disabled = !this.checked;
    if (this.checked) {
      inputLimitePersonalizado.focus();
    }
  });
  
  // Configura opções de período
  const radioPeriodos = document.querySelectorAll('input[name="periodo_opcao"]');
  const periodoIntervalo = document.querySelector('.periodo-intervalo');
  
  radioPeriodos.forEach(radio => {
    radio.addEventListener('change', function() {
      const isPersonalizado = this.value === 'personalizado';
      periodoIntervalo.style.display = isPersonalizado ? 'flex' : 'none';
      
      if (!isPersonalizado) {
        // Calcula datas baseadas na opção selecionada
        const hoje = new Date();
        const dataFim = hoje.toISOString().split('T')[0];
        document.getElementById('periodo_fim').value = dataFim;
        
        let dataInicio = new Date();
        switch(this.value) {
          case '1_mes':
            dataInicio.setMonth(dataInicio.getMonth() - 1);
            break;
          case 'ultimos_3_meses':
            dataInicio.setMonth(dataInicio.getMonth() - 3);
            break;
          case 'ultimos_6_meses':
            dataInicio.setMonth(dataInicio.getMonth() - 6);
            break;
          case 'ultimo_ano':
            dataInicio.setFullYear(dataInicio.getFullYear() - 1);
            break;
          case 'ultimos_2_anos':
            dataInicio.setFullYear(dataInicio.getFullYear() - 2);
            break;
        }
        
        document.getElementById('periodo_inicio').value = dataInicio.toISOString().split('T')[0];
      }
    });
  });
}

/**
 * Carrega a lista de revistas do servidor
 */
function carregarRevistas() {
  const selectRevistas = document.getElementById('revista');
  
  // Exibe mensagem de carregamento
  selectRevistas.innerHTML = '<option value="">Carregando revistas...</option>';
  
  // Faz requisição para obter revistas
  fetch(`${CONFIG.apiUrl}/revistas`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Erro ao carregar revistas');
      }
      return response.json();
    })
    .then(data => {
      // Armazena revistas no estado global
      ESTADO.revistas = data;
      
      // Agrupa revistas por especialidade
      const revistasPorEspecialidade = {};
      data.forEach(revista => {
        if (!revistasPorEspecialidade[revista.especialidade]) {
          revistasPorEspecialidade[revista.especialidade] = [];
        }
        revistasPorEspecialidade[revista.especialidade].push(revista);
      });
      
      // Limpa o select
      selectRevistas.innerHTML = '';
      
      // Adiciona opção para selecionar todas
      const optionTodas = document.createElement('option');
      optionTodas.value = 'todas';
      optionTodas.textContent = '-- Todas as Revistas --';
      selectRevistas.appendChild(optionTodas);
      
      // Adiciona revistas agrupadas por especialidade
      Object.keys(revistasPorEspecialidade).sort().forEach(especialidade => {
        const optgroup = document.createElement('optgroup');
        optgroup.label = especialidade;
        
        revistasPorEspecialidade[especialidade]
          .sort((a, b) => a.nome.localeCompare(b.nome))
          .forEach(revista => {
            const option = document.createElement('option');
            option.value = revista.id;
            option.textContent = revista.nome;
            optgroup.appendChild(option);
          });
        
        selectRevistas.appendChild(optgroup);
      });
      
      // Seleciona todas as revistas por padrão
      optionTodas.selected = true;
    })
    .catch(error => {
      console.error('Erro ao carregar revistas:', error);
      selectRevistas.innerHTML = '<option value="">Erro ao carregar revistas</option>';
      
      // Carrega revistas do arquivo local em caso de falha
      carregarRevistasLocal();
    });
}

/**
 * Carrega revistas de um arquivo local em caso de falha na API
 */
function carregarRevistasLocal() {
  // Dados de revistas em fallback
  const revistasLocal = [
    {
      "id": "thieme_connect",
      "nome": "Thieme Connect",
      "issn": "0000-0070",
      "especialidade": "Radiologia e Ortopedia",
      "url": "https://www.thieme-connect.com/products/ejournals/journal/10.1055/s-00000070",
      "descricao": "Plataforma da Thieme que abrange diversas revistas científicas de radiologia e ortopedia."
    },
    {
      "id": "ajr",
      "nome": "American Journal of Roentgenology (AJR)",
      "issn": "0361-803X",
      "especialidade": "Radiologia",
      "url": "https://www.ajronline.org",
      "descricao": "Revista científica líder em radiologia diagnóstica, intervencionista e relacionada à imagem."
    },
    {
      "id": "radiographics",
      "nome": "RadioGraphics",
      "issn": "0271-5333",
      "especialidade": "Radiologia",
      "url": "https://pubs.rsna.org/journal/radiographics",
      "descricao": "Revista educacional da Radiological Society of North America (RSNA)."
    },
    {
      "id": "radiology",
      "nome": "Radiology",
      "issn": "0033-8419",
      "especialidade": "Radiologia",
      "url": "https://pubs.rsna.org/journal/radiology",
      "descricao": "Revista científica da Radiological Society of North America (RSNA)."
    },
    {
      "id": "jbjs",
      "nome": "The Journal of Bone and Joint Surgery",
      "issn": "0021-9355",
      "especialidade": "Ortopedia",
      "url": "https://journals.lww.com/jbjsjournal",
      "descricao": "Uma das revistas mais respeitadas em ortopedia e cirurgia ortopédica."
    }
  ];
  
  ESTADO.revistas = revistasLocal;
  
  const selectRevistas = document.getElementById('revista');
  selectRevistas.innerHTML = '';
  
  // Adiciona opção para selecionar todas
  const optionTodas = document.createElement('option');
  optionTodas.value = 'todas';
  optionTodas.textContent = '-- Todas as Revistas --';
  selectRevistas.appendChild(optionTodas);
  
  // Agrupa revistas por especialidade
  const revistasPorEspecialidade = {};
  revistasLocal.forEach(revista => {
    if (!revistasPorEspecialidade[revista.especialidade]) {
      revistasPorEspecialidade[revista.especialidade] = [];
    }
    revistasPorEspecialidade[revista.especialidade].push(revista);
  });
  
  // Adiciona revistas agrupadas por especialidade
  Object.keys(revistasPorEspecialidade).sort().forEach(especialidade => {
    const optgroup = document.createElement('optgroup');
    optgroup.label = especialidade;
    
    revistasPorEspecialidade[especialidade]
      .sort((a, b) => a.nome.localeCompare(b.nome))
      .forEach(revista => {
        const option = document.createElement('option');
        option.value = revista.id;
        option.textContent = revista.nome;
        optgroup.appendChild(option);
      });
    
    selectRevistas.appendChild(optgroup);
  });
  
  // Seleciona todas as revistas por padrão
  optionTodas.selected = true;
}

/**
 * Configura eventos globais da aplicação
 */
function configurarEventos() {
  // Formulário de busca
  const formBusca = document.getElementById('form-busca');
  formBusca.addEventListener('submit', function(event) {
    event.preventDefault();
    realizarBusca();
  });
  
  // Botão limpar
  const btnLimpar = document.getElementById('btn-limpar');
  btnLimpar.addEventListener('click', function() {
    setTimeout(() => {
      inicializarFormulario();
      document.getElementById('tabela-resultados').innerHTML = '';
      document.getElementById('result-count').style.display = 'none';
    }, 100);
  });
  
  // Botões de exportação
  document.getElementById('btn-exportar-html').addEventListener('click', () => exportarResultados('html'));
  document.getElementById('btn-exportar-pdf').addEventListener('click', () => exportarResultados('pdf'));
  document.getElementById('btn-exportar-excel').addEventListener('click', () => exportarResultados('excel'));
  document.getElementById('btn-exportar-txt').addEventListener('click', () => exportarResultados('txt'));
}

/**
 * Exibe mensagem de feedback ao usuário
 */
function exibirMensagem(mensagem, tipo = 'sucesso') {
  const mensagemElement = document.getElementById('mensagem-feedback');
  mensagemElement.textContent = mensagem;
  mensagemElement.className = tipo === 'sucesso' ? 'mensagem-sucesso' : 'mensagem-erro';
  mensagemElement.style.display = 'block';
  
  // Esconde a mensagem após 5 segundos
  setTimeout(() => {
    mensagemElement.style.display = 'none';
  }, 5000);
}

/**
 * Função auxiliar para obter valores de múltiplos selects
 */
function getValoresSelect(select) {
  return Array.from(select.selectedOptions).map(option => option.value);
}

/**
 * Função auxiliar para formatar data para exibição
 */
function formatarData(dataString) {
  if (!dataString) return '';
  
  const data = new Date(dataString);
  return data.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
}
