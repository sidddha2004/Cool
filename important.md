# COOLGuard: Autonomous Visual Debugging and Performance Engineering for AI Coding Agents

## 1. YOUR ROLE AND MISSION

Act as the principal engineer, technical architect, computer-vision researcher, MCP specialist, cloud engineer, QA lead, and security reviewer responsible for delivering COOLGuard.

You are operating inside Claude Code and have access to its native tool-use capabilities. Use those capabilities aggressively but intelligently, including specialized subagents, parallel investigation, terminal commands, repository inspection, testing, and code review.

Your assignment is to BUILD the project, not merely propose an architecture.

You are responsible for taking the existing workspace from its actual current state to the strongest working, reproducible, demonstrable submission achievable within the available time.

You must:

1. Inspect the existing repository before making assumptions.
2. Independently verify the competition requirements and the current COOL/AWS integration requirements.
3. Investigate relevant technologies and their official documentation.
4. Design the complete system architecture.
5. Delegate independent investigations to specialized subagents.
6. Implement the system incrementally.
7. Run actual tests and experiments.
8. Integrate OpenCV 5, COOL, MCP, and AWS meaningfully.
9. Demonstrate an authentic agentic perception-decision-action workflow.
10. Produce reproducible evaluation results and evidence.
11. Review the project against every judging criterion.
12. Fix the highest-impact deficiencies before declaring completion.

Do not stop after producing a plan, architecture document, skeleton repository, or collection of placeholder files.

Continue through implementation, integration, testing, evaluation, documentation, and final review.

If an external prerequisite prevents complete execution, such as unavailable AWS credentials or an inaccessible COOL Marketplace subscription, implement and test everything that can safely be completed, document the exact blocker, and report which acceptance criteria remain unverified. Never fabricate a successful result.

The final product must be a credible engineering project that can be inspected, executed, understood, and evaluated by external judges.

---

# 2. PROJECT CONTEXT

Project name: COOLGuard.

Project category: Developer agents integrating COOL with Claude Code, Codex, Kiro, or other MCP-compatible systems.

Primary integration target: Claude Code.

Architecture objective: Build a reusable MCP-based developer-agent system that can later work with other compatible coding assistants.

Competition: OpenCV AI Competition 2026, powered by AWS.

Official competition page:
https://opencv26.devpost.com/

Official rules:
https://opencv26.devpost.com/rules

AWS Marketplace COOL listings:
https://aws.amazon.com/marketplace/

Official Claude Code MCP documentation:
https://code.claude.com/docs/en/mcp

Official Claude Code subagent documentation:
https://code.claude.com/docs/en/sub-agents

Official MCP specification:
https://modelcontextprotocol.io/

Research the relevant current documentation before settling implementation details. The URLs above are starting points, not substitutes for verifying the exact supported versions, APIs, licensing, deployment methods, and current competition requirements.

## The product we are building

COOLGuard is an autonomous visual debugging and performance-engineering assistant for AI-generated computer-vision code.

It integrates with Claude Code through MCP and provides specialized tools for:

* Inspecting OpenCV application environments.
* Understanding existing computer-vision pipelines.
* Generating controlled visual test cases.
* Executing real OpenCV 5 workloads.
* Detecting visual failures and regressions.
* Reproducing discovered failures.
* Helping a coding agent investigate and correct defects.
* Validating candidate fixes against regression tests.
* Benchmarking compatible implementations using COOL.
* Executing the core vision workload on AWS Graviton.
* Producing reproducible performance and correctness reports.

Its defining capability is an evidence-driven development loop.

**The system must do more than generate code: it must execute visual workloads, interpret their actual results, decide what to test or change next, and verify the consequences of those decisions.**

The primary demonstration should show an AI coding assistant producing or modifying a real computer-vision application, COOLGuard discovering a visual defect, the coding agent correcting the defect, and the corrected implementation passing regression tests.

A subsequent stage should demonstrate a compatible COOL workload executing on AWS Graviton and report real benchmark results.

---

# 3. FIRST PRINCIPLE: ELIMINATE UNVERIFIED ASSUMPTIONS

Before implementation, establish the facts.

Do not assume that:

* OpenCV 5 is installed.
* A particular OpenCV API exists in the installed version.
* The newest COOL Marketplace listing matches an older listing.
* A specific COOL package works on the local operating system.
* COOL accelerates every OpenCV operation.
* AWS credentials are configured.
* The user has subscribed to a Marketplace product.
* Claude Code supports a proposed MCP configuration format.
* A candidate optimization improves performance.
* A passing unit test establishes visual correctness.
* A generated image can be assigned an expected result without independent ground truth.
* A document scanner is necessarily the best demonstration after inspection and experimentation.

Verify these matters using available tools and authoritative sources.

If multiple technical approaches are possible, compare them against correctness, implementation effort, contest eligibility, reproducibility, operational risk, and remaining time.

Do not use unsupported claims from blog posts or AI-generated summaries when primary documentation or actual execution can resolve the uncertainty.

## Evidence rules

Maintain a clear distinction among:

1. Verified facts.
2. Directly observed runtime behavior.
3. Measured experimental results.
4. Design assumptions.
5. Inferences that still need validation.
6. Blocked requirements.

Every major architectural decision should have an explicit rationale.

When documenting an external technical claim, record its source URL and the date it was checked.

When reporting a codebase claim, inspect the relevant file before making the claim.

When reporting a benchmark result, preserve the underlying measurements and environment metadata.

When reporting a successful integration, show direct evidence that it works.

Never claim that a test passed unless it was actually executed and passed.

Never claim that COOL ran on Arm merely because the application was configured for Arm.

Never manufacture speedups, latency measurements, CPU utilization, cloud costs, screenshots, execution logs, test results, or AWS deployment evidence.

If a requirement is blocked, state that it is blocked.

---

# 4. COMPETITION JUDGING CRITERIA

Treat the published judging rubrics as engineering requirements rather than as a final documentation exercise.

Verify the rubrics against the official rules page before final submission.

## A. Overall competition: 100 points

### Technical execution — 30%

Judges evaluate:

* Correctness and depth of the OpenCV 5 implementation.
* Architecture.
* Reliability.
* Evaluation quality.

Engineering response:

