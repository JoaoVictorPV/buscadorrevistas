/**
 * Gerenciamento de temas (claro/escuro)
 * Permite alternar entre os temas e salva a preferência do usuário
 */

document.addEventListener('DOMContentLoaded', function() {
  // Elementos
  const btnAlternarTema = document.getElementById('btn-alternar-tema');
  const body = document.body;
  const temaCSS = document.getElementById('tema-css');
  
  // Verifica se há tema salvo no localStorage
  const temaSalvo = localStorage.getItem('tema');
  
  // Aplica o tema salvo ou mantém o padrão (escuro)
  if (temaSalvo === 'claro') {
    aplicarTemaClaro();
  } else {
    aplicarTemaEscuro();
  }
  
  // Adiciona evento de clique ao botão de alternar tema
  btnAlternarTema.addEventListener('click', function() {
    if (body.classList.contains('tema-escuro')) {
      aplicarTemaClaro();
    } else {
      aplicarTemaEscuro();
    }
  });
  
  // Função para aplicar tema claro
  function aplicarTemaClaro() {
    body.classList.remove('tema-escuro');
    body.classList.add('tema-claro');
    temaCSS.href = 'static/css/tema-claro.css';
    localStorage.setItem('tema', 'claro');
  }
  
  // Função para aplicar tema escuro
  function aplicarTemaEscuro() {
    body.classList.remove('tema-claro');
    body.classList.add('tema-escuro');
    temaCSS.href = 'static/css/tema-escuro.css';
    localStorage.setItem('tema', 'escuro');
  }
});
