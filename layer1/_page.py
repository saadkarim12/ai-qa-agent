PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI QA Agent</title>
<style>
:root{
  --bg:#0e1116; --panel:#161b22; --panel2:#1c232c; --line:#2a323d;
  --text:#e6edf3; --dim:#8b949e; --accent:#4c9aff;
  --crit:#f85149; --high:#f0883e; --med:#58a6ff; --low:#7d8590;
  --warn:#d29922; --ok:#3fb950;
}
*{box-sizing:border-box}
body{margin:0;font:14px/1.55 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
     background:var(--bg);color:var(--text)}
header{padding:18px 24px;border-bottom:1px solid var(--line);display:flex;
       align-items:baseline;gap:14px;flex-wrap:wrap}
header h1{margin:0;font-size:17px;font-weight:600;letter-spacing:.2px}
header .sub{color:var(--dim);font-size:12.5px}
.layout{display:grid;grid-template-columns:330px 1fr;gap:0;min-height:calc(100vh - 61px)}
.side{border-right:1px solid var(--line);padding:18px;overflow-y:auto;max-height:calc(100vh - 61px)}
.main{padding:22px 26px;overflow-y:auto;max-height:calc(100vh - 61px)}
h2{font-size:11px;text-transform:uppercase;letter-spacing:.9px;color:var(--dim);
   margin:20px 0 9px;font-weight:600}
h2:first-child{margin-top:0}
.fx{padding:8px 10px;border:1px solid transparent;border-radius:7px;cursor:pointer;margin-bottom:3px}
.fx:hover{background:var(--panel)}
.fx.on{background:var(--panel2);border-color:var(--accent)}
.fx .n{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}
.fx .d{color:var(--dim);font-size:11.5px;margin-top:2px}
button{font:inherit;background:var(--panel2);color:var(--text);border:1px solid var(--line);
       border-radius:7px;padding:9px 14px;cursor:pointer}
