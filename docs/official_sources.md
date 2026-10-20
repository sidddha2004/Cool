# Sources and verification status (checked 2026-10-14)

**Limitation:** `opencv26.devpost.com`, its `/rules` page, `opencv.org` and `docs.opencv.org` returned HTTP 403 to our fetch tool.
Everything below marked "secondary" must be re-read in a browser before submission.

| claim | source | status |
|---|---|---|
| Final deadline Oct 26 2026; Devpost header may show 11:45 PM PDT vs 11:59 PM PT elsewhere → target 11:45 PM PDT | opencv.org page via search summary; GitHub repo quoting Devpost | secondary |
| Award criteria (COOL must run the claimed core workload on Graviton/Arm; Agentic Vision: visual evidence must change the next action; AI coding assistant alone does not qualify) | https://github.com/archipelagoing/AWSOpenCVAICompetition2026 (quotes Devpost) | secondary |
| Overall rubric weights (30/20/20/10/10/10) | task brief (`important.md`) | **not independently verified** |
| Submission: tech report, public/judge repo, architecture diagram, working demo, ≤5 min video | same GitHub quote | secondary |
| COOL = Cloud-Optimized OpenCV Library, AWS Marketplace AMIs for Graviton2/4/5 | https://aws.amazon.com/marketplace/pp/prodview-igdweaoo6prb6 and sibling listings | secondary (search/summary) |
| OpenCV 5.0.0.93 on PyPI (2026-07-02) | `pip index versions` run locally 2026-10-14; installed and imported 5.0.0 | **verified by execution** |
| `mcp` 2.3.0 on PyPI; 2.x renamed FastMCP→MCPServer | `pip index`, import error message, tests | **verified by execution** |
| Claude Code MCP/subagent docs | https://code.claude.com/docs/en/mcp (not fetched) ; `claude mcp list` run locally shows project server pending approval | partial |

Subagent use: two research subagents (competition, COOL) and two reviewers (security, evaluation) ran; the independent
"competition red-team" reviewer was **not** run.
