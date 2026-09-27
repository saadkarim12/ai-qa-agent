PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Test Case Writer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#f5f6f8; --surface:#ffffff; --sunken:#eef0f4; --line:#dde1e8; --line-strong:#c7cdd7;
  --ink:#161a22; --ink-soft:#3b4453; --muted:#6a7383;
  --accent:#1d3f8a; --accent-ink:#ffffff; --accent-soft:#e8edf8;
  --crit:#b3261e; --high:#a3570d; --med:#1b5f95; --low:#687181;
  --warn:#8a5a00; --warn-bg:#fdf5e1; --warn-line:#ecd29a;
  --bad:#a32118; --bad-bg:#fcecea; --ok:#1d6b42;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0f1319; --surface:#161b23; --sunken:#1c222c; --line:#2a313c; --line-strong:#39414e;
    --ink:#e7ebf1; --ink-soft:#bdc5d1; --muted:#8b95a4;
    --accent:#86a8ee; --accent-ink:#0c1526; --accent-soft:#1b2537;
    --crit:#f0877e; --high:#e2a566; --med:#7cb7e6; --low:#8b95a4;
    --warn:#e7bd62; --warn-bg:#2a2313; --warn-line:#5a4722;
    --bad:#f0877e; --bad-bg:#2c1716; --ok:#6fc594;
  }
}
:root[data-theme="dark"]{
  --ground:#0f1319; --surface:#161b23; --sunken:#1c222c; --line:#2a313c; --line-strong:#39414e;
  --ink:#e7ebf1; --ink-soft:#bdc5d1; --muted:#8b95a4;
  --accent:#86a8ee; --accent-ink:#0c1526; --accent-soft:#1b2537;
  --crit:#f0877e; --high:#e2a566; --med:#7cb7e6; --low:#8b95a4;
  --warn:#e7bd62; --warn-bg:#2a2313; --warn-line:#5a4722;
  --bad:#f0877e; --bad-bg:#2c1716; --ok:#6fc594;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font:400 14.5px/1.55 "IBM Plex Sans",-apple-system,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1320px;margin:0 auto;padding:0 28px 80px}
header{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;padding:26px 0 20px}
h1{font:600 21px/1.2 "IBM Plex Sans",sans-serif;margin:0;letter-spacing:-.01em}
.tagline{color:var(--muted);font-size:13.5px}
.model{margin-left:auto;font:500 12px/1 "IBM Plex Mono",monospace;color:var(--muted);
  padding:6px 9px;border:1px solid var(--line);border-radius:3px;background:var(--surface)}

.card{background:var(--surface);border:1px solid var(--line);border-radius:4px}
.input{padding:20px 22px;display:grid;grid-template-columns:1fr 300px;gap:22px}
label.f{display:block;font-weight:600;font-size:12.5px;margin-bottom:7px;color:var(--ink-soft)}
.hint{font-size:12.5px;color:var(--muted);margin-top:7px}
textarea,input[type=url]{width:100%;font:400 13.5px/1.55 "IBM Plex Mono",monospace;
  color:var(--ink);background:var(--ground);border:1px solid var(--line-strong);border-radius:3px;
  padding:11px 12px}
textarea{min-height:230px;resize:vertical}
textarea:focus,input:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
.side{display:flex;flex-direction:column;gap:18px}
.btn{font:600 14px/1 "IBM Plex Sans",sans-serif;border-radius:3px;padding:12px 16px;cursor:pointer;
  border:1px solid var(--accent);background:var(--accent);color:var(--accent-ink)}
.btn:disabled{opacity:.55;cursor:not-allowed}
.btn.quiet{background:transparent;color:var(--accent)}
.btn:focus-visible,.link:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.link{background:none;border:0;padding:0;color:var(--accent);font:inherit;font-size:13px;
  cursor:pointer;text-decoration:underline;text-underline-offset:3px;text-align:left}
.rules{font-size:12.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
.rules b{color:var(--ink-soft);font-weight:600}
.rules ul{margin:6px 0 0;padding-left:17px} .rules li{margin:3px 0}

.toolbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.toolbar label.f{margin:0}
.toolbar .spacer{flex:1}
.drop-hint{font-size:12px;color:var(--muted)}
textarea.over{outline:2px dashed var(--accent);outline-offset:2px}
fieldset.models{border:0;padding:0;margin:0;display:flex;flex-direction:column;gap:7px}
fieldset.models legend{font-weight:600;font-size:12.5px;color:var(--ink-soft);margin-bottom:7px;padding:0}
.model-opt{display:grid;grid-template-columns:auto 1fr auto;gap:2px 9px;align-items:baseline;
  padding:9px 11px;border:1px solid var(--line-strong);border-radius:3px;cursor:pointer;background:var(--surface)}
.model-opt:has(input:checked){border-color:var(--accent);box-shadow:inset 3px 0 0 var(--accent);background:var(--accent-soft)}
.model-opt input{margin:0;grid-row:span 2;align-self:center;accent-color:var(--accent)}
.model-opt .nm{font-weight:600;font-size:13.5px;color:var(--ink)}
.model-opt .meta{font:400 11.5px "IBM Plex Mono",monospace;color:var(--muted);text-align:right;white-space:nowrap}
.model-opt .nt{font-size:12px;color:var(--muted);grid-column:2 / span 2}
.live{display:flex;align-items:center;gap:10px;margin:26px 0 4px;font-size:14px;color:var(--ink-soft)}
.live .clock{font:500 13px "IBM Plex Mono",monospace;color:var(--muted);font-variant-numeric:tabular-nums}
.sstat{font:400 12.5px "IBM Plex Mono",monospace;color:var(--muted);margin:0 0 8px}
.sstat.ok{color:var(--ok)} .sstat.bad{color:var(--bad)}
tr.new td{animation:arrive .5s ease-out}
@keyframes arrive{from{background:var(--accent-soft)}to{background:transparent}}
.notice{margin:18px 0 0;padding:12px 15px;border-radius:3px;font-size:13.5px}
.notice.bad{background:var(--bad-bg);color:var(--bad);border:1px solid var(--bad)}
.notice.warn{background:var(--warn-bg);color:var(--warn);border:1px solid var(--warn-line)}
.working{margin:26px 0;color:var(--muted);font-size:14px;display:flex;gap:10px;align-items:center}
.spin{width:14px;height:14px;border:2px solid var(--line-strong);border-top-color:var(--accent);
  border-radius:50%;animation:s .8s linear infinite}
@keyframes s{to{transform:rotate(360deg)}}

.bar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:28px 0 6px}
.bar .sum{font-size:14px;color:var(--ink-soft)} .bar .sum b{color:var(--ink)}
.bar .cost{font:400 12px "IBM Plex Mono",monospace;color:var(--muted)}
.bar .actions{margin-left:auto;display:flex;gap:9px}

.story{margin-top:26px}
.story h2{font:600 16px/1.3 "IBM Plex Sans",sans-serif;margin:0 0 8px;text-wrap:balance}
.story h2 .id{font-family:"IBM Plex Mono",monospace;font-weight:500;color:var(--muted);
  margin-right:8px;font-size:14px}
blockquote{margin:0 0 12px;padding:8px 13px;border-left:3px solid var(--line-strong);
  color:var(--ink-soft);font-size:13.5px;white-space:pre-line;max-width:80ch}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:4px;background:var(--surface)}
