---
title: "Glider orchestration: hoops, swarms, and why one-shot chat wasn't enough"
description: "I've been building Glider, a local-first AI harness that sits above Cursor. This post is about the orchestration side: Loop Engineering hoops, parallel workers, feeds, and per-run workspaces."
pubDate: 2026-07-25
tags:
  - AI
  - Agents
  - Go
  - Orchestration
  - Cursor
  - Ollama
draft: true
---

I've been building **Glider**, a local-first AI harness that sits above Cursor: dual-mode proxy (gateway + MITM), Ollama/vLLM offload, and a proper Loop Engineering layer so agent work isn't just "paste a prompt and hope." This post is about the **orchestration** side — hoops, swarms, feeds, workspaces — walked through with a real sample: the **repo security audit** hoop.

Repo / setup notes live in the Glider tree (`docs/SETUP.md` if you're cloning it). Here I'm writing for "why did I build it this way?"

---

### Before we start — is orchestration even *needed*?

Chat UIs (Cursor included) are absurdly good at **one turn**. You ask, something answers, life moves on.

The moment you want *systems* — clone a repo, audit it from a few angles, write a report, pause so a human can look, and *not* re-download the same repo three times because the model made up a file path — one-shot chat falls over. You don't need a smarter model first. You need a **system that prompts agents** in a fixed order: look around → plan → do the work → score the result → remember what happened — with clear stop conditions and tools that can't wander all over your hard drive.

And that's when I thought:

*why not make the harness own the workflow shape — who runs, in what order, what they share — not just which model answers?*

I'm not claiming this is the final form of agent orchestration. I *am* claiming that once you feel the pain of "the checker started chatting instead of scoring" and "three workers each invented their own copy of the repo," you stop treating a staged workflow as optional polish.

---

## Okay let's break it down

**Glider has two core layers:**

1. **Inference** — which model answers (your laptop's Ollama, your cloud API keys, or Cursor's own cloud)
2. **Orchestration** — how a *job* is broken into steps (plan, clone, audit in parallel, human review, score, save)

The shared path for every completion looks like this:

**alias → tokenize → router → transform → orchestrator**

In plain English:

- **Alias** — rewrite the client's model ID to a real backend name. Cursor asks for `gpt-4o`; Glider's `model_aliases` config turns that into `qwen2.5-coder:14b` (or whichever model you actually want to serve) before anything else runs.
- **Tokenize** — count/estimate tokens so the router and transform steps know how big this request is
- **Router** — pick local vs cloud (typing `/cloud` in Cursor can mean "keep this turn on Cursor's cloud")
- **Transform** — shorten or tweak the prompt if it's too big for the local model
- **Orchestrator** — actually call the model and stream the answer back

Orchestration (hoops and swarms) sits *on top* of that. A step in a job can say "prefer local" or "prefer cloud," but it still goes through the same path — it doesn't replace it.

![Glider orchestration stack](/blog/glider-orchestration/01-orchestration-stack.svg)

A few words you'll see a lot:

| Word | Plain meaning |
|------|----------------|
| **Hoop** | One saved job / playbook (goal + ordered steps). You start it, it runs through the steps, then stops. |
| **Stage / node** | One step on that playbook (plan, clone, review, …). |
| **Swarm** | Several helpers working on the same goal at once, then merging results. |
| **Workspace** | A private folder on disk for *this* run — scratch files vs finished reports. |
| **HITL / human_gate** | A pause where a person must approve before the job continues. |
| **Actor** | A stage that does real work — runs tools, writes files, calls APIs. Most "do something" steps are actors. |
| **Planner** | A stage that only outputs text (a checklist / strategy). No tool access — keeps it from accidentally doing work early. |
| **Critic** | A stage that scores or judges another stage's output. Hard format (`SCORE` + `REASON`), no rewriting. |
| **Router** | A stage (or pipeline step) that decides *where* a request runs — local model, cloud API, or Cursor's own backend. |
| **Memory** | Load or save a short note between runs so the next execution isn't starting from zero. |
| **Context** | A shared whiteboard for the current run — stages write facts here so later stages don't have to re-derive them. |
| **Feeds** | Data arrows: one stage's summary gets injected into a later stage's prompt as extra context (not control flow). |

---

## What the repo security audit hoop is trying to do

Before the graph: **what is the job even for?**

Goal in one sentence:

> Clone a real GitHub repo into a safe sandbox, check it for code quality and security issues (without inventing fake CVEs), let a human glance at the findings, score whether the audit is actually useful, then save the result.

Target in the sample: [Unbrokify](https://github.com/singhutsav5502/Unbrokify).  
Output we want: Scope, clone result, quality findings, security findings, priority fixes, residual risk — with file paths that *actually exist* in the clone.

That sample lives at `samples/hoops/clone-repo-security-audit.yaml`. It's the one that forced most of the design decisions below.

---

## Walkthrough: the stage graph

In the Glider dashboard, that job shows up as a **Stage Graph**. Solid green arrows = "do this next." Dashed orange arrows = "loop back if something's wrong."

![Repo security audit stage graph in Glider](/blog/glider-orchestration/repo-security-audit-graph.png)

*Left: building blocks you can drag. Center: the job. Right: what just finished in the last run.*

### Where files go for this run

When you hit **Start**, Glider makes a folder just for this job:

```text
~/.glider/workspace/runs/clone-repo-security-audit/
  work/   ← download the repo here, temporary files
  out/    ← finished notes and the report
```

So if a step says "put the repo in `audit-target`," it really means:

`…/runs/clone-repo-security-audit/work/audit-target`

Not a random folder next to Glider's own source code. Tools and listings all use that same rule.

![Per-run workspace](/blog/glider-orchestration/04-workspace-binding.svg)

### Step 1 — Load audit context (`memory`)

**What it does:** If you've run this job before and "learning" is on, pull back a short note of what happened last time so the planner isn't starting from zero. First run? Almost nothing to load — that's fine.

Think of it as opening yesterday's sticky note before you start today's audit.

### Step 2 — Route (`router`)

**What it does:** Prefer the **local** model (Ollama on your machine) for the rest of the steps. Audits call a lot of tools and can take a while; keeping that on a local model is the default for this sample.

### Step 3 — Plan clone + audit (`planner`)

**What it does:** Write a short checklist only. It is **not** allowed to download the repo.

Why? If the planner can run tools, it will try — then later steps get confused by half-failed attempts. So the plan is just text, something like:

1. Next step clones the repo into `audit-target`  
2. List the folders / languages  
3. Run quality + security checks in parallel  
4. Human looks, then a checker scores the report  

### Step 4 — Clone / inventory (`actor`)

**What it does:** Actually download the repo (the only step that should), then list what's inside.

It calls something like "clone this GitHub URL into `audit-target`," then lists that folder so we know the download worked. It should describe the *real* tree — not invent files.

### Step 5 — Verify clone landed (`actor`)

**What it does:** Double-check the download before spending time on the expensive parallel audit.

- Folder present → say `CLONE_OK` and list top-level names  
- Missing → say `CLONE_MISSING` and stop  

No security findings yet. This exists so we don't send three auditors into an empty folder.

### Step 6 — Seed shared context (`context`)

**What it does:** Write a few shared facts onto a whiteboard the later steps can read: the goal, the plan, and especially **where the clone lives**.

Later workers should ask "where's the clone?" from that whiteboard instead of downloading the repo again or guessing a Windows path.

### Step 7 — Parallel quality + security (`actor`)

**What it does:** Spin up two helpers at once on the *same* clone:

- one leans **security** (auth, injection patterns, secrets — no fake CVE numbers)  
- one leans **code quality** (error handling, messy hotspots, tests)

They write notes into the run's `out/` folder. They are **not** allowed to clone again — if they try an undeclared tool, Glider rejects it.

Two ways to run "several helpers":

![Fanout vs nested swarm](/blog/glider-orchestration/03-fanout-vs-swarm.svg)

- **Fanout** (default here) — quick parallel pass inside this one step, then merge  
- **Swarm** — heavier "team sheet" mode (optional; you turn it on explicitly)

### Step 8 — Operator review (`human_gate`)

**What it does:** Pause. A person looks at what the agents produced (the UI shows a short "here's what to review" summary). Click approve to continue, or reject / send it back.

Without this, a bad audit can race straight into "ship it."

### Step 9 — Audit completeness critic (`critic`)

**What it does:** A **different** role from the writers. It doesn't rewrite the audit and it mostly doesn't use tools. It only answers: "is this report honest and usable?" with two lines:

```text
SCORE: 0.0-1.0
REASON: one short sentence
```

This sample wants about **0.75** or higher. Score near zero if the clone never worked, if findings point at files that aren't in the repo, or if the "audit" is just the model asking you for more files.

### Step 10 — Persist audit (`memory`)

**What it does:** Save how this cycle went so the next run (or the learning bits) can see it. On the graph this is often the last highlighted node when a run finishes clean.

### The orange dashed arrows

From the critic you can loop back:

| Arrow | Meaning in plain English |
|-------|---------------------------|
| back to **planner** | Report wasn't good enough — rethink the plan and try another round |
| back to **human gate** | Score too low — get a person involved again instead of spinning forever |

Happy path is still mostly left-to-right: … → human review → critic → save.

![Audit hoop happy path](/blog/glider-orchestration/05-audit-hoop-flow.svg)

---

## The same idea without the audit nouns

Any hoop is the same Loop Engineering shape:

![Hoop cycle](/blog/glider-orchestration/02-hoop-cycle.svg)

There's also a special arrow type called **feeds**: one step's summary gets pasted into a later step's prompt as extra context. That's *data*, not "who runs next" — you still need a normal flow arrow if the later step should run.

---

## Bugs this shape was built to stop

These all happened for real while building:

- Treating the long English *goal* as a folder path and listing the wrong place  
- "Call every GitHub tool" literally trying to call a tool named `*`  
- The checker chatting ("can you send me the files?") instead of giving a score  
- Parallel helpers each downloading their own copy of the repo  
- "Clone worked!" in the model's prose while the file listing looked at a different folder  

Orchestration isn't "more config files." It's fencing those failure modes.

---

## Design principles I optimized for

1. **Writer ≠ checker** — separate score step with a hard format  
2. **Sandbox by default** — tools don't treat Glider's own source repo as the project  
3. **One folder pair per run** — scratch (`work`) and deliverables (`out`)  
4. **Compose the job** — steps and arrows are data (graph editor + YAML)  

---

## If you want to poke it

```powershell
ollama pull qwen2.5-coder:14b
go build -o glider.exe ./cmd/glider
.\glider.exe --config configs\glider.yaml
# dashboard → http://127.0.0.1:8081
powershell -File scripts\seed-samples.ps1
go run ./scripts/loadhoop -file samples/hoops/clone-repo-security-audit.yaml -start
```

Open **Hoops → Graph** for that hoop — you should see the same stage graph as the screenshot. **Workspace** tab → that run's `work` and `out` folders.

Point Cursor's OpenAI Base URL at `http://127.0.0.1:8080/v1` if you want Chat/Agent to go through Glider's gateway. MITM / `/cloud` is the other path (Cursor's cloud for that sticky turn) — details in the setup doc.

---

## Closing thought

You don't need a hoop graph on day one. But once agents touch real work, picking a model stops being the product — the *workflow shape* is what matters: who runs, in what order, what they share, and when a human gets a veto.

The repo audit earlier was just one example. What matters across jobs is stop conditions and feedback loops.

### Further reading

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic's patterns guide. The orchestrator-workers and evaluator-optimizer sections map directly onto hoops.
- [Orchestration and handoffs](https://developers.openai.com/api/docs/guides/agents/orchestration) — OpenAI on when to hand off vs. keep one agent in charge. Good framing if you're deciding where to split.
