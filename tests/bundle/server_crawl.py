#!/usr/bin/env python3
"""
Headless-browser crawl of a running StrictDoc server (bundle verification).

Fails on: any HTTP response >= 400 (documents, JS, CSS, fonts, icons, images,
XHR/fetch, Turbo streams), any failed request (connection refused, aborted
asset loads), any browser console message of type "error", and any uncaught
page exception (pageerror).

Usage:
  python server_crawl.py --base-url http://127.0.0.1:8001 --out results.json \
      [--max-pages 300] [--smoke] [--forms] [--ignore-console REGEX]

Exit code 0 = no failures, 1 = failures found, 2 = crawler error.
"""
import argparse
import json
import re
import sys
import time
from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

from playwright.sync_api import sync_playwright

# Never follow: destructive or download-only GET endpoints, websockets,
# Turbo-stream action fragments (exercised separately by clicking), PDFs.
SKIP_PATTERNS = [
    r"/actions/",
    r"delete",
    r"remove",
    r"/export_html2pdf/",
    r"/reqif/export",
    r"/ws/",
    r"\.(pdf|zip|reqif|reqifz|xlsx|xls|json)$",
]
# Caps per URL category so huge projects (hundreds of source files) don't
# dominate the crawl budget.
CATEGORY_CAPS = [
    ("source_file", re.compile(r"_source_files/|/source_file"), 25),
    ("doc_deep_trace", re.compile(r"-DEEP-TRACE\.html$"), 20),
    ("doc_trace", re.compile(r"-TRACE\.html$"), 20),
    ("doc_table", re.compile(r"-TABLE\.html$"), 20),
    ("doc_pdf_view", re.compile(r"-PDF\.html$"), 20),
    ("doc", re.compile(r"\.html$"), 60),
]


def categorize(path):
    for name, rx, cap in CATEGORY_CAPS:
        if rx.search(path):
            return name, cap
    return "screen", 10_000


class PageRecorder:
    def __init__(self, base_netloc, ignore_console):
        self.base_netloc = base_netloc
        self.ignore_console = ignore_console
        self.reset()

    def reset(self):
        self.bad_responses = []
        self.failed_requests = []
        self.console_errors = []
        self.page_errors = []
        self.responses = 0

    def on_response(self, resp):
        self.responses += 1
        if resp.status >= 400:
            self.bad_responses.append(
                {
                    "url": resp.url,
                    "status": resp.status,
                    "type": resp.request.resource_type,
                }
            )

    def on_requestfailed(self, req):
        failure = req.failure or ""
        # Navigations we cancel ourselves are not asset failures.
        if "ERR_ABORTED" in str(failure) and req.resource_type == "document":
            return
        self.failed_requests.append(
            {"url": req.url, "type": req.resource_type, "failure": str(failure)}
        )

    def on_console(self, msg):
        if msg.type != "error":
            return
        text = msg.text
        if self.ignore_console and re.search(self.ignore_console, text):
            return
        loc = msg.location or {}
        self.console_errors.append({"text": text[:500], "location": loc.get("url")})

    def on_pageerror(self, err):
        self.page_errors.append(str(err)[:500])

    def snapshot(self):
        return {
            "bad_responses": list(self.bad_responses),
            "failed_requests": list(self.failed_requests),
            "console_errors": list(self.console_errors),
            "page_errors": list(self.page_errors),
            "responses": self.responses,
        }


KNOWN_UPSTREAM = []


def split_known(entry):
    """Move failures matching a --known-upstream regex to entry['known_upstream']."""
    if not KNOWN_UPSTREAM:
        return
    page = entry.get("url", "")
    known = []
    for key, field in (("bad_responses", "url"), ("failed_requests", "url"),
                       ("console_errors", "location")):
        keep = []
        for item in entry.get(key, []):
            probe = f"{page} {item.get(field) or ''}"
            if any(re.search(rx, probe) for rx in KNOWN_UPSTREAM):
                known.append({key: item})
            else:
                keep.append(item)
        entry[key] = keep
    if known:
        entry["known_upstream"] = known