* Build an actual image/video-processing workload.
* Make OpenCV 5 integral to its visual analysis.
* Use meaningful test cases and measurable acceptance criteria.
* Test error conditions, corrupted inputs, timeouts, and unexpected outputs.
* Validate the complete workflow end to end.
* Avoid placeholder implementations and superficial API calls.

### Innovation — 20%

Judges evaluate originality and thoughtful use of computer vision or AI.

Engineering response:

Build an evidence-driven visual debugging agent with an adaptive testing process, reproducible failure cases, regression protection, and benchmark-guided development.

Do not present ordinary LLM code generation as the innovation.

Demonstrate the distinctive workflow directly.

### Real-world impact — 20%

Judges evaluate the importance of the problem, usefulness, and evidence of potential benefit.

Engineering response:

Address a concrete developer problem: visual defects that escape ordinary tests, failures that are difficult to reproduce, and performance optimizations that accidentally change application behavior.

Use a realistic demonstration, measurable outcomes, and explicit limitations.

Do not claim industry adoption, productivity improvements, or financial savings without evidence.

### User experience — 10%

Engineering response:

Provide a simple, usable workflow with meaningful progress information, readable failure reports, accessible visual comparisons, and clear recovery instructions.

A polished CLI with useful generated artifacts is preferable to an unfinished dashboard.

### Documentation and presentation — 10%

Engineering response:

Produce accurate installation instructions, an architecture diagram, a tool-flow diagram, evaluation documentation, benchmark results, troubleshooting instructions, and a demonstration script.

Every documented command must be tested when feasible.

### Cloud delivery, reproducibility, and responsible operation — 10%

Engineering response:

Use AWS meaningfully, make executions reproducible, log decisions and measurements, secure the execution environment, control resource consumption, and preserve human oversight.

Provide reliable cleanup instructions.

## B. Best Use of COOL Award

The published special-award criteria are:

* Verified COOL integration on AWS Graviton, or the Arm component of a documented hybrid architecture: 30%.
* Architecture and technical quality: 25%.
* Measured performance, cost, reliability, or developer-productivity value: 20%.
* Innovation: 15%.
* Reproducibility and demonstration: 10%.

The central eligibility requirement is that COOL executes the claimed core workload on AWS Graviton or the Arm component of a documented hybrid architecture.

A local demonstration on Windows or x86 Linux is not sufficient evidence of this requirement.

A generic ARM deployment without proof that the selected COOL implementation actually performs the core workload is not sufficient evidence either.

### Mandatory implementation requirements for COOL

1. Identify the applicable COOL distribution and supported AWS environment.
2. Verify its installation, runtime prerequisites, supported operations, and licensing or Marketplace requirements.
3. Select an AWS Graviton environment that is actually compatible with the verified distribution.
4. Execute the core computer-vision pipeline using that COOL environment.
5. Preserve evidence identifying the runtime, processor architecture, library build, and executing workload.
6. Compare results against an appropriate baseline.
7. Document the architecture, environment, experiment method, and results.
8. Explain any separation between a local developer workstation and the remote Arm execution worker.
9. Report limitations and failed optimization attempts honestly.

Investigate which COOL operations the selected distribution actually accelerates.

Potential candidates include image resizing, adaptive Gaussian thresholding, and contour detection, subject to verification against the selected version.

Use relevant operations in the core pipeline where appropriate.

Do not add an artificial COOL call that has no meaningful role in the workload merely to claim integration.

Do not assume that a specific speedup applies to our application because a vendor publishes aggregate benchmarks.

## C. Agentic Vision Award

The published special-award criteria are:

* Substantive OpenCV 5 and agent integration: 30%.
* Orchestration and appropriate autonomy: 25%.
* Task effectiveness and evaluation: 20%.
* Failure handling, observability, security, and human control: 15%.
* User experience, documentation, and demonstration: 10%.

The official requirements are especially important for our developer-agent category.

Our product must iteratively invoke, evaluate, and adjust a real OpenCV 5 workload, using COOL where applicable, and culminate in a running image/video application.

Using Claude Code merely to write our project does not itself satisfy the requirement.

The visual results or runtime measurements must change subsequent actions.

### Mandatory agentic behavior

Implement and demonstrate a genuine feedback loop:

1. Execute a real visual workload.
2. Inspect its actual visual-analysis outputs.
3. Evaluate outputs against acceptance criteria.
4. Identify a defect, uncertainty, or performance issue.
5. Select a subsequent test, experiment, configuration, or code change because of that evidence.
6. Execute the next action.
7. Evaluate the new result.
8. Accept, reject, or revise the candidate.
9. Produce an auditable trace showing how evidence influenced decisions.
10. End with a running implementation and verified results.

Do not implement a sequence of hard-coded steps that only appears adaptive.

Deterministic policies are acceptable for bounded decisions when the policy is transparent and the decision depends on actual measured results.

Any claim about autonomous behavior must be supported by an observable execution trace.

A trace must record the actual inputs, outputs, selected action, rationale, experiment identifiers, and final outcome.

## D. Submission strategy

Optimize the implementation for both special-award paths while satisfying the overall rubric.

Do not let award-specific features compromise the core workload.

Prioritize, in this order:

1. A correct, running OpenCV 5 application.
2. A genuine, evidence-driven agent loop.
3. Reliable visual regression testing.
4. Verified COOL execution on AWS Graviton.
5. Reproducible comparative measurements.
6. Security, observability, and graceful failure handling.
7. Documentation and presentation quality.
8. Optional interface enhancements.

If time or resource constraints prevent a component from being completed, report that explicitly instead of disguising it with a mock.

---

# 5. REQUIRED CLAUDE CODE SUBAGENT STRATEGY

Use Claude Code's native subagent capabilities.

Consult the current official subagent documentation before choosing how to define or invoke custom agents.

Use parallel delegation when investigations are independent and sequential delegation when results depend on earlier work.

Do not create excessive subagents for trivial tasks.

Do not permit multiple subagents to edit the same files concurrently.

The main agent owns overall architecture, coordination, integration, acceptance decisions, and final verification.

## Subagent 1: Competition and requirements researcher

Suggested name: `competition-researcher`.

Responsibilities:

* Inspect the official Devpost overview and rules.
* Verify both special-award rubrics.
* Identify explicit eligibility requirements.
* Identify the evidence required for Agentic Vision.
* Identify the evidence required for the COOL award.
* Record the official deadline and resolve conflicting deadline displays by treating the earlier time as the safe target.
* Produce a requirements checklist with source URLs.
* Identify possible disqualification risks arising from unsupported claims or missing functionality.

