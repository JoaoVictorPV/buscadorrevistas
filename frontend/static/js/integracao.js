/**
 * Integração do frontend com o backend para busca em APIs científicas
 * Este módulo substitui a função de busca simulada por uma integração real com o backend
 */

// Modifica a função realizarBusca para usar o backend real
function realizarBuscaReal() {
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
  
  // Faz requisição ao backend
  fetch(`${CONFIG.apiUrl}/buscar`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(parametrosBusca)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Erro na requisição: ${response.status} ${response.statusText}`);
    }
    return response.json();
  })
  .then(data => {
    // Verifica se a resposta contém resultados
    if (data.status === 'ok' && data.resultados) {
      // Armazena resultados no estado global
      ESTADO.resultados = data.resultados;
      
      // Exibe resultados
      exibirResultados(data.resultados);
      
      // Exibe mensagem de sucesso se houver
      if (data.msg) {
        exibirMensagem(data.msg);
      }
    } else {
      // Exibe mensagem de erro ou aviso
      exibirMensagem(data.msg || 'Nenhum resultado encontrado.', data.status === 'erro' ? 'erro' : 'sucesso');
      ESTADO.resultados = [];
      document.getElementById('tabela-resultados').innerHTML = '<div class="sem-resultados">Nenhum resultado encontrado. Tente modificar os termos de busca ou ampliar o período.</div>';
    }
  })
  .catch(erro => {
    console.error('Erro na busca:', erro);
    exibirMensagem(`Erro ao realizar a busca: ${erro.message}. Usando dados simulados temporariamente.`, 'erro');
    
    // Em caso de erro, usa a busca simulada como fallback
    buscarDadosSimulados(parametrosBusca)
      .then(resultados => {
        ESTADO.resultados = resultados;
        exibirResultados(resultados);
      });
  })
  .finally(() => {
    // Esconde indicador de carregamento
    ESTADO.carregando = false;
    document.getElementById('loading').style.display = 'none';
  });
}

/**
 * Exporta resultados usando o backend
 */
function exportarResultadosReal(formato) {
  // Verifica se há resultados para exportar
  if (!ESTADO.resultados || ESTADO.resultados.length === 0) {
    exibirMensagem('Não há resultados para exportar. Realize uma busca primeiro.', 'erro');
    return;
  }
  
  // Exibe indicador de carregamento
  document.getElementById('loading').style.display = 'flex';
  
  // Prepara dados para exportação
  const dadosExportacao = {
    formato,
    busca: ESTADO.ultimaBusca,
    resultados: ESTADO.resultados
  };
  
  // Faz requisição ao backend
  fetch(`${CONFIG.apiUrl}/exportar`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(dadosExportacao)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Erro na requisição: ${response.status} ${response.statusText}`);
    }
    
    // Verifica o tipo de resposta
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      // Resposta JSON (provavelmente erro ou URL para download)
      return response.json().then(data => {
        if (data.status === 'erro') {
          throw new Error(data.msg);
        }
        
        // Se for URL para download, redireciona
        if (data.url) {
          window.open(data.url, '_blank');
          return { status: 'ok', msg: `Exportação em ${formato.toUpperCase()} realizada com sucesso!` };
        }
        
        return data;
      });
    } else {
      // Resposta binária (arquivo para download)
      return response.blob().then(blob => {
        // Obtém nome do arquivo do cabeçalho Content-Disposition
        let filename = 'resultados.' + formato;
        const disposition = response.headers.get('content-disposition');
        if (disposition && disposition.includes('filename=')) {
          const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
          const matches = filenameRegex.exec(disposition);
          if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, '');
          }
        }
        
        // Cria link para download e clica nele
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        return { status: 'ok', msg: `Exportação em ${formato.toUpperCase()} realizada com sucesso!` };
      });
    }
  })
  .then(data => {
    // Exibe mensagem de sucesso
    exibirMensagem(data.msg || `Exportação em ${formato.toUpperCase()} realizada com sucesso!`);
  })
  .catch(erro => {
    console.error('Erro na exportação:', erro);
    exibirMensagem(`Erro ao exportar em ${formato.toUpperCase()}: ${erro.message}. Usando exportação local temporariamente.`, 'erro');
    
    // Em caso de erro, usa a exportação local como fallback
    switch (formato) {
      case 'html':
        exportarHTML();
        break;
      case 'pdf':
        exportarPDF();
        break;
      case 'excel':
        exportarExcel();
        break;
      case 'txt':
        exportarTXT();
        break;
    }
  })
  .finally(() => {
    // Esconde indicador de carregamento
    document.getElementById('loading').style.display = 'none';
  });
}

// Substitui as funções originais pelas versões integradas ao backend
// Descomente estas linhas quando o backend estiver pronto
// window.realizarBusca = realizarBuscaReal;
// window.exportarResultados = exportarResultadosReal;