button:hover{border-color:var(--accent)}
button.primary{background:var(--accent);border-color:var(--accent);color:#04101f;font-weight:600;width:100%}
button.primary:disabled{opacity:.5;cursor:not-allowed}
label.row{display:flex;align-items:center;gap:9px;color:var(--dim);font-size:12.5px;margin:12px 0}
button.ghost{background:transparent;border:1px dashed var(--line);color:var(--dim);
  width:100%;font-size:12.5px;padding:7px;margin-bottom:4px}
button.ghost:hover{color:var(--text);border-color:var(--accent)}
.dl{display:flex;gap:9px;align-items:center;flex-wrap:wrap;background:var(--panel);
    border:1px solid var(--accent);border-radius:10px;padding:14px 16px;margin-bottom:18px}
.dl b{font-size:14px}
.dl a{display:inline-block;padding:8px 14px;border-radius:7px;background:var(--accent);
      color:#04101f;font-weight:600;text-decoration:none;font-size:13px}
.dl a.alt{background:var(--panel2);color:var(--text);border:1px solid var(--line);font-weight:500}
.fld{width:100%;background:var(--panel2);color:var(--text);border:1px solid var(--line);
     border-radius:7px;padding:7px 9px;font:inherit;font-size:12.5px;margin-bottom:6px}
.fld::placeholder{color:#6b7683}
.drop{border:1.5px dashed var(--line);border-radius:9px;padding:16px;text-align:center;
      color:var(--dim);font-size:12.5px;cursor:pointer}
.drop:hover,.drop.over{border-color:var(--accent);color:var(--text)}
.stats{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:18px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:10px 14px;min-width:88px}
.stat .v{font-size:20px;font-weight:600}
.stat .k{color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:.6px;margin-top:2px}
.card{background:var(--panel);border:1px solid var(--line);border-left-width:3px;
      border-radius:9px;padding:14px 16px;margin-bottom:11px}
.card.Critical{border-left-color:var(--crit)} .card.High{border-left-color:var(--high)}
.card.Medium{border-left-color:var(--med)}   .card.Low{border-left-color:var(--low)}
.card h3{margin:0 0 9px;font-size:12.5px;font-family:ui-monospace,Menlo,monospace;
         font-weight:500;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tag{font-size:10.5px;padding:2px 7px;border-radius:20px;border:1px solid var(--line);
     color:var(--dim);font-family:ui-sans-serif,sans-serif;letter-spacing:.3px}
.tag.Critical{color:var(--crit);border-color:var(--crit)}
.tag.High{color:var(--high);border-color:var(--high)}
.tag.Medium{color:var(--med);border-color:var(--med)}
.tag.Low{color:var(--low);border-color:var(--low)}
.tag.jira{color:var(--accent);border-color:var(--accent)}
.tag.llm{color:#bc8cff;border-color:#bc8cff}
.f{display:grid;grid-template-columns:86px 1fr;gap:4px 12px;font-size:13px}
.f dt{color:var(--dim);font-size:11.5px;text-transform:uppercase;letter-spacing:.5px;padding-top:2px}
.f dd{margin:0}
.flags{margin-top:10px;padding-top:9px;border-top:1px solid var(--line)}
.flag{color:var(--warn);font-size:12px;display:flex;gap:7px;margin-top:3px}
.warns{background:rgba(210,153,34,.09);border:1px solid rgba(210,153,34,.35);
       border-radius:9px;padding:12px 15px;margin-bottom:18px}
.warns .t{color:var(--warn);font-size:11px;text-transform:uppercase;letter-spacing:.8px;
          font-weight:600;margin-bottom:6px}
.warns div.w{font-size:12.5px;color:var(--dim);margin-top:3px}
.err{background:rgba(248,81,73,.09);border:1px solid rgba(248,81,73,.4);
     border-radius:9px;padding:14px 16px;color:var(--crit)}
.tabs{display:flex;gap:6px;margin-bottom:14px}
.tab{padding:6px 13px;border-radius:7px;cursor:pointer;font-size:12.5px;color:var(--dim)}
.tab.on{background:var(--panel2);color:var(--text)}
pre{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:15px;
    overflow-x:auto;font-size:12px;line-height:1.5}
.empty{color:var(--dim);text-align:center;padding:70px 20px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;color:var(--dim);font-size:10.5px;text-transform:uppercase;letter-spacing:.6px;
   padding:7px 9px;border-bottom:1px solid var(--line);font-weight:600}
td{padding:7px 9px;border-bottom:1px solid var(--line)}
tr.defer td{opacity:.45}
.P1{color:var(--crit)} .P2{color:var(--high)} .P3{color:var(--med)} .P4{color:var(--low)}
.mono{font-family:ui-monospace,Menlo,monospace}
.why{color:var(--dim);font-size:11.5px;margin-top:6px;font-family:ui-monospace,Menlo,monospace}
.steps{margin:8px 0 0;padding-left:18px;font-size:12.5px}
.steps li{margin:2px 0}
.steps .exp{color:var(--ok)}
.sec{margin:24px 0 10px;font-size:12px;text-transform:uppercase;letter-spacing:.9px;color:var(--dim);font-weight:600}
.note{color:var(--dim);font-size:12px;margin:3px 0}
.bar{height:5px;border-radius:3px;background:var(--panel2);overflow:hidden;display:flex;margin-top:5px}
.bar i{display:block;height:100%}
@media(max-width:880px){.layout{grid-template-columns:1fr}
  .side{max-height:none;border-right:none;border-bottom:1px solid var(--line)}}
</style></head><body>
<header>
  <h1>AI QA Agent</h1>
  <span class="sub">requirements document + application &rarr; QA test plan</span>
  <span class="sub" id="mode" style="margin-left:auto"></span>
</header>
<div class="layout">
  <aside class="side">
    <h2>1 &middot; Requirements document</h2>
    <div class="drop" id="drop">
      Drop a file here or click to browse<br>
      <span id="exts" style="font-size:11px"></span>
    </div>
    <input type="file" id="file" style="display:none">
    <div class="note">Or pick a sample below. Optional if you give a URL.</div>

    <h2>2 &middot; Application to test</h2>
    <input id="url" class="fld" placeholder="https://your-app.example.com"
           autocomplete="off" autocorrect="off" spellcheck="false">
    <input id="username" class="fld" placeholder="test username (if sign-in needed)"
           autocomplete="off" autocorrect="off" spellcheck="false" data-1p-ignore>
    <input id="password" class="fld" type="text" placeholder="test password"
           autocomplete="off" autocorrect="off" spellcheck="false" data-1p-ignore>
    <input id="probe" class="fld" placeholder="extra paths to try, e.g. /admin"
           autocomplete="off" spellcheck="false">
    <div class="note">Optional. Leave blank to work from the document alone.</div>
    <button id="usedemo" class="ghost">Use the bundled demo app</button>

    <h2>3 &middot; Generate</h2>
    <label class="row">Run budget
      <input type="number" id="budget" value="12" min="1" max="600" class="fld"
             style="width:64px;margin:0 0 0 6px;display:inline-block"> minutes</label>
    <label class="row"><input type="checkbox" id="llm"> Allow AI enrichment
      <span id="llmnote"></span></label>
    <button class="primary" id="run" disabled>Generate test plan</button>
    <div class="note" id="status"></div>

    <div id="list"></div>
  </aside>
  <main class="main" id="out">
    <div class="empty">Pick a fixture on the left, or drop in your own document.</div>
  </main>
</div>
<script>
let picked=null, upload=null, fixtures=[];
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function refreshRun(){
  $("run").disabled = !($("url").value.trim() || picked || upload);
}
$("url").addEventListener("input", refreshRun);
$("usedemo").onclick=()=>{
  $("url").value="http://127.0.0.1:8020";
  $("username").value="customer@example.com";
  $("password").value="Passw0rd!23";
  $("probe").value="/admin";
  refreshRun();
};
fetch("/api/fixtures").then(r=>r.json()).then(d=>{
  fixtures=d.fixtures;
  $("exts").textContent=d.supported.join("  ");
  $("mode").textContent=d.llm_configured?"LLM credentials detected":"offline mode \\u00b7 no LLM credentials";
  $("llmnote").innerHTML=d.llm_configured?"":'<span style="color:var(--dim)">(no key set)</span>';
  const groups={};
  fixtures.forEach(f=>{(groups[f.group]=groups[f.group]||[]).push(f)});
  let html="";
  for(const g in groups){
    html+="<h2>"+esc(g)+"</h2>";
    groups[g].forEach(f=>{
      html+='<div class="fx" data-rel="'+esc(f.rel)+'"><div class="n">'+esc(f.name)+
            '</div><div class="d">'+esc(f.desc)+"</div></div>";
    });
  }
  $("list").innerHTML=html;
  document.querySelectorAll(".fx").forEach(el=>el.onclick=()=>{
    document.querySelectorAll(".fx").forEach(x=>x.classList.remove("on"));
    el.classList.add("on"); picked=el.dataset.rel; upload=null; refreshRun();
  });
});

$("drop").onclick=()=>$("file").click();
$("file").onchange=e=>{ if(e.target.files[0]) take(e.target.files[0]); };
["dragover","dragleave","drop"].forEach(ev=>$("drop").addEventListener(ev,e=>{
  e.preventDefault(); $("drop").classList.toggle("over",ev==="dragover");
  if(ev==="drop"&&e.dataTransfer.files[0]) take(e.dataTransfer.files[0]);
}));
function take(f){
  const r=new FileReader();
  r.onload=()=>{ upload={filename:f.name,content_b64:r.result.split(",")[1]}; picked=null;
    document.querySelectorAll(".fx").forEach(x=>x.classList.remove("on"));
    $("drop").innerHTML="<b>"+esc(f.name)+"</b><br><span style='font-size:11px'>"+
      f.size.toLocaleString()+" bytes &middot; click to change</span>";
    refreshRun(); };
  r.readAsDataURL(f);
}

$("run").onclick=()=>{
  const body=Object.assign(
    {use_llm:$("llm").checked, budget_minutes:parseInt($("budget").value,10)||null,
     url:$("url").value.trim(), username:$("username").value.trim(),
     password:$("password").value, probe:$("probe").value.trim()},
    upload||(picked?{fixture:picked}:{}));
  const crawling=!!$("url").value.trim();
  $("run").disabled=true;
  $("status").textContent = crawling
    ? "Reading the document and exploring the application\u2026" : "Reading the document\u2026";
  $("out").innerHTML='<div class="empty">'+
    (crawling?"Exploring the application in a real browser. This takes a few seconds\u2026"
             :"Reading the document\u2026")+"</div>";
  fetch("/api/extract",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify(body)})
    .then(r=>r.json())
    .then(d=>{ $("status").textContent=""; refreshRun(); render(d); })
    .catch(e=>{ $("status").textContent=""; refreshRun();
                $("out").innerHTML='<div class="err">'+esc(e)+"</div>"; });
};

function render(d){
  if(d.error){
    $("out").innerHTML='<div class="err"><b>'+esc(d.error)+"</b>"+
      (d.trace?"<pre>"+esc(d.trace)+"</pre>":"")+"</div>"; return;
  }
  const s=d.stats, R=s.by_risk, tot=s.total||1;
  const seg=(n,c)=>n?'<i style="width:'+(n/tot*100)+'%;background:'+c+'"></i>':"";
  let h="";
  if(d.run_id){
    h+='<div class="dl"><b>Your test plan is ready &mdash; download it:</b>'+
       '<a href="/api/report?format=docx&id='+esc(d.run_id)+'">Word (.docx)</a>'+
       '<a class="alt" href="/api/report?format=html&id='+esc(d.run_id)+'" target="_blank">'+
       'HTML (print to PDF)</a>'+
       '<a class="alt" href="/api/report?format=md&id='+esc(d.run_id)+'">Markdown</a>'+
       '<span class="note" style="margin-left:auto">'+esc(d.plan_stats.total)+
       ' tests &middot; '+esc(d.plan_stats.coverage_pct)+'% coverage</span></div>';
  }
  h+='<div class="tabs"><div class="tab on" data-t="v">Requirements</div>'+
        '<div class="tab" data-t="p">Test Plan</div>'+
        (d.app_map?'<div class="tab" data-t="a">App Map</div>':"")+
        '<div class="tab" data-t="j">JSON</div></div>';
  h+='<div id="view">';
  h+='<div class="stats">'+
     stat(s.total,"requirements")+
     '<div class="stat"><div class="v">'+R.Critical+" / "+R.High+" / "+R.Medium+" / "+R.Low+
     '</div><div class="k">crit / high / med / low</div><div class="bar">'+
     seg(R.Critical,"var(--crit)")+seg(R.High,"var(--high)")+seg(R.Medium,"var(--med)")+
     seg(R.Low,"var(--low)")+"</div></div>"+
     stat(s.ambiguous,"ambiguous")+stat(s.confirmed,"confirmed")+
     stat(s.avg_confidence,"avg confidence")+
     stat(Object.entries(s.by_method||{}).map(e=>e[0]+" "+e[1]).join(", ")||"\\u2014","extracted by")+
     "</div>";
  if(d.warnings&&d.warnings.length){
    h+='<div class="warns"><div class="t">Warnings &mdash; '+d.warnings.length+"</div>"+
       d.warnings.map(w=>'<div class="w">'+esc(w)+"</div>").join("")+"</div>";
  }
  if(!d.requirements.length){
    h+='<div class="empty">No requirements extracted from <b>'+esc(d.document_name)+
       "</b>.<br>If that is unexpected, the warnings above say why.</div>";
  }
  d.requirements.forEach((r,i)=>{
    const m=(d.extraction_methods||[])[i]||"rules";
    h+='<div class="card '+esc(r.risk)+'"><h3>'+esc(r.source_ref)+
       '<span class="tag '+esc(r.risk)+'">'+esc(r.risk)+"</span>"+
       '<span class="tag '+esc(r.source)+'">'+esc(r.source)+"</span>"+
       '<span class="tag '+esc(m)+'">'+esc(m)+"</span>"+
       '<span class="tag">conf '+r.confidence.toFixed(2)+"</span></h3>"+
       '<dl class="f">'+
       row("actor",r.actor)+row("workflow",r.workflow)+
       (r.precondition?row("given",r.precondition):"")+
       row("rule",r.rule)+row("expected",r.expected_outcome)+"</dl>";
    if(r.ambiguity_flags.length){
      h+='<div class="flags">'+r.ambiguity_flags.map(f=>
         '<div class="flag"><span>&#9888;</span><span>'+esc(f)+"</span></div>").join("")+"</div>";
    }
    h+="</div>";
  });
  h+="</div>";
  h+='<div id="plan" style="display:none">'+planHtml(d)+"</div>";
  h+='<div id="appmap" style="display:none">'+mapHtml(d)+"</div>";
  h+='<pre id="json" style="display:none">'+esc(JSON.stringify(
      {requirements:d.requirements,plan:d.plan},null,2))+"</pre>";
  $("out").innerHTML=h;
  document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{
    document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on")); t.classList.add("on");
    const k=t.dataset.t;
    $("view").style.display=k==="v"?"block":"none";
    $("plan").style.display=k==="p"?"block":"none";
    $("appmap").style.display=k==="a"?"block":"none";
    $("json").style.display=k==="j"?"block":"none";
  });
}
function mapHtml(d){
  const m=d.app_map, st=d.app_stats;
  if(!m) return '<div class="empty">No application was crawled.</div>';
  let h='<div class="stats">'+stat(st.pages,"pages")+stat(st.forms,"forms")+
        stat(st.elements,"elements")+stat(st.journeys,"journeys")+
        stat(m.authenticated?"yes":"no","authenticated")+
        stat(st.blocked_actions,"blocked actions")+"</div>";

  h+='<div class="sec">Pages</div><table><tr><th>Path</th><th>Status</th><th>Forms</th>'+
     "<th>Links</th><th>Notes</th></tr>";
  m.pages.forEach(p=>{
    let note="";
    if(p.access_denied) note='<span class="P1">access denied</span>';
    else if(p.requires_auth) note='<span class="P2">sign-in required</span>';
    h+='<tr><td class="mono">'+esc(p.path)+"</td><td>"+p.status+"</td><td>"+p.forms.length+
       "</td><td>"+p.links.length+"</td><td>"+note+"</td></tr>";
  });
  h+="</table>";

  if(m.blocked_actions.length){
    h+='<div class="sec">Blocked by the Safety Governor</div>';
    m.blocked_actions.forEach(b=>{
      h+='<div class="note" style="color:var(--crit)">&times; '+esc(b)+"</div>"; });
    h+='<div class="note">These were never clicked.</div>';
  }

  if(m.journeys.length){
    h+='<div class="sec">Journey candidates</div>';
    m.journeys.forEach(j=>{
      h+='<div class="note"><b>'+esc(j.name)+'</b> &nbsp;<span class="mono">'+
         esc(j.paths.join(" \u2192 "))+"</span> &nbsp;<span style='opacity:.7'>"+
         esc(j.rationale)+" (confidence "+j.confidence+")</span></div>"; });
  }

  h+='<div class="sec">Forms and elements</div>';
  m.pages.filter(p=>p.forms.length).forEach(p=>{
    p.forms.forEach(f=>{
      h+='<div class="card"><h3>'+esc(p.path)+'<span class="tag">'+esc(f.method.toUpperCase())+
         " "+esc(f.action||p.path)+"</span></h3>";
      h+='<table><tr><th>Field</th><th>Type</th><th>Required</th><th>Preferred locator</th></tr>';
      f.fields.forEach(x=>{
        h+="<tr><td>"+esc(x.name)+'</td><td>'+esc(x.input_type||x.kind)+"</td><td>"+
           (x.required?'<span class="P1">yes</span>':"no")+'</td><td class="mono">'+
           esc((x.locators[0]||{}).value||"")+"</td></tr>"; });
      if(f.submit)
        h+='<tr><td colspan="3"><b>'+esc(f.submit.name)+"</b>"+
           (f.submit.safety==="block"?' <span class="P1">blocked: '+
            esc(f.submit.safety_reason||"")+"</span>":"")+'</td><td class="mono">'+
           esc((f.submit.locators[0]||{}).value||"")+"</td></tr>";
      h+="</table></div>";
    });
  });
  return h;
}

function planHtml(d){
  const p=d.plan, ps=d.plan_stats;
  if(!p||!ps) return '<div class="empty">No plan.</div>';
  const st=p.strategy, cv=p.coverage, ex=p.execution_plan;
  let h="";

  h+='<div class="stats">'+stat(ps.total,"test cases")+
     stat(Object.entries(ps.by_priority||{}).sort().map(e=>e[0]+" "+e[1]).join("  ")||"\u2014","priority")+
     stat(cv.coverage_pct+"%","requirement coverage")+
     stat(ps.needs_clarification,"need clarification")+
     stat(ex.selected_tests+" / "+ex.total_tests,"fit in budget")+
     stat(ps.estimated_minutes+" min","selected runtime")+"</div>";

  h+='<div class="sec">Test strategy</div>';
  h+='<div class="note">'+esc(st.scope_summary)+"</div>";
  h+='<div class="note mono">'+esc(st.scoring_formula)+"</div>";
  h+='<div class="note">Not scored yet: '+esc(st.unavailable_signals.join("; "))+"</div>";

  h+='<div class="sec">Coverage by workflow</div><table><tr><th>Workflow</th>'+
     "<th>Requirements</th><th>Tests</th><th>Covered</th></tr>";
  cv.by_workflow.forEach(w=>{ h+="<tr><td>"+esc(w.workflow)+"</td><td>"+w.requirements+
     "</td><td>"+w.tests+"</td><td>"+w.coverage_pct+"%</td></tr>"; });
  h+="</table>";
  if(cv.unclear_refs.length)
    h+='<div class="note" style="color:var(--warn)">Needs clarification: '+
       esc(cv.unclear_refs.join(", "))+"</div>";

  h+='<div class="sec">Prioritised execution plan</div><table>'+
     "<tr><th>#</th><th>Score</th><th>Pri</th><th>Test</th><th>Cum</th></tr>";
  ex.order.forEach(r=>{
    h+='<tr class="'+(r.selected?"":"defer")+'"><td class="mono">'+r.rank+
       '</td><td class="mono">'+r.score.toFixed(1)+'</td><td class="'+esc(r.priority)+'">'+
       esc(r.priority)+"</td><td>"+esc(r.title)+
       (r.selected?"":' <span class="tag">deferred</span>')+
       '</td><td class="mono">'+Math.round(r.cumulative_seconds/60)+"m</td></tr>";
  });
  h+="</table>";

  h+='<div class="sec">Test cases</div>';
  p.test_cases.forEach(t=>{
    h+='<div class="card '+esc(t.risk)+'"><h3>'+esc(t.id)+
       '<span class="tag '+esc(t.priority)+'">'+esc(t.priority)+"</span>"+
       '<span class="tag">'+esc(t.category)+"</span>"+
       '<span class="tag">score '+t.score.toFixed(1)+"</span></h3>";
    h+="<div><b>"+esc(t.title)+"</b></div>";
    h+='<div class="why">'+Object.entries(t.score_breakdown||{})
        .map(e=>esc(e[0])+" "+e[1]).join("  +  ")+"</div>";
    if(t.page_path)
      h+='<div class="note mono">page '+esc(t.page_path)+" &middot; "+esc(t.binding)+"</div>";
    h+='<ol class="steps">'+t.steps.map(s2=>"<li>"+esc(s2.action)+
        (s2.locator?' <span class="mono" style="opacity:.6">['+esc(s2.locator)+"]</span>":"")+
        (s2.expected?' <span class="exp">&rarr; '+esc(s2.expected)+"</span>":"")+"</li>").join("")+"</ol>";
    h+='<dl class="f" style="margin-top:9px">'+row("expected",t.expected_result)+
       row("traces to",t.requirement_refs.join(", "))+"</dl>";
    if(t.needs_clarification&&t.clarification_reasons.length)
      h+='<div class="flags">'+t.clarification_reasons.map(q=>
         '<div class="flag"><span>?</span><span>'+esc(q)+"</span></div>").join("")+"</div>";
    h+="</div>";
  });

  h+='<div class="sec">Test data requirements</div>';
  p.test_data.forEach(td=>{
    h+='<div class="card"><h3>'+esc(td.id)+'<span class="tag">'+esc(td.sensitivity)+
       '</span><span class="tag">'+td.used_by.length+" tests</span></h3>"+
       "<div><b>"+esc(td.name)+"</b></div>"+'<div class="note">'+esc(td.description)+"</div>"+
       '<div class="note mono">'+esc(td.fields.join(", "))+"</div></div>";
  });

  h+='<div class="sec">Limitations</div>';
  st.limitations.forEach(l=>{ h+='<div class="note">&bull; '+esc(l)+"</div>"; });
  return h;
}
const stat=(v,k)=>'<div class="stat"><div class="v">'+esc(v)+'</div><div class="k">'+k+"</div></div>";
const row=(k,v)=>"<dt>"+k+"</dt><dd>"+esc(v)+"</dd>";
</script></body></html>"""
