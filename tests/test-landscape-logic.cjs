// 纯 JS/DOM 模型回归，不启动浏览器，也不冒充字体测量、下载或视觉验收。
// 用法：node tests/test-landscape-logic.cjs [真实 HTML]
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const template=fs.readFileSync(path.join(__dirname,'../docker/landscape.html'),'utf8');
const script=template.match(/<script>\s*('use strict';[\s\S]*?)<\/script>/)[1];
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
class Element {
 constructor(tag){this.tag=tag;this.attrs={};this.children=[];this.events={};this.style={};this._text='';this.clientWidth=1000;}
 set textContent(text){this._text=String(text);this.children=[];}
 get textContent(){return this._text+this.children.map(n=>n.textContent).join('');}
 setAttribute(k,v){this.attrs[k]=String(v);}
 removeAttribute(k){delete this.attrs[k];}
 append(...nodes){for(let n of nodes){if(typeof n==='string'){const t=new Element('#text');t.textContent=n;n=t;}n.parentElement=this;this.children.push(n);}}
 replaceChildren(...nodes){this.children=[];this._text='';this.append(...nodes);}
 addEventListener(name,fn){this.events[name]=fn;}
 click(){if(this.events.click)this.events.click();}
 remove(){const p=this.parentElement;if(p)p.children=p.children.filter(n=>n!==this);}
 // Deterministic font-width surrogate solely to exercise wrapping branches.
 getComputedTextLength(){return [...this.textContent].length*14;}
}
function xml(n){if(n.tag==='#text')return esc(n.textContent);return `<${n.tag}${Object.entries(n.attrs).map(([k,v])=>` ${k}="${esc(v)}"`).join('')}>${esc(n._text)}${n.children.map(xml).join('')}</${n.tag}>`;}
function descendants(n){return n.children.flatMap(c=>[c,...descendants(c)]);}
function harness(data,width=1000){
 const ids={};for(const id of ['landscape-data','class-filter','class-count','bin-count','genome-size','source','checksum','chart','rows','legend','selection','tooltip','empty','csv','svg-download'])ids[id]=new Element(id==='chart'?'svg':'div');
 ids['landscape-data'].textContent=JSON.stringify(data);ids['class-filter'].value='all';
 const parent=new Element('div');parent.clientWidth=width;parent.append(ids.chart);const body=new Element('body');body.append(parent);
 const blobs=[];const context=vm.createContext({document:{body,getElementById:id=>ids[id],createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t),createTextNode:s=>{const n=new Element('#text');n.textContent=s;return n;}},window:{addEventListener(){}},URL:{createObjectURL:b=>{blobs.push(b);return 'blob:unit-model';},revokeObjectURL(){}},Blob,setTimeout(){},XMLSerializer:class{serializeToString(n){return xml(n);}}});
 vm.runInContext(script,context);return {ids,body,blobs,run:code=>vm.runInContext(code,context)};
}
const base={schema:'taffish-repeatmasker-landscape-v1',source:'report.divsum',source_sha256:'a'.repeat(64),title:'Two repeat classes',genome_size:330,classes:['DNA/hAT','Unknown/Novel'],class_bp:[140,140],bins:Array.from({length:71},(_,i)=>[i,i===0?140:0,i===0?140:0])};
const tests=[];function test(name,fn){fn();tests.push(name);}
test('native select / decorative arrow / focus / forced-colors source contract',()=>{
 assert.match(template,/<label for="class-filter">Show class<\/label><span class="select-control"><select id="class-filter">/);
 assert.match(template,/\.select-control::after\{[^}]*right:17px;top:50%;[^}]*pointer-events:none/);
 assert.match(template,/select\{[^}]*appearance:none;[^}]*padding-right:44px/);
 assert.match(template,/button,select\{[^}]*line-height:1\.375;min-height:44px/);
 assert.match(template,/select:focus-visible,[^}]*outline:3px solid var\(--accent\)/);
 assert.match(template,/@media\(forced-colors:active\)\{select\{appearance:auto;[^}]*\}\.select-control::after\{display:none\}\}/);
});
test('nice ticks / fixed filter scale / data unchanged',()=>{
 const h=harness(base);assert.deepEqual(JSON.parse(h.run('JSON.stringify(scale.ticks.map(t=>t.label))')),['0','25','50','75','100']);
 const before=h.run('JSON.stringify(D)');const bars=()=>descendants(h.ids.chart).filter(n=>n.attrs.class==='bar');
 assert.equal(bars().length,2);const height=bars()[1].attrs.height;h.ids['class-filter'].value='1';h.ids['class-filter'].events.change();
 assert.equal(bars().length,1);assert.equal(bars()[0].attrs.height,height);assert.equal(h.ids.rows.children.length,1);assert.equal(h.run('JSON.stringify(D)'),before);
 for(const event of ['pointerenter','focus','click']){bars()[0].events[event]();assert.match(h.ids.tooltip.textContent,/Unknown\/Novel.*140 bp.*42\.424242%/);}
});
for(const width of [320,390,640,900,1200,1600])test('chart model geometry width '+width,()=>{
 const h=harness(base,width);const w=Math.max(640,width);assert.equal(h.ids.chart.attrs.viewBox,`0 0 ${w} 424`);
 for(const n of descendants(h.ids.chart).filter(n=>n.attrs.class==='bar')){assert(Number(n.attrs.x)>=0);assert(Number(n.attrs.y)>=40);assert(Number(n.attrs.x)+Number(n.attrs.width)<=w);assert(Number(n.attrs.height)>0);}
 assert(!xml(h.ids.chart).includes('rotate(-90'));
});
for(const peak of [0,1e-14,0.00015,0.2,1,84.84848485,100,200,9e17])test('axis finite and distinct '+peak,()=>{
 const h=harness(base),a=JSON.parse(h.run(`JSON.stringify(axis(${peak}))`));assert(a.max>=peak&&a.max>0);assert(new Set(a.ticks.map(t=>t.label)).size===a.ticks.length);assert(a.ticks.length>=2&&a.ticks.length<=6);
});
test('zero data retains table and shows empty state',()=>{
 const d=structuredClone(base);d.bins=d.bins.map(row=>[row[0],0,0]);const h=harness(d);assert.equal(h.ids.empty.hidden,false);assert.equal(h.ids.rows.children.length,2);assert.equal(descendants(h.ids.chart).filter(n=>n.attrs.class==='bar').length,0);
});
test('extreme small nonzero percentage is not shown as zero',()=>{const h=harness(base);assert.match(h.run('displayPercent(1e-12)'),/e-12/);});
test('full SVG has title / legend / source / selection / denominator',()=>{
 const h=harness(base);const s=h.run('exportChart()'),content=s.replace(/<[^>]+>/g,'');for(const text of [base.title,...base.classes,base.source,base.source_sha256,'330 bp','not unique masked fraction'])assert(content.includes(text),text);
 assert(!s.includes('tabindex'));assert(!s.includes('-100000px'));assert.equal(h.body.children.length,1);
 h.ids['class-filter'].value='1';h.ids['class-filter'].events.change();const filtered=h.run('exportChart()');assert(filtered.includes('Unknown/Novel'));assert(!filtered.includes('DNA/hAT'));
});
test('long unicode title / class / path wraps export without omission or injection',()=>{
 const d=structuredClone(base);d.title='长标题🌱'.repeat(70);d.classes[1]='Unknown/'+('VeryLongName<&>'.repeat(24));d.source='long-input-'.repeat(40)+'.divsum';const h=harness(d,390);const s=h.run('exportChart()');
 assert((s.match(/<tspan/g)||[]).length>15);assert(Number(s.match(/height="([0-9]+)"/)[1])>700);assert(!s.includes('<&>'));assert(h.ids.legend.textContent.includes(d.classes[1]));assert(h.ids.source.textContent.endsWith(d.source));
});
test('more than eight classes use extended colors and complete rows',()=>{
 const d=structuredClone(base);d.classes=Array.from({length:24},(_,i)=>'Class/'+i);d.class_bp=d.classes.map(()=>1);d.bins=[[0,...d.class_bp]];const h=harness(d);assert.equal(h.ids.rows.children.length,24);assert.equal(new Set(Array.from({length:24},(_,i)=>h.run(`color(${i})`))).size,24);
});
(async()=>{
 const h=harness(base);h.ids['class-filter'].value='1';h.ids.csv.click();const csv=await h.blobs[0].text();const rows=csv.trim().split('\r\n');assert.equal(rows.length,143);assert(rows[1].includes('DNA/hAT'));assert(rows[2].includes('Unknown/Novel'));assert.equal(Number(rows[1].split(',')[4]),140*100/330);tests.push('CSV remains full and numerically unrounded under filter (Blob model)');
 if(process.argv[2]){const real=fs.readFileSync(process.argv[2],'utf8');const data=JSON.parse(real.match(/<script id="landscape-data" type="application\/json">(.*?)<\/script>/s)[1]);assert.equal(real.match(/<script>\s*('use strict';[\s\S]*?)<\/script>/)[1],script);assert.equal(real.match(/<style>([\s\S]*?)<\/style>/)[1],template.match(/<style>([\s\S]*?)<\/style>/)[1]);assert.match(real,/<span class="select-control"><select id="class-filter">/);const h=harness(data);assert.equal(h.ids.rows.children.length,data.classes.length);tests.push('real helper artifact embeds current CSS / native select / script / classes');}
 console.log(JSON.stringify({status:'PASS',count:tests.length,tests,boundary:'Unit DOM model only; no browser, CSS layout, actual fonts, native downloads or visual PASS.'},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
