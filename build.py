#!/usr/bin/env python3
"""T의 일기 안내 사이트(GitHub Pages).

../docs/privacy-policy.md의 '## 한국어' · '## English' · '## Consumer Health Data Privacy Policy'를
정적 페이지로 만든다. 외부 요청 0 — 글꼴·스크립트·분석 도구 없음.

    python3 -I build.py            # values.json의 값으로 채움(없으면 {{...}}를 '확인 필요'로 칠한 미리보기)
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT.parent / "docs" / "privacy-policy.md"
VALUES = json.loads((ROOT / "values.json").read_text()) if (ROOT / "values.json").exists() else {}

def sections(md):
    out, cur = {}, None
    for line in md.split("\n"):
        if line.startswith("## "):
            cur = line[3:].strip(); out[cur] = []
        elif cur is not None:
            out[cur].append(line.rstrip())
    return out

def fill(key):
    v = VALUES.get(key)
    if v is None:
        return f'<mark class="todo">{key}</mark>'
    v = html.escape(v)
    return f'<a href="mailto:{v}">{v}</a>' if key == "EMAIL" else v

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: fill(m.group(1)), s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)

def render(lines):
    """마크다운 일부(제목 ###, 굵게, 링크, 표, 목록, 문단)만. 돌려주는 것: (h1, 본문 HTML, 목차 [(id, 제목)])"""
    out, toc, para, h1 = [], [], [], None
    i = 0
    def flush():
        if para:
            text = " ".join(para)
            cls = ' class="meta"' if re.match(r"(버전|Version|Effective) ", text) else ""
            out.append(f"<p{cls}>{inline(text)}</p>"); para.clear()
    while i < len(lines):
        l = lines[i]
        if not l.strip() or l.strip() == "---":
            flush(); i += 1; continue
        if h1 is None and re.fullmatch(r"\*\*(.+)\*\*", l.strip()):
            h1 = re.fullmatch(r"\*\*(.+)\*\*", l.strip()).group(1); i += 1; continue
        if l.startswith("### "):
            flush(); hid = f"s{len(toc) + 1}"; title = l[4:].strip(); toc.append((hid, title))
            out.append(f'<h2 id="{hid}">{inline(title)}</h2>'); i += 1; continue
        if l.startswith("|"):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells): rows.append(cells)
                i += 1
            head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'); continue
        m = re.match(r"(- |\d+\. )", l)
        if m:
            flush(); tag = "ul" if m.group(1) == "- " else "ol"; items = []
            while i < len(lines) and re.match(r"(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i])); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        para.append(l.strip()); i += 1
    flush()
    return h1, "\n".join(out), toc

CSS = """
:root{--bg:#f2f1ee;--card:#fff;--ink:#111;--muted:#6b6b6b;--line:#e3e0d8;--hl:#ffe45c;--hl-under:#ffe45c;--todo-bg:#ffd9d6;--todo-ink:#8a1c1c;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0b0b0c;--card:#1b1b1d;--ink:#f2f2f2;--muted:#9a9a9a;--line:#2a2a2b;--hl:#ffd60a;--hl-under:rgba(255,214,10,.42);--todo-bg:#5a1f1c;--todo-ink:#ffd9d6;color-scheme:dark}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.72 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR","Segoe UI",Roboto,sans-serif;word-break:keep-all;overflow-wrap:anywhere}
.wrap{max-width:760px;margin:0 auto;padding:20px max(16px,env(safe-area-inset-right)) 64px max(16px,env(safe-area-inset-left))}
header.top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:28px}
.brand{display:flex;align-items:center;gap:10px;color:inherit;text-decoration:none;font-weight:700}
.brand img{width:32px;height:32px;border-radius:8px}
nav.lang a{color:var(--muted);text-decoration:none;font-size:14px;margin-left:12px}
nav.lang a[aria-current]{color:var(--ink);font-weight:700}
h1{font-size:28px;line-height:1.35;margin:0 0 6px;letter-spacing:-.02em}
h1 span{background:linear-gradient(transparent 60%,var(--hl-under) 60%);padding:0 2px}
h2{font-size:18px;margin:40px 0 10px;letter-spacing:-.01em;scroll-margin-top:16px}
p.meta{color:var(--muted);margin-top:0}
a{color:inherit;text-decoration-color:var(--hl);text-decoration-thickness:3px;text-underline-offset:2px}
.tbl{overflow-x:auto;margin:14px 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.6}
th,td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}
tr:last-child td{border-bottom:0}
th{font-weight:700;white-space:nowrap}
ul,ol{padding-left:1.3em}
li{margin:4px 0}
details.toc{background:var(--card);border-radius:12px;padding:10px 16px;margin:20px 0 8px}
details.toc summary{cursor:pointer;font-weight:700}
details.toc ol{margin:8px 0 4px;font-size:15px}
mark.todo{background:var(--todo-bg);color:var(--todo-ink);border-radius:4px;padding:0 4px;font-weight:700;font-size:.9em}
footer{margin-top:56px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
.hero{display:flex;gap:18px;align-items:center;margin:8px 0 28px}
.hero img{width:96px;height:96px;border-radius:22px;flex:none}
.links{display:grid;gap:10px;margin:18px 0}
.links a{display:block;background:var(--card);border-radius:14px;padding:14px 16px;text-decoration:none;font-weight:700}
.links a small{display:block;font-weight:400;color:var(--muted)}
@media print{:root{--bg:#fff;--card:#fff;--ink:#111;--muted:#555;--line:#ddd;--hl:#ffe45c;--hl-under:#ffe45c;--todo-bg:#ffd9d6;--todo-ink:#8a1c1c;color-scheme:light}body{-webkit-print-color-adjust:exact;print-color-adjust:exact}details.toc{display:none}.tbl{overflow:visible}}
"""

PAGES = {  # 경로: (언어, 원본 구역, 문서 제목, 목차 이름)
    "ko/privacy": ("ko", "한국어", "T의 일기 개인정보 처리방침", "목차"),
    "en/privacy": ("en", "English", "T's Diary Privacy Policy", "Contents"),
    "en/health-data": ("en", "Consumer Health Data Privacy Policy", "T's Diary Consumer Health Data Privacy Policy", None),
}

def shell(lang, title, path, body, alt=None):
    up = "../" * path.count("/") + ("../" if path else "")
    cur = ' aria-current="page"'
    langs = "" if alt is None else "".join(
        f'<a href="{up}{p}/"{cur if p == path else ""} lang="{l}">{n}</a>' for p, l, n in alt)
    contact = fill("EMAIL")
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title><link rel="icon" href="{up}icon.png"><link rel="apple-touch-icon" href="{up}icon.png">
<style>{CSS}</style></head><body><div class="wrap">
<header class="top"><a class="brand" href="{up}"><img src="{up}icon.png" alt="">T의 일기 · T's Diary</a><nav class="lang">{langs}</nav></header>
{body}
<footer>{"문의" if lang == "ko" else "Contact"} · {contact}</footer>
</div></body></html>
"""

def main():
    md = SRC.read_text(); sec = sections(md)
    alt = [("ko/privacy", "ko", "한국어"), ("en/privacy", "en", "English")]
    for path, (lang, key, title, toc_name) in PAGES.items():
        h1, body, toc = render(sec[key])
        toc_html = "" if not toc_name else (f'<details class="toc"><summary>{toc_name}</summary><ol>'
                    + "".join(f'<li><a href="#{i}">{inline(t)}</a></li>' for i, t in toc) + "</ol></details>")
        main_html = f"<main><h1><span>{inline(h1)}</span></h1>\n" + body.replace("</p>", "</p>" + toc_html, 1) + "</main>"
        d = ROOT / path; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(shell(lang, title, path, main_html, alt if toc_name else None))
    home = """<main>
<div class="hero"><img src="icon.png" alt="T의 일기 앱 아이콘"><div><h1><span>T의 일기</span></h1><p class="meta">T's Diary · iPhone</p></div></div>
<p>그날 머문 동네, 수면·걸음·운동, 사진, 일정, 날씨가 먼저 채워진 일기 앱이에요. 기록은 이 iPhone에서 처리하고, 개발자에게 보내지 않아요.</p>
<p lang="en">A diary that starts with the facts of your day — places, sleep, steps, photos, events and weather. Everything is processed on your iPhone and never sent to us.</p>
<div class="links">
<a href="ko/privacy/">개인정보 처리방침<small>한국어</small></a>
<a href="en/privacy/" lang="en">Privacy Policy<small>English</small></a>
<a href="en/health-data/" lang="en">Consumer Health Data Privacy Policy<small>English</small></a>
</div>
<p class="meta">App Store 출시를 준비하고 있어요 · Coming soon to the App Store</p>
</main>"""
    (ROOT / "index.html").write_text(shell("ko", "T의 일기 · T's Diary", "", home))
    (ROOT / ".nojekyll").write_text("")
    print("built:", ", ".join(["index.html"] + [p + "/index.html" for p in PAGES]), "| values:", "set" if VALUES else "missing (preview)")

main()
