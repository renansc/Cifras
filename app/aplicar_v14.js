
/* Correções V14: menu, rolagem e apresentação em duas telas */
(function(){
 const oldNewsong=newsong;
 newsong=function(){window.ntNewSongOrigin=true;oldNewsong()};
 const oldClosem=closem;
 closem=function(id){
   oldClosem(id);
   if(id==='smodal'&&window.ntNewSongOrigin){
     window.ntNewSongOrigin=false;
     ntMenu('main');
   }
 };
 const oldSave=savesong;
 savesong=function(){
   const wasNew=!!window.ntNewSongOrigin;
   window.ntNewSongOrigin=false;
   oldSave();
   if(wasNew&&document.getElementById('smodal')&&!document.getElementById('smodal').classList.contains('on'))ntMenu('main');
 };
 const menu=document.getElementById('nt-menu-swipe');
 if(menu)menu.addEventListener('wheel',e=>{
   if(!ntIsOpen()||Math.abs(e.deltaY)<2&&Math.abs(e.deltaX)<2)return;
   e.preventDefault();
   const now=Date.now();
   if(now-(window.ntLastWheel||0)<320)return;
   window.ntLastWheel=now;
   ntMove((Math.abs(e.deltaY)>=Math.abs(e.deltaX)?e.deltaY:e.deltaX)>0?1:-1);
 },{passive:false});
 const oldStage=stage;
 stage=function(id,rid){
   oldStage(id,rid);
   const s=song(id);
   if(s&&window.ntPresentationEnabled)ntSendSong(s);
 };
 const query=new URLSearchParams(location.search);
 const controller=query.get('controller') || window.NT_CONTROL_KEY;
 window.ntPresentationEnabled=!!controller;
 async function ntSendSong(s){
   try{
     const payload={title:s.title||'',artist:s.artist||'',key:s.key||'',text:s.text!=null?s.text:'',html:s.text==null?s.html||'':'',fontSize:fs,columns:cols,dark:document.getElementById('stage').classList.contains('dark')};
     const r=await fetch('/api/present',{method:'POST',headers:{'Content-Type':'application/json','X-Controller-Key':controller},body:JSON.stringify(payload)});
     if(!r.ok)throw new Error('Servidor recusou a atualização ('+r.status+')');
     const badge=document.getElementById('nt-tv-status');if(badge)badge.textContent='TV sincronizada ✓';
   }catch(e){
     const badge=document.getElementById('nt-tv-status');if(badge)badge.textContent='TV desconectada';
     console.warn('Apresentação:',e);
   }
 }
 window.ntSendSong=ntSendSong;
 ['plus','minus','setcols','cyclecols','theme'].forEach(name=>{const orig=window[name];if(typeof orig!=='function')return;window[name]=function(...args){const result=orig.apply(this,args);if(window.ntPresentationEnabled&&sid){const current=song(sid);if(current)ntSendSong(current)}return result}});
 if(controller){
   const bar=document.querySelector('#nt-app-menu .nt-head-buttons');
   if(bar){
     const label=document.createElement('span');label.id='nt-tv-status';label.style.cssText='color:#b8ff56;font-size:11px';label.textContent='Modo controle da TV';
     bar.prepend(label);
   }
 }
})();
