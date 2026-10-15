
let wheelIndex=0,wheelCards=[];
const wheelPalette=[['#224f40','#0b211c','#9ee8a533'],['#183f4c','#0c2026','#67b8ce33'],['#463b20','#1c180e','#efca6733'],['#3d2b4b','#190f22','#a97acb33'],['#234d3a','#0b241b','#b8ff5633'],['#3c3130','#201412','#e0a07533']];
function wheelVisible(){const e=document.getElementById('nt-wheel');return !!e&&e.classList.contains('open')}
function wheelShow(delta=0){
 if(!Array.isArray(order)||!order.length)return;
 wheelIndex=((wheelVisible()?wheelIndex:Math.max(0,pos))+delta+order.length)%order.length;
 document.getElementById('nt-wheel').classList.add('open');document.body.style.overflow='hidden';
 wheelBuild();
}
function wheelBuild(){
 const axis=document.getElementById('wheel-axis');axis.replaceChildren();wheelCards=[];
 order.forEach((id,i)=>{
  const s=song(id);if(!s)return;
  const card=document.createElement('button');card.type='button';card.className='wheel-card';
  const pal=wheelPalette[i%wheelPalette.length];
  card.style.setProperty('--bg1',pal[0]);card.style.setProperty('--bg2',pal[1]);card.style.setProperty('--glow',pal[2]);
  for(const [klass,val] of [['w-number','MÚSICA '+String(i+1).padStart(2,'0')],['w-glyph','♫'],['w-title',s.title||'Sem título'],['w-artist',s.artist||''],['w-key',s.key?'TOM · '+s.key:'TOM NÃO INFORMADO'],['w-action','ABRIR CIFRA ↗']]){
    const el=document.createElement('span');el.className=klass;el.textContent=val;card.appendChild(el);
  }
  card.setAttribute('aria-label',s.title||'Música');
  card.onclick=()=>{if(i===wheelIndex)wheelOpenSelected();else wheelGo(i)};
  axis.appendChild(card);wheelCards.push({card,i});
 });
 wheelRender();
}
function wheelRender(){
 const n=order.length;if(!n)return;
 wheelCards.forEach(({card,i})=>{
  let offset=i-wheelIndex;
  if(offset>n/2)offset-=n;
  if(offset< -n/2)offset+=n;
  const a=Math.abs(offset),scale=Math.max(.62,1-a*.13);
  card.style.transform=`translate3d(${offset*83}px,${offset*105}px,${-a*190}px) rotateY(${offset*-23}deg) rotateX(${offset*5}deg) scale(${scale})`;
  card.style.opacity=a>2?'0':String(1-a*.27);
  card.style.filter=`brightness(${1-a*.23})`;
  card.style.zIndex=String(20-a);
  card.style.pointerEvents=a<=2?'auto':'none';
  card.tabIndex=a<=2?0:-1;
 });
 document.getElementById('wheel-counter').textContent=(wheelIndex+1)+' / '+n;
}
function wheelGo(i){wheelIndex=i;wheelRender()}
function wheelMove(delta){if(!wheelVisible())return;wheelIndex=(wheelIndex+delta+order.length)%order.length;wheelRender()}
function wheelClose(){document.getElementById('nt-wheel').classList.remove('open');document.body.style.overflow=''}
function wheelOpenSelected(){const id=order[wheelIndex];if(!id)return;const rid=rep;wheelClose();stage(id,rid)}
(function(){
 const el=document.getElementById('wheel-view');let sx=null,sy=null;
 el.addEventListener('touchstart',e=>{if(e.touches.length===1){sx=e.touches[0].clientX;sy=e.touches[0].clientY}},{passive:true});
 el.addEventListener('touchend',e=>{if(sx===null)return;const dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.2)wheelMove(dx<0?1:-1);sx=null},{passive:true});
 let mx=null;el.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse')mx=e.clientX});
 el.addEventListener('pointerup',e=>{if(mx===null)return;const d=e.clientX-mx;if(Math.abs(d)>60)wheelMove(d<0?1:-1);mx=null});
 document.addEventListener('keydown',e=>{if(!wheelVisible())return;if(e.key==='Escape')wheelClose();if(e.key==='ArrowLeft'){e.preventDefault();wheelMove(-1)}if(e.key==='ArrowRight'){e.preventDefault();wheelMove(1)}});
})();
