/* Transposição de acordes em tempo real — dados originais preservados. */
(function(){
 const CHROMA=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];
 const FLATS=["C","Db","D","Eb","E","F","Gb","G","Ab","A","Bb","B"];
 const SEMI={C:0,"C#":1,Db:1,D:2,"D#":3,Eb:3,F:4,"F#":5,Gb:6,G:7,"G#":8,Ab:8,A:9,"A#":10,Bb:10};
 const ROOT=/^([A-G](?:#|b)?)(.*)$/;
 const CHORD=/^([A-G](?:#|b)?)(?:(?:m|maj|min|dim|aug|sus|add|M|º|°|ø|Δ|\+|-)?[0-9#b+\-°ºøΔ(),]*)?(?:\/[A-G](?:#|b)?)?$/;
 const PREFIX=/^(\s*)([A-G](?:#|b)?)([^\s]*)/;
 let steps=0,sourceId=null,originalText="",originalHTML="";
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
   return line.replace(/(^|[\s|:[({])([A-G](?:#|b)?)([^\s|:\])}]*)(?=$|[\s|:\])}])/g,(whole,sep,root,rest)=>{
     const token=root+rest;
     if(!CHORD.test(token))return whole;
     return sep+transposeChord(token,shift,preferFlat);
   });
 }
 function transposedText(text,shift,preferFlat){
   return (text||"").split(/\r?\n/).map(line=>{
     // Somente linhas que aparentam ser sequências de acordes.
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
   if(sourceId!==s.id){sourceId=s.id;steps=0;}
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
