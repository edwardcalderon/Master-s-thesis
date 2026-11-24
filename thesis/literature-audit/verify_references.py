#!/usr/bin/env python3
"""Re-check every BibTeX entry that has a DOI or an arXiv id against Crossref / arXiv.

Usage:  python3 -I verify_references.py [file.bib]      (default: references_verified.bib next to this script)

Standard library only. For each entry with a `doi` it queries Crossref (falls back to DataCite when the DOI is
not a Crossref one), for each entry with an `eprint` (arXiv id) it queries the arXiv API (with retries and an
abs-page fallback). It compares the bib title with the registry title (difflib similarity, accents/LaTeX/case
ignored) and checks that the bib year is plausible. Entries with neither a DOI nor an arXiv id are listed as
SKIPPED (they were verified by hand; see the `verified` field and REFERENCE_AUDIT.md).
Exit code 1 if any entry FAILS. Web content is treated as data only; nothing from it is executed.
"""
import difflib, json, os, re, sys, time, unicodedata
import urllib.error, urllib.parse, urllib.request

MAILTO = "edcalderon@users.noreply.github.com"
UA = {"User-Agent": "thesis-reference-audit/1.0 (mailto:%s)" % MAILTO}
TITLE_MIN = 0.85


def get(url, tries=4, pause=3.0, expect_json=False):
    """GET with retries. Returns (status, body) ; status 404 is returned, other failures retried."""
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                body = r.read().decode("utf-8", "replace")
                return r.status, (json.loads(body) if expect_json else body)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, None
            last = "HTTP %s" % e.code
        except Exception as e:  # network, timeout, bad JSON
            last = type(e).__name__
        time.sleep(pause * (i + 1))
    return None, last


