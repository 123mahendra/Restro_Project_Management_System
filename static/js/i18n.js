const I18N = (function(){
  const lang = localStorage.getItem('lang') || 'en';
  let dict = {};
  async function load(){
    try{
      const res = await fetch('/static/i18n/' + lang + '.json');
      dict = await res.json();
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if(dict[key]) el.textContent = dict[key];
      });
    }catch(e){ console.warn('i18n load failed', e); }
  }
  return { load, lang };
})();
document.addEventListener('DOMContentLoaded', ()=>I18N.load());
