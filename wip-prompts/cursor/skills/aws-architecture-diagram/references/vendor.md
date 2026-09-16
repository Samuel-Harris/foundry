# Vendored AWS architecture-diagram skill

This directory snapshots the AWS Labs agent-plugins `aws-architecture-diagram` skill so Cursor can generate draw.io diagrams without the deploy-on-aws plugin.

- Upstream: [awslabs/agent-plugins](https://github.com/awslabs/agent-plugins) (`deploy-on-aws` plugin)
- License: Apache-2.0
- What was copied: `references/*.md`, example `.drawio` files, `scripts/lib/*`, `validate-drawio.sh`, `requirements.txt`
- Local changes: `SKILL.md` (output path, no plugin hook, no diagrams.net URL, same-account VPC placement), this file, plus same-account notes in `layout-guidelines.md` and `xml-rules.md`
