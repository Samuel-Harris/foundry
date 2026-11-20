import {
  Card,
  CardBody,
  CardHeader,
  Code,
  CollapsibleSection,
  Divider,
  H1,
  H2,
  H3,
  Link,
  Pill,
  Row,
  Stack,
  Stat,
  Text,
  useHostTheme,
} from "cursor/canvas";

type Action = "add" | "update" | "delete";
type Basis = "evidence" | "judgement" | "silence";

interface Evidence {
  source: "transcript" | "review" | "static";
  ref: string;
  url: string | null;
  quote: string;
}

interface Item {
  title: string;
  action: Action;
  basis: Basis;
  path: string;
  package: string;
  section: string | null;
  change: string;
  rationale: string;
  evidence: Evidence[];
  sources: number;
  shortfall?: string;
}

interface PackageGroup {
  package: string;
  files: { path: string; items: Item[] }[];
}

interface Report {
  repo: string;
  window: { start: string; end: string };
  foundry_commit: string;
  min_sources: number;
  sources: {
    pull_requests: number;
    review_comments: number;
    sessions: number;
    sessions_by_host: Record<string, number>;
    sessions_per_model: Record<string, number>;
  };
  counts: Record<Action, number>;
  coverage: string[];
  recommendations: PackageGroup[];
  obsolete: PackageGroup[];
  watching: PackageGroup[];
}

const TITLE = "__TITLE__";
const REPORT: Report = __REPORT_JSON__;

function plural(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}

function evidenceLabel(item: Evidence): string {
  if (item.source === "review") return `PR #${item.ref}`;
  if (item.source === "transcript") return `session ${item.ref.slice(0, 8)}`;
  return item.ref;
}

function itemCount(groups: PackageGroup[]): number {
  return groups.reduce(
    (total, group) => total + group.files.reduce((sum, file) => sum + file.items.length, 0),
    0
  );
}

function EvidenceList({ items }: { items: Evidence[] }) {
  const theme = useHostTheme();
  if (items.length === 0) return null;
  return (
    <CollapsibleSection title="Evidence" count={items.length}>
      <Stack gap={6}>
        {items.map((item, index) => (
          <div
            key={`${item.ref}-${index}`}
            style={{ borderLeft: `2px solid ${theme.stroke.secondary}`, paddingLeft: 10 }}
          >
            <Row gap={8} align="center" wrap>
              {item.url ? (
                <Link href={item.url}>{evidenceLabel(item)}</Link>
              ) : (
                <Code>{evidenceLabel(item)}</Code>
              )}
              <Text size="small" tone="secondary">
                "{item.quote}"
              </Text>
            </Row>
          </div>
        ))}
      </Stack>
    </CollapsibleSection>
  );
}

function ItemCard({ item }: { item: Item }) {
  const theme = useHostTheme();
  const basis = item.basis === "evidence" ? plural(item.sources, "source") : item.basis;
  return (
    <Card>
      <CardHeader
        trailing={
          <Row gap={6}>
            <Pill size="sm">{item.action}</Pill>
            <Pill size="sm">{basis}</Pill>
          </Row>
        }
      >
        {item.title}
      </CardHeader>
      <CardBody>
        <Stack gap={10}>
          {item.section && (
            <Text size="small" tone="tertiary">
              Section: {item.section}
            </Text>
          )}
          {item.shortfall && (
            <Text size="small" tone="tertiary">
              Short of the bar: {item.shortfall}
            </Text>
          )}
          <div
            style={{
              background: theme.fill.quaternary,
              borderRadius: theme.radius.md,
              padding: 10,
              whiteSpace: "pre-wrap",
              fontFamily: "monospace",
              fontSize: 12,
            }}
          >
            {item.change}
          </div>
          <Text>{item.rationale}</Text>
          {item.evidence.length > 0 && <Divider />}
          <EvidenceList items={item.evidence} />
        </Stack>
      </CardBody>
    </Card>
  );
}

function Packages({ groups, empty }: { groups: PackageGroup[]; empty: string }) {
  if (groups.length === 0) {
    return <Text tone="secondary">{empty}</Text>;
  }
  return (
    <Stack gap={20}>
      {groups.map((group) => (
        <Stack key={group.package} gap={12}>
          <H3>{group.package}</H3>
          {group.files.map((file) => (
            <Stack key={file.path} gap={8}>
              <Code>{file.path}</Code>
              {file.items.map((item) => (
                <ItemCard key={`${item.path}-${item.title}`} item={item} />
              ))}
            </Stack>
          ))}
        </Stack>
      ))}
    </Stack>
  );
}

export default function GuidanceRetro() {
  const theme = useHostTheme();
  const { sources, counts } = REPORT;
  const hosts = Object.entries(sources.sessions_by_host)
    .map(([host, n]) => `${n} ${host}`)
    .join(", ");
  const models = Object.entries(sources.sessions_per_model)
    .map(([model, n]) => `${model} (${n})`)
    .join(", ");

  return (
    <div style={{ background: theme.bg.editor, color: theme.text.primary, padding: 24 }}>
      <Stack gap={24}>
        <Stack gap={4}>
          <H1>{TITLE}</H1>
          <Text size="small" tone="secondary">
            {REPORT.repo}, {REPORT.window.start} to {REPORT.window.end}, Foundry at{" "}
            {REPORT.foundry_commit}
          </Text>
        </Stack>

        <Row gap={24} wrap>
          <Stat value={counts.add} label="To add" />
          <Stat value={counts.update} label="To update" />
          <Stat value={counts.delete} label="To delete" />
          <Stat value={sources.pull_requests} label="PRs with comments" />
          <Stat value={sources.review_comments} label="Review comments" />
          <Stat value={sources.sessions} label="Agent sessions" />
        </Row>

        <Text size="small" tone="secondary">
          Sessions: {hosts || "none"}. Models: {models || "not recorded"}.
        </Text>
        {REPORT.coverage.map((note) => (
          <Text key={note} size="small" tone="tertiary">
            {note}
          </Text>
        ))}

        <Divider />

        <Stack gap={16}>
          <H2>Recommendations</H2>
          <Packages groups={REPORT.recommendations} empty="No change cleared the evidence bar." />
        </Stack>

        <CollapsibleSection title="Possibly obsolete" count={itemCount(REPORT.obsolete)}>
          <Stack gap={12}>
            <Text size="small" tone="secondary">
              Guidance whose target failure never appeared in the window. It may be working, or
              models may no longer need it.
            </Text>
            <Packages groups={REPORT.obsolete} empty="Nothing listed." />
          </Stack>
        </CollapsibleSection>

        <CollapsibleSection title="Watching" count={itemCount(REPORT.watching)}>
          <Stack gap={12}>
            <Text size="small" tone="secondary">
              Patterns seen in fewer than {REPORT.min_sources} distinct sessions or PRs.
            </Text>
            <Packages groups={REPORT.watching} empty="Nothing listed." />
          </Stack>
        </CollapsibleSection>
      </Stack>
    </div>
  );
}
