---
name: aws-architecture-diagram
description: Generate validated AWS architecture diagrams as uncompressed draw.io XML with official AWS4 icons, numbered step legends, and same-account VPC placement. Invoke with /aws-architecture-diagram to analyze Terraform, CDK, or CloudFormation, or to brainstorm a stack. Self-contained — does not require the Cursor AWS plugin. Do not produce diagrams.net preview URLs.
disable-model-invocation: true
---

# AWS Architecture Diagram

Generate official-style AWS architecture diagrams as uncompressed draw.io XML. This skill vendors the AWS Labs `aws-architecture-diagram` workflow, references, and validators (Apache-2.0). Do not call or require the Cursor deploy-on-aws plugin.

Resolve `references/` and `scripts/` relative to this skill directory (the folder that contains this `SKILL.md`).

## Purpose

Match AWS Reference Architecture diagrams: title and subtitle, teal numbered step badges, right-sidebar legend, 48x48 service icons inside 120x120 category containers, Helvetica, orthogonal data flow.

## Placement overlay

These rules override the vendored "external actor" placement guidance.

- Output directory: if the repo has `.devtools/agents/artefacts/`, write to `.devtools/agents/artefacts/architecture-diagrams/<descriptive-name>.drawio`; otherwise write to `.cursor/artefacts/architecture-diagrams/<descriptive-name>.drawio`. Create the directory. Do not commit the diagram unless the user asks.
- Do not terraform apply. Do not edit production infrastructure.
- There is no PostToolUse draw.io hook. After writing, run `scripts/lib/` yourself (see Validate and export).
- **Same-account placement.** App servers, APIs, batch producers, and any other compute that runs in the AWS account stay **inside** the AWS Cloud group. Put them in the product VPC as ECS/Fargate/EC2 icons, not as Users/external-actor containers. Isolated VPCs are sibling VPC groups in the same account. Cross-VPC traffic that is actually SQS/S3 must be drawn through those regional services, not as peering unless the infra has a peering resource.
- Use the Users/external-actor pattern (`fillColor=#f5f5f5`, `resIcon=mxgraph.aws4.users`) only for actors that are truly outside the account: end users, on-premises, or third-party SaaS. The post-processor will shove `#f5f5f5` "user" boxes out of AWS Cloud; do not draw in-account services that way.
- If the user already named a concrete system, skip the extra "confirm the architecture" prompt and generate.

## Instructions

You are an AWS architecture diagram generator that produces draw.io XML with official AWS4 icons.

### Step 1: Determine mode

**Mode A — Codebase analysis:** If the user says "analyze", "scan", "from code", or points at a repo:

1. Scan CloudFormation, CDK, or Terraform (`resource "aws_*"`).
2. Extract services, relationships, VPC structure, and data flow.
3. If there is no AWS infrastructure, scan Dockerfiles, databases, APIs, ML stacks, and brokers. Map non-AWS tech with `references/general-icons.md`.
4. Mixed architectures: AWS4 icons for AWS, general icons for the rest. Same layout rules.
5. Confirm only when the target system is still ambiguous.
6. Ask which diagram type fits, unless the type is obvious (VPC/container for an isolated ECS plane).

**Mode B — Brainstorming:** If the user describes a stack or says "brainstorm" / "from scratch":

1. Ask 3-5 focused questions (purpose, services, scale, security, traffic).
2. Propose the architecture and data flow.
3. Iterate if needed, then generate.

### Step 2: Styling

Independent of mode:

- **Sketch mode**: only if the user says "sketch", "hand-drawn", or "sketchy". Default off.
- **Legend**: on by default for 7+ services or branching paths. Off only if the user says "no legend", "without legend", "skip steps", or "no sidebar".
- **Export format**: png/svg/pdf only when asked. Default `.drawio`.

### Step 3: Generate XML

Load references now, not before:

1. `references/xml-rules.md`
2. `references/style-guide.md`
3. `references/xml-templates-structure.md`
4. `references/layout-guidelines.md`

Use the example table only as conceptual guidance. Open an example `.drawio` only if layout is still unclear.

| Diagram type | Primary example | Secondary |
| --- | --- | --- |
| Serverless / API | `example-saas-backend.drawio` | `example-event-driven.drawio` |
| Event-driven / async | `example-event-driven.drawio` | `example-microservices.drawio` |
| Microservices / ECS | `example-microservices.drawio` | `example-complex-platform.drawio` |
| Multi-region | `example-multi-region-active-active.drawio` | — |
| Complex (13+ services) | `example-complex-platform.drawio` | `example-saas-backend.drawio` |
| AI / AgentCore | `example-agentcore.drawio` | `example-event-driven.drawio` |
| Sketch mode | `example-sketch.drawio` | plus one from above |

If the architecture includes non-AWS services, also read `references/general-icons.md`.

### Step 4: Validate and export

`SCRIPT_ROOT` is this skill's `scripts/` directory.
`OUT_DIR` is the output directory from Placement overlay.
`PY` is the first existing of `.pixi/envs/default/bin/python`, `backend/.venv/bin/python`, `python3`.

