#!/usr/bin/env python3
"""Regenerate the #activity analytics section in index.html.

Every number is derived from this repo's git history — nothing is hand-typed.
Run it from anywhere after new work lands to refresh the funnel, the timeline
and the insights:

    python3 tools/build_activity.py

It rewrites only the block between the "activity analytics" comment markers,
so personal card blocks are never touched. Safe to run repeatedly.

If someone new starts committing, add their email to E2S below so their work is
attributed to the right tile; unmapped emails are ignored.
"""
import json, re, subprocess, collections, datetime as dt

import os
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=REPO).stdout

# ── identity: who made a commit = the GitHub login the API reports for it ──
# (the cards are keyed by GitHub username, so no email map is needed; the map
# below is a fallback for commits the API cannot attribute)
def _sha2login():
    try:
        out = sh("gh api --paginate 'repos/mody-sahariar1/vv-wall/commits?per_page=100' --jq '.[] | [.sha, (.author.login // \"\")] | @tsv'")
        return {l.split('\t')[0]: l.split('\t')[1] for l in out.strip().split('\n') if '\t' in l and l.split('\t')[1]}
    except Exception:
        return {}
SHA2LOGIN = _sha2login()
MAINTAINER = "mody-sahariar1"
def who(h, ae):
    return SHA2LOGIN.get(h) or E2S.get((ae or "").lower())
E2S_OLD = {
 "modi.sahil.im@gmail.com":"sahilmodi1965","163586523+sahilmodi1965@users.noreply.github.com":"sahilmodi1965",
 "sushant@mantra4change.com":"sushantM4C","nishant.kumar@mantra4change.com":"nishantkumar-m4c",
 "deepthi@mantra4change.com":"Deepthi-jb","rafi@mantra4change.com":"rafimantra",
 "pratikjain@pratiks-macbook-air.local":"pratikjain-SG","pratik.jain@mantra4change.com":"pratikjain-SG",
 "79907331+prateek-slokam@users.noreply.github.com":"Prateek-slokam","wasim@mantra4change.com":"wasimxvi",
 "shamakamble-art@users.noreply.github.com":"shamakamble-art","shama.kamble@mantra4change.com":"shamakamble-art",
 "deepa.p@mantra4change.com":"deepap-13","akhil@colabglobalconsulting.com":"akhilskashinath7",
 "akhil.rocks16@gmail.com":"akhilskashinath7","nivedithamohan@nivedithas-macbook-air-2.local":"niveditham-lgtm",
 "gaupalemunna76@gmail.com":"gaupalemunna76","sujeet.kumar@mantra4change.com":"sujeetkumar-ui",
 "kumari.shalini@mantra4change.com":"kumarishalini-sketch","sg@mantra4change.com":"kumarishalini-sketch",
 "315639019+sanskriti-boop@users.noreply.github.com":"sanskriti-boop","sanskriti@shikshalokam.org":"sanskriti-boop",
 "sg.communications@mantra4change.com":"syedhyder-sudo","devansh@mantra4change.com":"devansh181",
 "programs@mantra4change.com":"sindhu-obsidian","jaydev@mantra4change.com":"jaydev-lang",
 "arshul@shikshalokam.org":"arshulm","anoushka.anil@mantra4change.com":"Anoushka27002",
 "vernon@mantra4change.com":"vernon13579","aileen@mantra4change.com":"aileen-ship-it",
 "priyankapal@priyankas-macbook-air.local":"priyankapal-123","frpc@mantra4change.com":"varunkumar-creator",
 "saurabh@mantra4change.com":"endeavourindia","narayan-hh@users.noreply.github.com":"narayan-hh",
 "santosh@mantra4change.com":"Santosh-Mantra4Change","lovepreet@mantra4change.com":"lovepreet-giti",
 "harsen@mantra4change":"harsen-alt","gurudutt@shikshalokam.org":"guru-shikshagraha",
}
E2S = {"sahariar.mody567@gmail.com":"mody-sahariar1","modi.sahil.im@gmail.com":"sahilmodi1965"}
try:
    NAMES = json.load(open(f"{REPO}/tools/names.json"))
except Exception:
    NAMES = {}
NAMES_OLD = {"sahilmodi1965":"Sahil Modi","sushantM4C":"Sushant","nishantkumar-m4c":"Nishant Kumar","Deepthi-jb":"Deepthi J",
 "rafimantra":"Rafi","pratikjain-SG":"Pratik Jain","Prateek-slokam":"Prateek Agarwal","wasimxvi":"Syed Wasim",
 "shamakamble-art":"Shama Kamble","deepap-13":"Deepa P","akhilskashinath7":"Akhil S Kashinath","niveditham-lgtm":"Niveditha Mohan",
 "gaupalemunna76":"Munna Gaupale","sujeetkumar-ui":"Sujeet Kumar","kumarishalini-sketch":"Shalini Kumari","sanskriti-boop":"Sanskriti Shree",
 "syedhyder-sudo":"Syed Hyder","devansh181":"Devansh","sindhu-obsidian":"Sindhu","jaydev-lang":"Jaydev Lang","arshulm":"Arshul M",
 "Anoushka27002":"Anoushka Anil","vernon13579":"Vernon","aileen-ship-it":"Aileen","priyankapal-123":"Priyanka Pal",
 "varunkumar-creator":"Varun Kumar","endeavourindia":"Saurabh","narayan-hh":"Narayan","Santosh-Mantra4Change":"Santosh",
 "lovepreet-giti":"Lovepreet","harsen-alt":"Harsen","guru-shikshagraha":"Gurudutt"}

html = open(f"{REPO}/index.html").read()
claimed, order = {}, []
for m in re.finditer(r'<!-- ===== START (\S+) =====(.*?)<!-- ===== END \1 =====', html, re.S):
    claimed[m.group(1)] = 'class="empty"' not in m.group(2); order.append(m.group(1))

BLANK = {"main":0,"content":0,"merges":0,"unmerged":0,"first":None,"last":None,"branches":set(),"times":[]}
P = collections.defaultdict(lambda: dict(BLANK, branches=set(), times=[]))
def add(line, on_main):
    _h, _an, ae, ad, s = line.split('|', 4)
    slug = who(_h, ae)
    if not slug: return
    p = P[slug]; ismerge = s.lower().startswith("merge")
    if on_main:
        p["main"] += 1
        p["merges" if ismerge else "content"] += 1
        if not ismerge:
            p["times"].append(dt.datetime.strptime(ad, "%Y-%m-%d %H:%M:%S"))
    elif not ismerge:
        p["unmerged"] += 1
    if p["first"] is None or ad < p["first"]: p["first"] = ad
    if p["last"] is None or ad > p["last"]: p["last"] = ad

FMT = "--pretty=format:'%H|%an|%ae|%ad|%s' --date=format:'%Y-%m-%d %H:%M:%S'"
for l in sh(f"git log main {FMT}").strip().split('\n'): add(l, True)
# only published (origin) branches count as "waiting" — local scratch branches are noise
for l in sh(f"git log --remotes=origin --not main {FMT}").strip().split('\n'):
    if l.strip(): add(l, False)

branch_names = [b.strip() for b in sh("git for-each-ref --format='%(refname:short)' refs/remotes/origin").strip().split('\n')
                if b.strip() and not b.strip().endswith(('/HEAD', '/main')) and b.strip() != 'origin']
