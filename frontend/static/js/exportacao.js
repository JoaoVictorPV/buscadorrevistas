/**
 * Módulo de exportação do Buscador de Revistas Científicas
 * Gerencia a exportação dos resultados em diferentes formatos
 */

/**
 * Exporta os resultados no formato especificado
 */
function exportarResultados(formato) {
  // Verifica se há resultados para exportar
  if (!ESTADO.resultados || ESTADO.resultados.length === 0) {
    exibirMensagem('Não há resultados para exportar. Realize uma busca primeiro.', 'erro');
    return;
  }
  
  // Exibe indicador de carregamento
  document.getElementById('loading').style.display = 'flex';
  
  // Simula tempo de processamento
  setTimeout(() => {
    try {
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
        default:
          throw new Error('Formato de exportação não suportado');
      }
      
      // Exibe mensagem de sucesso
      exibirMensagem(`Exportação em ${formato.toUpperCase()} realizada com sucesso!`);
    } catch (erro) {
      console.error('Erro na exportação:', erro);
      exibirMensagem(`Erro ao exportar em ${formato.toUpperCase()}: ${erro.message}`, 'erro');
    } finally {
      // Esconde indicador de carregamento
      document.getElementById('loading').style.display = 'none';
    }
  }, 1000);
}

/**
 * Exporta os resultados em formato HTML
 */