Restrictions:

* Begin in read-only mode.
* Do not modify application code.
* Distinguish explicit rules from recommendations.

Output:

A concise requirements matrix mapping every relevant rule to an implementation task, an acceptance test, and a planned piece of evidence.

## Subagent 2: Repository auditor

Suggested name: `repository-auditor`.

Responsibilities:

* Inspect the actual project directory.
* Read existing project instructions and documentation.
* Inspect dependency files, source code, tests, configuration, and deployment artifacts.
* Check the Git status and existing changes.
* Identify which components already work.
* Detect unfinished work, broken tests, security issues, and architectural inconsistencies.
* Determine which existing components should be reused.

Restrictions:

* Do not overwrite existing user changes.
* Begin read-only.
* Do not assume an empty repository.

Output:

A repository inventory, an implementation gap analysis, and a list of files likely to require changes.

## Subagent 3: COOL and AWS specialist

Suggested name: `cool-arm-engineer`.

Responsibilities:

* Research the available COOL distributions.
* Verify official Marketplace installation and execution instructions.
* Compare supported AWS Graviton offerings.
* Identify supported Python or C++ environments.
* Verify the selected version and compatible operations.
* Determine how to establish proof that the actual pipeline executes through COOL on Arm.
* Design a fair baseline.
* Investigate benchmark methodology and reproducibility.
* Identify AWS permissions, billing, Marketplace, region, and deployment prerequisites.

Restrictions:

* Do not subscribe to Marketplace products.
* Do not launch billable resources.
* Do not modify the AWS account.
* Do not assume that a currently documented setup works in our account.

Output:

A source-backed implementation plan, prerequisite checklist, chosen deployment approach, baseline methodology, cost considerations, and explicit uncertainties.

## Subagent 4: Computer-vision testing engineer

Suggested name: `vision-test-engineer`.

Responsibilities:

* Design the core visual-analysis workload.
* Evaluate a document-scanning pipeline as the primary demonstration.
* Determine the simplest credible visual task that exercises relevant OpenCV 5 and COOL operations.
* Design deterministic image generation and known ground truth.
* Develop a visual robustness testing strategy.
* Establish metrics for geometric correctness and task success.
* Define failure categories.
* Design regression tests.
* Investigate which failures can be reproducibly minimized.

Restrictions:

* Do not assume that a threshold or contour detector works merely because its output looks plausible.
* Do not generate tests whose expected outcomes are copied from the implementation under test.
* Separate synthetic test coverage from real-world validation.

Output:

A concrete vision-task specification, dataset plan, test matrix, acceptance criteria, and known limitations.

## Subagent 5: MCP and agent architecture specialist

Suggested name: `mcp-architecture-engineer`.

Responsibilities:

* Verify the current MCP specification and compatible Python SDK.
* Verify Claude Code's present MCP configuration format.
* Design tool schemas and error responses.
* Design the evidence-driven execution protocol.
* Design structured experiment records and traceability.
* Recommend integration boundaries between the local coding assistant and remote execution environment.
* Identify incompatibilities and avoid redundant infrastructure.

Restrictions:

* Do not invent APIs.
* Do not introduce an unnecessary orchestration framework.
* Do not build a second generalized coding assistant.

Output:

A concrete MCP server design, tool contracts, configuration strategy, and sequence diagram.

## Subagent 6: Evaluation and benchmark reviewer

Suggested name: `evaluation-engineer`.

Responsibilities:

* Independently review the proposed benchmark design.
* Identify confounding variables.
* Design baseline-versus-optimized comparisons.
* Specify warm-up, repetition, measurement, and aggregation procedures.
* Identify which metrics can actually be collected.
* Define statistical and reporting safeguards.
* Define what evidence supports each proposed performance claim.

Output:

An evaluation protocol and a checklist that prevents invalid comparisons or unsupported performance claims.

## Subagent 7: Security and reliability reviewer

Suggested name: `security-reviewer`.

Responsibilities:

* Threat-model the MCP server.
* Investigate risks from generated code, untrusted images, shell commands, filesystem paths, and remote execution.
* Review credential handling.
* Review AWS permission boundaries.
* Recommend execution isolation, resource limits, timeouts, audit logging, and safe cleanup.
* Review the handling of malformed or adversarial inputs.
* Identify operations that should require human approval.

Output:

A prioritized security review and concrete mitigations.

## Subagent 8: Independent competition red-team reviewer

Suggested name: `competition-red-team`.

Responsibilities:

After a running vertical slice exists, evaluate it independently against the official rubrics.

Ask:

* Could a judge reasonably conclude that COOL integration is superficial?
* Is the evidence sufficient to prove actual execution on Arm?
* Does visual evidence genuinely influence subsequent actions?
* Is the system autonomous in a meaningful and observable way?
* Do the evaluation results demonstrate task effectiveness?
* Are failures observable and recoverable?
* Could the same benchmark be reproduced?
* Are our claims supported by artifacts?
* Does the demonstration show a running workload rather than a static mockup?

Output:

A ranked list of deficiencies and the smallest set of changes that would most improve the submission.

## Coordination protocol

First, dispatch independent read-only investigations in parallel.

Then:

1. Collect the reports.
2. Reconcile disagreements against primary sources.
3. Write the architecture decisions.
4. Establish file ownership for implementation tasks.
5. Implement the simplest end-to-end vertical slice.
6. Integrate the components sequentially.
7. Delegate independent reviews and tests.
8. Have the main agent resolve findings and run final verification.

Every subagent report must distinguish verified findings from recommendations and assumptions.

Do not blindly accept another agent's conclusion. Verify critical claims, API compatibility, benchmark methodology, and competition eligibility.

If native subagents are unavailable in the current session, state this limitation and continue with equivalent structured, sequential investigations. Do not pretend that subagents were run.

---

# 6. CORE PRODUCT DESIGN

## Primary user problem

AI coding assistants can generate computer-vision implementations quickly, but visual defects may survive ordinary testing.

Examples include:

* Incorrect document boundaries under shadows.
* Failure on perspective-distorted images.
* Poor behavior on noisy or blurry frames.
* Regressions introduced by threshold changes.
* Output differences caused by changes in image preprocessing.
* Performance improvements that damage visual correctness.

