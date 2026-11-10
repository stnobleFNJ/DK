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

  /* 플레이 기록 → 관리자(admin/collect.php). 처음 화면을 벗어나면 시작, DK.done()에서 완료, 중간에 나가면 진행 상황만 남긴다.
     실패해도 게임에는 영향이 없다(로컬 파일로 열어도 그냥 무시). */
  const track=(()=>{
    const m=location.pathname.match(/\/games\/([^/]+)\//),game=m?m[1]:'';
    const course=/^m/.test(game)?'중기':/^h/.test(game)?'후기':'전기';
    const API=new URL('../../admin/collect.php',location.href).href;
    // <body data-track="hub">: 처음 화면이 방·주제 고르기 허브인 게임(처음 화면으로 돌아가도 한 판이 이어짐)
    const hub=()=>document.body.dataset.track==='hub';
    // 완료 뒤 새 판으로 볼 버튼(다시하기 등). 그 밖의 버튼(다시 듣기·고치기·기록 보기)으로 바뀐 화면은 기록하지 않는다
    const NEW=/^(again|restart|retry|redo|fresh|reset|replay|start|new|other|wrong)/;
    let sid='',t0=0,steps=0,trail=[],fin=false,lastAct='';
    const rid=()=>Date.now().toString(36)+Math.random().toString(36).slice(2,12);
    function send(event,extra,snap){
      const s=snap||{sid,t0,steps,trail};
      if(!s.sid||!game||location.protocol==='file:')return;
      const body=JSON.stringify(Object.assign({sid:s.sid,game,title:document.title,course,event,steps:s.steps,trail:s.trail,elapsed:Math.round((Date.now()-s.t0)/1000)},extra||{}));
      try{if(event==='exit'&&navigator.sendBeacon)navigator.sendBeacon(API,new Blob([body],{type:'application/json'}));
        else fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body,keepalive:body.length<60000}).catch(()=>{})}catch(e){}  // keepalive는 64KB까지만 됨
    }
    function screen(view){  // 화면이 바뀔 때마다
      const home=view.querySelector('.hbar .brand')||(!view.querySelector('[data-act=home]')&&view.querySelector('[data-act=start]'));
      const act=lastAct;lastAct='';
      if(home){if(hub()&&!fin)return;if(sid&&!fin)send('exit');sid='';fin=false;return}
      if(fin&&!NEW.test(act))return;
      if(!sid||fin){sid=rid();t0=Date.now();steps=1;trail=[];fin=false;send('start');return}
      steps++;
    }
    document.addEventListener('click',e=>{  // 고른 것(버튼 글자)을 차례로 남긴다
      const b=e.target.closest('button,[data-act],[role=button],label,input[type=checkbox]');
      if(!b)return;
      lastAct=b.dataset.act||b.id||'';
      if(!sid||fin||/^(home|help)$/.test(b.dataset.act||'')||b.matches('[data-say],.spk'))return;
      const t=(b.innerText||b.getAttribute('aria-label')||b.value||'').replace(/\s+/g,' ').trim().slice(0,60);
      if(t&&trail.length<300)trail.push(t);
    },true);
    addEventListener('pagehide',()=>{if(sid&&!fin)send('exit')});
    // 결과 화면 글자. data-private 영역(직접 쓴 글·키·몸무게 등 '보내지 않는다'고 안내한 것)은 빼고 보낸다
    function text(v){
      if(!v)return '';
      let t=v.innerText;
      v.querySelectorAll('[data-private]').forEach(p=>{const s=p.innerText.trim();if(s)t=t.split(s).join('[비공개]')});
      return t.replace(/\n{2,}/g,'\n').trim().slice(0,3000);
    }
    // opt.noText: 결과 화면 글자를 보내지 않는다('어디에도 보내지 않아요'라고 안내한 게임 — 키·몸무게, 직접 쓴 글 등)
    function done(data,opt){  // 결과 화면을 그린 뒤 부른다
      if(!sid||fin)return;fin=true;
      if(steps<2)return;  // 처음 화면에서 바로 '지난 결과 보기' 같은 화면만 연 경우는 완료로 치지 않는다
      // 결과 화면 글자는 바로 읽어 두고(곧바로 다른 화면으로 가도 그대로), 보내기만 조금 뒤에
      const v=document.querySelector('.view'),priv=opt&&opt.noText;
      const snap={sid,t0,steps,trail:trail.slice()},res=priv?'(개인 정보 보호: 화면 내용은 저장하지 않음)':text(v);
      // 관리자 '게임 결과 화면 보기'용: 결과 화면 HTML(개인 정보 화면은 보내지 않음, 너무 크면 생략)
      const html=priv||!v?'':v.outerHTML,shot=html&&html.length<900000?{root:v.parentElement&&v.parentElement.id||'',html}:null;
      setTimeout(()=>send('done',{data:data||null,result:res,shot},snap),300);
    }
    return {screen,done};
  })();

  /* 화면 바꾸기 + 공통 버튼 연결 */
  function mount(root,html,handlers){
    root.innerHTML=`<div class="view">${html}</div>`;
    try{track.screen(root.firstElementChild)}catch(e){}
    root.scrollTop=0;window.scrollTo(0,0);
    root.querySelectorAll('[data-say]').forEach(b=>b.onclick=()=>speak(b.dataset.say));
    const help=document.getElementById('help');
    root.querySelectorAll('[data-act=help]').forEach(b=>b.onclick=()=>help&&help.showModal());
    for(const [act,fn] of Object.entries(handlers||{}))root.querySelectorAll(`[data-act="${act}"]`).forEach(b=>b.onclick=e=>fn(b,e));
  }

  return {esc,pad,shuffle,bat,ieyo,eul,wa,iga,eun,speak,store,SPK,LOGO,DKU,hbar,steps,seg,sayBig,mount,done:track.done,screen:track.screen};
})();
