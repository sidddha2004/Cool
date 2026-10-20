"""Build artifacts/report/index.html from the latest loop trace and saved experiments (no hand-entered numbers)."""
from __future__ import annotations

import html
import json
import shutil
import sys

from coolguard import experiments, paths, tools


def main() -> int:
    tid = (paths.ARTIFACTS / "last_trace_id.txt").read_text().strip() if len(sys.argv) < 2 else sys.argv[1]
    ev = experiments.read_trace(tid)
    out = paths.ARTIFACTS / "report"
    shutil.rmtree(out, ignore_errors=True)
    (out / "img").mkdir(parents=True)
    by = lambda s: [e for e in ev if e["step"] == s]
    rows = []
    for e in by("candidate_verified"):
        pc = "; ".join(f"{p['corpus']} {p['passed']}/{p['n']}" for p in e["evidence"]["per_corpus"])
        rows.append(f"<tr><td>{html.escape(e['candidate'].split('/')[-1])}</td><td class='{e['verdict']}'>{e['verdict']}</td>"
                    f"<td>{pc}</td><td>{e['evidence']['n_regressed']}</td><td>{e['evidence']['regressed_categories']}</td></tr>")
    decisions = "".join(
        f"<li><b>{html.escape(d['action'])}</b> (iteration {d['iteration']}, based on <code>{d['based_on_experiment']}</code>)<br>"
        f"<i>{html.escape(d['rationale'])}</i><br><small>evidence: {html.escape(json.dumps(d['evidence'])[:300])}</small></li>"
        for d in by("decision"))
    post = "".join(f"<li><b>{html.escape(d['action'])}</b>: {html.escape(d['rationale'])}</li>" for d in by("post_verification_decision"))

    # per-category on the unseen 'final' corpus, from saved experiment records
    fin = by("final_check")[-1]
    a, b = experiments.load(fin["baseline"]), experiments.load(fin["candidate"])
    cat_rows = "".join(
        f"<tr><td>{c}</td><td>{a['summary']['by_category'][c]['passed']}/{a['summary']['by_category'][c]['n']}</td>"
        f"<td>{b['summary']['by_category'][c]['passed']}/{b['summary']['by_category'][c]['n']}</td></tr>"
        for c in a["summary"]["by_category"])

    # visual: first failing case of the baseline on 'final' (shadow if present), re-run both candidates with stage output
    fails = [r for r in a["results"] if not r["accepted"]]
    pick = next((r for r in fails if r["category"] == "shadow"), fails[0])
    imgs = []
    for label, cand in (("v1 (baseline)", a["candidate"]), ("v7 (accepted candidate)", b["candidate"])):
        rec = tools.run_visual_regression_suite(cand, "artifacts/corpora/final", case_ids=[pick["case_id"]])
        full = experiments.load(rec["experiment_id"])
        art = paths.Path(full["artifact_dir"]) / "stages" / pick["case_id"] if hasattr(paths, "Path") else None
        from pathlib import Path
        art = Path(full["artifact_dir"]) / "stages" / pick["case_id"]
        if not art.exists():   # candidate passed -> stages were not saved for passes; rerun saving all
            from coolguard import runner
            full = runner.run_suite(cand, "artifacts/corpora/final", case_ids=[pick["case_id"]], save_stages="all")
            art = Path(full["artifact_dir"]) / "stages" / pick["case_id"]
        name = f"{label.split()[0]}_overlay.png"
        shutil.copy(art / "overlay_gt_green_det_red.png", out / "img" / name)
        r0 = full["results"][0]
        imgs.append(f"<figure><img src='img/{name}' width=420><figcaption>{label}: IoU {r0['iou']:.2f}, "
                    f"corner err {r0['corner_err']:.3f}, accepted={r0['accepted']}<br>green=ground truth, red=detected</figcaption></figure>")

    remote = by("remote_benchmark")[-1]
    html_doc = f"""<!doctype html><meta charset=utf-8><title>COOLGuard report</title>
<style>body{{font:14px system-ui;max-width:1000px;margin:2em auto}}td,th{{border:1px solid #ccc;padding:4px 8px}}
.ACCEPT{{color:#060}}.REJECT{{color:#a00}}.PARTIAL{{color:#a60}}figure{{display:inline-block;margin:6px}}table{{border-collapse:collapse}}</style>
<h1>COOLGuard run report</h1><p>trace <code>{tid}</code>. All numbers below are read from saved experiment records.</p>
<h2>Candidate verification (regression-gated)</h2><table><tr><th>candidate</th><th>verdict</th><th>pass counts per corpus</th><th>regressions vs v1</th><th>regressed categories</th></tr>{''.join(rows)}</table>
<h2>Policy decisions driven by measured evidence</h2><ol>{decisions}</ol><h3>Post-verification decisions</h3><ol>{post}</ol>
<h2>Unseen corpus ('final', synthetic): v1 vs accepted candidate</h2><table><tr><th>category</th><th>v1</th><th>v7</th></tr>{cat_rows}</table>
<p>Case shown: <code>{pick['case_id']}</code> (a v1 failure)</p>{''.join(imgs)}
<h2>COOL / AWS Graviton</h2><p><b>status: {remote.get('status')}</b>; verified_on_graviton={remote.get('verified_on_graviton')}. {html.escape(str(remote.get('reason')))}</p>
<h2>Limitations</h2><ul><li>Synthetic corpus only; single page, fully in frame, uniform background. No real-photo validation.</li>
<li><code>dev</code> and <code>heldout</code> were used while developing candidates; only <code>final</code> was untouched during iteration.</li>
<li>Candidates are authored by the coding assistant; the policy chooses actions, not code.</li>
<li>Automated ACCEPT is not production-ready: human review required.</li></ul>"""
    (out / "index.html").write_text(html_doc, encoding="utf-8")
    print("wrote", out / "index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