table{border-collapse:collapse;width:100%;min-width:1180px;font-size:13px;
  font-variant-numeric:tabular-nums}
th{position:sticky;top:0;background:var(--sunken);text-align:left;font-weight:600;font-size:11px;
  letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding:9px 11px;
  border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:10px 11px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--ink-soft)}
tr:last-child td{border-bottom:0}
tr.flag td:first-child{box-shadow:inset 3px 0 0 var(--warn)}
td.id{font:500 12.5px "IBM Plex Mono",monospace;color:var(--ink);white-space:nowrap}
td.obj{color:var(--ink);font-weight:500;min-width:170px}
td ol,td ul{margin:0;padding-left:18px} td li{margin:2px 0}
td ul.plain{list-style:none;padding:0}
code{font:400 12px "IBM Plex Mono",monospace;background:var(--sunken);padding:1px 5px;
  border-radius:2px;color:var(--ink)}
code.ph{background:transparent;border:1px dashed var(--line-strong);color:var(--muted)}
.src{display:flex;flex-direction:column;gap:4px;white-space:nowrap}
.pill{display:inline-block;font:500 11px/1 "IBM Plex Mono",monospace;padding:4px 7px;
  border-radius:2px;border:1px solid var(--line-strong);color:var(--muted)}
.pill.stated{border-color:var(--ok);color:var(--ok)}
.pill.derived{border-color:var(--accent);color:var(--accent)}
.tag{font:600 11.5px "IBM Plex Mono",monospace}
.Critical,.P1{color:var(--crit)} .High,.P2{color:var(--high)}
.Medium,.P3{color:var(--med)} .Low,.P4{color:var(--low)}
.checks{margin:10px 0 0;padding:11px 14px;background:var(--warn-bg);border:1px solid var(--warn-line);
  border-radius:3px;font-size:13px;color:var(--warn)}