COOLGuard helps developers uncover and reproduce these failures before accepting changes.

Its role is not to guarantee the absence of all bugs. It is to make important failures discoverable, reproducible, measurable, and less likely to return.

## Primary demonstration workload

Investigate a document-scanning pipeline as the initial task.

The workload should:

* Accept an image or frame.
* Identify a document region.
* Estimate its boundary.
* Produce a perspective-corrected output when appropriate.
* Report confidence or validation evidence.
* Expose intermediate processing stages for debugging.
* Evaluate correctness against independently known ground truth.

Select operations such as resizing, adaptive thresholding, and contour detection only after verifying their suitability and their availability in the selected OpenCV/COOL build.

The workload is a vehicle for demonstrating COOLGuard, not the ultimate product.

COOLGuard's architecture must make it possible to apply the same debugging workflow to other image/video applications later.

## Dataset and test corpus

Start with a deterministic, generated corpus.

Generate document-like images with known geometry and systematically vary conditions such as:

* Perspective and rotation.
* Illumination gradients.
* Shadows.
* Blur.
* Noise.
* Resolution.
* Compression.
* Image contrast.

Record the random seed, transformation parameters, ground-truth coordinates, and generation version.

Use independent ground truth generated from the known image transformations.

Do not use the detector's own outputs as ground truth.

Where feasible, supplement the synthetic corpus with a small, appropriately licensed real-world sample. Verify the dataset provenance and license before inclusion.

Do not block the implementation on obtaining an external dataset.

Clearly distinguish synthetic robustness results from results on real photographs.

## Visual evaluation

Select metrics suited to the actual task.

Potential metrics include:

* Successful document-boundary detection.
* Polygon intersection-over-union.
* Normalized corner-coordinate error.
* Failure rate by transformation category.
* Regression pass rate.
* Output validity.

Choose tolerances through explicit task requirements and validation, not to make the candidate look successful.

Preserve representative successful and failed samples.

Produce side-by-side visual comparisons with ground truth, detected geometry, and relevant intermediate stages.

---

# 7. REQUIRED SYSTEM ARCHITECTURE

Design for clear boundaries and reproducible execution.

The initial architecture should contain these logical components.

## A. Claude Code integration

Claude Code acts as the coding assistant and developer-facing orchestration layer.

It must be able to invoke COOLGuard tools through a configuration verified against the current official Claude Code documentation.

Do not confuse the coding assistant with the application being submitted.

The submitted product must itself implement the demonstrated developer-agent workflow.

## B. MCP server

Implement a real MCP server using the current official SDK and a transport supported by the chosen local integration.

Use structured, validated input and output schemas.

Make tools discoverable and their purposes clear.

Return structured errors with actionable explanations.

The server must not expose unrestricted shell execution or unrestricted filesystem access merely because the caller is an AI agent.

Implement at least these logical capabilities:

### 1. `inspect_vision_environment`

Discover and report:

* Python version.
* OpenCV version.
* OpenCV module path.
* Available processing operations.
* Platform and architecture.
* Whether a verified COOL installation is available.
* Relevant runtime configuration.

Do not infer COOL availability solely from an environment variable.

### 2. `analyze_vision_pipeline`

Inspect the project's relevant source code and identify the known pipeline stages.

Report exact file and line references where practical.

Avoid pretending that static inspection proves runtime behavior.

### 3. `generate_visual_test_cases`

Generate deterministic visual variants and maintain their ground-truth metadata.

Enforce limits on corpus size, image dimensions, and processing time.

### 4. `run_visual_regression_suite`

Execute the real application against a defined test corpus.

Return:

* Case identifiers.
* Actual measurements.
* Acceptance status.
* Failure categories.
* Output artifact paths.
* A concise diagnostic summary.

### 5. `analyze_visual_failures`

Analyze actual failed cases and identify useful evidence for the next investigation step.

Use measured results, transformation metadata, and intermediate processing outputs.

Do not manufacture a root cause when the evidence only identifies a correlation.

### 6. `reproduce_visual_failure`

Save a reproducible failing case with the relevant input, transformation parameters, expected result, actual result, and execution metadata.

Where implemented, minimize a failure through controlled transformations and verify the minimized case independently.

Do not claim formal minimality unless the minimization procedure establishes it.

### 7. `benchmark_vision_pipeline`

Run a controlled benchmark and record actual measurements, environment details, and workload settings.

Clearly distinguish local baseline results from remote Arm/COOL results.

### 8. `run_cool_graviton_benchmark`

Invoke the verified remote execution mechanism for the selected COOL environment.

Return actual remote execution status, runtime identity, measurements, and evidence artifacts.

If remote execution is unavailable, return an explicit blocked status rather than fabricating results.

### 9. `compare_implementations`

Compare saved experiment records and report correctness and performance differences.

Reject comparisons when the experimental conditions are insufficiently comparable, or explicitly identify the limitation.

### 10. `verify_candidate_fix`

Run the relevant failing cases and the complete required regression suite against a candidate implementation.

Report whether the candidate satisfies the established acceptance criteria.

Implement fewer tools initially if necessary, but ensure that each exposed tool works end to end.

## C. Vision execution worker

Provide a well-defined execution boundary for computer-vision jobs.

The worker executes the actual OpenCV 5 application, captures intermediate results, and records metrics.

Use a local worker for development and testing.

Use a verified AWS Graviton COOL environment for the required cloud workload.

Keep the interfaces consistent across environments where technically practical.

## D. Experiment and decision controller

Implement the evidence-driven testing process.

Maintain explicit experiment state, limits, and decision records.

Do not require a large multi-agent framework for bounded testing decisions.

Use a transparent adaptive policy where it provides reliable outcomes.

The coding assistant can then use the observed evidence to choose a subsequent test, configuration, or code modification.

## E. Benchmark and report generator

Produce machine-readable results and a human-readable summary.

Include:

* Test and experiment identifiers.
* Source revision or code hash.
* Dataset and configuration.
* Runtime details.
* Measurements.
* Acceptance criteria.
* Test outcome.
* Failure artifacts.
* Relevant limitations.

Every claim in the report must be traceable to actual experiments.

---

# 8. THE ESSENTIAL AGENTIC FEEDBACK LOOP

This component determines whether COOLGuard is genuinely agentic or merely a collection of MCP tools.

