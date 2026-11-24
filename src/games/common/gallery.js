/* 모두의 작품 모음: 결과 화면에서 내 작품을 이름과 함께 올리고, 다른 사람이 올린 작품을 함께 본다.
   그림은 올리지 않고 고른 번호(data)만 보낸다 → 각 게임의 render(data)가 다시 그린다.
   서버: ../../admin/gallery.php (PHP·DB). PHP 없이 열면(로컬 미리보기) "지금은 볼 수 없어요"만 보인다.
   쓰기: DKGallery.mount(el,{game:'4-1',title:'모두의 옷차림 보기',what:'옷차림',data:{…},render:d=>html,alt:d=>글,cw:'104px',shareText})
*/
window.DKGallery=(()=>{
  const API='../../admin/gallery.php';
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const store={get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
  const css=`.gal{margin:26px 0 8px;padding:16px 14px 14px;background:var(--paper);border:1.5px solid var(--line);border-radius:14px;box-shadow:2px 3px 0 var(--line)}
.gal h2{margin:0 0 4px;font:var(--hw) 24px/1.2 var(--fh)}
.gal .gs{margin:0 0 12px;font:500 14px/1.5 var(--fb);color:var(--muted)}
.gal .up{display:flex;gap:8px;align-items:stretch}
.gal .up input{flex:1;min-width:0;padding:12px;border:1.5px solid var(--line);border-radius:10px;font:600 17px var(--fb);color:var(--ink);background:#fff}
.gal .up input:focus{outline:3px solid var(--ac);outline-offset:1px}
.gal .up .btn{flex:none;width:auto;padding:12px 16px;font-size:16px}
.gal .gm{min-height:1.4em;margin:8px 0 0;font:600 14px/1.4 var(--fb);color:var(--muted)}
.gal .gm.ok{color:var(--ok)}.gal .gm.no{color:var(--no)}
.gal .gt{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.gal .gt .btn{padding:11px;font-size:15px}
.gal .gl{display:grid;grid-template-columns:repeat(auto-fill,minmax(var(--gw,104px),1fr));gap:14px 10px;margin:14px 0 0;padding:0;list-style:none}
.gal .gl li{position:relative;background:#fff;padding:5px 5px 6px;box-shadow:0 3px 8px rgba(60,40,20,.16);transform:rotate(var(--r,0deg))}
.gal .gl li.me{box-shadow:0 0 0 3px var(--ac),0 3px 8px rgba(60,40,20,.16)}
.gal .gl li.me::before{content:'나';position:absolute;z-index:3;top:-8px;left:-8px;width:26px;height:26px;border-radius:50%;background:var(--ac);color:#fff;font:700 13px/26px var(--fb);text-align:center}
.gal .gl .gn{display:block;margin-top:5px;font:var(--hw) 17px/1.2 var(--fh);text-align:center;word-break:break-all}
.gal .ge{margin:14px 0 0;padding:16px;text-align:center;font:600 15px/1.5 var(--fb);color:var(--muted);border:1.5px dashed var(--line);border-radius:10px}`;
  function addCss(){if(document.getElementById('dk-gal-css'))return;const s=document.createElement('style');s.id='dk-gal-css';s.textContent=css;document.head.appendChild(s)}
  async function api(opt){
    const r=await fetch(API+(opt?'':'?game='+encodeURIComponent(cur.game)+'&_='+Date.now()),opt||{cache:'no-store'});
    let j=null;try{j=await r.json()}catch(e){}
    if(!j)throw new Error('down');
    return j;
  }
  let cur=null;
  function mount(el,o){
    addCss();cur=o;
    const mine=store.get('dkgal-'+o.game)||[],nm=store.get('dkgal-name')||'';
    el.innerHTML=`<section class="gal" aria-labelledby="galh"><h2 id="galh">${esc(o.title)}</h2>
      <p class="gs">내 ${esc(o.what)}을 올리면 다른 사람들과 함께 볼 수 있어요.</p>
      <div class="up"><input id="galn" maxlength="10" placeholder="이름 (10자까지)" aria-label="내 이름" value="${esc(nm)}" autocomplete="off"><button class="btn pri" id="galup">올리기</button></div>
      <p class="gm" id="galm" aria-live="polite"></p>
      <div class="gt"><button class="btn sec" id="galre">↻ 새로고침</button><button class="btn sec" id="galsh">공유하기</button></div>
      <ul class="gl" id="gall" aria-label="${esc(o.title)}"></ul><p class="ge" id="gale" hidden></p></section>`;
    if(o.cw)el.querySelector('.gl').style.setProperty('--gw',o.cw);   // 카드 최소 너비(가로로 긴 그림은 넓게)
    const $=id=>el.querySelector('#'+id),msg=(t,c)=>{$('galm').textContent=t;$('galm').className='gm'+(c?' '+c:'')};
    let posted=false;
    async function load(){
      const ul=$('gall'),em=$('gale');
      try{
        const j=await api();
        if(!j.ok)throw 0;
        const ids=store.get('dkgal-'+o.game)||[];
        ul.innerHTML=j.items.map((it,i)=>`<li class="${ids.includes(it.id)?'me':''}" style="--r:${[-1.5,1,-.5,1.5][i%4]}deg">${o.render(it.data)}<span class="gn">${esc(it.name)}</span></li>`).join('');
        ul.querySelectorAll('li').forEach((li,i)=>{const a=o.alt&&o.alt(j.items[i].data);a&&li.setAttribute('aria-label',j.items[i].name+': '+a)});
        em.hidden=!!j.items.length;em.textContent='아직 올라온 작품이 없어요. 첫 번째로 올려 보세요!';
      }catch(e){ul.innerHTML='';em.hidden=false;em.textContent='지금은 볼 수 없어요.';$('galup').disabled=true}
    }
    $('galup').onclick=async()=>{
      const name=$('galn').value.replace(/[<>]/g,'').trim();
      if(!name){msg('이름을 적어 주세요.','no');$('galn').focus();return}
      if(posted){msg('이미 올렸어요.','ok');return}
      $('galup').disabled=true;msg('올리는 중…');
      try{
        const j=await api({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({game:o.game,name,data:o.data})});
        if(!j.ok){msg(j.msg||'올리지 못했어요.','no');$('galup').disabled=false;return}
        posted=true;const ids=store.get('dkgal-'+o.game)||[];ids.push(j.id);store.set('dkgal-'+o.game,ids.slice(-50));store.set('dkgal-name',name);
        msg('올렸어요! 아래에서 다른 사람들 것과 비교해 보세요.','ok');try{window.DK&&DK.speak('올렸어요!')}catch(e){}
        load();
      }catch(e){msg('지금은 올릴 수 없어요.','no');$('galup').disabled=false}
    };
    $('galn').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();$('galup').click()}};
    $('galre').onclick=()=>{msg('');load()};
    $('galsh').onclick=async()=>{
      const url=location.href.split('#')[0],text=o.shareText||document.title;
      if(navigator.share){try{await navigator.share({title:document.title,text,url});return}catch(e){if(e&&e.name==='AbortError')return}}
      try{await navigator.clipboard.writeText(url);msg('링크를 복사했어요. 카톡이나 문자에 붙여 넣어 보내요.','ok')}
      catch(e){msg('주소창의 링크를 복사해서 보내 주세요.')}
    };
    setTimeout(load,500);   // 결과 화면 저장(DK.done) 뒤에 목록을 채운다
    return {reload:load};
  }
  return {mount};
})();