for b in branch_names:
    name = b.split('/', 1)[1]
    match = [s for s in claimed if name.lower().startswith(s.lower()[:8])]
    tgt = match[0] if match else who(sh(f"git log -1 --pretty=format:'%H' {b}").strip(), sh(f"git log -1 --pretty=format:'%ae' {b}").strip())
    if tgt: P[tgt]["branches"].add(name)

people = {}
for s in set(claimed) | set(P):
    p = P.get(s, dict(BLANK, branches=set(), times=[]))
    people[s] = dict(p, branches=sorted(p["branches"]), slug=s, name=NAMES.get(s, s), claimed=claimed.get(s, False), card=s in claimed)

# ── funnel (strictly nested) ────────────────────────────────────────────────
tiles   = [s for s in claimed]
showed  = [s for s, p in people.items() if p["main"] or p["unmerged"] or p["branches"]]
real    = [s for s in showed if people[s]["content"] or people[s]["unmerged"]]
onmain  = [s for s in real if people[s]["content"]]
livetile= [s for s in onmain if people[s]["claimed"]]
untouched = sorted([s for s in tiles if not people[s]["main"] and not people[s]["unmerged"] and not people[s]["branches"]])
# a tile only counts as "open" if it is genuinely unclaimed — someone else may have
# published a tile on the author's behalf, which leaves no git trace for that person
open_tiles = [s for s in untouched if not claimed[s]]

