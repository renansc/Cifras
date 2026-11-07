const CACHE='nanotech-cifras-offline-v1';
const APP=['./','./index.html','./cifras.html','./saida/NanotechSoft-Cifras.html','./Dados_App_Cifras.json','./assets/nanotechsoft-logo.png','./manifest.webmanifest'];
self.addEventListener('install',event=>{
 event.waitUntil(caches.open(CACHE).then(async cache=>{
  await Promise.all(APP.map(async path=>{try{const response=await fetch(new Request(path,{cache:'reload'}));if(response.ok)await cache.put(path,response)}catch(e){console.warn('Arquivo indisponível para cache',path,e)}}));
  await self.skipWaiting();
 }));
});
self.addEventListener('activate',event=>{
 event.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('nanotech-cifras-offline-')&&k!==CACHE).map(k=>caches.delete(k)))),self.clients.claim()]));
});
self.addEventListener('fetch',event=>{
 const req=event.request;
 if(req.method!=='GET'||new URL(req.url).origin!==self.location.origin)return;
 const url=new URL(req.url);
 if(req.mode==='navigate'){
  event.respondWith(fetch(req).then(async response=>{
   if(response.ok){const cache=await caches.open(CACHE);await cache.put(req,response.clone())}
   return response;
  }).catch(async()=>{const cache=await caches.open(CACHE);return await cache.match(req,{ignoreSearch:true})||await cache.match('./saida/NanotechSoft-Cifras.html')||await cache.match('./index.html')||Response.error()}));
  return;
 }
 // JSON: consulta rede primeiro; se offline, usa última cópia armazenada.
 if(url.pathname.endsWith('/Dados_App_Cifras.json')){
  event.respondWith(fetch(req).then(async response=>{if(response.ok)(await caches.open(CACHE)).put('./Dados_App_Cifras.json',response.clone());return response}).catch(async()=>await (await caches.open(CACHE)).match('./Dados_App_Cifras.json')||Response.error()));
  return;
 }
 event.respondWith(caches.match(req,{ignoreSearch:true}).then(hit=>hit||fetch(req)));
});