// Record an Omelette standalone animation (e.g. ../splicelogic-annimations/
// splicelogic-summary-standalone.html) frame by frame as 1920x1080 PNGs, with
// the play bar hidden. Drives headless Chrome over the DevTools protocol, no
// npm deps. Used by scripts/record-splicelogic-summary.sh.
//   node scripts/record-animation.mjs <file or url> <outdir> <fps>
// Kill stray `--remote-debugging-port` Chromes first: they slow it to a crawl.
import { spawn } from 'node:child_process';
async function launch(w, h) {
  const port = 9300 + Math.floor(Math.random() * 500);
  const proc = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new', '--hide-scrollbars', `--remote-debugging-port=${port}`,
    `--window-size=${w},${h}`, '--user-data-dir=' + process.env.TMPDIR + '/cdp-prof-' + port,
    '--force-device-scale-factor=1', 'about:blank'], { stdio: 'ignore' });
  let tabs;
  for (let i = 0; i < 50; i++) {
    try { tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; }
    catch { await new Promise(r => setTimeout(r, 200)); }
  }
  const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);
  let id = 0; const pend = new Map(); const listeners = [];
  ws.onmessage = e => { const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result); }
    else listeners.forEach(f => f(m)); };
  const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
  const evaluate = async expr => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails)); return r.result.value; };
  return { send, evaluate, close: () => { ws.close(); proc.kill(); } };
}
import { writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
let [url, outdir, fpsS, only] = process.argv.slice(2);
if (!/^[a-z]+:/.test(url)) url = 'file://' + resolve(url);
const fps = +fpsS; mkdirSync(outdir, { recursive: true });
const c = await launch(1920, 1300);
await c.send('Page.enable');
await c.send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1300, deviceScaleFactor: 1, mobile: false });
await c.send('Page.navigate', { url });
await new Promise(r => setTimeout(r, 5000));
const info = await c.evaluate(`(() => {
  const st = document.createElement('style');
  st.textContent = '[data-omelette-chrome]{display:none!important} html,body{margin:0;background:#fff}';
  document.head.appendChild(st);
  // pause playback
  document.querySelector('[data-omelette-chrome] button')?.click();
  const svg = document.querySelector('[data-om-sync-seek]');
  svg.style.setProperty('transform', 'none', 'important');
  svg.style.setProperty('transform-origin', '0 0', 'important');
  svg.style.setProperty('position', 'fixed', 'important');
  svg.style.setProperty('left', '0', 'important');
  svg.style.setProperty('top', '0', 'important');
  window.__seek = t => new Promise(res => { svg.dispatchEvent(new CustomEvent('data-om-seek-to-time-frame', { detail: { time: t, sync: true } }));
    requestAnimationFrame(() => requestAnimationFrame(res)); });
  const r = svg.getBoundingClientRect();
  return { dur: +svg.getAttribute('data-om-exportable-video-with-duration-secs'), x: r.x, y: r.y, w: r.width, h: r.height };
})()`);
console.error(JSON.stringify(info));
const times = only ? only.split(',').map(Number) : Array.from({ length: Math.round(info.dur * fps) }, (_, i) => i / fps);
for (const [i, t] of times.entries()) {
  await c.evaluate(`__seek(${t})`);
  await c.evaluate(`__seek(${t})`);
  const { data } = await c.send('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 1 } });
  writeFileSync(`${outdir}/f${String(i).padStart(5, '0')}.png`, Buffer.from(data, 'base64'));
  if (i % 50 === 0) console.error(`frame ${i}/${times.length}`);
}
c.close();