1. Write `OUT_DIR/<descriptive-name>.drawio`.
2. Requires `defusedxml>=0.7.1` (`scripts/requirements.txt`). Confirm `$PY -c "import defusedxml"` works. If it does not, say so and skip the scripts; do not invent a pass.
3. Post-process, then validate:

```bash
"$PY" SCRIPT_ROOT/lib/post_process_drawio.py OUT_DIR/<filename>.drawio
"$PY" SCRIPT_ROOT/lib/validate_drawio.py OUT_DIR/<filename>.drawio
```

4. If validation fails, fix and re-run.
5. PNG/SVG/PDF: see `references/cli-export.md`. Keep the `.drawio` (do not delete it after export).
6. Tell the user: file path, diagram type and services, validation status, and alt text under 100 characters. Do not generate or present a diagrams.net preview URL. Do not run `scripts/lib/drawio_url.py`.

## Defaults

- Mode: brainstorm if there is no codebase context; analyze if they pointed at a repo or named a system in it
- Font: `fontFamily=Helvetica` (Comic Sans MS only in sketch mode)
- Icon: 48x48 inside 120x120 containers
- Spacing: 180px horizontal, 120px vertical (220/160 for 13+ services)
- Legend: always for 7+ services unless opted out
- Dark mode: `light-dark()` on structural fills, `fillStyle=auto`
- Grid: off (`grid=0`)
- XML: uncompressed `<mxfile><diagram><mxGraphModel>`

## Error handling

- XML validation failure: fix, rewrite, re-validate
- Unknown shape: `references/aws4-shapes-services.md`
- draw.io desktop CLI missing: keep `.drawio`, skip raster export
- Invalid edge: every `source`/`target` must be an existing `mxCell` id
- No `--` inside XML comments
- Escape `&amp;`, `&lt;`, `&gt;`, `&quot;` in attributes

## Style rules

Full tables: `references/style-guide.md`.

- All text: `fontFamily=Helvetica;`
- Structural fills: `light-dark()` + `fillStyle=auto;`
- Region groups: `container=0`. Services `parent="aws-cloud"` with absolute coords
- Group `fontColor` matches `strokeColor` (VPC `#8C4FFF`, public subnet `#248814`, private subnet `#147EBA`, region `#00A4A6`). Never `#AAB7B8`
- Font sizes: title 30 bold > subtitle 16 > group 14 bold > container 12 bold > service 10 > edge 11
- AgentCore: `resIcon=mxgraph.aws4.bedrock_agentcore`
- Sketch: `sketch=1;curveFitting=1;jiggle=2` on non-icons only

## Diagram types

VPC/network, serverless, multi-region, CI/CD, data flow, container, hybrid. Layout patterns: `references/diagram-templates-basic.md` and `references/diagram-templates-advanced.md`.

## XML generation

Details: `references/xml-rules.md`.

Always use:

```xml
<mxfile host="Electron" version="29.6.1">
  <diagram name="Page-1" id="diagram-1">
    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="1100" pageHeight="850" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- `id="0"` and `id="1"` are required
- `mxgraph.aws4.*` only. Container value = category ("Compute"). Icon value = service name plus optional italic sub-label
- Edges connect to **icons**, not category containers
- Edge labels are child cells, `connectable="0"`, `relative="1"`, `labelBackgroundColor=none`
- Nested containers only for real boundaries: VPC, subnet, AZ
- Auxiliary (CloudWatch, CloudTrail, X-Ray, IAM): dashed group inside AWS Cloud, no step numbers, no edges
- Every other service is primary: edges and step numbers
- No `background` on `mxGraphModel`
- No compressed/base64 diagram payloads
- Descriptive cell ids (`vpc-app`, `svc-fargate-api`)

## Layout

Details: `references/layout-guidelines.md`.

- Orthogonal edges; waypoints around intervening containers
- Multiple outbound edges leave different anchors
- Step badges: teal `#007CBD` 28x28 near the source end
- Legend height matches diagram height

## File naming

Kebab-case, new file unless the user asked to update an existing diagram.

## Stop conditions

- Stop after a validated `.drawio`, or after reporting that `defusedxml` is missing
- Stop and ask if the user wants a diagram of something that is not AWS and has no mappable general icon
- Do not install Cursor plugins, do not terraform apply, do not commit gitignored artefacts, do not emit diagrams.net URLs

## Verification

Test: invoke this skill on a named AWS stack (Terraform/CDK/CloudFormation) with the Cursor AWS plugin unused.

Pass:

- File exists under the output directory above as `.drawio`
- `validate_drawio.py` prints `VALIDATION PASSED`
- Icons use `mxgraph.aws4.*` inside category containers; title, numbered steps, and legend are present
- In-account compute sits in a VPC group **inside** AWS Cloud, not as Users boxes outside the account boundary
- Isolated VPCs are sibling groups in the same account; no invented peering
- No diagrams.net preview URL

Fail: plugin required at runtime; in-account compute drawn outside AWS Cloud; invalid XML; commit of the artefact without being asked.

## Provenance

Vendored from the AWS Labs `deploy-on-aws` plugin skill `aws-architecture-diagram` (Apache-2.0). See `references/vendor.md`.
