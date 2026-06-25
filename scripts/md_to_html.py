#!/usr/bin/env python3
"""Minimal, dependency-free Markdown to styled HTML for viewing AIOS docs.
Handles headings, bold, tables, ordered/unordered lists, blockquotes,
fenced code blocks, horizontal rules and paragraphs. Not a full spec parser,
just enough to make our roadmap/strategy docs pleasant to read in a browser.
"""
import sys, re, html, pathlib

def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text

def convert(md):
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(html.escape(lines[i]))
                i += 1
            out.append("<pre><code>" + "\n".join(block) + "</code></pre>")
            i += 1
            continue

        # horizontal rule
        if line.strip() == "---":
            out.append("<hr>")
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # table (header row then separator row of ---)
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i+1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><thead><tr>"] + [f"<th>{inline(h)}</th>" for h in header] + ["</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # blockquote (may span multiple lines)
        if line.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(inline(lines[i].lstrip(">").strip()))
                i += 1
            out.append("<blockquote>" + "<br>".join(quote) + "</blockquote>")
            continue

        # unordered list
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        # ordered list
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue

        # blank line
        if line.strip() == "":
            i += 1
            continue

        # paragraph
        out.append("<p>" + inline(line) + "</p>")
        i += 1

    return "\n".join(out)

STYLE = """
:root { --ink:#1A1A1A; --paper:#FFFFFF; --gold:#C8A227; --gold2:#E8C766; --mute:#5b5b5b; }
* { box-sizing:border-box; }
body { font-family:'Poppins','Helvetica Neue',Arial,sans-serif; color:var(--ink);
  background:#f4f2ee; margin:0; padding:48px 16px; line-height:1.6; }
.page { max-width:820px; margin:0 auto; background:var(--paper);
  padding:64px 72px; box-shadow:0 4px 30px rgba(0,0,0,.08); border-radius:4px; }
h1 { font-size:2.1rem; line-height:1.2; margin:0 0 .3em; border-bottom:3px solid var(--gold); padding-bottom:.3em; }
h2 { font-size:1.5rem; margin:2em 0 .5em; color:var(--ink); }
h2::before { content:""; display:inline-block; width:10px; height:10px; background:var(--gold);
  margin-right:10px; transform:rotate(45deg); vertical-align:middle; }
h3 { font-size:1.15rem; margin:1.6em 0 .4em; color:var(--mute); }
p { margin:.7em 0; }
strong { color:var(--ink); }
a { color:var(--gold); }
ul,ol { margin:.6em 0 1em; padding-left:1.4em; }
li { margin:.3em 0; }
hr { border:none; border-top:1px solid #e3ddd2; margin:2.4em 0; }
blockquote { background:#faf7f0; border-left:4px solid var(--gold); margin:1.2em 0;
  padding:.8em 1.2em; color:#3a3a3a; border-radius:0 4px 4px 0; }
code { background:#f0ece3; padding:.1em .4em; border-radius:3px; font-size:.9em; }
pre { background:var(--ink); color:#e8e8e8; padding:1.1em 1.3em; border-radius:6px;
  overflow-x:auto; font-size:.82rem; line-height:1.45; }
pre code { background:none; color:inherit; padding:0; }
table { border-collapse:collapse; width:100%; margin:1.2em 0; font-size:.92rem; }
th { background:var(--ink); color:var(--paper); text-align:left; padding:10px 12px; }
td { padding:10px 12px; border-bottom:1px solid #ece6da; vertical-align:top; }
tr:nth-child(even) td { background:#faf8f4; }
"""

def main():
    src = pathlib.Path(sys.argv[1])
    dst = src.with_suffix(".html")
    body = convert(src.read_text())
    title = src.stem.replace("-", " ").title()
    dst.write_text(f"<!doctype html><html><head><meta charset='utf-8'>"
                   f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
                   f"<title>{html.escape(title)}</title><style>{STYLE}</style></head>"
                   f"<body><div class='page'>{body}</div></body></html>")
    print(dst)

if __name__ == "__main__":
    main()