Implement and demonstrate the following behavior.

## Initial execution

The coding agent invokes a tool to inspect the environment and run the baseline application.

The workload processes actual images.

The evaluator compares the results with independent ground truth.

## Evidence analysis

The agent receives actual failures, visual artifacts, task scores, and runtime measurements.

It identifies a meaningful problem.

Example:

The initial document detector performs well on clean inputs but fails on a subset of images with strong shadows.

This conclusion must arise from experiment results, not from a fabricated example.

## Next-action selection

The observed failures influence what happens next.

The agent might:

* Select a targeted lighting-related test.
* Inspect intermediate grayscale or threshold images.
* Adjust a validated configuration parameter.
* Ask the coding assistant to investigate the thresholding stage.
* Compare an alternative processing method.
* Execute a candidate correction.

Log the reason for the selected next action and the evidence that prompted it.

## Candidate evaluation

Execute the candidate on both the failing cases and the established regression suite.

Compare correctness and performance with the baseline.

Reject candidates that violate correctness requirements.

Do not optimize only for speed while ignoring the main visual task.

## Iteration limits

Define:

* Maximum iterations.
* Maximum generated test cases.
* Maximum execution duration.
* Maximum remote benchmark budget.
* Conditions for early termination.
* Conditions requiring human approval.

Avoid unbounded loops.

## Acceptance and human control

A candidate may be marked as passing only after it satisfies the actual evaluation criteria.

A candidate passing automated tests is not automatically production-ready.

Preserve changes for review.

Do not commit, push, deploy to production, or overwrite important files without appropriate authorization.

## Auditable agent trace

Record the real execution sequence:

```text
Environment inspected
        |
        v
Baseline workload executed
        |
        v
Actual visual results evaluated
        |
        v
Failure identified
        |
        v
Targeted test selected
        |
        v
Candidate change proposed
        |
        v
Candidate executed
        |
        v
Regression suite evaluated
        |
        +---- Failure --> Investigate or reject
        |
        +---- Pass ----> Preserve candidate for review
```

The demonstration must show that actual visual-analysis results or measured performance changed a subsequent plan, configuration, test, tool call, or code modification.

Do not substitute a predetermined transcript or hard-coded success message for a real execution trace.

---

# 9. COOL ON AWS GRAVITON: IMPLEMENTATION AND VERIFICATION

Treat the COOL integration as a first-class engineering task.

## Phase A: Verify the available environment

Research the current relevant AWS Marketplace offering and verify:

* Exact product and version.
* Supported CPU architecture.
* Supported AWS instance families.
* Operating system.
* Installed OpenCV/COOL version.
* Available language bindings.
* Installation and activation instructions.
* Licensing and subscription requirements.
* Actual pricing and trial terms.
* Relevant AWS permissions.
* Whether the user's AWS account has access.

Do not blindly copy installation instructions from a different COOL release.

Choose a supported environment based on verified evidence.

## Phase B: Define the baseline

Design the fairest practical baseline.

Prefer comparison against a standard OpenCV build of the same relevant version on the same Arm instance when this is supported and technically reproducible.

If this cannot be achieved, select another appropriate baseline and document the version, architecture, compiler/build differences, and limitations.

An x86 comparison may provide useful context, but it does not automatically isolate the effect of COOL.

Do not attribute the entire difference between two different machines to the COOL library.

## Phase C: Execute the real workload

The same representative document-processing pipeline must run on the Arm environment.

The selected COOL operations must contribute to the actual image-processing work.

Do not benchmark a single isolated function and then claim that the complete application achieves the same speedup.

Record enough detail to establish which runtime performed the work.

Possible evidence includes:

* Processor architecture.
* AWS instance type.
* Operating system.
* Python executable.
* OpenCV version.
* Active module path.
* Available build information.
* Actual workload configuration.
* Benchmark command.
* Exit status.
* Output checksums.
* Captured measurements.

Check the applicability and reliability of each evidence source.

Never expose account credentials or other secrets in evidence files.

## Phase D: Design the benchmark

Control the conditions under which measurements are collected.

Specify:

* Input corpus.
* Input resolutions.
* Processing operations.
* Batch size.
* Warm-up procedure.
* Repetition count.
* Runtime and dependency versions.
* Concurrency.
* Instance configuration.
* Measurement method.
* Aggregation method.

Where appropriate, report:

* Median latency.
* P95 latency.
* Throughput.
* CPU utilization.
* Peak memory usage.
* Cost per fixed amount of work.

Report a measurement only when it can actually be obtained and interpreted.

For latency measurements, use a monotonic high-resolution clock.

Separate initialization and compilation costs from steady-state execution if the use case calls for it.

Preserve raw results.

Do not cherry-pick the fastest run.

Use a consistent input set and identical correctness criteria.

## Phase E: Calculate and report results

Report baseline and candidate results in a table.

For example:

| Metric                  | Baseline                            | COOL on Arm                         | Difference                           |
| ----------------------- | ----------------------------------- | ----------------------------------- | ------------------------------------ |
| Median latency          | Measured                            | Measured                            | Calculated                           |
| P95 latency             | Measured                            | Measured                            | Calculated                           |
| Throughput              | Measured                            | Measured                            | Calculated                           |
| CPU utilization         | Measured                            | Measured                            | Calculated                           |
| Peak memory             | Measured                            | Measured                            | Calculated                           |
| Cost per fixed workload | Measured or estimated transparently | Measured or estimated transparently | Calculated where comparable          |
| Correctness             | Evaluated                           | Evaluated                           | Compared against acceptance criteria |

These are required report fields where applicable, not fabricated benchmark values.

Record the actual figures.

If an appropriate metric cannot be collected, state why.

## Phase F: Cloud safety

Do not subscribe to a Marketplace product, create billable infrastructure, terminate existing instances, or alter account-wide security settings without the required user authorization.

Use existing permitted resources when available.

Inspect AWS configuration without exposing secrets.

Do not print access keys, session tokens, private keys, or sensitive environment variables into logs.

Use the narrowest practical permissions.

Prefer a secure execution mechanism compatible with the selected AMI rather than creating an unrestricted remote shell service.

Do not open unnecessary inbound ports.

Provide reliable resource-cleanup instructions.

If access to AWS is unavailable, complete local testing, remote-worker interfaces, deployment scripts, and documentation where possible, but clearly mark the cloud execution requirement as unverified.

