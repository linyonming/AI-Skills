#!/usr/bin/env python3
"""Render a self-contained potential stock screener dashboard.
Pure HTML/CSS/SVG/vanilla JS, no CDN.
"""
import argparse, html, json, math
from pathlib import Path


def e(x): return html.escape('' if x is None else str(x))
def arr(x): return x if isinstance(x, list) else []
def num(x, default=0):
    try:
        if x is None or x == '': return default
        v=float(str(x).replace('%','').replace(',',''))
        return default if math.isnan(v) or math.isinf(v) else v
    except Exception: return default

def color(score):
    s=num(score)
    if s>=7.5: return '#10b981','green'
    if s>=6: return '#2563eb','blue'
    if s>=4.5: return '#f59e0b','orange'
    return '#ef4444','red'

def ring(score, size=132, label='综合分'):
    s=max(0,min(10,num(score)))
    c,name=color(s); stroke=12; r=(size-stroke)/2; circ=2*math.pi*r; dash=circ*s/10; mid=size/2
    return f'''<svg class="ring ring-{name}" viewBox="0 0 {size} {size}" aria-label="{e(label)} {s:.1f}">
<defs><linearGradient id="rg-{name}-{size}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#67e8f9"/><stop offset=".55" stop-color="{c}"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>
<circle cx="{mid}" cy="{mid}" r="{r}" fill="none" stroke="rgba(255,255,255,.2)" stroke-width="{stroke}"/>
<circle class="ring-fg" cx="{mid}" cy="{mid}" r="{r}" fill="none" stroke="url(#rg-{name}-{size})" stroke-width="{stroke}" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {mid} {mid})"/>
<text x="50%" y="47%" text-anchor="middle" class="ring-score">{s:.1f}</text><text x="50%" y="64%" text-anchor="middle" class="ring-label">/10</text></svg>'''

def mini_ring(score):
    s=max(0,min(10,num(score))); c,_=color(s); size=54; stroke=6; r=(size-stroke)/2; circ=2*math.pi*r; dash=circ*s/10
    return f'<svg class="mini-ring" viewBox="0 0 {size} {size}"><circle cx="27" cy="27" r="{r}" fill="none" stroke="#e8eef8" stroke-width="{stroke}"/><circle cx="27" cy="27" r="{r}" fill="none" stroke="{c}" stroke-width="{stroke}" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 27 27)"/><text x="27" y="32" text-anchor="middle">{s:.1f}</text></svg>'