.checks b{display:block;margin-bottom:4px} .checks ul{margin:0;padding-left:18px}
.checks code{background:transparent;color:inherit}
.empty{color:var(--muted);font-size:14px;padding:44px 0;text-align:center}
@media (max-width:860px){.input{grid-template-columns:1fr}.wrap{padding:0 16px 60px}
  .model{margin-left:0}}
@media (prefers-reduced-motion:reduce){.spin{animation:none} tr.new td{animation:none}}
</style></head>
<body><div class="wrap">
<header>
  <h1>Test Case Writer</h1>
  <span class="tagline">Paste user stories and get test cases, ready for review and Playwright.</span>
  <span class="model" id="model">model: …</span>
</header>

<section class="card input">
  <div>
    <div class="toolbar">
      <label class="f" for="stories">User stories</label>
      <span class="spacer"></span>
      <button class="link" id="example">Fill in the example stories</button>
      <button class="btn quiet" id="upload" style="padding:7px 12px;font-size:13px">Upload stories</button>
      <input type="file" id="file" multiple accept=".txt,.md,.docx,.xlsx,.pdf" hidden>
    </div>
    <textarea id="stories" spellcheck="false" placeholder="User Story 1 — User Login
As a registered user
I want to log in to the website using valid credentials
So that I can access the application."></textarea>
    <div class="hint">One or more stories. Start each with “As a …”. A “User Story 1 — Title” line and a “Site URL:” line are optional. You can also drop .docx, .xlsx, .pdf, .txt or .md files onto this box.</div>
    <div id="upmsg"></div>
  </div>
  <div class="side">
    <div>
      <label class="f" for="site">Site URL</label>
      <input type="url" id="site" placeholder="https://www.saucedemo.com/" spellcheck="false" autocomplete="off">
      <div class="hint">Used if the stories don't include a “Site URL:” line.</div>
    </div>
    <fieldset class="models" id="models"><legend>Model</legend></fieldset>
    <button class="btn" id="go">Write test cases</button>
    <div class="rules">
      <b>How it stays grounded</b>
      <ul>
        <li>Test data comes only from your story or your examples for the same site. Anything else is a <code class="ph">&lt;placeholder&gt;</code> to fill in.</li>
        <li>No exact error messages or URLs unless they appear in your input.</li>
        <li>Anything that breaks these rules is flagged for review.</li>
      </ul>
    </div>
  </div>
</section>

<div id="out"><div class="empty">Test cases will appear here.</div></div>
</div>
<script>
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let last=null, exampleText="", exampleSite="";

let config=null;
const store={get(k){try{return localStorage.getItem(k)}catch(e){return null}},
             set(k,v){try{localStorage.setItem(k,v)}catch(e){}}};
const chosenModel=()=>{const r=document.querySelector('input[name=model]:checked');return r?r.value:null;};
function warm(){ if(!config||!config.configured||config.preview) return;
  fetch("api/warm",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({model:chosenModel()})}).catch(()=>{}); }