def is_fail(rec):
    split_known(rec)
    return bool(
        rec["bad_responses"]
        or rec["failed_requests"]
        or rec["console_errors"]
        or rec["page_errors"]
        or rec.get("status", 200) >= 400
        or rec.get("error")
    )


def settle(page, timeout_ms=15000):
    try:
        page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        pass


def crawl(page, rec, base_url, max_pages, seeds, smoke=False):
    smoke_seeded = False
    base = urlparse(base_url)
    queue = deque(urljoin(base_url, s) for s in seeds)
    seen = set()
    cat_counts = {}
    results = []
    while queue and len(results) < max_pages:
        url = urldefrag(queue.popleft())[0]
        if url in seen:
            continue
        seen.add(url)
        path = urlparse(url).path
        cat, cap = categorize(path)
        if cat_counts.get(cat, 0) >= cap:
            continue
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        rec.reset()
        entry = {"url": url, "category": cat}
        t0 = time.time()
        try:
            resp = page.goto(url, wait_until="load", timeout=90000)
            entry["status"] = resp.status if resp else 0
            settle(page)
            hrefs = page.eval_on_selector_all(
                "a[href]", "els => els.map(e => e.href)"
            )
            entry["is_document"] = (
                page.locator('[data-testid="node-root"]').count() > 0
            )
            if smoke and not smoke_seeded:
                smoke_seeded = True
                docs = page.eval_on_selector_all(
                    '[data-testid="tree-file-link"]', "els => els.map(e => e.href)"
                )
                docs = [d for d in docs if d.endswith(".html")]
                if docs:
                    queue.appendleft(docs[0])
            elif smoke and entry["is_document"]:
                # Visit the view switches this document actually links to.
                for h in hrefs:
                    if re.search(r"-(TABLE|TRACE|DEEP-TRACE)\.html$", h):
                        queue.appendleft(urldefrag(h)[0])
        except Exception as e:  # noqa: BLE001
            entry["error"] = str(e)[:500]
            hrefs = []
        entry["load_ms"] = int((time.time() - t0) * 1000)
        entry.update(rec.snapshot())
        entry["fail"] = is_fail(entry)
        results.append(entry)
        print(
            f"[{'FAIL' if entry['fail'] else 'PASS'}] {entry.get('status')} "
            f"{cat:15s} {url} ({entry['load_ms']} ms, {entry['responses']} req)",
            flush=True,
        )
        for h in hrefs:
            h = urldefrag(h)[0]
            u = urlparse(h)
            if u.scheme not in ("http", "https") or u.netloc != base.netloc:
                continue
            if any(re.search(p, h) for p in SKIP_PATTERNS):
                continue
            if h not in seen:
                queue.append(h)
    return results


FORM_ACTIONS = [
    # (screen kind, data-testid of the trigger, description)
    ("index", "project-edit-title-action", "edit project title form"),
    ("index", "tree-add-document-action", "new document form"),
    ("doc", "document-edit-config-action", "edit document config form"),
    ("doc", "node-edit-action", "edit requirement form"),
    ("doc", "node-add-requirement-below-action", "new requirement form"),
    ("doc", "node-add-section-below-action", "new section form"),
    ("doc", "node-add-text-below-action", "new text node form"),
    ("doc", "node-move-action", "move node dialog"),
]


def find_doc_with(page, doc_urls, testid):
    for u in doc_urls[:8]:
        try:
            page.goto(u, wait_until="load", timeout=90000)
            if page.locator(f'[data-testid="{testid}"]').count() > 0:
                return u
        except Exception:  # noqa: BLE001
            pass
    return doc_urls[0] if doc_urls else None