def css():
    return r'''
:root{--ink:#11213d;--muted:#64748b;--line:#dfe8f5;--card:rgba(255,255,255,.78);--green:#10b981;--red:#ef4444;--blue:#2563eb;--cyan:#06b6d4;--orange:#f59e0b;--purple:#8b5cf6;--shadow:0 18px 42px rgba(30,56,96,.10)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Arial,sans-serif;background:radial-gradient(circle at 8% 0,rgba(34,211,238,.18),transparent 28%),radial-gradient(circle at 92% 4%,rgba(139,92,246,.16),transparent 25%),linear-gradient(180deg,#edf5ff,#f7fbff 55%,#fff)}body:before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:linear-gradient(rgba(15,23,42,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(15,23,42,.045) 1px,transparent 1px),radial-gradient(circle,rgba(37,99,235,.11) 1px,transparent 1.4px);background-size:42px 42px,42px 42px,18px 18px}.page{max-width:1220px;margin:0 auto;padding:18px}.nav{position:sticky;top:0;z-index:20;margin:0 -8px 14px;padding:9px 10px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;background:rgba(241,247,255,.72);border:1px solid rgba(223,232,245,.7);border-radius:0 0 22px 22px;backdrop-filter:blur(16px);box-shadow:0 12px 34px rgba(15,23,42,.08)}.nav::-webkit-scrollbar{display:none}.nav a{white-space:nowrap;text-decoration:none;color:#1e3a8a;background:rgba(255,255,255,.75);border:1px solid rgba(203,213,225,.76);border-radius:999px;padding:8px 12px;font-size:12px;font-weight:900;transition:.22s}.nav a.active,.nav a:hover{color:white;background:linear-gradient(135deg,#2563eb,#06b6d4);border-color:transparent}.hero{position:relative;overflow:hidden;border-radius:32px;padding:30px;color:white;background:radial-gradient(circle at 76% -10%,rgba(34,211,238,.54),transparent 34%),radial-gradient(circle at 100% 72%,rgba(168,85,247,.38),transparent 30%),linear-gradient(135deg,#061327 0,#0b2a59 44%,#0f766e 74%,#3b1d74 100%);box-shadow:0 28px 70px rgba(15,35,80,.30)}.hero:before{content:"";position:absolute;inset:0;opacity:.2;background-image:radial-gradient(circle,rgba(255,255,255,.55) .7px,transparent .8px);background-size:8px 8px}.top{position:relative;display:flex;justify-content:space-between;gap:24px;align-items:center}.eyebrow{display:inline-flex;gap:8px;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.20);font-size:12px;font-weight:900}h1{font-size:43px;line-height:1.05;margin:12px 0 8px;letter-spacing:-.05em}.sub{opacity:.88;font-weight:650}.verdict{font-size:21px;font-weight:1000;margin-top:14px;max-width:820px;line-height:1.45;color:#f8fdff;text-shadow:0 0 18px rgba(103,232,249,.42),0 2px 12px rgba(0,0,0,.28)}.badges{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}.badge{padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.24);backdrop-filter:blur(14px);font-weight:950}.ring{width:132px;height:132px;overflow:visible}.ring-score{font-size:31px;font-weight:1000;fill:#fff}.ring-label{font-size:12px;font-weight:800;fill:rgba(255,255,255,.76)}.ring-fg{animation:ringDraw 1.1s ease both}.section{margin-top:20px}.grid{display:grid;gap:14px}.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}.card,.tile,.candidate,.risk-card,.source,.gloss{background:var(--card);border:1px solid rgba(223,232,245,.9);border-radius:22px;box-shadow:var(--shadow);backdrop-filter:blur(15px);animation:fadeInUp .55s ease both;transition:.22s;overflow:hidden;position:relative}.card:hover,.tile:hover,.candidate:hover{transform:translateY(-3px);box-shadow:0 22px 52px rgba(30,56,96,.15)}.card{padding:16px}.card:before,.tile:before,.candidate:before{content:"";position:absolute;inset:0 0 auto 0;height:3px;background:linear-gradient(90deg,#2563eb,#06b6d4)}.good:before{background:linear-gradient(90deg,#10b981,#67e8f9)}.warn:before{background:linear-gradient(90deg,#f59e0b,#facc15)}.bad:before{background:linear-gradient(90deg,#ef4444,#f97316)}h2{font-size:21px;margin:0 0 12px}.section-title{display:flex;align-items:center;justify-content:space-between;gap:12px}.section-title small{color:#64748b;font-weight:800}.top3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.candidate{padding:16px}.candidate .rank{position:absolute;right:14px;top:12px;font-size:34px;font-weight:1000;color:rgba(37,99,235,.13)}.candidate h3{margin:2px 0 5px;font-size:21px}.candidate .code{color:#64748b;font-size:12px;font-weight:800}.candidate .score{display:inline-flex;align-items:center;gap:6px;margin:10px 0;padding:6px 10px;border-radius:99px;background:#eef4ff;color:#1d4ed8;font-weight:1000}.mini-line{display:flex;gap:9px;padding:9px 10px;border-radius:14px;background:rgba(246,249,253,.82);margin:7px 0;font-size:13px;line-height:1.48}.mini-line span{width:7px;height:7px;border-radius:50%;background:#06b6d4;margin-top:6px;box-shadow:0 0 0 4px rgba(6,182,212,.11)}.funnel{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.funnel-step{padding:15px;border-radius:20px;background:linear-gradient(180deg,#fff,#f7fbff);border:1px solid #dfe8f5;box-shadow:0 10px 24px rgba(30,56,96,.07);position:relative}.funnel-step:not(:last-child):after{content:"→";position:absolute;right:-12px;top:40%;font-size:24px;color:#94a3b8;font-weight:1000}.funnel-step b{display:block;font-size:26px}.funnel-step span{font-size:13px;color:#64748b}.table-wrap{overflow-x:auto;border-radius:18px}.table{width:100%;min-width:1050px;border-collapse:separate;border-spacing:0;background:rgba(255,255,255,.82);border:1px solid #dfe8f5;border-radius:18px;overflow:hidden;font-size:12px;box-shadow:0 10px 24px rgba(30,56,96,.06)}.table th{background:linear-gradient(180deg,#eff6ff,#eaf3ff);text-align:left;padding:11px;color:#334155}.table td{padding:11px;border-top:1px solid #e8eef7;vertical-align:top}.table tr.top-row td{background:linear-gradient(90deg,#ecfeff,#f0f9ff)}.pill{display:inline-block;padding:5px 8px;border-radius:99px;font-size:11px;font-weight:950;background:#eef4ff;color:#315fc2}.pill.green{background:#dcfce7;color:#166534}.pill.orange{background:#fef3c7;color:#92400e}.pill.red{background:#fee2e2;color:#991b1b}.factor{display:grid;grid-template-columns:1fr 58px;gap:12px;align-items:center;padding:12px;border-radius:18px;border:1px solid #e2e8f0;background:rgba(255,255,255,.68);margin:9px 0}.factor b{display:block}.factor span{font-size:12px;color:#64748b}.mini-ring text{font-size:13px;font-weight:1000;fill:#172554}.matrix{height:360px;position:relative;border-radius:22px;background:linear-gradient(180deg,#fff,#f8fbff);border:1px solid #dfe8f5;overflow:hidden}.matrix:before{content:"";position:absolute;left:50%;top:0;bottom:0;border-left:1px dashed #cbd5e1}.matrix:after{content:"";position:absolute;top:50%;left:0;right:0;border-top:1px dashed #cbd5e1}.dot{position:absolute;transform:translate(-50%,-50%);width:var(--s);height:var(--s);border-radius:50%;background:linear-gradient(135deg,#2563eb,#06b6d4);box-shadow:0 12px 24px rgba(37,99,235,.25);display:grid;place-items:center;color:white;font-size:10px;font-weight:1000;border:2px solid white}.axis{position:absolute;color:#64748b;font-size:12px;font-weight:800}.risk-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.risk-card{padding:15px;min-height:122px}.risk-card.high{color:#7f1d1d;background:linear-gradient(135deg,#fff1f2,#fee2e2);border-color:#fca5a5;animation:riskPulse 2.4s infinite}.risk-card.mid{color:#7c2d12;background:linear-gradient(135deg,#fff7ed,#fef3c7);border-color:#fdba74}.risk-card.low{color:#14532d;background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#86efac}.risk-card strong{display:block;margin:6px 0}.risk-card span,.risk-card small{display:block;font-size:12px;line-height:1.45}.source,.gloss{padding:13px}.source b,.gloss b{display:block}.source span,.gloss span,.source small{display:block;color:#64748b;font-size:12px;margin-top:4px;line-height:1.45}.footer{font-size:12px;color:#738096;margin:20px 0 6px;line-height:1.7}@keyframes fadeInUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}@keyframes ringDraw{from{stroke-dashoffset:420;opacity:.35}to{stroke-dashoffset:0;opacity:1}}@keyframes riskPulse{0%,100%{box-shadow:0 12px 28px rgba(239,68,68,.12)}50%{box-shadow:0 12px 34px rgba(239,68,68,.28)}}@media(max-width:900px){.top3,.g4,.g3,.funnel{grid-template-columns:repeat(2,1fr)}.g2{grid-template-columns:1fr}.risk-grid{grid-template-columns:1fr 1fr}}@media(max-width:720px){.page{padding:10px}.top{display:block}h1{font-size:32px}.hero{padding:23px;border-radius:25px}.verdict{font-size:18px}.ring{margin-top:16px}.top3,.g4,.g3,.funnel,.risk-grid{grid-template-columns:1fr}.funnel-step:after{display:none}.matrix{height:300px}}
'''