fetch("api/config").then(r=>r.json()).then(c=>{
  config=c;
  exampleText=c.example_stories||""; exampleSite=c.example_site||"";
  const saved=store.get("tcgen.model");
  const pick=c.models.some(m=>m.key===saved)?saved:c.default_model;
  $("models").insertAdjacentHTML("beforeend", c.models.map(m=>
    '<label class="model-opt"><input type="radio" name="model" value="'+esc(m.key)+'"'+
    (m.key===pick?" checked":"")+'><span class="nm">'+esc(m.name)+'</span>'+
    '<span class="meta">'+esc(m.cost)+' · '+esc(m.speed)+'</span>'+
    '<span class="nt">'+esc(m.note)+'</span></label>').join(""));
  document.querySelectorAll('input[name=model]').forEach(r=>r.onchange=()=>{
    store.set("tcgen.model",r.value); $("model").textContent="model: "+c.models.find(m=>m.key===r.value).id; warm(); });
  $("model").textContent="model: "+c.models.find(m=>m.key===pick).id;
  if(c.preview){
    $("out").innerHTML='<div class="notice warn"><b>Preview — no AI is running.</b> '+
      'Writing test cases plays back your own example test cases from Sample US-TC.xlsx, '+
      'plus one deliberately invented case so you can see how the check flags it. '+
      'Real output needs an API key.</div>';
  } else if(!c.configured){
    $("out").innerHTML='<div class="notice bad">The AI model isn’t set up on this server yet. '+
      'An administrator needs to set ANTHROPIC_API_KEY.</div>';
  }
  warm();
}).catch(()=>{});

$("example").onclick=()=>{ $("stories").value=exampleText; if(!$("site").value) $("site").value=exampleSite; $("stories").focus(); };

// ---- upload -----------------------------------------------------------------
$("upload").onclick=()=>$("file").click();
$("file").onchange=e=>{ addFiles([...e.target.files]); e.target.value=""; };
const ta=$("stories");
["dragenter","dragover"].forEach(ev=>ta.addEventListener(ev,e=>{e.preventDefault();ta.classList.add("over");}));
["dragleave","drop"].forEach(ev=>ta.addEventListener(ev,e=>{e.preventDefault();ta.classList.remove("over");}));
ta.addEventListener("drop",e=>{ if(e.dataTransfer.files.length) addFiles([...e.dataTransfer.files]); });

async function addFiles(files){
  const msgs=[];
  for(const f of files){
    try{
      const b64=await new Promise((ok,bad)=>{const r=new FileReader();
        r.onload=()=>ok(String(r.result).split(",")[1]||""); r.onerror=()=>bad(r.error); r.readAsDataURL(f);});
      const res=await fetch("api/extract",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({filename:f.name,content_b64:b64})});
      const d=await res.json();
      if(!res.ok||d.error){ msgs.push('<div class="notice bad">'+esc(d.error||("Couldn’t read "+f.name))+"</div>"); continue; }
      ta.value=(ta.value.trim()?ta.value.trim()+"\n\n":"")+d.text;
      msgs.push('<div class="notice warn" style="color:var(--ink-soft);background:var(--sunken);border-color:var(--line)">'+
        esc(f.name)+": added "+d.stories_found+" "+(d.stories_found===1?"story":"stories")+
        (d.notes.length?" · "+esc(d.notes.join(" ")):"")+". Check the text, then write test cases.</div>");
    }catch(err){ msgs.push('<div class="notice bad">Couldn’t read '+esc(f.name)+".</div>"); }
  }
  $("upmsg").innerHTML=msgs.join("");
}

// ---- generate, streaming --------------------------------------------------------
let clock=null;
function startClock(){ const t0=Date.now(); const el=()=>document.querySelector(".live .clock");
  clock=setInterval(()=>{ const c=el(); if(c) c.textContent=((Date.now()-t0)/1000).toFixed(0)+"s"; },250); }
function stopClock(){ if(clock){clearInterval(clock);clock=null;} }

function liveRow(c, isNew){
  return '<tr class="'+(c.issues.length?"flag ":"")+(isNew?"new":"")+'">'+
    '<td class="id">'+esc(c.test_id)+"</td>"+
    '<td><div class="src"><span class="pill '+esc(c.derivation)+'">'+esc(c.derivation)+"</span>"+
      '<span style="font-size:12px;color:var(--muted)">'+esc(c.category)+"</span></div></td>"+
    '<td class="obj">'+esc(c.objective)+"</td>"+
    "<td>"+list(c.preconditions,false)+"</td>"+
    "<td>"+list(c.steps,true)+"</td>"+
    "<td>"+dataCell(c.test_data)+"</td>"+
    "<td>"+esc(c.expected_result)+"</td>"+
    '<td><span class="tag '+esc(c.risk)+'">'+esc(c.risk)+"</span></td>"+
    '<td><span class="tag '+esc(c.priority)+'">'+esc(c.priority)+"</span></td>"+
    "<td>"+list(c.evidence_requirements,false)+"</td>"+
    "<td>"+esc(c.status)+"</td></tr>";
}
const HEAD='<div class="tablewrap"><table><thead><tr><th>Test ID</th><th>Source</th><th>Objective</th>'+
  "<th>Preconditions</th><th>Steps</th><th>Test Data</th><th>Expected Result</th><th>Risk</th>"+
  "<th>Priority</th><th>Evidence</th><th>Status</th></tr></thead><tbody>";

