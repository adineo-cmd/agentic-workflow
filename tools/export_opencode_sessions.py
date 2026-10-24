import json, os, re, sqlite3, shutil
from datetime import datetime

DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
OUT = os.environ.get("OPENCODE_EXPORT_DIR", os.path.expanduser("~/opencode-sessions"))

def ts(ms):
    if not ms:
        return "?"
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")

def slugify(s, n=42):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return (s[:n].strip("-")) or "untitled"

def clip(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + " …[truncated]"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

sessions = con.execute("""
    SELECT id, directory, parent_id, title, time_created, time_updated,
           time_archived, idle_outcome, cost, tokens_input, tokens_output
    FROM session_v2 ORDER BY time_updated DESC
""").fetchall()

roots = [s for s in sessions if not s["parent_id"]]
children = [s for s in sessions if s["parent_id"]]

todos = {}
for r in con.execute("SELECT session_id, content, status, position FROM todo ORDER BY position"):
    todos.setdefault(r["session_id"], []).append(
        {"content": r["content"], "status": r["status"], "position": r["position"]})

events = {}
for r in con.execute(
        "SELECT session_id, type, seq, data FROM session_message ORDER BY session_id, seq"):
    try:
        data = json.loads(r["data"])
    except Exception:
        data = {}
    events.setdefault(r["session_id"], []).append(
        {"type": r["type"], "seq": r["seq"], "data": data})

def event_text(ev):
    d = ev["data"]
    if ev["type"] in ("user", "synthetic", "system", "idle"):
        return d.get("text") or ""
    if ev["type"] == "assistant":
        out = []
        for p in d.get("content", []):
            if p.get("type") == "text":
                out.append(p.get("text") or "")
        return "\n".join(out)
    return ""

def render_transcript(s, evs, fh):
    fh.write(f"# Transcript — {s['title'] or 'untitled'}\n\n")
    fh.write(f"- session: `{s['id']}`\n- directory: `{s['directory']}`\n")
    if s["parent_id"]:
        fh.write(f"- forked from: `{s['parent_id']}`\n")
    fh.write(f"- created: {ts(s['time_created'])} · last activity: {ts(s['time_updated'])}\n\n---\n\n")
    for ev in evs:
        t, d = ev["type"], ev["data"]
        if t == "assistant":
            wrote = False
            for p in d.get("content", []):
                pt = p.get("type")
                if pt == "text" and (p.get("text") or "").strip():
                    fh.write(f"## 🤖 assistant\n\n{clip(p['text'], 4000)}\n\n")
                    wrote = True
                elif pt == "tool":
                    st = p.get("state", {})
                    inp = st.get("input") or {}
                    hint = ""
                    if isinstance(inp, dict):
                        hint = inp.get("name") or inp.get("command") or inp.get("path") or ""
                        hint = clip(str(hint), 80)
                    fh.write(f"`[tool] {p.get('tool') or '?'} — {st.get('status','?')}"
                             f"{': ' + hint if hint else ''}`\n\n")
                elif pt == "patch":
                    fh.write("`[patch applied]`\n\n")
            if not wrote:
                model = (d.get("model") or {}).get("id", "")
                fh.write(f"`[assistant turn — tools/reasoning only ({model})]`\n\n")
        elif t in ("user", "synthetic"):
            txt = (d.get("text") or "").strip()
            if txt:
                who = "👤 user" if t == "user" else "· synthetic/context"
                fh.write(f"## {who}\n\n{clip(txt, 4000)}\n\n")
        elif t in ("system", "idle", "model-switched", "compaction"):
            txt = (d.get("text") or d.get("reason") or "").strip()
            if txt:
                fh.write(f"> [{t}] {clip(txt, 300)}\n\n")

def export_session(s, group):
    sid = s["id"]
    evs = events.get(sid, [])
    user_texts = [event_text(e) for e in evs if e["type"] == "user"]
    asst_idx = [i for i, e in enumerate(evs) if e["type"] == "assistant"]
    open_todos = [t for t in todos.get(sid, []) if t["status"] in ("pending", "in_progress")]

    if s["idle_outcome"] in ("failed", "interrupted"):
        status, reason = "incomplete", f"session ended: {s['idle_outcome']}"
    elif open_todos:
        status, reason = "incomplete", f"{len(open_todos)} open todo(s)"
    elif user_texts and asst_idx and asst_idx[-1] < max(
            i for i, e in enumerate(evs) if e["type"] in ("user", "synthetic")):
        status, reason = "incomplete", "last user message was never answered"
    elif not user_texts:
        status, reason = "empty", "no user messages"
    elif s["idle_outcome"] == "succeeded":
        status, reason = "likely complete", "idle outcome: succeeded"
    else:
        status, reason = "likely complete", "no failure signal"

    proj = slugify(os.path.basename(s["directory"].rstrip("/")) or "home", 24) or "home"
    date = datetime.fromtimestamp((s["time_updated"] or s["time_created"]) / 1000).strftime("%Y-%m-%d")
    folder = os.path.join(OUT, group, proj, f"{date}_{slugify(s['title'])}_{sid}")
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, "transcript.md"), "w") as fh:
        render_transcript(s, evs, fh)

    first_user = clip(user_texts[0], 600) if user_texts else "(none)"
    last_user = clip(user_texts[-1], 400) if user_texts else ""
    last_asst = ""
    for e in reversed(evs):
        if e["type"] == "assistant":
            t = event_text(e)
            if t.strip():
                last_asst = clip(t, 500)
                break
    models = sorted({((e["data"].get("model") or {}).get("id") or
                      e["data"].get("modelID") or "?") for e in evs if e["type"] == "assistant"})[:6]
    n_asst = len(asst_idx)

    with open(os.path.join(folder, "SESSION.md"), "w") as fh:
        fh.write(f"# {s['title'] or 'untitled session'}\n\n")
        fh.write(f"| field | value |\n|---|---|\n")
        fh.write(f"| status | **{status.upper()}** — {reason} |\n")
        fh.write(f"| session id | `{sid}` |\n| project dir | `{s['directory']}` |\n")
        fh.write(f"| created | {ts(s['time_created'])} |\n| last activity | {ts(s['time_updated'])} |\n")
        if s["parent_id"]:
            fh.write(f"| forked from | `{s['parent_id']}` |\n")
        fh.write(f"| messages | {len(user_texts)} user / {n_asst} assistant |\n")
        fh.write(f"| models | {', '.join(models)} |\n")
        fh.write(f"| tokens | {s['tokens_input'] + s['tokens_output']:,} |\n\n")
        if open_todos:
            fh.write("## Open todos (unfinished work)\n\n")
            for t in open_todos:
                fh.write(f"- [{'x' if t['status']=='completed' else ' '}] {t['content']}\n")
            fh.write("\n")
        fh.write("## First user request\n\n> " + first_user.replace("\n", "\n> ") + "\n\n")
        if status == "incomplete" and last_user:
            fh.write("## Last user message (where it stopped)\n\n> " + last_user.replace("\n", "\n> ") + "\n\n")
        if last_asst:
            fh.write("## Last assistant response\n\n> " + last_asst.replace("\n", "\n> ") + "\n\n")
        fh.write("Full conversation: [transcript.md](transcript.md)\n")

    return {
        "proj": proj, "group": group, "folder": os.path.relpath(folder, OUT),
        "title": s["title"] or "untitled", "date": date, "status": status, "reason": reason,
        "updated": ts(s["time_updated"]), "msgs": len(user_texts) + n_asst,
        "open": len(open_todos), "parent": s["parent_id"] or "",
    }