def js():
    return '''(()=>{const links=[...document.querySelectorAll('.nav a')];const by={};links.forEach(a=>{const id=a.getAttribute('href')?.slice(1);if(id)by[id]=a});const io=new IntersectionObserver(es=>{es.forEach(en=>{if(en.isIntersecting){links.forEach(a=>a.classList.remove('active'));let a=by[en.target.id];if(a){a.classList.add('active');a.scrollIntoView({inline:'center',block:'nearest',behavior:'smooth'});}}})},{rootMargin:'-42% 0px -52% 0px'});document.querySelectorAll('section[id]').forEach(s=>io.observe(s));})();'''

def lines(items, maxn=3):
    out=''
    for x in arr(items)[:maxn]: out += f'<div class="mini-line"><span></span><b>{e(x)}</b></div>'
    return out or '<div class="mini-line"><span></span><b>待补充</b></div>'

def top3_html(items):
    out=''
    for i,c in enumerate(arr(items)[:3],1):
        out += f'''<div class="candidate good"><div class="rank">#{i}</div><div class="code">{e(c.get('code'))} · {e(c.get('industry'))}</div><h3>{e(c.get('name'))}</h3><span class="score">综合分 {e(c.get('score'))}</span><p><b>入选：</b>{e(c.get('reason'))}</p><p><b>触发：</b>{e(c.get('trigger'))}</p><p><b>风险：</b>{e(c.get('risk'))}</p></div>'''
    return out or '<div class="card">暂无 Top3</div>'