function onEvent(ev){
  if(ev.type==="stories"){
    let h='<div class="live"><span class="spin"></span><span id="livemsg">Writing test cases for '+
      ev.stories.length+" "+(ev.stories.length===1?"story":"stories")+
      ' at once</span><span class="clock">0s</span></div>';
    ev.stories.forEach(s=>{
      h+='<section class="story" id="st-'+esc(s.id)+'"><h2><span class="id">'+esc(s.id)+"</span>"+esc(s.title)+"</h2>"+
        "<blockquote>"+esc(s.text)+"</blockquote>"+
        '<div class="sstat" id="ss-'+esc(s.id)+'">Writing…</div>'+
        HEAD+'</tbody></table></div></section>';
    });
    $("out").innerHTML=h;
  } else if(ev.type==="case"){
    const sec=$("st-"+ev.story_id); if(!sec) return;
    sec.querySelector("tbody").insertAdjacentHTML("beforeend", liveRow(ev.case,true));
    $("ss-"+ev.story_id).textContent="Writing… "+ev.n+" test case"+(ev.n===1?"":"s")+" so far";
  } else if(ev.type==="story_done"){
    const el=$("ss-"+ev.story_id); if(el){ el.className="sstat ok"; el.textContent="Done · "+ev.count+" test cases · "+ev.seconds+"s"; }
  } else if(ev.type==="story_error"){
    const el=$("ss-"+ev.story_id); if(el){ el.className="sstat bad"; el.textContent=ev.error; }
  } else if(ev.type==="done"){
    stopClock(); last=ev; render(ev);
  } else if(ev.type==="error"){
    stopClock(); $("out").innerHTML='<div class="notice bad">'+esc(ev.error)+"</div>";
  }
}

$("go").onclick=async()=>{
  const stories=$("stories").value.trim();
  if(!stories){ $("out").innerHTML='<div class="notice bad">Paste or upload at least one user story first.</div>'; return; }
  $("go").disabled=true;
  $("out").innerHTML='<div class="live"><span class="spin"></span><span>Starting…</span><span class="clock">0s</span></div>';
  startClock();
  try{
    const r=await fetch("api/generate/stream",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({stories, site_url:$("site").value.trim(), model:chosenModel()})});
    if(!r.ok){ const d=await r.json().catch(()=>({})); stopClock();
      $("out").innerHTML='<div class="notice bad">'+esc(d.error||("Request failed ("+r.status+")"))+"</div>"; return; }
    const reader=r.body.getReader(); const dec=new TextDecoder(); let buf="";
    for(;;){
      const {value,done}=await reader.read(); if(done) break;
      buf+=dec.decode(value,{stream:true});
      let i; while((i=buf.indexOf("\n\n"))>=0){
        const chunk=buf.slice(0,i); buf=buf.slice(i+2);
        const line=chunk.split("\n").find(l=>l.startsWith("data: "));
        if(line){ try{ onEvent(JSON.parse(line.slice(6))); }catch(e){} }
      }
    }
  }catch(e){
    $("out").innerHTML='<div class="notice bad">Couldn’t reach the server. Check your connection and try again.</div>';
  }finally{ stopClock(); $("go").disabled=false; }
};