def open_forms(page, rec, base_url, doc_urls):
    results = []
    for kind, testid, desc in FORM_ACTIONS:
        url = base_url if kind == "index" else find_doc_with(page, doc_urls, testid)
        if url is None:
            continue
        entry = {"form": desc, "testid": testid, "url": url}
        try:
            page.goto(url, wait_until="load", timeout=90000)
            settle(page)
            rec.reset()
            n_forms_before = page.locator("form").count()
            loc = page.locator(f'[data-testid="{testid}"]').first
            if loc.count() == 0:
                entry["error"] = f"trigger {testid} not found on page"
            else:
                # Triggers live in hover menus; a DOM click goes through
                # Turbo's document-level click handler like a real click.
                loc.evaluate("el => el.click()")
                try:
                    page.wait_for_function(
                        "n => document.querySelectorAll('form').length > n "
                        "|| document.querySelector('[data-testid=form-cancel-action],"
                        "[data-testid=move-node-cancel],[data-testid=move-node-tree]')",
                        arg=n_forms_before,
                        timeout=15000,
                    )
                    entry["form_opened"] = True
                except Exception:
                    entry["form_opened"] = False
                    entry["error"] = "form did not appear within 15s"
                settle(page, 8000)
            entry.update(rec.snapshot())
        except Exception as e:  # noqa: BLE001
            entry["error"] = str(e)[:500]
            entry.update(rec.snapshot())
        entry["fail"] = is_fail(entry)
        results.append(entry)
        print(
            f"[{'FAIL' if entry['fail'] else 'PASS'}] form: {desc} "
            f"({entry.get('error', 'opened')})",
            flush=True,
        )
    return results


def search_checks(page, rec, base_url, query):
    out = []
    for path in [f"/search?q={query}", "/search?q=REQ"]:
        rec.reset()
        entry = {"url": urljoin(base_url, path), "category": "search"}
        try:
            resp = page.goto(entry["url"], wait_until="load", timeout=60000)
            entry["status"] = resp.status if resp else 0
            settle(page)
        except Exception as e:  # noqa: BLE001
            entry["error"] = str(e)[:500]
        entry.update(rec.snapshot())
        entry["fail"] = is_fail(entry)
        out.append(entry)
        print(f"[{'FAIL' if entry['fail'] else 'PASS'}] search {entry['url']}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-pages", type=int, default=300)
    ap.add_argument("--smoke", action="store_true", help="index + 3 pages + 1 form")
    ap.add_argument("--forms", action="store_true")
    ap.add_argument("--search-query", default="requirement")
    ap.add_argument("--ignore-console", default=None)
    ap.add_argument("--extra-seed", action="append", default=[])
    ap.add_argument("--known-upstream", action="append", default=[],
                    help="regex over '<page-url> <resource-url>'; matches are "
                         "recorded as known_upstream instead of failures")
    args = ap.parse_args()
    base_url = args.base_url.rstrip("/") + "/"
    KNOWN_UPSTREAM.extend(args.known_upstream)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        rec = PageRecorder(urlparse(base_url).netloc, args.ignore_console)
        page.on("response", rec.on_response)
        page.on("requestfailed", rec.on_requestfailed)
        page.on("console", rec.on_console)
        page.on("pageerror", rec.on_pageerror)

        seeds = ["/"] + args.extra_seed
        max_pages = 8 if args.smoke else args.max_pages
        pages = crawl(page, rec, base_url, max_pages, seeds, smoke=args.smoke)
        searches = search_checks(page, rec, base_url, args.search_query)
        doc_urls = [
            r["url"] for r in pages if r.get("is_document") and r["category"] == "doc"
        ]
        forms = []
        if args.forms or args.smoke:
            forms = open_forms(page, rec, base_url, doc_urls)
            if args.smoke:
                forms = [f for f in forms if f["testid"] in (
                    "node-edit-action", "project-edit-title-action")]
        browser.close()

    all_entries = pages + searches + forms
    summary = {
        "base_url": base_url,
        "pages": len(pages),
        "searches": len(searches),
        "forms": len(forms),
        "failures": sum(1 for e in all_entries if e["fail"]),
        "known_upstream": sum(1 for e in all_entries if e.get("known_upstream")),
        "categories": sorted({e["category"] for e in pages}),
    }
    with open(args.out, "w") as f:
        json.dump({"summary": summary, "pages": pages, "searches": searches,
                   "forms": forms}, f, indent=2)
    print(json.dumps(summary, indent=2))
    sys.exit(1 if summary["failures"] else 0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"crawler error: {e}", file=sys.stderr)
        sys.exit(2)
