# Security

## Trust model - read this first
**Candidate scanner code is executed as trusted code.** The worker is a separate process with a timeout, an
environment *allow-list* (no cloud/API credentials are passed), an image-size cap (`OPENCV_IO_MAX_IMAGE_PIXELS`), and a
report written to a file (stdout noise or forged stdout JSON is ignored). It is **not a sandbox**: it runs as the same OS user
with the same filesystem and network, so malicious candidate code could read `~/.aws`, `~/.ssh`, or `config/remote.json`
and could rewrite experiment records. Only run candidates you (or your coding assistant) wrote and reviewed; for untrusted
code use a container/VM or a low-privilege user - not implemented.

## Controls implemented
- MCP tools are allow-listed; no shell or free-form file access. Candidates only from `candidates/`, corpora only from
  `artifacts/corpora/` (`paths.resolve_inside`, symlink-resolving). Tested (`test_path_traversal_and_bad_inputs_rejected`).
- `trace_id` / `experiment_id` validated (`^[A-Za-z0-9_-]{1,80}$`) - an independent review found `trace_id` path traversal; fixed and tested.
- Corpus limits (400 cases, 2048 px, 20 seeds), repeat/timeout caps, per-run timeouts.
- Remote: fixed command set, host/user/venv regex-validated, no caller shell text, billable-run budget persisted on disk
  (`artifacts/remote_budget.json`, max 3, not a tool parameter), remote `timeout`.
- Worker stderr is truncated and labelled untrusted before it reaches the model (it may contain prompt-injection text).
- No automatic commit/push/deploy; ACCEPT only *preserves* a candidate for human review.

## Known gaps (from the security review, not yet fixed)
- No memory/CPU limits or process-tree kill (grand-child processes can outlive a timeout; on Windows especially).
- Remote: candidate runs with the instance's privileges incl. IMDS - use an instance profile with **no permissions**, IMDSv2
  hop-limit 1. `StrictHostKeyChecking=accept-new` is trust-on-first-use. Remote probe files are trusted as produced by the host.
- `pip install` on the instance is version-constrained but not hash-pinned.
- `manifest.json` in a corpus is trusted (a malicious candidate could plant one).