def funnel_html(items):
    return ''.join(f'<div class="funnel-step"><b>{e(x.get("count"))}</b><strong>{e(x.get("stage"))}</strong><span>{e(x.get("note"))}</span></div>' for x in arr(items))

def table_html(rows):
    body=''
    for r in arr(rows):
        cls=' class="top-row"' if num(r.get('rank'))<=3 else ''
        body += f'''<tr{cls}><td><b>#{e(r.get('rank'))} {e(r.get('name'))}</b><br><span>{e(r.get('code'))}</span></td><td>{e(r.get('price'))}</td><td><b>{e(r.get('score'))}</b><br><span class="pill green">{e(r.get('style'))}</span></td><td>{e(r.get('industry'))}</td><td>{e(r.get('reason'))}</td><td>{e(r.get('trigger'))}</td><td>{e(r.get('risk'))}</td><td>{e(r.get('invalid'))}</td></tr>'''
    return f'<div class="table-wrap"><table class="table"><thead><tr><th>排名/股票</th><th>价格</th><th>分数/风格</th><th>行业</th><th>入选理由</th><th>触发条件</th><th>风险</th><th>失效</th></tr></thead><tbody>{body}</tbody></table></div>'

def factors_html(items):
    out=''
    for f in arr(items): out += f'<div class="factor"><div><b>{e(f.get("name"))}</b><span>{e(f.get("note"))}</span></div>{mini_ring(f.get("score"))}</div>'
    return out

def matrix_html(items):
    out='<div class="matrix"><span class="axis" style="left:12px;top:10px">成长/弹性 ↑</span><span class="axis" style="right:12px;bottom:10px">估值性价比 →</span>'
    for x in arr(items):
        xp=max(6,min(94,num(x.get('x'),5)*10)); yp=100-max(8,min(92,num(x.get('y'),5)*10)); sz=max(28,min(56,22+num(x.get('score'),5)*3))
        out += f'<div class="dot" style="left:{xp:.1f}%;top:{yp:.1f}%;--s:{sz:.0f}px" title="{e(x.get("name"))}">{e(str(x.get("name",""))[:2])}</div>'
    return out+'</div>'

def risks_html(items):
    out=''
    for r in arr(items):
        lv=str(r.get('level') or '中'); cls='high' if lv in ['高','极高','high'] else ('low' if lv in ['低','low'] else 'mid')
        icon='✕' if cls=='high' else ('✓' if cls=='low' else '!')
        out += f'<div class="risk-card {cls}"><b>{icon}</b><strong>{e(lv)}风险</strong><span>{e(r.get("text"))}</span><small>{e(r.get("mitigation"))}</small></div>'
    return out

