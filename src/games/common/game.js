/* 생애주기 게임 공통 도우미 — data/dk/typeA.html의 함수들을 옮겼다. */
'use strict';
const DK=(()=>{
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pad=n=>String(n).padStart(2,'0');
  const shuffle=a=>{a=[...a];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};

  /* 받침에 맞는 조사 */
  const bat=w=>{const c=w.charCodeAt(w.length-1);return c>=0xAC00&&c<=0xD7A3&&(c-0xAC00)%28!==0};
  const ieyo=w=>bat(w)?'이에요':'예요', eul=w=>bat(w)?'을':'를', wa=w=>bat(w)?'과':'와', iga=w=>bat(w)?'이':'가', eun=w=>bat(w)?'은':'는';

  function speak(text){try{const s=speechSynthesis;s.cancel();const u=new SpeechSynthesisUtterance(text);u.lang='ko-KR';u.rate=.9;const v=s.getVoices().find(v=>/ko/i.test(v.lang));if(v)u.voice=v;s.speak(u)}catch(e){}}

  /* 이 기기에만 저장 */
  const store=prefix=>({get(k,d){try{const v=localStorage.getItem(prefix+k);return v==null?d:JSON.parse(v)}catch(e){return d}},set(k,v){try{localStorage.setItem(prefix+k,JSON.stringify(v))}catch(e){}}});

  const SPK='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7"/><path d="M19 6a8.5 8.5 0 0 1 0 12"/></svg>';
  const LOGO='../common/dku-logo.png';
  const DKU=`<footer class="dku"><img src="${LOGO}" alt="단국대학교"></footer>`;

  /* 상단 바: 처음 화면에는 브랜드, 그 밖에는 ‹ 처음 버튼 (게이트에서 새 창으로 열리므로 목록 버튼은 두지 않는다) */
  const hbar=(brand,back)=>`<header class="hbar">${back?'<button class="hb" data-act="home" aria-label="처음으로">‹ 처음</button>':`<span class="brand"><i class="bm">${esc(brand.mark)}</i>${brand.html}</span>`}<span class="hr"><button class="help" data-act="help" aria-label="게임 방법 보기">?</button></span></header>`;
  const steps=(names,cur)=>`<div class="steps" aria-label="${cur+1}단계 ${esc(names[cur])}">${names.map((n,i)=>`${i?'<i></i>':''}<b class="${i<=cur?'d':''}">${i+1}</b>${esc(n)}`).join('')}</div>`;
  const seg=(total,done)=>`<div class="seg" aria-label="${done+1}번째, 모두 ${total}개">${Array.from({length:total},(_,i)=>`<i class="${i<done?'d':i===done?'c':''}"></i>`).join('')}</div>`;
  const sayBig=t=>`<p class="saybig"><span>“${esc(t)}”</span><button class="spk" data-say="${esc(t)}" aria-label="소리로 듣기">${SPK}</button></p>`;

  /* 화면 바꾸기 + 공통 버튼 연결 */
  function mount(root,html,handlers){
    root.innerHTML=`<div class="view">${html}</div>`;
    root.scrollTop=0;window.scrollTo(0,0);
    root.querySelectorAll('[data-say]').forEach(b=>b.onclick=()=>speak(b.dataset.say));
    const help=document.getElementById('help');
    root.querySelectorAll('[data-act=help]').forEach(b=>b.onclick=()=>help&&help.showModal());
    for(const [act,fn] of Object.entries(handlers||{}))root.querySelectorAll(`[data-act="${act}"]`).forEach(b=>b.onclick=e=>fn(b,e));
  }

  return {esc,pad,shuffle,bat,ieyo,eul,wa,iga,eun,speak,store,SPK,LOGO,DKU,hbar,steps,seg,sayBig,mount};
})();