rows_index = [export_session(s, "") for s in roots]
children_index = [export_session(s, "_children") for s in children]

with open(os.path.join(OUT, "INDEX.md"), "w") as fh:
    fh.write("# opencode sessions — export\n\n")
    fh.write(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} from "
             "`~/.local/share/opencode/opencode.db` (v2.1.3).\n\n")
    fh.write(f"- **Your chats (root sessions — what opencode's sidebar shows): {len(rows_index)}**\n")
    fh.write(f"- Forked child sessions (created by subagents/task runs, hidden in the UI): "
             f"{len(children_index)} — kept separately under `_children/`, none are deleted chats\n\n")
    fh.write("## 🚧 Incomplete root chats — pick-up list\n\n")
    fh.write("| last activity | session | status reason | msgs | folder |\n|---|---|---|---|---|\n")
    for r in sorted([r for r in rows_index if r["status"] == "incomplete"],
                    key=lambda r: r["updated"], reverse=True):
        fh.write(f"| {r['updated']} | {clip(r['title'],60)} | {r['reason']} | {r['msgs']} "
                 f"| [{r['folder'].split('/')[-1]}]({r['folder']}/SESSION.md) |\n")
    for proj in sorted({r["proj"] for r in rows_index}):
        sub = [r for r in rows_index if r["proj"] == proj]
        fh.write(f"\n## project: {proj} ({len(sub)} chats)\n\n")
        fh.write("| last activity | session | status | msgs | folder |\n|---|---|---|---|\n")
        for r in sorted(sub, key=lambda r: r["updated"], reverse=True):
            fh.write(f"| {r['updated']} | {clip(r['title'],60)} | {r['status']} | {r['msgs']} "
                     f"| [{r['folder'].split('/')[-1]}]({r['folder']}/SESSION.md) |\n")
    fh.write(f"\n## Forked child sessions ({len(children_index)}, hidden in opencode UI)\n\n")
    fh.write("| last activity | session | status | parent | folder |\n|---|---|---|---|---|\n")
    for r in sorted(children_index, key=lambda r: r["updated"], reverse=True):
        fh.write(f"| {r['updated']} | {clip(r['title'],50)} | {r['status']} | `{r['parent'][:20]}…` "
                 f"| [{r['folder'].split('/')[-1]}]({r['folder']}/SESSION.md) |\n")

stats = {}
for r in rows_index:
    stats[r["status"]] = stats.get(r["status"], 0) + 1
print(f"root chats: {len(rows_index)} {stats}")
print(f"forked children: {len(children_index)}")
print(f"output: {OUT}")