function exportarHTML() {
  // Cria o conteúdo HTML
  const titulo = `Resultados da busca: ${ESTADO.ultimaBusca.palavras}`;
  const dataExportacao = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  
  let html = `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${titulo}</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          line-height: 1.6;
          color: #333;
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }
        h1 {
          color: #3a6ea8;
          border-bottom: 2px solid #3a6ea8;
          padding-bottom: 10px;
        }
        .info {
          background: #f5f5f5;
          padding: 15px;
          border-radius: 5px;
          margin-bottom: 20px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 20px;
        }
        th, td {
          padding: 12px 15px;
          border: 1px solid #ddd;
          text-align: left;
        }
        th {
          background-color: #3a6ea8;
          color: white;
          font-weight: bold;
        }
        tr:nth-child(even) {
          background-color: #f2f2f2;
        }
        tr:hover {
          background-color: #e9f0f7;
        }
        a {
          color: #3a6ea8;
          text-decoration: none;
        }
        a:hover {
          text-decoration: underline;
        }
        .footer {
          margin-top: 30px;
          text-align: center;
          font-size: 0.9em;
          color: #666;
        }
      </style>
    </head>
    <body>
      <h1>${titulo}</h1>
      
      <div class="info">
        <p><strong>Data da exportação:</strong> ${dataExportacao}</p>
        <p><strong>Termos de busca:</strong> ${ESTADO.ultimaBusca.palavras}</p>
        <p><strong>Período:</strong> ${formatarData(ESTADO.ultimaBusca.periodo_inicio)} a ${formatarData(ESTADO.ultimaBusca.periodo_fim)}</p>
        <p><strong>Total de resultados:</strong> ${ESTADO.resultados.length}</p>
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
  `;
  
  // Adiciona cada resultado à tabela
  ESTADO.resultados.forEach(resultado => {
    html += `
      <tr>
        <td><a href="${resultado.url}" target="_blank">${resultado.titulo}</a></td>
        <td>${resultado.autores}</td>
        <td>${resultado.revista}</td>
        <td>${formatarData(resultado.data_publicacao)}</td>
        <td><a href="https://doi.org/${resultado.doi}" target="_blank">${resultado.doi}</a></td>
        <td>${resultado.fonte}</td>
      </tr>
    `;
  });
  
  // Finaliza o HTML
  html += `
        </tbody>
      </table>
      
      <div class="footer">
        <p>Exportado pelo Buscador de Revistas Científicas</p>
      </div>
    </body>
    </html>
  `;
  
  // Cria um blob e faz o download
  const blob = new Blob([html], { type: 'text/html' });
  const nomeArquivo = `resultados_${ESTADO.ultimaBusca.palavras.replace(/\s+/g, '_').substring(0, 30)}_${new Date().toISOString().split('T')[0]}.html`;
  
  // Cria link para download e clica nele
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = nomeArquivo;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Exporta os resultados em formato PDF
 * Nota: Esta é uma implementação simulada. Em produção, seria feita uma requisição ao backend
 * para gerar o PDF usando bibliotecas como WeasyPrint ou xhtml2pdf.
 */
function exportarPDF() {
  // Em um ambiente real, faríamos uma requisição ao backend
  // Aqui, simulamos o comportamento para demonstração
  
  // Cria um formulário para enviar ao backend
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = `${CONFIG.apiUrl}/exportar/pdf`;
  form.target = '_blank'; // Abre em nova aba
  
  // Adiciona os dados da busca como campos ocultos
  const addCampo = (nome, valor) => {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = nome;
    input.value = valor;
    form.appendChild(input);
  };
  
  addCampo('palavras', ESTADO.ultimaBusca.palavras);
  addCampo('periodo_inicio', ESTADO.ultimaBusca.periodo_inicio);
  addCampo('periodo_fim', ESTADO.ultimaBusca.periodo_fim);
  addCampo('resultados', JSON.stringify(ESTADO.resultados));
  
  // Simula o envio do formulário
  // Em produção, este formulário seria realmente enviado ao backend
  
  // Para demonstração, criamos um PDF simulado
  const nomeArquivo = `resultados_${ESTADO.ultimaBusca.palavras.replace(/\s+/g, '_').substring(0, 30)}_${new Date().toISOString().split('T')[0]}.pdf`;
  
  // Exibe mensagem informativa
  exibirMensagem(`Em um ambiente de produção, o PDF seria gerado pelo backend e baixado como "${nomeArquivo}"`);
}

/**
 * Exporta os resultados em formato Excel
 * Nota: Esta é uma implementação simulada. Em produção, seria feita uma requisição ao backend
 * para gerar o Excel usando bibliotecas como openpyxl.
 */
function exportarExcel() {
  // Em um ambiente real, faríamos uma requisição ao backend
  // Aqui, simulamos o comportamento para demonstração
  
  // Cria um CSV simples para demonstração
  let csv = 'Título,Autores,Revista,Data,DOI,Fonte\n';
  
  ESTADO.resultados.forEach(resultado => {
    // Escapa aspas e adiciona aspas em torno de cada campo
    const titulo = `"${resultado.titulo.replace(/"/g, '""')}"`;
    const autores = `"${resultado.autores.replace(/"/g, '""')}"`;
    const revista = `"${resultado.revista.replace(/"/g, '""')}"`;
    const data = `"${formatarData(resultado.data_publicacao)}"`;
    const doi = `"${resultado.doi}"`;
    const fonte = `"${resultado.fonte}"`;
    
    csv += `${titulo},${autores},${revista},${data},${doi},${fonte}\n`;
  });
  
  // Cria um blob e faz o download
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const nomeArquivo = `resultados_${ESTADO.ultimaBusca.palavras.replace(/\s+/g, '_').substring(0, 30)}_${new Date().toISOString().split('T')[0]}.csv`;
  
  // Cria link para download e clica nele
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = nomeArquivo;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Exibe mensagem informativa
  exibirMensagem(`Exportado como CSV. Em um ambiente de produção, um arquivo Excel seria gerado pelo backend.`);
}

/**
 * Exporta os resultados em formato TXT
 */
function exportarTXT() {
  // Cria o conteúdo de texto
  const titulo = `Resultados da busca: ${ESTADO.ultimaBusca.palavras}`;
  const dataExportacao = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  
  let texto = `${titulo}\n`;
  texto += `=`.repeat(titulo.length) + `\n\n`;
  texto += `Data da exportação: ${dataExportacao}\n`;
  texto += `Termos de busca: ${ESTADO.ultimaBusca.palavras}\n`;
  texto += `Período: ${formatarData(ESTADO.ultimaBusca.periodo_inicio)} a ${formatarData(ESTADO.ultimaBusca.periodo_fim)}\n`;
  texto += `Total de resultados: ${ESTADO.resultados.length}\n\n`;
  texto += `=`.repeat(80) + `\n\n`;
  
  // Adiciona cada resultado
  ESTADO.resultados.forEach((resultado, index) => {
    texto += `[${index + 1}] ${resultado.titulo}\n`;
    texto += `Autores: ${resultado.autores}\n`;
    texto += `Revista: ${resultado.revista}\n`;
    texto += `Data: ${formatarData(resultado.data_publicacao)}\n`;
    texto += `DOI: ${resultado.doi}\n`;
    texto += `URL: ${resultado.url}\n`;
    texto += `Fonte: ${resultado.fonte}\n`;
    texto += `\n${'-'.repeat(80)}\n\n`;
  });
  
  // Adiciona rodapé
  texto += `\nExportado pelo Buscador de Revistas Científicas\n`;
  
  // Cria um blob e faz o download
  const blob = new Blob([texto], { type: 'text/plain;charset=utf-8' });
  const nomeArquivo = `resultados_${ESTADO.ultimaBusca.palavras.replace(/\s+/g, '_').substring(0, 30)}_${new Date().toISOString().split('T')[0]}.txt`;
  
  // Cria link para download e clica nele
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = nomeArquivo;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
