(()=>{
  const dialog=document.getElementById('search-dialog');
  const input=document.getElementById('site-search');
  const results=document.getElementById('search-results');
  const open=document.getElementById('search-open');
  const close=document.getElementById('search-close');
  const menu=document.getElementById('menu-open');
  const sidebar=document.getElementById('site-sidebar');
  const dataScript=[...document.scripts].find(s=>/\/search-data\.js(?:$|\?)/.test(s.src));
  const siteRoot=dataScript?new URL('../',dataScript.src):new URL('./',location.href);
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const resultUrl=url=>new URL(url,siteRoot).href;
  function run(){
    const q=input.value.trim().toLowerCase();
    const tokens=q.split(/[^a-z0-9+#.-]+/).filter(Boolean);
    if(!q){results.innerHTML='<div class="result"><span>Type an intent, title, document ID, requirement ID, or engineering term.</span></div>';return;}
    const scored=(window.AIXEM_SEARCH||[]).map(d=>{
      const text=(d.id+' '+d.title+' '+d.summary+' '+d.aliases.join(' ')+' '+d.intents.join(' ')+' '+d.headings.join(' ')+' '+d.requirements.join(' ')).toLowerCase();
      let score=0;
      for(const t of tokens){
        if(d.id.toLowerCase()===t)score+=40;
        if(d.title.toLowerCase().includes(t))score+=12;
        if(d.aliases.some(x=>x.toLowerCase().includes(t)))score+=10;
        if(d.intents.some(x=>x.toLowerCase().includes(t)))score+=10;
        if(text.includes(t))score+=2;
      }
      return [score,d];
    }).filter(x=>x[0]>0).sort((a,b)=>b[0]-a[0]||a[1].title.localeCompare(b[1].title)).slice(0,15);
    results.innerHTML=scored.length
      ?scored.map(([,d])=>`<a class="result" href="${esc(resultUrl(d.url))}"><strong>${esc(d.title)}</strong><span>${esc(d.id)} · ${esc(d.summary)}</span></a>`).join('')
      :'<div class="result"><span>No canonical document matched this query.</span></div>';
  }
  function closeNav(){document.body.classList.remove('nav-open');menu?.setAttribute('aria-expanded','false');}
  menu?.addEventListener('click',()=>{const next=!document.body.classList.contains('nav-open');document.body.classList.toggle('nav-open',next);menu.setAttribute('aria-expanded',String(next));});
  sidebar?.addEventListener('click',e=>{if(e.target.closest('a'))closeNav();});
  open?.addEventListener('click',()=>{dialog.showModal();input.focus();run();});
  close?.addEventListener('click',()=>dialog.close());
  input?.addEventListener('input',run);
  window.addEventListener('keydown',e=>{
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();dialog.showModal();input.focus();run();}
    if(e.key==='Escape'){if(dialog?.open)dialog.close();closeNav();}
  });
  document.addEventListener('click',e=>{if(document.body.classList.contains('nav-open')&&!sidebar?.contains(e.target)&&e.target!==menu)closeNav();});
})();