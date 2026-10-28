### Trace forensics

**You own the diagnosis from the artefact.**

Distinct from **Runtime forensics**, which instruments the live process. Here the capture already exists. The artefact is a fixed dataset, read it, don't re-run it. Keep tooling generic: a DevTools or trace parser for cpuprofile and `.json.gz`, a text editor for a spindump, your heap tooling for a heapsnapshot.

1. Identify the format and load it with the right tool. Parse large artefacts in a subagent (the **principle-guard-the-context-window** skill) and keep the reduced finding in the main thread. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section.
2. Transform the raw artefact into a form you can query. Dump the trace or heap snapshot into sqlite, one row per sample, frame, or node. Reach the queryable shape before you read.
3. Narrow to the cause. Query for the frames that hold the most time and walk the call tree to the hot path. For a leak, follow the retainer chain from the leaked object to a GC root. For a spindump, find the thread stuck on-CPU or blocked and its wait reason.
4. Attribute to source. Map the hot frame to file, symbol, and line via the artefact's own symbols. A frame with no source mapping is not yet a diagnosis. Resolve the symbols, or say plainly the artefact does not carry them.
5. If you have a paired capture, diff the before and after artefacts to confirm. Otherwise, mark the finding as the strongest hypothesis the artefact supports, not a confirmed cause.
6. Hand back a cited diagnosis, no fix unless asked. Route to Bug fix or Perf issue once the cause is known. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only forensics`.

**Reply:** the artefact and format, the reduced finding, the source location, the artefact paths, and whether a paired capture confirmed it.