Do not represent a local fallback as proof of AWS Graviton execution.

---

# 10. SECURITY, OBSERVABILITY, AND RESPONSIBLE OPERATION

The system will process code and images and may execute generated computer-vision implementations. Treat it as a security-sensitive developer tool.

Investigate at least the following risks:

* Arbitrary command execution.
* Malicious or malformed images.
* Path traversal.
* Unsafe generated code.
* Shell injection.
* Dependency compromise.
* Unrestricted network access.
* Credential leakage.
* Excessive resource consumption.
* Infinite execution loops.
* Accidental modifications to unrelated files.
* Unsafe automated code acceptance.
* Cloud resource abuse.

Implement proportional safeguards:

1. Allow-listed execution entry points where possible.
2. Restricted workspace access.
3. Isolated execution for untrusted candidate code.
4. Timeouts and resource limits.
5. Input-size limits.
6. Structured logging.
7. Safe failure handling.
8. Restricted network and AWS permissions.
9. Explicit approval for risky operations.
10. Reproducible cleanup.

Do not assume a Python subprocess is a security sandbox merely because it is launched separately.

Choose isolation appropriate to the threat model.

If a stronger isolation mechanism requires additional infrastructure, explain the tradeoff and implement the safest practical approach.

## Observability

Every meaningful execution should have an experiment identifier.

Logs should make it possible to understand:

* What was executed.
* Which inputs were used.
* Which configuration was active.
* What the application observed.
* What decision was made next.
* Why that action was selected.
* What happened after the action.
* Whether the experiment met its acceptance criteria.

Do not log sensitive image contents or credentials unnecessarily.

Make experiment failures distinguishable from infrastructure failures.

---

# 11. CODEBASE AND IMPLEMENTATION QUALITY

Use the simplest architecture that satisfies the requirements.

Do not overengineer.

Do not introduce Kafka, Kubernetes, a large microservice architecture, a vector database, or a generalized multi-agent framework unless an experimentally supported requirement makes one necessary.

Prefer modular Python components with clear interfaces.

Use a suitable dependency-management approach already established by the repository, or select a reproducible one if none exists.

Pin or constrain dependencies appropriately.

Check compatibility instead of relying on assumed package versions.

Add type annotations where useful.

Use structured errors rather than returning successful-looking placeholder data.

Avoid unnecessary abstractions.

Keep evaluation logic separate from candidate implementations so that the implementation cannot simply dictate its own success criteria.

Avoid embedding benchmark outputs, precomputed success traces, or expected measurements as if they were live experiment results.

Do not create mock implementations that become confused with production evidence.

Mocks may be used in isolated unit tests where appropriate, but end-to-end acceptance tests must exercise actual components.

Preserve existing project conventions when they are sound.

Do not overwrite user work or discard uncommitted changes.

---

# 12. TESTING REQUIREMENTS

Create and execute a layered testing strategy.

## A. Unit tests

Cover:

* Input validation.
* Image transformation generation.
* Ground-truth geometry.
* Metric calculations.
* Acceptance criteria.
* Failure classification.
* Benchmark aggregation.
* Experiment serialization.
* Runtime detection.
* Configuration parsing.

## B. Integration tests

Verify:

* MCP tool registration.
* MCP input/output schemas.
* Tool error handling.
* Execution of the actual OpenCV pipeline.
* Generation and loading of test artifacts.
* Experiment record consistency.
* Comparison between saved runs.

## C. Visual correctness tests

Test:

* Clean images.
* Rotation and perspective changes.
* Uneven lighting.
* Shadows.
* Blur.
* Noise.
* Different resolutions.
* Invalid or corrupted inputs.

Measure performance by condition, not merely across the aggregate dataset.

Keep tests deterministic wherever practical.

## D. Regression tests

When a failure is discovered:

1. Save its reproducing input.
2. Save the ground truth.
3. Record transformation parameters.
4. Confirm that the saved case reproduces the failure.
5. Introduce the corrected implementation.
6. Confirm that the case now passes.
7. Rerun the existing regression suite.

A regression test must check meaningful behavior rather than merely whether a process exits successfully.

## E. Agentic workflow tests

Verify that the next action is actually derived from the previous experiment's output.

Include at least one test showing that distinct failure conditions lead to different justified next actions.

Verify that iteration limits, failure paths, and acceptance gates work.

Check that a failed candidate cannot be reported as successful.

## F. Cloud integration tests

Run these only when the environment is available and authorized.

Verify the actual remote environment and the actual COOL execution path.

Check that failed remote jobs are reported correctly.

Preserve remote logs and experiment metadata.

Do not count skipped cloud tests as passed.

## G. End-to-end acceptance test

The final workflow should:

1. Inspect the environment.
2. Generate or load the test corpus.
3. Run the baseline vision pipeline.
4. Detect at least one known failure if the corpus and initial configuration are designed to produce one.
5. Preserve the failing input and diagnostic evidence.
6. Produce a justified subsequent action.
7. Evaluate the candidate correction.
8. Run regression tests.
9. Execute the appropriate COOL workload on AWS Graviton when access is available.
10. Produce a reproducible report.
11. Record any remaining limitations.

Do not engineer the application to fail arbitrarily just to create a dramatic demonstration. Use a controlled, documented test case with an explainable defect.

If the initial detector is already robust, use a known defective candidate or a deliberately constrained initial configuration in the test harness, and label that setup transparently.

---

# 13. RECOMMENDED IMPLEMENTATION PLAN

Adapt the plan after repository inspection.

Do not assume the workspace is empty or force this precise directory structure if an existing architecture provides a better solution.

A possible structure is:

```text
coolguard/
├── src/
│   └── coolguard/
│       ├── mcp_server.py
│       ├── config.py
│       ├── models.py
│       ├── vision/
│       │   ├── pipeline.py
│       │   ├── synthetic_data.py
│       │   └── transformations.py
│       ├── evaluation/
│       │   ├── ground_truth.py
│       │   ├── metrics.py
│       │   ├── regression.py
│       │   └── failure_analysis.py
│       ├── agent/
│       │   ├── controller.py
│       │   ├── policies.py
│       │   └── experiment_state.py
│       ├── benchmark/
│       │   ├── runner.py
│       │   └── comparison.py
│       ├── cloud/
│       │   ├── runtime_probe.py
│       │   └── remote_runner.py
│       └── reporting/
│           ├── artifacts.py
│           └── report.py
├── tests/
├── scripts/
├── config/
├── artifacts/
├── docs/
│   ├── architecture.md
│   ├── evaluation.md
│   ├── security.md
│   ├── deployment.md
│   └── official_sources.md
├── README.md
└── pyproject.toml
```