function dataCell(items){
  if(!items.length) return "—";
  return '<ul class="plain">'+items.map(t=>{
    const ph=/^<[^<>]+>$/.test(t.value.trim());
    return "<li>"+esc(t.name)+' <code class="'+(ph?"ph":"")+'">'+esc(t.value)+"</code></li>";
  }).join("")+"</ul>";
}
function list(items, ordered){
  if(!items.length) return "—";
  const tag=ordered?"ol":"ul";
  return "<"+tag+">"+items.map(i=>"<li>"+esc(i).replace(/`([^`]+)`/g,(m,v)=>{
    const ph=/^&lt;.+&gt;$/.test(v); return '<code class="'+(ph?"ph":"")+'">'+v+"</code>";
  })+"</li>").join("")+"</"+tag+">";
}

function render(d){
  const flagged=d.cases.filter(c=>c.issues.length).length;
  const u=d.usage;
  let h='<div class="bar"><div class="sum"><b>'+d.cases.length+' test cases</b> from '+
    d.stories.length+' '+(d.stories.length===1?"story":"stories")+
    (flagged?' · <span style="color:var(--warn)">'+flagged+' to check before running</span>':"")+
    '</div><span class="cost">'+esc(u.model)+' · $'+u.cost_usd.toFixed(4)+' · '+u.seconds+'s</span>'+
    '<div class="actions"><button class="btn quiet" id="copy">Copy markdown</button>'+
    '<button class="btn" id="dl">Download .md</button></div></div>';
  (d.notes||[]).forEach(n=>{ h+='<div class="notice warn">'+esc(n)+"</div>"; });

  d.stories.forEach(s=>{
    const rows=d.cases.filter(c=>c.story_id===s.id);
    h+='<section class="story"><h2><span class="id">'+esc(s.id)+"</span>"+esc(s.title)+"</h2>";
    h+="<blockquote>"+esc(s.text)+"</blockquote>";
    if(d.errors[s.id]){ h+='<div class="notice bad">'+esc(d.errors[s.id])+"</div></section>"; return; }
    if(!rows.length){ h+='<div class="empty">No test cases for this story.</div></section>'; return; }
    h+='<div class="tablewrap"><table><thead><tr><th>Test ID</th><th>Source</th><th>Objective</th>'+
       "<th>Preconditions</th><th>Steps</th><th>Test Data</th><th>Expected Result</th><th>Risk</th>"+
       "<th>Priority</th><th>Evidence</th><th>Status</th></tr></thead><tbody>";
    rows.forEach(c=>{
      h+='<tr class="'+(c.issues.length?"flag":"")+'">'+
        '<td class="id">'+esc(c.test_id)+"</td>"+
        '<td><div class="src"><span class="pill '+esc(c.derivation)+'">'+esc(c.derivation)+"</span>"+
          '<span style="font-size:12px;color:var(--muted)">'+esc(c.category)+"</span></div></td>"+
        '<td class="obj">'+esc(c.objective)+"</td>"+
        "<td>"+list(c.preconditions,false)+"</td>"+
        "<td>"+list(c.steps,true)+"</td>"+
        "<td>"+dataCell(c.test_data)+"</td>"+
        "<td>"+esc(c.expected_result)+"</td>"+
        '<td><span class="tag '+esc(c.risk)+'">'+esc(c.risk)+"</span></td>"+
        '<td><span class="tag '+esc(c.priority)+'">'+esc(c.priority)+"</span></td>"+
        "<td>"+list(c.evidence_requirements,false)+"</td>"+
        "<td>"+esc(c.status)+"</td></tr>";
    });
    h+="</tbody></table></div>";
    const fl=rows.filter(c=>c.issues.length);
    if(fl.length){
      h+='<div class="checks"><b>Check before running</b><ul>';
      fl.forEach(c=>c.issues.forEach(i=>{
        const msg=esc(i.replace(/^(grounding|format): /,"")).replace(/`([^`]+)`/g,"<code>$1</code>");
        h+="<li>"+esc(c.test_id)+" — "+msg+"</li>";
      }));
      h+="</ul></div>";
    }
    h+="</section>";
  });
  $("out").innerHTML=h;
  $("dl").onclick=()=>{
    const stamp=new Date().toISOString().slice(0,16).replace(/[-:T]/g,"");
    const a=document.createElement("a");
    a.href=URL.createObjectURL(new Blob([last.markdown],{type:"text/markdown"}));
    a.download="test-cases-"+stamp+".md"; a.click(); URL.revokeObjectURL(a.href);
  };
  $("copy").onclick=async()=>{
    try{ await navigator.clipboard.writeText(last.markdown); $("copy").textContent="Copied"; }
    catch(e){ $("copy").textContent="Copy failed"; }
    setTimeout(()=>{ $("copy").textContent="Copy markdown"; },1800);
  };
}
</script>
</body></html>"""