RAMP =["#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]  # validated ordinal, cream surface
FUNNEL = [
    ("Tiles on the wall",    len(tiles),    "blocks that exist on the page"),
    ("Started working",      len(showed),   "made a draft copy, or saved something"),
    ("Saved their own work", len(real),     "at least one batch of their own edits"),
    ("Published it",         len(onmain),   "those edits reached the shared page"),
    ("Their tile is live",   len(livetile), "and everyone can see it today"),
]
# each gap is framed as the work available at that step, not as a failure
def plural(n, one, many): return f"{n} {one if n == 1 else many}"
DROPS = [
    f"{plural(len(open_tiles), 'of these tiles is', 'of these tiles are')} completely open — the quickest win on the board",
    f"{plural(len(showed)-len(real), 'person has', 'people have')} a draft copy but no saved edits of their own yet",
    f"{plural(len(real)-len(onmain), 'person has', 'people have')} finished work ready to publish — listed below",
    f"{plural(len(onmain)-len(livetile), 'person', 'people')} improved the page for everyone else before claiming a tile",
]

# ── timeline (continuous 30-min buckets on main) ────────────────────────────
raw = collections.Counter()
for ad in sh("git log main --pretty=format:'%ad' --date=format:'%Y-%m-%d %H:%M'").strip().split('\n'):
    d, t = ad.split(' '); h, mi = t.split(':')
    raw[dt.datetime.strptime(f"{d} {h}:{'00' if int(mi) < 30 else '30'}", "%Y-%m-%d %H:%M")] += 1
t0, t1 = min(raw), max(raw)
series, cur = [], t0
while cur <= t1:
    series.append((cur, raw.get(cur, 0))); cur += dt.timedelta(minutes=30)

total_main   = sum(p["main"] for p in people.values())
total_content= sum(p["content"] for p in people.values())
total_merges = sum(p["merges"] for p in people.values())
total_stranded = sum(p["unmerged"] for p in people.values())
merge_pct = round(100 * total_merges / total_main)
peak = max(series, key=lambda x: x[1])

stuck = sorted([p for p in people.values() if p["unmerged"] > 0 and p["content"] == 0], key=lambda x: -x["unmerged"])
partial = sorted([p for p in people.values() if p["unmerged"] > 0 and p["content"] > 0], key=lambda x: -x["unmerged"])
rescued = [p for p in people.values() if p["claimed"] and p["content"] == 0]
# ── system friction: what makes publishing harder than it needs to be ───────
merged_branches = [b for b in branch_names if sh(f"git rev-list --count main..{b}").strip() == "0"]
live_branches   = [b for b in branch_names if b not in merged_branches]

split_identity = {}
for slug in people:
    emails = {e for e, s in E2S.items() if s == slug}  # fallback map only
    used = {e for e in emails if sh(f'git log --all -1 --author="{e}" --pretty=format:%H').strip()}
    if len(used) > 1: split_identity[slug] = sorted(used)
machine_emails = sorted({e for e in E2S if e.endswith('.local')})

# PR data is a nice-to-have; the page still builds without network/gh
pr_total = pr_merged = pr_slow = pr_unmerged = pr_authors = 0
pr_median = pr_max = 0.0
try:
    prs = json.loads(sh("gh pr list --state all --limit 100 --json number,author,state,createdAt,mergedAt"))
    def _p(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')) if s else None
    waits = sorted((_p(p['mergedAt']) - _p(p['createdAt'])).total_seconds() / 60
                   for p in prs if p.get('mergedAt'))
    pr_total = len(prs); pr_merged = len(waits)
    pr_slow = sum(1 for w in waits if w > 60)
    pr_unmerged = sum(1 for p in prs if p['state'] == 'CLOSED' and not p.get('mergedAt'))
    pr_authors = len({p['author']['login'] for p in prs})
    if waits:
        pr_median = waits[len(waits)//2]
        pr_max = waits[-1]
except Exception as e:
    print("note: PR stats unavailable, skipping that friction row —", e)

# ── who edited outside their own tile? (boundary probing / QA behaviour) ────
def blocks_at(rev):
    """slug -> (start,end) line numbers in index.html at a given revision"""
    txt = sh(f"git show {rev}:index.html")
    out, lines = {}, txt.split('\n')
    open_at = {}
    for i, ln in enumerate(lines, 1):
        m = re.search(r'<!-- ===== START (\S+) =====', ln)
        if m: open_at[m.group(1)] = i
        m = re.search(r'<!-- ===== END (\S+) =====', ln)
        if m and m.group(1) in open_at: out[m.group(1)] = (open_at[m.group(1)], i)
    return out

# Deliberately strict: only edits landing INSIDE another named person's tile count.
# Touching the shared <style> block is routine here (people add rules for their own
# card up there), so counting it would drown the real signal.
cross_edits = collections.Counter()
cross_detail = collections.defaultdict(set)
theme_edits = collections.Counter()
for line in sh(f"git log main --no-merges {FMT} -- index.html").strip().split('\n'):
    if not line.strip(): continue
    h, _an, ae, _ad, _s = line.split('|', 4)
    me = who(h, ae)
    if not me or me == MAINTAINER: continue   # the maintainer edits everywhere by role
    diff = sh(f"git show --unified=0 --format= {h} -- index.html")
    if re.search(r'^\+\s*:root\s*\{', diff, re.M): theme_edits[me] += 1
    hunks = [int(m.group(1)) for m in re.finditer(r'^@@ -\d+(?:,\d+)? \+(\d+)', diff, re.M)]
    if not hunks: continue
    rng = blocks_at(h)
    for ln in hunks:
        owner = next((s for s, (a, b) in rng.items() if a <= ln <= b), None)
        if owner and owner != me:
            cross_edits[me] += 1
            cross_detail[me].add(owner)
            break
explorers = sorted(cross_edits.items(), key=lambda x: -x[1])

FRICTION = []
if pr_total:
    FRICTION.append((
        "Two ways to publish, and the slower one is winning",
        f"The guide says publish straight to the shared page, no approval needed. Still, {pr_total} review requests were "
        f"opened by {pr_authors} people. Most cleared in about a minute &mdash; but {pr_slow} waited over an hour "
        f"(longest {pr_max/60:.0f}h) and {pr_unmerged} never went live.",
        "Say one thing, and say it first."))
FRICTION += [
    ("One file, everyone in it",
     f"All {len(tiles)} tiles share a single file, which is why {total_merges} of {total_main} saves ({merge_pct}%) exist "
     "only to untangle two people&rsquo;s edits.",
     "One file per tile, stitched together automatically."),
    ("Publishing fails when two people save at once",
     "Each of those untangling saves began as a refusal on someone&rsquo;s screen, with no obvious next step.",
     "A single <code>publish</code> command that fetches, replays and sends."),
    ("Nothing protects one tile from another",
     f"The rule is &ldquo;edit only your own block&rdquo;, but nothing enforces it &mdash; {len(cross_edits)} people have saves "
     "that reach into someone else&rsquo;s tile or the shared theme. Useful to know now rather than at 100 tiles.",
     "Ownership per tile, so a wrong edit is caught before it publishes, not after."),
    ("Finished drafts have no road to the page",
     f"{len(merged_branches)} of {len(branch_names)} draft copies are already published but never cleared, so only "
     f"{len(live_branches)} still hold live work &mdash; easy to lose your own in the noise.",
     "Clear each draft automatically once published."),
    ("Name settings unset, so credit splits",
     f"{len(split_identity)} people appear under two names, and some saves carry a laptop default like "
     "<code>yourname@macbook.local</code> that links to no account.",
     "Set name and email once during setup."),
    ("No preview before it is public",
     "There is no way to see your tile between saving and going live, so the safe move is to try less.",
     "A one-command local preview."),
]

# ── celebratory boards ──────────────────────────────────────────────────────
# Fun, generous, one winner each — never a ranked table of who did most.
# The facilitator is left out so the spotlight stays on the cohort.
CREW = {s: p for s, p in people.items() if p["times"] and s != MAINTAINER}

def board(emoji, title, slug, value, note):
    return dict(emoji=emoji, title=title, slug=slug,
                name=people[slug]["name"] if slug else "", value=value, note=note)

BOARDS = []
if CREW:
    # kept coming back — most separate days with something published
    days = {s: len({t.date() for t in p["times"]}) for s, p in CREW.items()}
    s_ = max(days, key=lambda k: (days[k], len(CREW[k]["times"])))
    BOARDS.append(board("&#127793;", "Kept coming back", s_, f"{days[s_]} days",
                        "showed up and published on the most separate days"))
    # smoothest publisher — largest share of saves that built something
    clean = {s: p["content"] / p["main"] for s, p in CREW.items() if p["main"] >= 4}
    if clean:
        s_ = max(clean, key=clean.get)
        BOARDS.append(board("&#10024;", "Smoothest publisher", s_, f"{round(clean[s_]*100)}%",
                            "of their saves built something &mdash; almost no untangling"))
    # Early bird & night owl. Anything before 05:00 belongs to the night before,
    # so it is ranked as "late", not as the earliest start of a new day.
    def clock(t):
        m = t.hour * 60 + t.minute
        return m + 24 * 60 if t.hour < 5 else m
    morning = {s: min((clock(t) for t in p["times"] if t.hour >= 5), default=None) for s, p in CREW.items()}
    morning = {s: v for s, v in morning.items() if v is not None}
    if morning:
        s_ = min(morning, key=morning.get)
        t_ = min((t for t in CREW[s_]["times"] if t.hour >= 5), key=clock)
        BOARDS.append(board("&#127749;", "Early bird", s_, t_.strftime("%H:%M"),
                            "first one publishing in the morning"))
    s_ = max(CREW, key=lambda k: max(clock(t) for t in CREW[k]["times"]))
    t_ = max(CREW[s_]["times"], key=clock)
    BOARDS.append(board("&#127769;", "Night owl", s_, t_.strftime("%H:%M"),
                        "still building long after everyone else logged off"))
    # busiest day for one person
    best = max(((s, c) for s, p in CREW.items()
                for c in [max(collections.Counter(t.date() for t in p["times"]).values())]),
               key=lambda x: x[1])
    BOARDS.append(board("&#9889;&#65039;", "Biggest day", best[0], f"{best[1]} saves",
                        "most published by one person in a single day"))
    # picked it up again — published on a later day than they started
    ret = {s: len([t for t in p["times"] if t.date() > min(x.date() for x in p["times"])])
           for s, p in CREW.items()}
    ret = {s: v for s, v in ret.items() if v}
    if ret:
        s_ = max(ret, key=ret.get)
        BOARDS.append(board("&#128260;", "Came back for more", s_, f"+{ret[s_]}",
                            "saves made on a day after they first started"))
    # first to improve someone else's tile
    if cross_detail:
        firsts = {}
        for line in sh(f"git log main --no-merges --reverse {FMT} -- index.html").strip().split('\n'):
            if not line.strip(): continue
            _h2, _an2, ae2, ad2, _s2 = line.split('|', 4)
            me = who(_h2, ae2)
            if me in cross_detail and me not in firsts and me != MAINTAINER:
                firsts[me] = ad2
        if firsts:
            s_ = min(firsts, key=firsts.get)
            BOARDS.append(board("&#129309;", "First to lend a hand", s_,
                                dt.datetime.strptime(firsts[s_], "%Y-%m-%d %H:%M:%S").strftime("%-d %b, %H:%M"),
                                "earliest save that improved somebody else&rsquo;s tile"))
    # the whole wall's busiest half hour — a group award, nobody named
    BOARDS.append(board("&#127881;", "Busiest half hour", None, f"{peak[1]} saves",
                        f"everyone at once, {peak[0].strftime('%-d %b at %H:%M')}"))

GLOSSARY = [
    ("Save", "commit", "One batch of finished edits, stored with your name on it."),
    ("Publish", "push", "Sending your saves to the shared page, where everyone can see them."),
    ("The shared page", "main", "The one official copy that the live website is built from."),
    ("Draft copy", "branch", "Your own private version. Safe to experiment in; invisible to others until you publish."),
    ("Untangling", "merge", "The extra work of combining your edits with someone else&rsquo;s when you both changed the same file."),
    ("Request for review", "pull request", "Asking someone to check and approve your work before it goes live."),
]

# ── SVG: funnel ─────────────────────────────────────────────────────────────
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

FW, ROW, GAP, LBL = 620, 34, 20, 178
fh = len(FUNNEL) * (ROW + GAP) - GAP
maxv = FUNNEL[0][1]
fs = [f'<svg class="ac-svg" viewBox="0 0 {LBL + FW + 46} {fh}" role="img" aria-label="The path from a tile on the wall to a tile live on the page">']
for i, (lab, val, _sub) in enumerate(FUNNEL):
    y = i * (ROW + GAP)
    w = max(6, round(FW * val / maxv))
    fs.append(f'<text x="{LBL - 12}" y="{y + ROW/2 + 4}" text-anchor="end" class="ac-ylab">{esc(lab)}</text>')
    fs.append(f'<rect x="{LBL}" y="{y}" width="{w}" height="{ROW}" rx="4" fill="{RAMP[i]}"/>')
    fs.append(f'<rect x="{LBL}" y="{y}" width="6" height="{ROW}" fill="{RAMP[i]}"/>')
    fs.append(f'<text x="{LBL + w + 10}" y="{y + ROW/2 + 4}" class="ac-val">{val}</text>')
    if i < len(FUNNEL) - 1:
        fs.append(f'<text x="{LBL + 10}" y="{y + ROW + GAP - 3}" class="ac-drop">&#8595; {esc(DROPS[i])}</text>')
fs.append('</svg>')
funnel_svg = "\n".join(fs)

# ── SVG: timeline area ──────────────────────────────────────────────────────
TW, TH, PADL, PADB = 840, 170, 34, 26
n = len(series)
ymax = 50
def tx(i): return PADL + (TW - PADL) * i / (n - 1)
def ty(v): return TH - PADB - (TH - PADB - 8) * v / ymax
pts = " ".join(f"{tx(i):.1f},{ty(v):.1f}" for i, (_d, v) in enumerate(series))
area = f"{PADL},{TH-PADB} {pts} {tx(n-1):.1f},{TH-PADB}"
ts = [f'<svg class="ac-svg" viewBox="0 0 {TW} {TH}" role="img" aria-label="Saved changes reaching the shared page in 30-minute buckets across 11-12 August 2026, with two sharp spikes during the live sessions">']
for gv in (0, 25, 50):
    ts.append(f'<line x1="{PADL}" y1="{ty(gv):.1f}" x2="{TW}" y2="{ty(gv):.1f}" class="ac-grid"/>')
    ts.append(f'<text x="{PADL - 8}" y="{ty(gv) + 4:.1f}" text-anchor="end" class="ac-tick">{gv}</text>')
ts.append(f'<polygon points="{area}" fill="#2a78d6" fill-opacity="0.10"/>')
ts.append(f'<polyline points="{pts}" fill="none" stroke="#2a78d6" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
for i, (d, v) in enumerate(series):
    if d.hour in (0, 6, 12, 18) and d.minute == 0:
        # keep the last tick inside the viewBox instead of letting it overhang the edge
        if tx(i) > TW - 46:
            ts.append(f'<text x="{TW}" y="{TH - 8}" text-anchor="end" class="ac-tick">{d.strftime("%d %b %H:%M")}</text>')
        else:
            ts.append(f'<text x="{tx(i):.1f}" y="{TH - 8}" text-anchor="middle" class="ac-tick">{d.strftime("%d %b %H:%M")}</text>')
pi = series.index(peak)
ts.append(f'<circle cx="{tx(pi):.1f}" cy="{ty(peak[1]):.1f}" r="4.5" fill="#2a78d6" stroke="#FBF3DA" stroke-width="2"/>')
ts.append(f'<text x="{tx(pi) - 8:.1f}" y="{ty(peak[1]) + 4:.1f}" text-anchor="end" class="ac-val">{peak[1]} saves &#183; live session</text>')
ts.append(f'<rect class="ac-hit" x="{PADL}" y="0" width="{TW-PADL}" height="{TH-PADB}" fill="transparent"/>')
ts.append(f'<line class="ac-cross" x1="0" y1="0" x2="0" y2="{TH-PADB}" stroke="#5B6B7B" stroke-width="1" opacity="0"/>')
ts.append('</svg>')
timeline_svg = "\n".join(ts)

# ── merge tax bar ───────────────────────────────────────────────────────────
cw = round(100 * total_content / total_main, 1)
merge_bar = (f'<div class="ac-stack" role="img" aria-label="Of {total_main} saved changes, {total_content} built something and {total_merges} only untangled edits">'
             f'<span style="width:{cw}%;background:#2a78d6"></span>'
             f'<span style="width:{100-cw}%;background:#eb6834"></span></div>')

def li_person(p, extra):
    return (f'<li><a href="https://github.com/{esc(p["slug"])}">@{esc(p["slug"])}</a>'
            f'<span class="ac-nm">{esc(p["name"])}</span><span class="ac-note">{extra}</span></li>')

def ready_item(p):
    br = esc(p["branches"][0]) if p["branches"] else "your-branch"
    n = p["unmerged"]
    also = (" &#183; " + str(p["content"]) + " already published") if p["content"] else ""
    return (f'<li><a href="https://github.com/{esc(p["slug"])}">@{esc(p["slug"])}</a>'
            f'<span class="ac-nm">{esc(p["name"])}</span>'
            f'<span class="ac-note">{n} finished save{"s" if n > 1 else ""} waiting in <code>{br}</code>{also}</span>'
            f'<code class="ac-cmd">git checkout {br} &amp;&amp; git pull --rebase origin main &amp;&amp; git push origin HEAD:main</code></li>')

ready = sorted(stuck + partial, key=lambda x: -x["unmerged"])
ready_items = "".join(ready_item(p) for p in ready)
ready_commits = sum(p["unmerged"] for p in ready)
open_items = "".join(
    f'<li><a href="https://github.com/{esc(s)}">@{esc(s)}</a>'
    f'<span class="ac-note">tile is on the page and unclaimed</span></li>' for s in open_tiles)

friction_items = "".join(
    f'<li><h4>{esc(t)}</h4><p class="ac-eff">{ev}</p><p class="ac-fix"><b>Easier would be:</b> {fx}</p></li>'
    for t, ev, fx in FRICTION)

def board_html(b):
    who = (f'<p class="w"><a href="index.html#{esc(b["slug"])}">{esc(b["name"])}</a></p>'
           if b["slug"] else '<p class="w">everyone, together</p>')
    return (f'<div class="bd"><span class="e">{b["emoji"]}</span>'
            f'<p class="t">{b["title"]}</p><p class="v">{b["value"]}</p>{who}'
            f'<p class="n">{b["note"]}</p></div>')
boards_html = "".join(board_html(b) for b in BOARDS)

glossary_items = "".join(
    f'<div class="ac-term"><dt>{plain}<span class="ac-jargon">{jargon}</span></dt><dd>{meaning}</dd></div>'
    for plain, jargon, meaning in GLOSSARY)

table_rows = "".join(
    f'<tr><td>{esc(lab)}</td><td class="ac-num">{val}</td><td>{esc(sub)}</td></tr>'
    for lab, val, sub in FUNNEL)

# table twin for the timeline — hourly totals, so no value is tooltip-only
hourly = collections.Counter()
for d, v in series: hourly[d.replace(minute=0)] += v
time_rows = "".join(
    f'<tr><td>{h.strftime("%-d %b, %H:%M")}&ndash;{(h + dt.timedelta(hours=1)).strftime("%H:%M")}</td>'
    f'<td class="ac-num">{c}</td></tr>'
    for h, c in sorted(hourly.items()) if c)

asof = sh("git log -1 --pretty=format:'%ad' --date=format:'%-d %b %Y, %H:%M'").strip()

# ── the last day, measured from the newest save rather than the wall clock, so
#    the figure still reads correctly whenever the page happens to be rebuilt ──
newest = max((t for p in people.values() for t in p["times"]), default=None)
saves_today = people_today = tiles_today = 0
if newest:
    since = newest - dt.timedelta(hours=24)
    recent = {s: [t for t in p["times"] if t >= since] for s, p in people.items()}
    recent = {s: v for s, v in recent.items() if v}
    saves_today = sum(len(v) for v in recent.values())
    people_today = len(recent)
    # tiles that stopped being placeholders in the last day
    since_arg = since.strftime("%Y-%m-%d %H:%M:%S")
    was = sh(f'git log main --before="{since_arg}" -1 --pretty=format:%H').strip()
    if was:
        then = sh(f"git show {was}:index.html")
        prev = {m.group(1): 'class="empty"' not in m.group(2) for m in
                re.finditer(r'<!-- ===== START (\S+) =====(.*?)<!-- ===== END \1 =====', then, re.S)}
        tiles_today = sum(1 for s, c in claimed.items() if c and not prev.get(s, False))

# ── compact funnel for the wall (no annotations, small rows) ────────────────
CW_, CROW, CGAP, CLBL = 470, 15, 10, 168
cfh = len(FUNNEL) * (CROW + CGAP) - CGAP
cf = [f'<svg class="ac-svg" viewBox="0 0 {CLBL + CW_ + 44} {cfh}" role="img" aria-label="From {len(tiles)} tiles on the wall to {len(livetile)} tiles live">']
for i, (lab, val, _s) in enumerate(FUNNEL):
    y = i * (CROW + CGAP); w = max(5, round(CW_ * val / FUNNEL[0][1]))
    cf.append(f'<text x="{CLBL-11}" y="{y+CROW-3}" text-anchor="end" class="ac-ylab">{esc(lab)}</text>')
    cf.append(f'<rect x="{CLBL}" y="{y}" width="{w}" height="{CROW}" rx="4" fill="{RAMP[i]}"/>')
    cf.append(f'<rect x="{CLBL}" y="{y}" width="5" height="{CROW}" fill="{RAMP[i]}"/>')
    cf.append(f'<text x="{CLBL+w+9}" y="{y+CROW-3}" class="ac-val">{val}</text>')
cf.append('</svg>')
compact_funnel = "\n".join(cf)

# ── CSS (plain string: no interpolation, so no brace escaping) ──────────────
CSS = """
 .ac{--ac-ink:#24303F;--ac-ink2:#5B6B7B;--ac-line:#E2D6B4;--ac-surface:#FBF3DA;color:var(--ac-ink)}
 .ac h2{margin:0 0 4px;font-size:1.1rem}
 .ac .ac-cap{color:var(--ac-ink2);font-size:.8rem;margin:0 0 18px}
 .ac h3{font-size:.82rem;margin:0 0 2px;letter-spacing:.04em;text-transform:uppercase;color:var(--ac-ink)}
 .ac .ac-sub{color:var(--ac-ink2);font-size:.76rem;margin:0 0 14px;line-height:1.6}
 .ac .ac-block{margin:0 0 30px}
 .ac .ac-svg{width:100%;height:auto;display:block;overflow:visible}
 .ac .ac-ylab{font:500 11px ui-monospace,SFMono-Regular,Menlo,monospace;fill:var(--ac-ink)}
 .ac .ac-val{font:600 11px ui-monospace,SFMono-Regular,Menlo,monospace;fill:var(--ac-ink)}
 .ac .ac-drop{font:400 10.5px ui-monospace,SFMono-Regular,Menlo,monospace;fill:var(--ac-ink2)}
 .ac .ac-tick{font:400 10px ui-monospace,SFMono-Regular,Menlo,monospace;fill:var(--ac-ink2)}
 .ac .ac-grid{stroke:var(--ac-line);stroke-width:1}
 .ac .ac-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(124px,1fr));gap:1px;
   background:var(--ac-line);border:1px solid var(--ac-line);border-radius:8px;overflow:hidden;margin:0 0 20px}
 .ac .ac-kpi{background:var(--ac-surface);padding:11px 13px}
 .ac .ac-kpi .k{display:block;font-size:.66rem;color:var(--ac-ink2);letter-spacing:.03em;margin-bottom:4px}
 .ac .ac-kpi .v{display:block;font-size:1.45rem;font-weight:600;line-height:1.1;color:var(--ac-ink)}
 .ac .ac-kpi .n{display:block;font-size:.64rem;color:var(--ac-ink2);margin-top:3px}
 .ac .ac-stack{display:flex;height:24px;border-radius:4px;overflow:hidden;gap:2px;background:var(--ac-surface);margin:0 0 8px}
 .ac .ac-stack span{display:block;height:100%}
 .ac .ac-legend{display:flex;flex-wrap:wrap;gap:15px;font-size:.73rem;color:var(--ac-ink2);margin:0}
 .ac .ac-legend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px}
 .ac .ac-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:26px}
 .ac ul.ac-list{list-style:none;margin:0;padding:0}
 .ac ul.ac-list li{padding:8px 0;border-bottom:1px solid var(--ac-line);font-size:.8rem;display:flex;flex-wrap:wrap;gap:3px 10px;align-items:baseline}
 .ac ul.ac-list li:last-child{border-bottom:none}
 .ac ul.ac-list a{color:var(--ac-ink);text-decoration:none;border-bottom:1px dotted var(--ac-ink2)}
 .ac .ac-nm{color:var(--ac-ink2);font-size:.74rem}
 .ac .ac-note{color:var(--ac-ink2);font-size:.72rem;flex-basis:100%}
 .ac code{font-size:.95em;background:rgba(36,48,63,.06);padding:1px 4px;border-radius:3px}
 .ac .ac-cmd{flex-basis:100%;display:block;margin-top:5px;font-size:.68rem;line-height:1.5;
   background:rgba(36,48,63,.06);border-radius:4px;padding:6px 8px;overflow-wrap:anywhere;white-space:pre-wrap}
 .ac .ac-reads{margin:0;padding:0;list-style:none;display:grid;gap:11px}
 .ac .ac-reads li{font-size:.79rem;line-height:1.6;color:var(--ac-ink2);border-left:2px solid var(--ac-line);padding-left:13px}
 .ac .ac-reads b{color:var(--ac-ink);font-weight:600}
 .ac details{margin-top:6px;font-size:.75rem;color:var(--ac-ink2)}
 .ac summary{cursor:pointer;padding:5px 0}
 .ac table{border-collapse:collapse;width:100%;margin-top:8px;font-size:.74rem}
 .ac th,.ac td{text-align:left;padding:5px 10px 5px 0;border-bottom:1px solid var(--ac-line);color:var(--ac-ink2)}
 .ac th{color:var(--ac-ink);font-weight:600}
 .ac .ac-num{font-variant-numeric:tabular-nums;color:var(--ac-ink)}
 .ac .ac-tip{position:absolute;pointer-events:none;background:var(--ac-surface);border:1px solid var(--ac-ink2);
   border-radius:6px;padding:5px 9px;font-size:.72rem;color:var(--ac-ink);white-space:nowrap;opacity:0;transition:opacity .12s;
   box-shadow:0 3px 10px rgba(36,48,63,.16);z-index:5}
 .ac .ac-wrap{position:relative}
 .ac .boards{display:grid;grid-template-columns:repeat(auto-fit,minmax(196px,1fr));gap:12px;margin:0 0 8px}
 .ac .bd{border:1px solid var(--ac-line);border-radius:12px;padding:15px 16px 13px;background:rgba(255,255,255,.34)}
 .ac .bd .e{font-size:1.4rem;line-height:1;display:block;margin-bottom:9px}
 .ac .bd .t{margin:0 0 6px;font-size:.7rem;letter-spacing:.05em;text-transform:uppercase;color:var(--ac-ink2)}
 .ac .bd .v{margin:0 0 2px;font-size:1.3rem;font-weight:600;color:var(--ac-ink);line-height:1.15}
 .ac .bd .w{margin:0 0 7px;font-size:.8rem;color:var(--ac-ink)}
 .ac .bd .w a{color:var(--ac-ink);text-decoration:none;border-bottom:1px dotted var(--ac-ink2)}
 .ac .bd .n{margin:0;font-size:.7rem;color:var(--ac-ink2);line-height:1.5}
 .ac .calm{font-size:.86rem;line-height:1.75;color:var(--ac-ink2);max-width:660px;margin:0 0 14px}
 .ac .calm b{color:var(--ac-ink);font-weight:600}
 .ac .ac-glossary{display:grid;grid-template-columns:repeat(auto-fit,minmax(238px,1fr));gap:1px;margin:0;
   background:var(--ac-line);border:1px solid var(--ac-line);border-radius:8px;overflow:hidden}
 .ac .ac-term{background:var(--ac-surface);padding:12px 14px}
 .ac .ac-glossary dt{font-weight:600;font-size:.83rem;color:var(--ac-ink);margin:0 0 4px}
 .ac .ac-glossary dd{margin:0;font-size:.74rem;line-height:1.55;color:var(--ac-ink2)}
 .ac .ac-jargon{display:inline-block;margin-left:7px;font-weight:400;font-size:.67rem;color:var(--ac-ink2);
   border:1px solid var(--ac-line);border-radius:20px;padding:1px 7px;vertical-align:1px}
 .ac .ac-jargon::before{content:"they call it "}
 .ac ol.ac-friction{list-style:none;counter-reset:f;margin:16px 0 0;padding:0;display:grid;gap:12px}
 .ac ol.ac-friction li{counter-increment:f;border:1px solid var(--ac-line);border-radius:10px;padding:13px 15px;background:rgba(255,255,255,.3)}
 .ac ol.ac-friction h4{margin:0 0 5px;font-size:.83rem;color:var(--ac-ink);font-weight:600}
 .ac ol.ac-friction h4::before{content:counter(f) ". ";color:var(--ac-ink2);font-weight:400}
 .ac .ac-eff{margin:0 0 7px;font-size:.77rem;line-height:1.6;color:var(--ac-ink2)}
 .ac .ac-fix{margin:0;font-size:.77rem;line-height:1.55;color:var(--ac-ink2);border-top:1px dotted var(--ac-line);padding-top:7px}
 .ac .ac-fix b{color:var(--ac-ink)}
 .ac .ac-more{display:inline-block;margin:2px 0 0;font-size:.8rem;color:var(--ac-ink);
   text-decoration:none;border-bottom:1px solid var(--ac-ink2);padding-bottom:1px}
 .ac .ac-foot{margin:22px 0 0;padding-top:14px;border-top:1px solid var(--ac-line);font-size:.72rem;color:var(--ac-ink2)}
 @media(max-width:560px){.ac .ac-nm{display:none}}
 .ac .whatson{display:grid;grid-template-columns:repeat(auto-fit,minmax(214px,1fr));gap:1px;
   background:var(--ac-line);border:1px solid var(--ac-line);border-radius:9px;overflow:hidden}
 .ac .whatson>div{background:var(--ac-surface);padding:12px 14px}
 .ac .whatson .wh{display:inline-block;font-size:.61rem;letter-spacing:.09em;text-transform:uppercase;
   color:#256abf;font-weight:600;margin-bottom:6px}
 .ac .whatson p{margin:0;font-size:.75rem;line-height:1.55;color:var(--ac-ink2)}
 .ac .whatson a{color:var(--ac-ink);text-decoration:none;border-bottom:1px solid #256abf}
 #homework{grid-column:1/-1;border:1px solid #256abf;border-left:4px solid #256abf;border-radius:10px;
   padding:20px 22px;margin-bottom:8px;background:rgba(255,255,255,.34)}
 #homework .hw-tag{display:inline-block;font-size:.64rem;letter-spacing:.09em;text-transform:uppercase;
   color:#FBF3DA;background:#256abf;border-radius:20px;padding:3px 11px;margin:0 0 10px}
 #homework h2{margin:0 0 4px;font-size:1.15rem}
 #homework .hw-lead{color:var(--ac-ink2);font-size:.8rem;margin:0 0 14px;max-width:640px;line-height:1.6}
 #homework .hw-box{position:relative;margin:0 0 12px}
 #homework pre{margin:0;background:rgba(36,48,63,.06);border:1px solid var(--ac-line);border-radius:8px;
   padding:14px 15px;padding-right:86px;font-size:.73rem;line-height:1.75;white-space:pre-wrap;overflow-wrap:anywhere;
   font-family:inherit;color:var(--ac-ink)}
 #homework .hw-copy{position:absolute;top:9px;right:9px;font:inherit;font-size:.68rem;cursor:pointer;
   background:#256abf;color:#FBF3DA;border:none;border-radius:6px;padding:5px 12px;transition:background .15s}
 #homework .hw-copy:hover{background:#184f95}
 #homework .hw-warn{margin:0 0 14px;font-size:.75rem;line-height:1.6;color:#8a3d16;
   background:rgba(235,104,52,.10);border:1px solid rgba(235,104,52,.35);border-radius:8px;padding:9px 12px}
 #homework ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
 #homework ul li{font-size:.78rem;line-height:1.6;color:var(--ac-ink2);
   border-left:2px solid var(--ac-line);padding-left:12px}
 #homework ul b{color:var(--ac-ink)}
"""

GMAIL_PROMPT = (
"I have Claude Code installed and the demo-brain folder on my computer. Guide me step by step, "
"one step at a time, and do not rush ahead. First: open my terminal, go into the demo-brain folder, "
"and launch Claude Code. Then: connect my own Gmail. Create a Google Cloud project in the Google "
"console, enable the Gmail API, create OAuth credentials for a desktop app, and store the credentials "
"file safely, outside any shared or git folder. Teach me safe handling as we go: I never paste the "
"file's contents into chat, never commit it to git, and only I approve access. Give me exact commands "
"and exact clicks, ask me for what you need, and after each step tell me what to paste back, or what "
"to screenshot, so you can verify before moving on. The finish line: from Claude Code, I reply to our "
"cohort email thread from my own Gmail. First a simple reply, then help me improve it into a rich "
"HTML email that keeps my signature, with an attachment: a short note on how I did this homework, "
"or any real piece of my work, like a report.")

HOMEWORK = '''<section id="homework" class="ac">
  <p class="hw-tag">Tonight</p>
  <h2>Make your card yours &mdash; three changes from home</h2>
  <p class="hw-lead">Open Claude Code inside the wall folder and say what you want, one sentence at a time. It edits your block and publishes it. Ideas:</p>
  <div class="hw-box">
    <button class="hw-copy" type="button">Copy</button>
    <pre id="hw-prompt">Add a line under my name about my programme and what we do. Change the background to a colour I like. Add a link to our website. Then publish it.</pre>
  </div>
  <ul>
    <li><b>Where:</b> your terminal, <code>cd ~/Desktop/vv-wall</code> then <code>claude</code>. Windows: <code>cd $HOME\\Desktop\\vv-wall</code> then <code>claude</code>.</li>
    <li><b>Done looks like:</b> your card on the live page with at least three things that are yours.</li>
    <li><b>Push rejected?</b> Say: someone else pushed, pull their work and push mine again.</li>
    <li><b>Stuck?</b> Screenshot it and show Claude &mdash; then reply on the thread, and Sahariar will unblock you.</li>
  </ul>
  <script>
  (function(){
    var btn=document.querySelector('#homework .hw-copy'), pre=document.getElementById('hw-prompt');
    if(!btn||!pre) return;
    btn.addEventListener('click',function(){
      var txt=pre.textContent;
      function ok(){ btn.textContent='Copied'; setTimeout(function(){btn.textContent='Copy';},1600); }
      if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(txt).then(ok,fallback); } else { fallback(); }
      function fallback(){ var t=document.createElement('textarea'); t.value=txt; t.style.position='fixed'; t.style.opacity='0'; document.body.appendChild(t); t.select(); try{document.execCommand('copy'); ok();}catch(e){ btn.textContent='Select and copy'; } document.body.removeChild(t); }
    });
  })();
  </script>
</section>

'''

TOOLTIP_JS = """
(function(){
  var svg=document.querySelector('.ac .ac-wrap .ac-svg');
  if(!svg) return;
  var tip=document.getElementById('ac-tip'), cross=svg.querySelector('.ac-cross'),
      hit=svg.querySelector('.ac-hit'), wrap=svg.closest('.ac-wrap');
  var data=__DATA__, PADL=__PADL__, TW=__TW__, n=data.length;
  function show(e){
    var r=svg.getBoundingClientRect(), sx=(e.clientX-r.left)/r.width*TW;
    var i=Math.round((sx-PADL)/(TW-PADL)*(n-1)); i=Math.max(0,Math.min(n-1,i));
    var x=PADL+(TW-PADL)*i/(n-1);
    cross.setAttribute('x1',x); cross.setAttribute('x2',x); cross.setAttribute('opacity','.35');
    tip.textContent=data[i][0]+' \\u00b7 '+data[i][1]+(data[i][1]===1?' save':' saves');
    tip.style.opacity='1';
    var wr=wrap.getBoundingClientRect(), px=r.left-wr.left+x/TW*r.width;
    tip.style.left=Math.min(Math.max(px-tip.offsetWidth/2,0),wr.width-tip.offsetWidth)+'px';
    tip.style.top=(r.top-wr.top-4)+'px';
  }
  function hide(){ tip.style.opacity='0'; cross.setAttribute('opacity','0'); }
  hit.addEventListener('mousemove',show); hit.addEventListener('mouseleave',hide);
  hit.addEventListener('touchmove',function(e){ if(e.touches[0]) show(e.touches[0]); },{passive:true});
})();
""".replace("__DATA__", json.dumps([[d.strftime('%-d %b %H:%M'), v] for d, v in series])) \
   .replace("__PADL__", str(PADL)).replace("__TW__", str(TW))

# ── the compact dashboard that lives on the wall ────────────────────────────
lead = (f"{ready_commits} finished save{'s' if ready_commits != 1 else ''} are waiting one step from the page"
        if ready_commits else "Everything finished has been published")

SECTION = f'''<!-- ===== homework + build stats: generated by tools/build_activity.py, not a personal block — please don't hand-edit ===== -->
{HOMEWORK}<section id="activity" class="ac">
<style>
 #activity{{grid-column:1/-1;border:1px solid var(--line,#E2D6B4);border-radius:10px;padding:20px 22px;margin-bottom:8px}}
{CSS}</style>

<h2>How this page is being built</h2>
<p class="ac-cap">Counted automatically from the project&rsquo;s history &mdash; {asof}.</p>

<div class="ac-kpis">
  <div class="ac-kpi"><span class="k">People building</span><span class="v">{len(showed)}</span></div>
  <div class="ac-kpi"><span class="k">Tiles live</span><span class="v">{sum(claimed.values())}</span><span class="n">of {len(tiles)}</span></div>
  <div class="ac-kpi"><span class="k">Saved changes</span><span class="v">{total_main}</span></div>
  <div class="ac-kpi"><span class="k">In the last day</span><span class="v">{saves_today}</span><span class="n">from {people_today} {'person' if people_today == 1 else 'people'}{f', {tiles_today} new tile' + ('' if tiles_today == 1 else 's') if tiles_today else ''}</span></div>
  <div class="ac-kpi"><span class="k">Ready to publish</span><span class="v">{total_stranded}</span><span class="n">one step away</span></div>
  <div class="ac-kpi"><span class="k">Busiest half hour</span><span class="v">{peak[1]}</span><span class="n">{peak[0].strftime('%-d %b, %H:%M')}</span></div>
</div>

{compact_funnel}

<p class="ac-sub" style="margin:16px 0 14px">{lead}. {len(open_tiles)} tile{'s are' if len(open_tiles) != 1 else ' is'} still open.
<a class="ac-more" href="analytics.html">See the full analytics &rarr;</a></p>

<div class="whatson">
  <div><span class="wh">Tonight</span><p><a href="#homework">Make your card yours</a> &mdash; three changes from home, published from Claude Code.</p></div>
  <div><span class="wh">Tomorrow</span><p>Day 3 &mdash; connect Claude to your own Gmail, Drive and Sheets, so it can work with your real data.</p></div>
  <div><span class="wh">Thursday</span><p>Day 4 &mdash; your own use cases, built live.</p></div>
</div>
</section>
<!-- ===== end build stats ===== -->'''

# ── the deep-dive page ──────────────────────────────────────────────────────
PAGE = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VV Demo Brain &mdash; How this page gets built</title>
<style>
  :root {{ --bg:#FBF3DA; --fg:#24303F; --dim:#5B6B7B; --line:#E2D6B4; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
         font-family:ui-monospace,SFMono-Regular,Menlo,monospace; line-height:1.6; padding:48px 24px; }}
  header, main {{ max-width:900px; margin:0 auto; }}
  header {{ margin-bottom:36px; }}
  h1 {{ font-size:1.7rem; margin:0 0 8px; }}
  .sub {{ color:var(--dim); margin:0 0 4px; }}
  .back {{ display:inline-block; margin-bottom:20px; color:var(--fg); font-size:.82rem;
           text-decoration:none; border-bottom:1px dotted var(--dim); }}
  footer {{ max-width:900px; margin:44px auto 0; color:var(--dim); font-size:.8rem;
            border-top:1px solid var(--line); padding-top:16px; }}
{CSS}</style>
</head>
<body>
<header>
  <a class="back" href="index.html">&larr; back to the wall</a>
  <h1>How this page gets built</h1>
  <p class="sub">A quiet look at what everyone has been making together. Every number is counted automatically from the project&rsquo;s own history &mdash; nothing here is typed by hand, and nothing is a ranking.</p>
  <p class="sub">{total_main} saved changes &middot; {len(branch_names)} draft copies &middot; {len(tiles)} tiles &middot; {asof}</p>
</header>

<main class="ac">

<div class="ac-kpis">
  <div class="ac-kpi"><span class="k">People building</span><span class="v">{len(showed)}</span><span class="n">have work in this project</span></div>
  <div class="ac-kpi"><span class="k">Tiles live</span><span class="v">{sum(claimed.values())}</span><span class="n">of {len(tiles)} on the page</span></div>
  <div class="ac-kpi"><span class="k">Saved changes</span><span class="v">{total_main}</span><span class="n">{total_content} built &#183; {total_merges} untangling</span></div>
  <div class="ac-kpi"><span class="k">Ready to publish</span><span class="v">{total_stranded}</span><span class="n">finished, one step away</span></div>
  <div class="ac-kpi"><span class="k">Busiest half hour</span><span class="v">{peak[1]}</span><span class="n">{peak[0].strftime('%-d %b, %H:%M')}</span></div>
</div>

<div class="ac-block">
  <h3>Little things worth noticing</h3>
  <p class="ac-sub">Not a scoreboard &mdash; just some nice moments the history happened to record. Everyone here helped build the same wall.</p>
  <div class="boards">{boards_html}</div>
</div>

<div class="ac-block">
  <h3>The path to the page</h3>
  <p class="ac-sub">Claiming a tile, writing something, and publishing it are three different steps. Each bar counts the people who cleared that step; the line beneath is the work still waiting there.</p>
  {funnel_svg}
  <details><summary>Show as a table</summary>
    <table><thead><tr><th>Step</th><th>People</th><th>Means</th></tr></thead><tbody>{table_rows}</tbody></table>
  </details>
</div>

<div class="ac-block ac-wrap">
  <h3>When the work happened</h3>
  <p class="ac-sub">Saved changes reaching the shared page, in half-hour blocks. Two live sessions, two peaks &mdash; and a steady tail of people carrying on by themselves.</p>
  {timeline_svg}
  <div class="ac-tip" id="ac-tip"></div>
  <details><summary>Show as a table</summary>
    <table><thead><tr><th>Hour</th><th>Saved changes</th></tr></thead><tbody>{time_rows}</tbody></table>
  </details>
</div>

<div class="ac-cols ac-block">
  <div>
    <h3>Ready to publish</h3>
    <p class="ac-sub">Finished work sitting in draft copies. Copy the line under your name and it is live in about a minute.</p>
    <ul class="ac-list">{ready_items}</ul>
  </div>
  <div>
    <h3>Tiles still open</h3>
    <p class="ac-sub">Already on the page, waiting for someone. The shortest route from opening the project to seeing your own work live.</p>
    <ul class="ac-list">{open_items}</ul>
  </div>
</div>

<div class="ac-block">
  <h3>What we could make easier</h3>
  <p class="ac-sub">None of this is about how anyone worked &mdash; it is about how the project is arranged, and every one of them has an easier arrangement. The bar shows the cost in one picture.</p>
  {merge_bar}
  <p class="ac-legend">
    <span><i style="background:#2a78d6"></i>{total_content} saves that built something</span>
    <span><i style="background:#eb6834"></i>{total_merges} saves that only untangled edits ({merge_pct}%)</span>
  </p>
  <ol class="ac-friction">{friction_items}</ol>
</div>

<div class="ac-block">
  <h3>The short version</h3>
  <ul class="ac-reads">
    <li><b>Starting was never the hard part.</b> {len(showed)} of {len(tiles)} people opened the project and {len(real)} wrote something of their own &mdash; {len(onmain)} got it published. The last step is where people stall, and that is a setup problem, not a skill problem.</li>
    <li><b>Somebody tested the edges &mdash; and that is a skill.</b> {len(cross_edits)} people made saves landing inside a tile other than their own, and {len(theme_edits)} changed the shared theme every tile sits on. Vernon did both: restyled another person&rsquo;s card, then switched the page background. Nothing stopped either change, because nothing is set up to stop anyone. Probing what a shared system actually permits &mdash; rather than what its instructions claim &mdash; is what testing looks like, and it surfaced a genuine gap, now listed above.</li>
    <li><b>One save in three is spent untangling.</b> {total_merges} of {total_main} saves exist only because {len(showed)} people share one file. It is the number that would fall furthest with a single change.</li>
    <li><b>{total_stranded} finished save{'s' if total_stranded != 1 else ''} are waiting in draft copies.</b> Not abandoned &mdash; finished. Publishing them is the cheapest way to make this page more complete today.</li>
    <li><b>Helping someone else publish works.</b> {len(rescued)} people&rsquo;s tiles are live because someone finished the last step for them rather than waiting.</li>
    <li><b>{len(open_tiles)} tiles are still open.</b> The easiest wins left on the board.</li>
  </ul>
</div>

<div class="ac-block">
  <h3>The words, in plain English</h3>
  <p class="ac-sub">The tools have their own vocabulary. Here it is translated, with the technical word beside it.</p>
  <dl class="ac-glossary">{glossary_items}</dl>
</div>

<p class="ac-foot">The steps are strictly nested: each row counts a subset of the row above it. &ldquo;Their tile is live&rdquo; counts only people who published their own tile; {len(rescued)} further tiles are live because someone else finished the last step for them, which is why the wall reads {sum(claimed.values())}.</p>

</main>
<footer>Regenerate with <code>python3 tools/build_activity.py</code> &middot; <a href="index.html" style="color:inherit">back to the wall</a></footer>
<script>{TOOLTIP_JS}</script>
</body>
</html>
'''

# ── write both ──────────────────────────────────────────────────────────────
# Find the whole generated region: from the FIRST banner (any generation of it)
# to the LAST closing marker. Matching every historical banner prefix means a
# renamed banner can never orphan the old block and silently duplicate it — the
# bug that once stacked four homework blocks on the wall.
STARTS = ('<!-- ===== activity analytics', '<!-- ===== build stats',
          '<!-- ===== homework + build stats', '<section id="leaderboard">')
ENDS = ('<!-- ===== end activity analytics ===== -->', '<!-- ===== end build stats ===== -->')
found = [html.index(m) for m in STARTS if m in html]
if found:
    start = min(found)
else:
    start = html.index('<section id="activity"')
end = max((html.rindex(c) + len(c) for c in ENDS if c in html), default=-1)
if end == -1:
    end = html.index('</section>', start) + len('</section>')
assert '===== START ' not in html[start:end], "refusing to write: a personal card block is inside the generated region"
open(f"{REPO}/index.html", "w").write(html[:start] + SECTION + html[end:])
open(f"{REPO}/analytics.html", "w").write(PAGE)

print("funnel", [(l, v) for l, v, _ in FUNNEL])
print("ready", [(p['name'], p['unmerged']) for p in ready], "open tiles", len(open_tiles))
print("explorers (edited beyond own tile)", explorers)
print(f"main={total_main} content={total_content} merges={total_merges} pct={merge_pct} waiting={total_stranded}")
print("wrote: index.html (compact dashboard) + analytics.html (deep dive)")
