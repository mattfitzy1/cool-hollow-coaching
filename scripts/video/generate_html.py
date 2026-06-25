#!/usr/bin/env python3
"""Generate the kinetic-typography animation HTML from timeline.json.
Deterministic: exposes window.seek(ms) and window.TOTAL for frame capture."""
import json, os

ROOT = "/Users/matthewfitzpatrick-buck/Desktop/matthew-fitzpatrick-aios-main"
DIR = os.path.join(ROOT, "outputs/videos/cool-hollow-brand")
tl = json.load(open(os.path.join(DIR, "timeline.json")))

HTML = """<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:1920px; height:1080px; overflow:hidden; background:#141210; }
  :root { --ink:#141210; --paper:#FFFFFF; --gold:#C8A227; --gold2:#E8C766; --mute:#9a948a; }
  #stage { position:relative; width:1920px; height:1080px;
    font-family:'Poppins','Helvetica Neue',Arial,sans-serif; color:var(--paper);
    background:#141210; overflow:hidden; }
  #glow { position:absolute; inset:-20%; background:radial-gradient(circle at 50% 40%,
    rgba(200,162,39,.16), rgba(200,162,39,0) 42%); }
  #vignette { position:absolute; inset:0; background:radial-gradient(ellipse at center,
    rgba(0,0,0,0) 52%, rgba(0,0,0,.55) 100%); pointer-events:none; }
  .wordmark { position:absolute; top:54px; left:64px; font-size:22px; font-weight:700;
    letter-spacing:.32em; color:var(--gold); opacity:.85; }
  .wordmark .dot { color:var(--mute); }
  .beat { position:absolute; inset:0; display:flex; flex-direction:column;
    align-items:center; justify-content:center; text-align:center; opacity:0;
    will-change:opacity,transform; padding:0 180px; }
  .kicker { font-size:30px; font-weight:700; letter-spacing:.30em; text-transform:uppercase;
    color:var(--gold); margin-bottom:38px; }
  .line { font-weight:700; font-size:118px; line-height:1.04; letter-spacing:-.01em; }
  .line.small { font-size:96px; }
  .num { color:var(--gold); font-weight:800; font-size:210px; letter-spacing:-.02em; }
  .accent { height:6px; width:0; background:var(--gold); margin:46px 0 0; border-radius:3px; }
  .sub { margin-top:40px; font-size:40px; font-weight:400; color:var(--mute);
    letter-spacing:.01em; }
  .brand .line { font-size:104px; font-weight:800; letter-spacing:.04em; color:var(--paper); }
  .brand .sub { color:var(--gold2); font-size:46px; font-weight:600; letter-spacing:.16em;
    text-transform:uppercase; margin-top:30px; }
  .brand .accent { background:linear-gradient(90deg,var(--gold),var(--gold2)); }
  #bar { position:absolute; left:0; bottom:0; height:5px; width:0; background:var(--gold); opacity:.9; }
</style></head>
<body><div id="stage">
  <div id="glow"></div>
  <div id="vignette"></div>
  <div class="wordmark" id="wm">COOL HOLLOW <span class="dot">/</span> COACHING</div>
  <div id="beats"></div>
  <div id="bar"></div>
</div>
<script>
const TIMELINE = __TIMELINE__;
window.TOTAL = TIMELINE.total_ms;
const beatsEl = document.getElementById('beats');
const IN_LEAD = 250, FADE = 520, OUT = 460;

// build beat DOM
TIMELINE.beats.forEach((b, i) => {
  const d = document.createElement('div');
  d.className = 'beat' + (b.brand ? ' brand' : '');
  if (b.kicker) { const k = document.createElement('div'); k.className='kicker'; k.textContent=b.kicker; d.appendChild(k); }
  const isNum = b.line.trim().startsWith('$');
  const l1 = document.createElement('div');
  l1.className = 'line' + (isNum ? '' : (b.line.length > 22 ? ' small' : ''));
  if (isNum) { l1.innerHTML = '<span class="num">' + b.line + '</span>'; }
  else { l1.textContent = b.line; }
  d.appendChild(l1);
  if (b.line2) { const l2 = document.createElement('div'); l2.className='line'+(b.line2.length>22?' small':''); l2.textContent=b.line2; d.appendChild(l2); }
  const ac = document.createElement('div'); ac.className='accent'; d.appendChild(ac);
  if (b.sub) { const s=document.createElement('div'); s.className='sub'; s.textContent=b.sub; d.appendChild(s); }
  d._accent = ac;
  beatsEl.appendChild(d);
  b._el = d;
});

function easeOut(x){ return 1 - Math.pow(1 - x, 3); }
function clamp(x){ return Math.max(0, Math.min(1, x)); }

window.seek = function(ms){
  // background drift + progress
  const p = clamp(ms / window.TOTAL);
  document.getElementById('bar').style.width = (p*1920) + 'px';
  const gx = 50 + 8*Math.sin(ms/9000), gy = 40 + 6*Math.cos(ms/11000);
  document.getElementById('glow').style.background =
    'radial-gradient(circle at '+gx+'% '+gy+'%, rgba(200,162,39,.16), rgba(200,162,39,0) 42%)';

  TIMELINE.beats.forEach((b, i) => {
    const inAt = b.start_ms - IN_LEAD;
    const next = TIMELINE.beats[i+1];
    const outAt = next ? (next.start_ms - IN_LEAD) : window.TOTAL;
    let op = 0, ty = 28, scale = 1;
    if (ms >= inAt && ms < outAt) {
      const fin = clamp((ms - inAt) / FADE);
      const fout = clamp((outAt - ms) / OUT);
      const e = easeOut(fin);
      op = Math.min(easeOut(fin), easeOut(fout));
      ty = 28 * (1 - e);
      scale = b.brand ? (0.96 + 0.04*e) : 1;
      // accent draw
      const aw = clamp((ms - (inAt+FADE*0.5)) / 620);
      const maxw = b.brand ? 360 : 230;
      b._el._accent.style.width = (easeOut(aw)*maxw) + 'px';
    }
    b._el.style.opacity = op;
    b._el.style.transform = 'translateY('+ty+'px) scale('+scale+')';
  });

  // hide wordmark on the final brand beat
  const last = TIMELINE.beats[TIMELINE.beats.length-1];
  document.getElementById('wm').style.opacity = (ms >= last.start_ms - IN_LEAD) ? 0 : 0.85;
};

window.seek(0);
window.__READY = true;
</script></body></html>"""

out = HTML.replace("__TIMELINE__", json.dumps(tl))
open(os.path.join(DIR, "brand-explainer.html"), "w").write(out)
print("wrote brand-explainer.html  (TOTAL", tl["total_ms"], "ms )")