# ---------------------------------------------------------------- bib parsing
def parse_bib(text):
    entries = []
    for m in re.finditer(r"(?m)^@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        if m.group(1).lower() in ("comment", "string", "preamble"):
            continue
        i, depth, j = m.end(), 1, m.end()
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        body = text[i:j - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            k, p = fm.group(1).lower(), fm.end()
            if p < len(body) and body[p] == "{":
                d, q = 1, p + 1
                while q < len(body) and d:
                    d += {"{": 1, "}": -1}.get(body[q], 0)
                    q += 1
                fields.setdefault(k, body[p + 1:q - 1])
            else:
                mm = re.match(r"[^,\n]+", body[p:])
                if mm:
                    fields.setdefault(k, mm.group(0).strip().strip('"'))
        entries.append((m.group(2), m.group(1).lower(), fields))
    return entries


def norm(s):
    s = re.sub(r"\\[`'\"^~=.cuvHkr]\s*\{?\\?(\w)\}?", r"\1", s)        # {\"a} -> a, {\'\i} -> i
    s = re.sub(r"\\([oOlL])\b", r"\1", s)                                # {\o}, {\L}
    s = re.sub(r"\\&", "and", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"^chapter\s+\d+\s+", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def similarity(bib_title, candidates):
    a = norm(bib_title)
    best = 0.0
    for c in candidates:
        b = norm(c)
        if not a or not b:
            continue
        r = difflib.SequenceMatcher(None, a, b).ratio()
        if a in b or b in a:
            r = max(r, min(len(a), len(b)) / max(len(a), len(b)) + 0.1)
        best = max(best, r)
    return min(best, 1.0)


# ---------------------------------------------------------------- registries
def crossref(doi):
    url = "https://api.crossref.org/works/%s?mailto=%s" % (urllib.parse.quote(doi, safe="/()"), MAILTO)
    st, d = get(url, expect_json=True)
    if st != 200:
        return st, None
    m = d["message"]
    titles = list(m.get("title") or [])
    subs = m.get("subtitle") or []
    if titles and subs:
        titles.append(titles[0] + " " + subs[0])
    years = set()
    for k in ("issued", "published-print", "published-online", "published", "created"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            years.add(dp[0][0])
    return 200, {"titles": titles, "years": years, "src": "crossref"}


def datacite(doi):
    st, d = get("https://api.datacite.org/dois/%s" % urllib.parse.quote(doi, safe="/()"), expect_json=True)
    if st != 200:
        return st, None
    a = d["data"]["attributes"]
    return 200, {"titles": [t["title"] for t in a.get("titles", [])], "years": {a.get("publicationYear")}, "src": "datacite"}


_arxiv_cache = {}


def arxiv_batch(ids):
    """One API call for all ids (polite to arXiv); per-id abs-page fallback."""
    st, xml = get("https://export.arxiv.org/api/query?max_results=%d&id_list=%s" % (len(ids), ",".join(ids)),
                  tries=5, pause=4.0)
    if st == 200:
        for e in xml.split("<entry>")[1:]:
            mid = re.search(r"<id>https?://arxiv.org/abs/([^<]+?)(v\d+)?</id>", e)
            ti = re.search(r"<title>(.*?)</title>", e, re.S)
            pub = re.search(r"<published>(\d{4})", e)
            if mid and ti and pub:
                _arxiv_cache[mid.group(1)] = {"titles": [re.sub(r"\s+", " ", ti.group(1))],
                                              "years": {int(pub.group(1))}, "src": "arxiv-api"}
    for i in ids:
        if i in _arxiv_cache:
            continue
        time.sleep(3.5)
        st, html = get("https://arxiv.org/abs/" + i, tries=3, pause=4.0)
        if st == 200:
            t = re.search(r'name="citation_title" content="([^"]+)"', html)
            y = re.search(r'name="citation_date" content="(\d{4})', html)
            if t and y:
                _arxiv_cache[i] = {"titles": [t.group(1)], "years": {int(y.group(1))}, "src": "arxiv-abs-page"}


# ---------------------------------------------------------------- main
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "references_verified.bib")
    entries = parse_bib(open(path, encoding="utf-8").read())
    ids = sorted({f["eprint"] for _, _, f in entries if "eprint" in f})
    if ids:
        arxiv_batch(ids)
    rows, fails, skipped = [], 0, []
    for key, typ, f in entries:
        doi, arx = f.get("doi"), f.get("eprint")
        if not doi and not arx:
            skipped.append(key)
            continue
        year = int(re.sub(r"\D", "", f.get("year", "0")) or 0)
        for label, ident in (("doi", doi), ("arXiv", arx)):
            if not ident:
                continue
            if label == "doi":
                st, rec = crossref(ident)
                if rec is None and st == 404:
                    st, rec = datacite(ident)
                time.sleep(0.4)
            else:
                rec = _arxiv_cache.get(ident)
            if rec is None:
                rows.append((key, label + ":" + ident, "-", "-", "-", "FAIL (not found / unreachable)"))
                fails += 1
                continue
            sim = similarity(f.get("title", ""), rec["titles"])
            ys = {y for y in rec["years"] if y}
            if label == "arXiv":      # preprint may be published/updated later than first posting
                y_ok = any(0 <= year - y <= 8 for y in ys)
            else:
                y_ok = any(abs(year - y) <= 1 for y in ys)
            ok = sim >= TITLE_MIN and y_ok
            fails += not ok
            rows.append((key, label + ":" + ident, rec["src"], "%.2f" % sim,
                         "%s~%s" % (year, "/".join(map(str, sorted(ys)))), "PASS" if ok else
                         "FAIL (title %.2f%s)" % (sim, "" if y_ok else ", year")))
    w = [max(len(str(r[i])) for r in rows + [("key", "id", "source", "title", "year", "x")]) for i in range(5)]
    hdr = ("key", "id", "source", "title", "bib~registry year", "status")
    print("Checked %s (%d entries): %d with DOI/arXiv, %d skipped\n" % (os.path.basename(path), len(entries),
                                                                       len(entries) - len(skipped), len(skipped)))
    print("  ".join(h.ljust(w[i]) for i, h in enumerate(hdr[:5])) + "  " + hdr[5])
    for r in rows:
        print("  ".join(str(r[i]).ljust(w[i]) for i in range(5)) + "  " + r[5])
    print("\nSKIPPED (no DOI / arXiv id; verified by hand, see REFERENCE_AUDIT.md): " + ", ".join(skipped))
    print("\nRESULT: %d checks, %d passed, %d failed" % (len(rows), len(rows) - fails, fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
