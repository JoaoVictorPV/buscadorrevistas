/**
 * Módulo de busca do Buscador de Revistas Científicas
 * Gerencia a execução de buscas e processamento de resultados
 */

/**
 * Realiza a busca com os parâmetros do formulário
 */
function realizarBusca() {
  // Obtém valores do formulário
  const palavras = document.getElementById('palavras').value.trim();
  const autor = document.getElementById('autor').value.trim();
  const periodoInicio = document.getElementById('periodo_inicio').value;
  const periodoFim = document.getElementById('periodo_fim').value;
  const revistasSelect = document.getElementById('revista');
  const revistas = getValoresSelect(revistasSelect);
  
  // Obtém limite de resultados
  let limiteResultados = 30;
  const radioLimite = document.querySelector('input[name="limite_resultados"]:checked');
  if (radioLimite.value === 'personalizado') {
    limiteResultados = parseInt(document.getElementById('input-limite-personalizado').value) || 30;
  } else {
    limiteResultados = parseInt(radioLimite.value);
  }
  
  // Validação básica
  if (!palavras) {
    exibirMensagem('Por favor, informe pelo menos uma palavra-chave para busca.', 'erro');
    return;
  }
  
  // Prepara parâmetros de busca
  const parametrosBusca = {
    palavras,
    autor,
    periodo_inicio: periodoInicio,
    periodo_fim: periodoFim,
    revistas: revistas[0] === 'todas' ? [] : revistas,
    limite: limiteResultados
  };
  
  // Armazena última busca no estado
  ESTADO.ultimaBusca = parametrosBusca;
  
  // Exibe indicador de carregamento
  ESTADO.carregando = true;
  document.getElementById('loading').style.display = 'flex';
  document.getElementById('tabela-resultados').innerHTML = '';
  
  // Em modo de desenvolvimento/demonstração, usamos dados simulados
  // Em produção, esta chamada seria substituída por uma requisição real à API
  setTimeout(() => {
    buscarDadosSimulados(parametrosBusca)
      .then(resultados => {
        // Armazena resultados no estado global
        ESTADO.resultados = resultados;
        
        // Exibe resultados
        exibirResultados(resultados);
        
        // Esconde indicador de carregamento
        ESTADO.carregando = false;
        document.getElementById('loading').style.display = 'none';
      })
      .catch(erro => {
        console.error('Erro na busca:', erro);
        exibirMensagem('Ocorreu um erro ao realizar a busca. Por favor, tente novamente.', 'erro');
        ESTADO.carregando = false;
        document.getElementById('loading').style.display = 'none';
      });
  }, 1500); // Simula tempo de resposta da API
}

/**
 * Função temporária que simula busca na API
 * Será substituída pela integração real com o backend
 */
async function buscarDadosSimulados(parametros) {
  console.log('Parâmetros de busca:', parametros);
  
  // Simula tempo de processamento
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Gera resultados simulados baseados nos parâmetros
  const quantidade = Math.min(parametros.limite, 50);
  const resultados = [];
  
  const revistas = ESTADO.revistas;
  const palavrasChave = parametros.palavras.toLowerCase().split(/\s+/);
  
  for (let i = 0; i < quantidade; i++) {
    // Seleciona uma revista aleatória ou das selecionadas
    let revista;
    if (parametros.revistas.length > 0) {
      const revistaId = parametros.revistas[Math.floor(Math.random() * parametros.revistas.length)];
      revista = revistas.find(r => r.id === revistaId) || revistas[0];
    } else {
      revista = revistas[Math.floor(Math.random() * revistas.length)];
    }
    
    // Gera data aleatória dentro do período especificado
    const inicio = new Date(parametros.periodo_inicio).getTime();
    const fim = new Date(parametros.periodo_fim).getTime();
    const dataAleatoria = new Date(inicio + Math.random() * (fim - inicio));
    const dataPublicacao = dataAleatoria.toISOString().split('T')[0];
    
    // Gera título com palavras-chave
    const tituloBase = [
      "Avaliação de técnicas de imagem para diagnóstico de",
      "Estudo comparativo de métodos de tratamento para",
      "Análise retrospectiva de casos clínicos de",
      "Revisão sistemática sobre abordagens terapêuticas em",
      "Correlação entre achados radiológicos e desfechos clínicos em pacientes com",
      "Novas perspectivas no manejo de pacientes com",
      "Impacto da ressonância magnética no diagnóstico precoce de",
      "Eficácia da tomografia computadorizada na avaliação de"
    ];
    
    const tituloComplemento = [
      "lesões do joelho",
      "fraturas vertebrais",
      "osteoartrite",
      "lesões ligamentares",
      "tumores ósseos",
      "doenças degenerativas da coluna",
      "patologias do quadril",
      "lesões musculoesqueléticas",
      "artrite reumatoide",
      "doenças inflamatórias articulares"
    ];
    
    // Inclui pelo menos uma palavra-chave da busca no título
    const palavraChave = palavrasChave[Math.floor(Math.random() * palavrasChave.length)];
    const titulo = `${tituloBase[Math.floor(Math.random() * tituloBase.length)]} ${palavraChave} em ${tituloComplemento[Math.floor(Math.random() * tituloComplemento.length)]}`;
    
    // Gera autores
    const autoresBase = [
      "Silva, A.J.",
      "Santos, M.R.",
      "Oliveira, C.T.",
      "Pereira, L.M.",
      "Costa, R.S.",
      "Almeida, F.G.",
      "Rodrigues, P.H.",
      "Ferreira, D.L.",
      "Martins, G.B.",
      "Souza, V.C."
    ];
    
    // Se autor foi especificado, inclui ele
    let autores = [];
    if (parametros.autor) {
      autores.push(parametros.autor);
      // Adiciona 1-3 co-autores
      const numCoAutores = 1 + Math.floor(Math.random() * 3);
      for (let j = 0; j < numCoAutores; j++) {
        autores.push(autoresBase[Math.floor(Math.random() * autoresBase.length)]);
      }
    } else {
      // Gera 2-4 autores aleatórios
      const numAutores = 2 + Math.floor(Math.random() * 3);
      for (let j = 0; j < numAutores; j++) {
        autores.push(autoresBase[Math.floor(Math.random() * autoresBase.length)]);
      }
    }
    
    // Remove duplicatas de autores
    autores = [...new Set(autores)];
    
    // Gera DOI
    const doi = `10.${1000 + Math.floor(Math.random() * 9000)}/${revista.id}.${2020 + Math.floor(Math.random() * 6)}.${10000 + Math.floor(Math.random() * 90000)}`;
    
    // Gera URL
    const url = `https://doi.org/${doi}`;
    
    // Adiciona resultado
    resultados.push({
      id: `result-${i}`,
      titulo,
      autores: autores.join('; '),
      revista: revista.nome,
      data_publicacao: dataPublicacao,
      doi,
      url,
      fonte: ['PubMed', 'Crossref', 'Semantic Scholar', 'OpenAlex', 'Unpaywall'][Math.floor(Math.random() * 5)]
    });
  }
  
  return resultados;
}
