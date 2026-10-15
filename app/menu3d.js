
/* Controlador de navegação por níveis: menu > submenu > cifra em tela cheia */
const ntSections=[
 {name:'REPERTÓRIOS',desc:'Escolha um repertório e navegue pelas músicas no carrossel.',icon:'♫',kind:'reps'},
 {name:'TODAS AS CIFRAS',desc:'Biblioteca completa de músicas, tons e cifras.',icon:'♬',kind:'library'},
 {name:'NOVA CIFRA',desc:'Cadastrar uma música e editar sua cifra.',icon:'＋',kind:'new-song'},
 {name:'NOVO REPERTÓRIO',desc:'Criar e organizar uma nova lista de músicas.',icon:'▤',kind:'new-rep'},
 {name:'BACKUP',desc:'Exportar seus repertórios, cifras e anotações.',icon:'⇩',kind:'backup'},
 {name:'RESTAURAR',desc:'Recuperar um backup JSON salvo anteriormente.',icon:'↻',kind:'restore'},
 {name:'IMPORTAR TXT',desc:'Importar músicas a partir de arquivos de texto.',icon:'⇧',kind:'import'}
];
let ntLevel='main',ntItems=ntSections,ntIndex=0,ntCurrentRep=null,ntReturn=null;
const ntEl=id=>document.getElementById(id);
function ntIsOpen(){return ntEl('nt-app-menu').classList.contains('on')}
function ntMenu(level='main',id=null,selected=0){
 ntLevel=level;ntCurrentRep=id;ntIndex=selected;
 if(level==='main')ntItems=ntSections;
 else if(level==='reps')ntItems=db.reps.map(r=>({name:r.name,desc:r.songs.length+' músicas'+(r.alias?' · '+r.alias:''),icon:'▤',kind:'rep',id:r.id}));
 else if(level==='songs')ntItems=(id?R(id)?.songs||[]:db.songs.map(s=>s.id)).map(x=>song(x)).filter(Boolean).map(s=>({name:s.title,desc:[s.artist,s.key&&'Tom '+s.key].filter(Boolean).join(' · '),icon:'♫',kind:'song',id:s.id,rep:id}));
 if(!ntItems.length)ntItems=[{name:'Nenhum item cadastrado',desc:'Use o menu principal para cadastrar.',icon:'＋',kind:'empty'}];
 ntIndex=Math.max(0,Math.min(ntIndex,ntItems.length-1));
 ntEl('nt-app-menu').classList.add('on');
 ntEl('nt-head-back').style.display=level==='main'?'none':'';
 ntEl('nt-crumb').textContent=level==='main'?'MENU PRINCIPAL':level==='reps'?'MENU / REPERTÓRIOS':'MENU / '+(id?R(id)?.name||'REPERTÓRIO':'TODAS AS CIFRAS');
 ntEl('nt-head-title').textContent=ntEl('nt-crumb').textContent;
 ntRender();
}
function ntRender(){
 const area=ntEl('nt-menu-cards');area.replaceChildren();
 const n=ntItems.length;
 ntItems.forEach((it,i)=>{
  let d=i-ntIndex;if(d>n/2)d-=n;if(d< -n/2)d+=n;
  if(Math.abs(d)>3)return;
  const b=document.createElement('button');b.className='nt-card';b.type='button';
  b.style.setProperty('--tone',['#20513b','#194554','#4a3e24','#393050','#214d40'][i%5]);
  b.style.transform=`translate(-50%,-50%) translate3d(${d*77}px,${d*80}px,${-Math.abs(d)*180}px) rotateY(${-d*24}deg) rotateX(${d*5}deg) scale(${Math.max(.6,1-Math.abs(d)*.11)})`;
  b.style.opacity=String(Math.max(.1,1-Math.abs(d)*.28));b.style.zIndex=String(20-Math.abs(d));
  b.innerHTML='<span class="nt-no"></span><span class="nt-symbol"></span><span class="nt-name"></span><span class="nt-sub"></span>';
  b.querySelector('.nt-no').textContent=String(i+1).padStart(2,'0')+' / '+String(n).padStart(2,'0');
  b.querySelector('.nt-symbol').textContent=it.icon;b.querySelector('.nt-name').textContent=it.name;b.querySelector('.nt-sub').textContent=it.desc||'';
  b.onclick=()=>{if(i===ntIndex)ntActivate();else{ntIndex=i;ntRender()}};
  area.appendChild(b);
 });
 const it=ntItems[ntIndex];
 ntEl('nt-menu-title').textContent=it.name;ntEl('nt-menu-desc').textContent=it.desc||'';
 ntEl('nt-menu-count').textContent=(ntIndex+1)+' / '+n;
 ntEl('nt-menu-open').textContent=it.kind==='song'?'ABRIR CIFRA ↗':it.kind==='rep'?'VER MÚSICAS ↗':'ABRIR ↗';
 ntRenderList();
}
function ntRenderList(){
 const list=ntEl('nt-item-list');list.replaceChildren();
 ntEl('nt-list-label').textContent=ntLevel==='main'?'FUNÇÕES DISPONÍVEIS':ntLevel==='reps'?'REPERTÓRIOS CADASTRADOS':'MÚSICAS / CIFRAS';
 ntItems.forEach((it,i)=>{
  const btn=document.createElement('button');btn.type='button';btn.className=i===ntIndex?'nt-active':'';
  btn.setAttribute('aria-current',i===ntIndex?'true':'false');
  const icon=document.createElement('span');icon.className='nt-item-icon';icon.textContent=it.icon;
  const body=document.createElement('span');body.className='nt-item-body';
  const name=document.createElement('span');name.className='nt-item-name';name.textContent=it.name;
  const meta=document.createElement('span');meta.className='nt-item-meta';meta.textContent=it.desc||'';
  const arrow=document.createElement('span');arrow.className='nt-item-arrow';arrow.textContent=i===ntIndex?'●':'›';
  body.append(name,meta);btn.append(icon,body,arrow);
  btn.onclick=()=>{if(i===ntIndex)ntActivate();else{ntIndex=i;ntRender()}};
  list.appendChild(btn);
 });
 const active=list.children[ntIndex];if(active&&window.innerWidth>760)active.scrollIntoView({block:'nearest'});
}
function ntMove(delta){ntIndex=(ntIndex+delta+ntItems.length)%ntItems.length;ntRender()}
function ntActivate(){
 const it=ntItems[ntIndex];if(!it)return;
 switch(it.kind){
 case 'reps':ntMenu('reps');break;
 case 'library':ntMenu('songs',null);break;
 case 'rep':ntMenu('songs',it.id);break;
 case 'song':ntReturn={level:ntLevel,id:ntCurrentRep,index:ntIndex};ntClose();stage(it.id,it.rep);break;
 case 'new-song':ntClose();newsong();break;
 case 'new-rep':ntClose();newrep();break;
 case 'backup':backup();break;
 case 'restore':restore();break;
 case 'import':importtxt();break;
 case 'empty':ntMenu('main');break;
 }
}
function ntBack(){if(ntLevel==='songs'&&ntCurrentRep)ntMenu('reps',null,Math.max(0,db.reps.findIndex(r=>r.id===ntCurrentRep)));else ntMenu('main')}
function ntClose(){ntEl('nt-app-menu').classList.remove('on');document.body.style.overflow=''}
function ntFromStage(delta=0){
 if(!Array.isArray(order)||!order.length)return ntMenu('main');
 const i=(pos+delta+order.length)%order.length;
 ntMenu('songs',rep,i);
}
(function(){
 const el=ntEl('nt-menu-swipe');let x=null,y=null;
 el.addEventListener('touchstart',e=>{if(e.touches.length===1){x=e.touches[0].clientX;y=e.touches[0].clientY}},{passive:true});
 el.addEventListener('touchend',e=>{if(x===null)return;const dx=e.changedTouches[0].clientX-x,dy=e.changedTouches[0].clientY-y;if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy)*1.2)ntMove(dx<0?1:-1);x=null},{passive:true});
 let mouse=null;el.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse')mouse=e.clientX});
 el.addEventListener('pointerup',e=>{if(mouse!==null&&Math.abs(e.clientX-mouse)>55)ntMove(e.clientX<mouse?1:-1);mouse=null});
 document.addEventListener('keydown',e=>{if(!ntIsOpen())return;if(e.key==='Escape')ntBack();else if(e.key==='ArrowLeft'){e.preventDefault();ntMove(-1)}else if(e.key==='ArrowRight'){e.preventDefault();ntMove(1)}});
})();
const ntOriginalBack=back;
back=function(){ntFromStage(0)};
prev=function(){ntFromStage(-1)};
next=function(){ntFromStage(1)};
const ntOriginalReps=reps,ntOriginalLibrary=library;
reps=function(){ntMenu('reps')};
library=function(){ntMenu('songs',null)};