Use actual names and boundaries appropriate to the selected technologies.

Avoid making files just to match a diagram.

## Stage 0: Inspect and establish the baseline

Immediately inspect:

* Workspace files.
* Existing instructions.
* Git status.
* Dependency configuration.
* Python and system versions.
* Existing tests.
* Available runtime environments.
* AWS configuration and credentials status without exposing any secrets.
* Existing OpenCV/COOL installations.

Record what is present and what is absent.

Do not modify the repository until you understand its current state.

## Stage 1: Resolve critical technical uncertainties

Complete the research tasks assigned to the subagents.

Determine:

* The exact OpenCV version and API strategy.
* The real COOL distribution to use.
* The compatible Graviton execution environment.
* The benchmark baseline.
* The MCP implementation strategy.
* The minimum viable document-scanning workflow.
* The required human approvals.

Record major choices in concise architecture decision records when that is useful.

Do not spend the majority of the available time researching optional features.

## Stage 2: Build a working vertical slice

Implement:

* One real OpenCV 5 application.
* One deterministic test corpus.
* Independent visual evaluation.
* One MCP integration.
* A working tool-call workflow.
* Structured execution results.

Verify the entire basic workflow before adding advanced functionality.

## Stage 3: Implement adaptive debugging

Add:

* Failure classification.
* Reproducible test cases.
* Failure analysis.
* Evidence-driven next-action selection.
* Candidate evaluation.
* Regression protection.
* An auditable execution trace.

Demonstrate at least one genuine iterative debugging cycle.

## Stage 4: Integrate COOL and AWS Graviton

Implement the verified deployment and execution mechanism.

Run a core vision workload through the actual selected COOL environment.

Capture environment evidence.

Execute the benchmark protocol and preserve the raw data.

If an authorization or access prerequisite blocks this stage, continue other tasks while documenting the exact blocker.

## Stage 5: Harden and evaluate

Run unit, integration, regression, security, and end-to-end tests.

Fix important defects.

Run the evaluation and competition red-team subagents.

Address critical findings before minor polish.

## Stage 6: Prepare the final submission

Produce:

* Complete source code.
* Reproducible installation instructions.
* Local development setup.
* MCP configuration instructions.
* Remote COOL/Arm execution instructions.
* Architecture diagram.
* Agent decision-flow diagram.
* Test and evaluation documentation.
* Actual benchmark results.
* Reproducible experiment artifacts.
* Security and limitations documentation.
* A polished demonstration script.

Create a judge-oriented checklist that maps each claimed capability to a source file, test, execution trace, or measurement.

Do not mark a requirement verified solely because its documentation exists.

---

# 14. BENCHMARK REPRODUCIBILITY AND EXPERIMENT RECORDS

Use a structured, versioned experiment format.

An illustrative schema is:

```json
{
  "experiment_id": "unique-id",
  "code_revision": "verified-revision-or-hash",
  "dataset_id": "verified-dataset-version",
  "configuration_hash": "verified-hash",
  "runtime": {
    "os": "observed-value",
    "architecture": "observed-value",
    "python_version": "observed-value",
    "opencv_version": "observed-value",
    "cool_version": "observed-value-or-unverified",
    "aws_instance_type": "observed-value-or-not-applicable"
  },
  "measurements": {
    "latency_ms": null,
    "throughput_fps": null,
    "cpu_percent": null,
    "peak_memory_mb": null
  },
  "correctness": {
    "evaluated": false,
    "metrics": {},
    "acceptance_passed": false
  },
  "execution": {
    "status": "not-run",
    "decision_trace_id": "trace-id"
  }
}
```

This is a proposed schema, not an execution result.

Use null or an explicit unavailable status where a value has not been measured.

Do not populate real-looking measurements with invented defaults.

Make experiment identifiers unique.

Preserve raw observations, summary statistics, and the exact command or procedure needed to reproduce the run.

Record software and environment changes between experiments.

A result should be reproducible without relying on undocumented manual steps.

---

# 15. REQUIRED USER EXPERIENCE

Avoid a complicated dashboard until the engineering workflow works.

Provide a simple way for a developer to:

1. Inspect the environment.
2. Run a visual test suite.
3. Inspect failures.
4. Ask the coding assistant to investigate a failure.
5. Benchmark a candidate implementation.
6. Compare runs.
7. Review the final report.

The primary experience may use Claude Code's interaction surface, MCP tools, and generated artifacts.

Make progress understandable.

Communicate whether a task is running, failed, completed, or blocked.

Show the exact location of useful outputs.

Explain what was tested and what remains unverified.

Preserve the developer's ability to inspect and control modifications.

If time permits after the core workflow is validated, create a small HTML report with:

* Run summary.
* Visual comparisons.
* Failure categories.
* Benchmark comparisons.
* Execution traces.
* Acceptance status.

Do not build a large frontend at the expense of the working vision application.

---

# 16. DOCUMENTATION AND DEMONSTRATION

Design the presentation for judges who may inspect the code and reproduce the result.

## README

Include:

* Problem statement.
* Proposed solution.
* System architecture.
* Core functionality.
* Verified prerequisites.
* Installation instructions.
* How to configure Claude Code.
* How to run the local workload.
* How to run the visual test suite.
* How to access the COOL/Arm benchmark environment.
* How to reproduce results.
* How to run tests.
* Known limitations.
* Security considerations.
* Resource cleanup.

## Architecture documentation

Include:

1. System component diagram.
2. MCP tool-flow diagram.
3. Agentic perception-decision-action diagram.
4. Local and cloud deployment architecture.
5. Trust boundaries.
6. Data and artifact flow.

Explain the relationship between the local development machine, Claude Code, MCP server, vision worker, and AWS Graviton execution environment.

Do not depict an unimplemented component as deployed.

## Demonstration plan

Create a short, authentic demonstration that shows:

