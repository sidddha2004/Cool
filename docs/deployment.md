# Running the COOL benchmark on AWS Graviton (human steps)

Nothing here was executed by the assistant: no AWS credentials, no Marketplace subscription, no resources exist.
Marketplace details below come from secondary sources (the official pages returned HTTP 403 to our fetch on 2026-10-14) -
**re-verify every item in the listing before subscribing.**

| listing (per research, unverified) | version | instances | notes |
|---|---|---|---|
| COOL for Graviton4 `prodview-fdvbfiewzuehs` | 3.1, "built on OpenCV 5.0" | c8g/m8g/r8g | venvs under `/opt/cool/venvs`, Python 3.10-3.12 |
| COOL for Graviton5 `prodview-igdweaoo6prb6` | 1.0, OpenCV 5.1.0 + KleidiCV | c9g/m9g | Python 3.12-3.14; recommended ≥ m9g.4xlarge |
| COOL for Graviton2 `prodview-jz6w32bsfv6sg` | 1.3 | c6g/m6g/r6g | OpenCV version not stated |
7-day free trial then usage-based software fee + EC2 cost. License check uses instance metadata: copied/snapshot AMIs fail.

1. **You** subscribe to a COOL AMI and launch an instance (Ubuntu 24.04, Graviton generation matching the AMI). Use a security
   group with inbound SSH from your IP only, and an instance profile with **no permissions**.
2. Create `config/remote.json` from `config/remote.example.json` (git-ignored). Pre-seed `~/.ssh/known_hosts` from the console output.
3. In Claude Code (or CLI): `python -m coolguard.cli remote --candidate candidates/scanner_v7.py --corpus artifacts/corpora/final --repeats 30 --threads 4`
   (max 3 runs per `artifacts/remote_budget.json`).
4. `verified_cool_on_graviton` is true only if the remote probe shows `cv2` imported from `/opt/cool/...` on `aarch64` and a different
   module path than the pip baseline. Inspect `artifacts/experiments/remote-*.artifacts/remote_out/` (`probe_*.json`,
   `*_build_info.txt`, 10 raw bench files). Check the COOL build's OpenCV version equals 5.0.0 before attributing differences to COOL.
5. **Cleanup:** terminate the instance, delete the key pair/security group you created, and cancel the Marketplace subscription
   (the trial converts to paid). Confirm in the EC2 console that no instance/volume/Elastic IP remains.

Cost: instance-hours × (EC2 + software fee). Per the research, e.g. m8g.4xlarge software fee ≈ $0.04/h plus EC2 - confirm current pricing.
