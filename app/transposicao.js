/* Transposição de acordes em tempo real — dados originais preservados. */
(function(){
 const CHROMA=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];
 const FLATS=["C","Db","D","Eb","E","F","Gb","G","Ab","A","Bb","B"];
 const SEMI={C:0,"C#":1,Db:1,D:2,"D#":3,Eb:3,E:4,F:5,"F#":6,Gb:6,G:7,"G#":8,Ab:8,A:9,"A#":10,Bb:10};
 const ROOT=/^([A-G](?:#|b)?)(.*)$/;
 const CHORD=/^[A-G](?:#|b)?(?:(?:m(?:aj|in)?|dim|aug|sus|add|M|º|°|ø|Δ|\+|-)?[0-9#b+\-°ºøΔ(),]*)?(?:\/[A-G](?:#|b)?)?$/;
 let steps=0,sourceId=null;
 function transposeRoot(note,shift,flats){
   if(!Object.prototype.hasOwnProperty.call(SEMI,note))return note;
   return (flats?FLATS:CHROMA)[((SEMI[note]+shift)%12+12)%12];
 }
 function transposeChord(chord,shift,preferFlat){
   return chord.split("/").map((section,i)=>{
     const m=ROOT.exec(section);if(!m)return section;
     return transposeRoot(m[1],shift,preferFlat||m[1].includes("b"))+m[2];
   }).join("/");
 }
 function tonic(key,shift){
   const m=/^([A-G](?:#|b)?)(.*)$/.exec((key||"").trim());if(!m)return key||"—";
   return transposeRoot(m[1],shift,m[1].includes("b"))+m[2];
 }
 function transposeLine(line,shift,preferFlat){
   return line.replace(/(^|\s)([|:[({]*)([A-G](?:#|b)?(?:m(?:aj|in)?|dim|aug|sus|add|M|º|°|ø|Δ|\+|-)?[0-9#b+\-°ºøΔ(),]*(?:\/[A-G](?:#|b)?)?)([|:\])}]*)(?=\s|$)/g,
     (whole,space,before,chord,after)=>CHORD.test(chord)?space+before+transposeChord(chord,shift,preferFlat)+after:whole);
 }
 function transposedText(text,shift,preferFlat){
   return (text||"").split(/\r?\n/).map(line=>{
     const explicit=/^(\s*)([@=])(\s*)(.*)$/.exec(line);
     if(explicit){
       if(explicit[2]==="=")return line;
       return explicit[1]+explicit[2]+explicit[3]+transposeLine(explicit[4],shift,preferFlat);
     }
     const pieces=line.trim().split(/\s+/).filter(Boolean);
     const chordLine=pieces.length>0&&pieces.every(x=>CHORD.test(x.replace(/^[|:[({]+|[|:\])}]+$/g,"")));
     return chordLine?transposeLine(line,shift,preferFlat):line;
   }).join("\n");
 }
 function transposedHTML(html,shift,preferFlat){
   if(!html||!shift)return html||"";
   const container=document.createElement("div");
   container.innerHTML=html;
   container.querySelectorAll(".chord").forEach(el=>{
     const original=el.textContent;
     const value=original.trim();
     if(CHORD.test(value))el.textContent=original.replace(value,transposeChord(value,shift,preferFlat));
   });
   container.querySelectorAll(".chordline").forEach(el=>{
     // Compatível com cifras HTML importadas.
     if(!el.querySelector(".chord"))el.textContent=transposeLine(el.textContent,shift,preferFlat);
   });
   return container.innerHTML;
 }
 function current(){
   return typeof song==="function"&&sid?song(sid):null;
 }
 function transformed(s){
   const flat=!!(s.key||"").includes("b");
   return {
     key:tonic(s.key,steps),
     text:s.text!=null?transposedText(s.text,steps,flat):"",
     html:s.text==null?transposedHTML(s.html||"",steps,flat):""
   };
 }
 function render(s){
   if(!s)return;
   const data=transformed(s);
   const chart=document.getElementById("chart");
   if(!chart)return;
   chart.innerHTML=s.text!=null?manual(data.text):data.html;
   [...chart.querySelectorAll(".line,.chordline,.cifra-line")].forEach((el,i)=>el.dataset.i=i);
   if(typeof notes==="function")notes();
   document.getElementById("stitle").textContent=(s.title||"")+" — "+(s.artist||"")+" — "+data.key;
   const badge=document.getElementById("nt-current-tone");
   if(badge){badge.textContent="Tom: "+data.key+(steps?" ("+(steps>0?"+":"")+steps+")":"");badge.title="Restaurar tom original: "+(s.key||"não informado");}
 }
 window.ntTransposeRender=function(s){
   if(!s)return;
   // Toda abertura de cifra (inclusive após salvar no editor) começa no tom original.
   sourceId=s.id;
   steps=0;
   render(s);
 };
 window.ntChangeTone=function(delta){
   const s=current();if(!s)return;
   steps=Math.max(-24,Math.min(24,steps+delta));
   const y=window.scrollY;render(s);window.scrollTo(0,y);
   if(window.ntPresentationEnabled&&typeof window.ntSendSong==="function")window.ntSendSong(s);
 };
 window.ntResetTone=function(){
   const s=current();if(!s)return;
   steps=0;const y=window.scrollY;render(s);window.scrollTo(0,y);
   if(window.ntPresentationEnabled&&typeof window.ntSendSong==="function")window.ntSendSong(s);
 };
 window.ntCurrentTranspose=function(s){return transformed(s||current());};
})();

/* Editor de cifra no palco: modifica os dados originais, sem sair da apresentação. */
(function(){
 let panel=null, editingId=null;
 function close(){if(panel){panel.remove();panel=null;}editingId=null;}
 window.ntEditOnStage=function(){
   if(panel)return;
   const s=typeof song==="function"&&sid?song(sid):null;
   if(!s)return alert("Abra uma cifra antes de editar.");
   editingId=s.id;
   panel=document.createElement("section");
   panel.id="nt-stage-editor";
   panel.style.cssText="position:fixed;inset:52px 12px 85px;z-index:1000;background:#202020;color:white;border:2px solid #6c9cbd;border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:8px;box-shadow:0 0 0 100vmax #0009;";
   const heading=document.createElement("strong");
   heading.textContent="✎ Editar cifra e letra — "+(s.title||"");
   const hint=document.createElement("small");
   hint.textContent="Editando a cifra original (tom "+(s.key||"não informado")+"). Alterações de tom feitas na apresentação não são gravadas automaticamente.";
   const metadata=document.createElement("div");
   metadata.style.cssText="display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:8px";
   function field(label,value){
     const wrap=document.createElement("label");
     wrap.style.cssText="display:flex;flex-direction:column;gap:4px;font-size:13px;font-weight:bold";
     const input=document.createElement("input");
     input.type="text";input.value=value||"";
     input.style.cssText="width:100%;padding:9px;background:#fff;color:#111;border:1px solid #999;border-radius:7px";
     wrap.append(document.createTextNode(label),input);
     metadata.appendChild(wrap);
     return input;
   }
   const nameInput=field("NOME DA MÚSICA",s.title);
   const artistInput=field("ARTISTA",s.artist);
   const keyInput=field("TOM ORIGINAL",s.key);
   const observationInput=field("OBSERVAÇÃO / DESCRIÇÃO",s.observation);
   const area=document.createElement("textarea");
   area.id="nt-stage-editor-text";
   area.style.cssText="flex:1;min-height:100px;width:100%;resize:none;background:#fff;color:#111;font:16px/1.5 monospace;padding:12px;border-radius:7px;white-space:pre;tab-size:4;";
   area.value=typeof textof==="function"?textof(s):(s.text||"");
   const marking=document.createElement("div");
   marking.style.cssText="display:flex;gap:6px;flex-wrap:wrap;align-items:center";
   function markLines(symbol){
     const start=area.selectionStart,end=area.selectionEnd,old=area.value;
     const from=old.lastIndexOf("\n",Math.max(0,start-1))+1;
     const next=old.indexOf("\n",end>start?end-1:start);
     const to=next<0?old.length:next;
     const selected=old.slice(from,to),lines=selected.split("\n");
     const result=lines.map(line=>{
       if(!line.trim())return line;
       const clean=line.replace(/^(\s*)[@=]\s?/, "$1");
       return symbol?clean.replace(/^(\s*)/, "$1"+symbol+" "):clean;
     }).join("\n");
     area.value=old.slice(0,from)+result+old.slice(to);
     area.focus();area.setSelectionRange(from,from+result.length);
   }
   for(const [label,symbol] of [["♪ ACORDE","@"],["T LETRA","="],["LIMPAR MARCAÇÃO",""]]){
     const btn=document.createElement("button");btn.type="button";btn.textContent=label;
     btn.onclick=()=>markLines(symbol);marking.appendChild(btn);
   }
   const help=document.createElement("small");
   help.textContent="Selecione uma ou mais linhas e clique em ACORDE ou LETRA. @ = acorde, = = letra; as marcas não aparecem no palco. Linhas antigas continuam automáticas.";
   const actions=document.createElement("div");
   actions.style.cssText="display:flex;gap:8px;flex-wrap:wrap";
   const saveButton=document.createElement("button");
   saveButton.textContent="✓ SALVAR E VOLTAR À CIFRA";
   saveButton.style.background="#226e45";
   const cancelButton=document.createElement("button");
   cancelButton.textContent="CANCELAR";
   const initial=JSON.stringify([area.value,nameInput.value,artistInput.value,keyInput.value,observationInput.value]);
   cancelButton.onclick=()=>{if(JSON.stringify([area.value,nameInput.value,artistInput.value,keyInput.value,observationInput.value])!==initial&&!confirm("Descartar alterações?"))return;close();};
   saveButton.onclick=()=>{
     const current=typeof song==="function"?song(editingId):null;
     if(!current)return alert("Cifra não encontrada.");
     const newTitle=nameInput.value.trim();
     if(!newTitle)return alert("Informe o nome da música.");
     const previous={title:current.title,artist:current.artist,key:current.key,observation:current.observation,text:current.text,html:current.html,pending:current.pending};
     current.title=newTitle;
     current.artist=artistInput.value.trim();
     current.key=keyInput.value.trim();
     current.observation=observationInput.value.trim();
     if(area.value!==(typeof textof==="function"?textof({text:previous.text,html:previous.html}):(previous.text||""))){
       current.text=area.value;
       current.html="";
       current.pending=!area.value.trim();
     }
     try{save();}catch(e){
       Object.assign(current,previous);
       return;
     }
     close();
     if(typeof stage==="function")stage(current.id,rep);
   };
   actions.append(saveButton,cancelButton);
   panel.append(heading,hint,metadata,marking,help,area,actions);
   document.body.appendChild(panel);
   area.focus();
 };
})();
