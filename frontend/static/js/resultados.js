/**
 * Módulo de resultados do Buscador de Revistas Científicas
 * Gerencia a exibição e manipulação dos resultados de busca
 */

/**
 * Exibe os resultados da busca na tabela
 */
function exibirResultados(resultados) {
  const tabelaContainer = document.getElementById('tabela-resultados');
  const contadorResultados = document.getElementById('result-count');
  
  // Verifica se há resultados
  if (!resultados || resultados.length === 0) {
    tabelaContainer.innerHTML = '<div class="sem-resultados">Nenhum resultado encontrado. Tente modificar os termos de busca ou ampliar o período.</div>';
    contadorResultados.style.display = 'none';
    return;
  }
  
  // Atualiza contador de resultados
  contadorResultados.textContent = resultados.length;
  contadorResultados.style.display = 'inline-block';
  
  // Cria tabela
  const tabela = document.createElement('table');
  tabela.className = 'tabela-resultados';
  
  // Cria cabeçalho
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  
  const colunas = [
    { id: 'titulo', nome: 'Título' },
    { id: 'autores', nome: 'Autores' },
    { id: 'revista', nome: 'Revista' },
    { id: 'data_publicacao', nome: 'Data' },
    { id: 'doi', nome: 'DOI' },
    { id: 'fonte', nome: 'Fonte' }
  ];
  
  colunas.forEach(coluna => {
    const th = document.createElement('th');
    th.textContent = coluna.nome;
    th.dataset.coluna = coluna.id;
    headerRow.appendChild(th);
    
    // Adiciona evento de clique para ordenação
    th.addEventListener('click', () => ordenarResultados(coluna.id));
  });
  
  thead.appendChild(headerRow);
  tabela.appendChild(thead);
  
  // Cria corpo da tabela
  const tbody = document.createElement('tbody');
  
  resultados.forEach(resultado => {
    const row = document.createElement('tr');
    
    // Título com link
    const tdTitulo = document.createElement('td');
    const linkTitulo = document.createElement('a');
    linkTitulo.href = resultado.url;
    linkTitulo.target = '_blank';
    linkTitulo.textContent = resultado.titulo;
    linkTitulo.title = 'Abrir artigo em nova aba';
    tdTitulo.appendChild(linkTitulo);
    row.appendChild(tdTitulo);
    
    // Autores
    const tdAutores = document.createElement('td');
    tdAutores.textContent = resultado.autores;
    row.appendChild(tdAutores);
    
    // Revista
    const tdRevista = document.createElement('td');
    tdRevista.textContent = resultado.revista;
    row.appendChild(tdRevista);
    
    // Data de publicação
    const tdData = document.createElement('td');
    tdData.textContent = formatarData(resultado.data_publicacao);
    row.appendChild(tdData);
    
    // DOI com link
    const tdDoi = document.createElement('td');
    const linkDoi = document.createElement('a');
    linkDoi.href = `https://doi.org/${resultado.doi}`;
    linkDoi.target = '_blank';
    linkDoi.textContent = resultado.doi;
    linkDoi.title = 'Abrir DOI em nova aba';
    tdDoi.appendChild(linkDoi);
    row.appendChild(tdDoi);
    
    // Fonte
    const tdFonte = document.createElement('td');
    tdFonte.textContent = resultado.fonte;
    row.appendChild(tdFonte);
    
    tbody.appendChild(row);
  });
  
  tabela.appendChild(tbody);
  tabelaContainer.innerHTML = '';
  tabelaContainer.appendChild(tabela);
}

/**
 * Ordena os resultados por uma coluna específica
 */
function ordenarResultados(coluna) {
  if (!ESTADO.resultados || ESTADO.resultados.length === 0) return;
  
  // Determina direção da ordenação
  const direcaoAtual = ESTADO.direcaoOrdenacao || 'asc';
  const novaDirecao = direcaoAtual === 'asc' ? 'desc' : 'asc';
  ESTADO.direcaoOrdenacao = novaDirecao;
  
  // Armazena coluna atual
  ESTADO.colunaOrdenacao = coluna;
  
  // Ordena resultados
  const resultadosOrdenados = [...ESTADO.resultados].sort((a, b) => {
    let valorA, valorB;
    
    // Tratamento especial para data
    if (coluna === 'data_publicacao') {
      valorA = new Date(a[coluna]).getTime();
      valorB = new Date(b[coluna]).getTime();
    } else {
      valorA = a[coluna].toLowerCase();
      valorB = b[coluna].toLowerCase();
    }
    
    // Compara valores
    if (valorA < valorB) return novaDirecao === 'asc' ? -1 : 1;
    if (valorA > valorB) return novaDirecao === 'asc' ? 1 : -1;
    return 0;
  });
  
  // Atualiza cabeçalhos da tabela para mostrar ordenação
  const headers = document.querySelectorAll('.tabela-resultados th');
  headers.forEach(th => {
    th.classList.remove('ordenado-asc', 'ordenado-desc');
    if (th.dataset.coluna === coluna) {
      th.classList.add(novaDirecao === 'asc' ? 'ordenado-asc' : 'ordenado-desc');
    }
  });
  
  // Exibe resultados ordenados
  exibirResultados(resultadosOrdenados);
}

/**
 * Filtra resultados por texto
 */
function filtrarResultados(texto) {
  if (!ESTADO.resultados || ESTADO.resultados.length === 0) return;
  if (!texto) {
    exibirResultados(ESTADO.resultados);
    return;
  }
  
  const termosBusca = texto.toLowerCase().split(/\s+/);
  
  const resultadosFiltrados = ESTADO.resultados.filter(resultado => {
    // Busca em todos os campos relevantes
    const conteudo = `${resultado.titulo} ${resultado.autores} ${resultado.revista} ${resultado.doi}`.toLowerCase();
    
    // Verifica se todos os termos estão presentes
    return termosBusca.every(termo => conteudo.includes(termo));
  });
  
  exibirResultados(resultadosFiltrados);
}