def source_html(items):
    return ''.join(f'<div class="source"><b>{e(x.get("name"))}</b><span>{e(x.get("source"))}</span><small>{e(x.get("status"))}</small></div>' for x in arr(items))

def render(d):
    top3=arr(d.get('top3')) or arr(d.get('top10'))[:3]
    avg=sum(num(x.get('score')) for x in top3)/(len(top3) or 1)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(d.get('title'))}</title><style>{css()}</style></head><body><div class="page">
<nav class="nav"><a href="#overview" class="active">总览</a><a href="#funnel">漏斗</a><a href="#top">榜单</a><a href="#matrix">机会地图</a><a href="#deep">深挖</a><a href="#risk">风险</a><a href="#track">跟踪</a><a href="#source">数据</a></nav>
<section class="hero" id="overview"><div class="top"><div><div class="eyebrow">Potential Stock Screener · {e(d.get('date'))}</div><h1>{e(d.get('title'))}</h1><div class="sub">{e(d.get('market'))} · {e(d.get('theme'))} · {e(d.get('universe'))}</div><div class="verdict">{e(d.get('verdict'))}</div><div class="badges"><span class="badge">机会等级：{e(d.get('opportunity_level'))}</span><span class="badge">风险等级：{e(d.get('risk_level'))}</span><span class="badge">Top3均分：{avg:.1f}/10</span></div></div>{ring(avg,132,'Top3均分')}</div></section>
<section class="section" id="top"><div class="section-title"><h2>🏆 核心观察 Top 3</h2><small>首屏先看最值得跟踪的候选</small></div><div class="top3">{top3_html(top3)}</div></section>
<section class="section card" id="funnel"><h2>🔎 筛选漏斗</h2><div class="funnel">{funnel_html(d.get('funnel'))}</div></section>
<section class="section card"><h2>📋 Top 10 潜力榜</h2>{table_html(d.get('top10'))}</section>
<section class="section grid g2" id="matrix"><div class="card"><h2>🧭 机会地图</h2>{matrix_html(d.get('matrix') or d.get('top10'))}</div><div class="card"><h2>📊 因子概览</h2>{factors_html(d.get('factor_summary'))}</div></section>
<section class="section grid g3" id="deep"><div class="card good"><h2>🚀 重点逻辑</h2>{lines([x.get('reason') for x in top3],3)}</div><div class="card warn"><h2>📈 触发条件</h2>{lines([x.get('trigger') for x in top3],3)}</div><div class="card bad"><h2>🔴 失效条件</h2>{lines([x.get('invalid') for x in top3],3)}</div></section>
<section class="section" id="risk"><div class="section-title"><h2>⚠️ 风险热力图</h2><small>高风险优先看</small></div><div class="risk-grid">{risks_html(d.get('risk_heatmap'))}</div></section>
<section class="section grid g2"><div class="card"><h2>🧹 剔除名单</h2>{table_html(d.get('excluded'))}</div><div class="card" id="track"><h2>🎯 跟踪计划</h2>{lines(d.get('tracking_plan'),8)}</div></section>
<section class="section grid g2" id="source"><div><h2>🧾 数据可信度</h2><div class="grid g3">{source_html(d.get('data_sources'))}</div></div><div><h2>🕳️ 盲区与术语</h2>{lines(d.get('blind_spots'),5)}<div class="grid g2">{''.join(f'<div class="gloss"><b>{e(x.get("term"))}</b><span>{e(x.get("desc"))}</span></div>' for x in arr(d.get('glossary')))}</div></div></section>
<div class="footer">免责声明：本看板基于公开信息与聚合数据筛选，仅作研究参考，不构成投资建议；候选股为观察池，不代表确定买入或收益承诺。</div>
</div><script>{js()}</script></body></html>'''

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--out-html','--out',dest='out_html',required=True)
    a=ap.parse_args(); d=json.load(open(a.input,encoding='utf-8')); Path(a.out_html).write_text(render(d),encoding='utf-8'); print(json.dumps({'html':a.out_html},ensure_ascii=False))
if __name__=='__main__': main()