1. The coding assistant invoking COOLGuard tools.
2. A real OpenCV 5 application processing images.
3. Visual test outputs exposing a failure.
4. The evidence changing the next action.
5. A candidate fix being tested.
6. Regression-test results.
7. Actual COOL execution on Arm, when available.
8. A reproducible benchmark comparison.
9. The final generated report.

The demonstration must not rely on fabricated terminal output or prerecorded results presented as live execution.

It is acceptable to include a previously completed benchmark in the demonstration if it is clearly identified as a saved run and its underlying artifacts are available.

Explain the real limitations of the project.

---

# 17. RESOURCE AND TIME PRIORITIES

The competition deadline is close.

After the initial inspection, organize remaining work around verified milestones and the actual time available.

Prioritize a working, end-to-end submission over an ambitious incomplete architecture.

Do not spend time adding unrelated infrastructure.

Do not introduce additional cloud services without a clear requirement.

Do not optimize code before establishing a trustworthy baseline.

Do not optimize optional metrics while correctness testing is incomplete.

Do not produce extensive planning documents while the main workflow remains unimplemented.

Where two alternatives are similarly effective, choose the simpler, safer, more reproducible implementation.

Preserve enough time for:

* A real cloud experiment.
* A final end-to-end test.
* Evidence collection.
* Documentation.
* The final demonstration.
* Submission before the verified deadline.

Never consume the remaining time on low-value polishing while a critical competition requirement remains unverified.

---

# 18. DEFINITION OF DONE

The project is not complete merely because the code has been written.

Track each criterion as:

* VERIFIED: directly tested or supported by recorded evidence.
* IMPLEMENTED, NOT VERIFIED: code exists but required validation has not succeeded.
* BLOCKED: a documented external prerequisite prevents verification.
* NOT IMPLEMENTED: work remains outstanding.
* NOT APPLICABLE: justified with evidence.

## Core application

* [ ] A real OpenCV 5 vision workload exists.
* [ ] The application processes actual images or video.
* [ ] Visual correctness has independent ground truth and evaluation criteria.
* [ ] Deterministic test cases can be reproduced.
* [ ] Failures are meaningfully observable.

## MCP and developer-agent integration

* [ ] A real MCP server exists.
* [ ] Claude Code can invoke its implemented tools.
* [ ] Tool schemas and errors are validated.
* [ ] The coding assistant can use actual visual-analysis outputs.
* [ ] Evidence influences subsequent actions.
* [ ] An actual iterative agentic workflow is demonstrated.
* [ ] The workflow culminates in a running application.

## Debugging and regression protection

* [ ] Visual failures can be preserved as reproducible cases.
* [ ] Candidate changes are evaluated against acceptance criteria.
* [ ] Existing regression tests are retained.
* [ ] Failed candidates do not appear successful.
* [ ] Iteration and resource limits work.

## COOL and AWS

* [ ] The selected COOL distribution and execution environment are verified.
* [ ] The AWS environment is compatible with the selected distribution.
* [ ] The core vision workload actually executes through COOL on Arm.
* [ ] Runtime identity and architecture evidence are recorded.
* [ ] The baseline is appropriate and its limitations are documented.
* [ ] Measurements derive from real experiments.
* [ ] Raw results and reproduction instructions are preserved.
* [ ] AWS costs and cleanup are accounted for.

## Evaluation and reliability

* [ ] Unit tests pass.
* [ ] Integration tests pass.
* [ ] Visual regression tests run.
* [ ] Error and failure paths are tested.
* [ ] Agent decision traces are auditable.
* [ ] Security findings are reviewed.
* [ ] The end-to-end workflow works in the available environment.
* [ ] All skipped or blocked tests are explicitly identified.

## Submission

* [ ] README and setup instructions are complete.
* [ ] Architecture diagrams match the implementation.
* [ ] Actual benchmark artifacts are included.
* [ ] The final demonstration can be reproduced.
* [ ] The official judging criteria have been reviewed again.
* [ ] Claims in the submission are supported by evidence.
* [ ] Known limitations are disclosed.
* [ ] The final submission is ready before the verified deadline.

A checkbox may be marked complete only when its stated evidence requirement has been satisfied.

---

# 19. YOUR IMMEDIATE EXECUTION INSTRUCTIONS

Begin now.

Do not respond with another proposal or ask me to confirm the architecture.

First, inspect the repository, available tools, local runtime, Git status, and current instructions.

Then launch the independent read-only subagents described in Section 5, using Claude Code's current supported capabilities.

While those investigations run, inspect the workspace and establish the initial baseline.

Collect the reports, resolve critical uncertainties, and select the simplest technically sound implementation.

Create a concise execution checklist with explicit completion criteria.

Implement the core vertical slice immediately.

Run it.

Inspect its actual outputs.

Fix defects.

Add the evidence-driven debugging loop.

Verify the MCP integration.

Investigate and implement the real COOL/Graviton path.

Run the available tests and experiments.

Have independent reviewers challenge the results.

Resolve the highest-impact findings.

Complete the documentation and judge-oriented evidence.

Do not stop at the end of a phase merely to summarize what you would do next. Continue to the next phase whenever prerequisites allow.

If one phase is blocked, continue with independent work and return to the blocked phase when possible.

Use native subagents to accelerate independent investigations, testing, and reviews. Keep final integration and acceptance decisions under the main agent's control.

Before potentially destructive operations, irreversible account changes, Marketplace subscriptions, or billable AWS deployments, obtain the necessary authorization. Everything else that is safe, reversible, and available in the existing workspace should proceed without unnecessary interruptions.

Do not expose secrets.

Do not overwrite unrelated user changes.

Do not fabricate capability, execution, performance, or judging evidence.

Do not mark incomplete work as complete.

At the end, provide a concise but evidence-backed status report containing:

1. What is implemented.
2. What actually works.
3. Tests and commands that were executed.
4. Actual results and artifact locations.
5. Whether the AWS Graviton/COOL execution requirement has been verified.
6. Whether the Agentic Vision requirements have been demonstrated.
7. Remaining blockers and limitations.
8. The current competition-readiness assessment.
9. The highest-impact unfinished task, if any.

The objective is not to create the appearance of a sophisticated system.

**The objective is to build a working, reproducible developer agent that discovers visual defects, uses evidence to guide debugging, verifies improvements, and demonstrates meaningful COOL execution on AWS Graviton.**

Start with repository inspection and execute the project to completion.
