import { ChangeEvent, DragEvent, useEffect, useMemo, useState } from "react";
import { Download, FileText, Layers, RefreshCw, Save, ShieldCheck, Sparkles, Upload } from "lucide-react";

type Mode = {
  mode_id: string;
  name: string;
  description: string;
  recommended_for: string[];
  enabled_committees: string[];
  required_sections: string[];
  depth: string;
  include_persona_appendix: boolean;
};

type Config = {
  board_id: string;
  modes: Mode[];
  template_version: string;
  llm?: LlmConfig;
};

type LlmConfig = {
  configured: boolean;
  base_url: string;
  model: string;
  missing: string[];
  config_file: string;
  timeout?: number;
  max_tokens?: number;
  continuations?: number;
};

type Preview = {
  record: Record<string, unknown>;
  board_memo: string;
  visual_report?: VisualReport;
  visual_report_markdown?: string;
  prompt_bundle: string;
  evidence_packets: Array<Record<string, string>>;
  assumptions: Array<Record<string, unknown>>;
  ontology_trace?: OntologyTraceHit[];
  ontology_rule_hits?: OntologyRuleHit[];
  committee_rule_matrix?: CommitteeRuleMatrix[];
  persona_graph_refs?: Array<Record<string, unknown>>;
  model_comparisons?: Array<Record<string, unknown>>;
  action_audit?: Array<Record<string, unknown>>;
  governance_checks?: string[];
  material_pack?: MaterialPack;
  review_run?: ReviewRun;
  action_items?: Array<Record<string, unknown>>;
  calibration_events?: Array<Record<string, unknown>>;
};

type VisualHero = {
  title: string;
  decision_id: string;
  mode_id: string;
  mode_label: string;
  decision: string;
  decision_label: string;
  confidence_label: string;
  source_block_count: number;
  material_file_count: number;
};

type VisualCard = {
  card_id: string;
  title: string;
  body: string;
  tone: string;
  value?: string;
  meta?: string;
  badges?: string[];
  source_fields: string[];
};

type VisualRoadmapItem = {
  day: number;
  title: string;
  body: string;
  evidence?: string;
};

type VisualAppendixSection = {
  title: string;
  body: string;
  source_fields?: string[];
};

type VisualReport = {
  schema_version: string;
  hero: VisualHero;
  seat_view_cards: VisualCard[];
  persona_graph_cards: VisualCard[];
  model_comparison_cards: VisualCard[];
  action_audit_cards: VisualCard[];
  decision_cards: VisualCard[];
  committee_cards: VisualCard[];
  ontology_cards: VisualCard[];
  evidence_cards: VisualCard[];
  assumption_cards: VisualCard[];
  insight_cards: VisualCard[];
  roadmap: VisualRoadmapItem[];
  appendix_sections: VisualAppendixSection[];
};

type OntologyTraceHit = {
  persona_id: string;
  persona_name?: string;
  committee: string;
  ontology_level?: string;
  source_quality?: string;
  rule_id: string;
  rule_description?: string;
  triggered_by: string[];
  supporting_evidence?: string[];
  positive_signals?: string[];
  red_flags?: string[];
  missing_evidence?: string[];
  counter_test?: string;
  confidence_boundary?: string[];
};

type OntologyRuleHit = {
  persona_id: string;
  persona_name?: string;
  committee: string;
  rule_id: string;
  triggered_by: string[];
  missing_evidence?: string[];
  counter_test?: string;
  confidence_boundary?: string[];
};

type CommitteeRuleMatrix = {
  committee: string;
  rule_hits: Array<{
    persona_id: string;
    persona_name?: string;
    rule_id: string;
    triggered_by: string[];
  }>;
};

type MaterialFile = {
  file_id?: string;
  name: string;
  size: number;
  type: string;
  status?: string;
  content?: string;
};

type SourceBlock = {
  block_id: string;
  file_id: string;
  source_file: string;
  text: string;
};

type MaterialPack = {
  pack_id: string;
  title: string;
  files: MaterialFile[];
  source_blocks: SourceBlock[];
  warnings: string[];
};

type ReviewRun = {
  run_id: string;
  mode_id: string;
  stages: Array<{
    stage_id: string;
    name: string;
    status: string;
    summary: string;
  }>;
};

const fallbackConfig: Config = {
  board_id: "default",
  template_version: "local-fallback",
  llm: {
    configured: false,
    base_url: "https://api.openai.com/v1",
    model: "gpt-4.1",
    missing: ["SUPER_BOARD_LLM_API_KEY 或 OPENAI_API_KEY"],
    config_file: ".super-board-model.json"
  },
  modes: [
    {
      mode_id: "deep_board_review",
      name: "深度董事会审议",
      description: "完整七委员会审议，适合可转发建议书。",
      recommended_for: ["产品需求", "项目计划", "商业计划"],
      enabled_committees: ["business-leaders", "startup-mentors", "investment-masters", "consulting-elite", "product-users", "organization-china", "philosophy-humanities"],
      required_sections: ["证据包", "假设账本", "决策记录条目"],
      depth: "deep",
      include_persona_appendix: true
    }
  ]
};

const committeeLabels: Record<string, string> = {
  "business-leaders": "商业与长期价值委员会",
  "startup-mentors": "创业与非共识机会委员会",
  "investment-masters": "投资与风险委员会",
  "consulting-elite": "战略与竞争委员会",
  "product-users": "产品与用户委员会",
  "organization-china": "组织与中国商业实践委员会",
  "philosophy-humanities": "哲学与人文委员会",
  "synthetic-users": "用户模拟组"
};

const modeLabels: Record<string, string> = {
  quick_triage: "快速审议",
  deep_board_review: "深度董事会审议",
  red_team: "红队反证审查",
  pre_mortem: "事前验尸",
  investment_committee: "投资委员会",
  product_discovery: "产品发现审议",
  go_to_market_review: "市场进入审议",
  synthetic_user_panel: "用户模拟委员会"
};

const fieldLabels: Record<string, string> = {
  claim: "判断",
  claim_type: "判断类型",
  evidence_source: "证据来源",
  confidence: "置信度",
  counterevidence: "反向证据",
  disproof_test: "反证实验",
  assumption: "假设",
  type: "类型",
  checkpoints: "检查点",
  decision_id: "决策编号",
  created_at: "创建时间",
  input_type: "输入类型",
  mode_id: "审议模式",
  title: "标题",
  decision: "建议",
  assumptions: "待验证假设",
  evidence_packets: "依据",
  follow_up_checkpoints: "复盘检查点",
  material_pack: "材料包",
  source_blocks: "来源块",
  source_file: "来源文件",
  source_block_id: "来源块",
  source_excerpt: "来源摘录",
  action_items: "行动项",
  review_run: "审议流程",
  calibration_events: "校准事件",
  ontology_trace: "本体触发明细",
  ontology_rule_hits: "本体规则命中",
  committee_rule_matrix: "委员会规则链",
  triggered_specialists: "按需触发专家",
  selected_seats: "本次审议席位",
  seat_viewpoints: "席位代表观点",
  seat_selection_trace: "席位选择轨迹",
  persona_graph_refs: "人物图谱引用",
  model_comparisons: "模型制衡关系",
  action_audit: "动作审计",
  governance_checks: "治理检查",
  claim_id: "主张编号",
  model_id: "模型编号",
  source_ids: "来源编号",
  boundary_id: "边界编号",
  counter_test_id: "反证编号",
  relation_ids: "关系编号",
  display_name: "显示名称",
  committee_name: "委员会名称",
  selection_reason: "入选原因",
  evidence_basis: "证据门槛",
  counter_signal: "反证信号",
  viewpoint: "代表观点",
  matched_signals: "命中信号",
  persona_id: "本体人物",
  persona_name: "人物名称",
  committee: "委员会",
  ontology_level: "本体层级",
  source_quality: "来源质量",
  rule_id: "规则编号",
  rule_description: "规则说明",
  triggered_by: "触发词",
  supporting_evidence: "支持证据",
  positive_signals: "正向信号",
  red_flags: "风险信号",
  missing_evidence: "证据缺口",
  counter_test: "反证实验",
  confidence_boundary: "置信边界",
  pack_id: "材料包编号",
  files: "文件",
  warnings: "提示",
  file_id: "文件编号",
  name: "名称",
  size: "大小",
  status: "状态",
  content: "内容",
  block_id: "来源块编号",
  text: "文本",
  run_id: "运行编号",
  stages: "阶段",
  stage_id: "阶段编号",
  summary: "摘要",
  action_id: "行动编号",
  description: "描述",
  owner: "负责人",
  due: "截止时间",
  event_id: "事件编号",
  signal: "信号",
  note: "备注",
  day: "天数",
  question: "问题"
};

const valueLabels: Record<string, string> = {
  fact: "事实",
  inference: "推断",
  assumption: "假设",
  process: "流程",
  high: "高",
  medium: "中",
  low: "低",
  unknown: "未识别",
  product_requirement: "产品需求",
  project_plan: "项目计划",
  business_plan: "商业计划",
  Pending: "待判断",
  Go: "推进",
  Pivot: "调整",
  "No-Go": "不推进"
  , not_started: "未开始",
  in_progress: "进行中",
  validated: "已验证",
  failed: "失败",
  read: "已读取",
  empty: "空内容",
  ready: "就绪",
  pending_model: "等待模型",
  pending_followup: "等待复盘"
};

const supportedUploadTypes = ".md,.markdown,.txt,.json,.csv,.yaml,.yml";
const detailTabs = [
  ["materials", "材料摘要"],
  ["ontology", "本体触发"],
  ["rules", "规则链"],
  ["evidence", "依据"],
  ["assumptions", "待验证假设"],
  ["flow", "生成过程"],
  ["record", "归档记录"]
] as const;

type DetailTab = typeof detailTabs[number][0];

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function Badge({ children }: { children: string }) {
  return <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-600">{children}</span>;
}

function displayModel(config: Config) {
  const llm = config.llm;
  if (!llm) return "模型状态未知";
  return llm.configured ? `模型 ${llm.model}` : "模型未配置";
}

function displayMode(modeId: string) {
  return modeLabels[modeId] ?? modeId;
}

function displayCommittee(committeeId: string) {
  return committeeLabels[committeeId] ?? committeeId;
}

function localizeValue(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(localizeValue);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, entry]) => [
        fieldLabels[key] ?? key,
        localizeValue(entry)
      ])
    );
  }
  if (typeof value === "string") {
    return modeLabels[value] ?? valueLabels[value] ?? value;
  }
  return value;
}

function formatJson(value: unknown) {
  return JSON.stringify(localizeValue(value), null, 2);
}

function downloadText(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function filenameBaseFromName(name: string) {
  const cleanName = name.trim().split(/[\\/]/).pop() ?? "";
  return cleanName.replace(/\.[^.]+$/, "").trim();
}

function safeDownloadBaseName(value: unknown) {
  const raw = String(value ?? "").trim();
  const normalized = filenameBaseFromName(raw)
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, "-")
    .replace(/\s+/g, " ")
    .replace(/-+/g, "-")
    .replace(/^[.\-\s]+|[.\-\s]+$/g, "");
  return normalized || "SuperBoard";
}

function boardMemoFilename(preview: Preview) {
  const files = preview.material_pack?.files ?? [];
  const sourceName = files.length === 1
    ? files[0]?.name
    : preview.material_pack?.title ?? preview.record.title;
  return `${safeDownloadBaseName(sourceName)}-SuperBoard董事会建议书.md`;
}

function visualReportFilename(preview: Preview, extension = "md") {
  const files = preview.material_pack?.files ?? [];
  const sourceName = files.length === 1
    ? files[0]?.name
    : preview.material_pack?.title ?? preview.record.title;
  return `${safeDownloadBaseName(sourceName)}-SuperBoard视觉版建议书.${extension}`;
}

function renderVisualReportHtml(preview: Preview) {
  const markdown = preview.visual_report_markdown ?? "";
  const escaped = markdown
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>${preview.visual_report?.hero.title ?? "视觉版董事会建议书"}</title><style>body{margin:0;background:#f8fafc;color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:1120px;margin:32px auto;background:white;border:1px solid #e2e8f0;border-radius:16px;padding:32px}pre{white-space:pre-wrap;line-height:1.7;font-size:14px}</style></head><body><main><pre>${escaped}</pre></main></body></html>`;
}

function renderRecordMarkdown(record: Record<string, unknown>) {
  return [
    `# 决策记录：${record.title ?? ""}`,
    "",
    `- 决策编号：${record.decision_id ?? ""}`,
    `- 审议模式：${displayMode(String(record.mode_id ?? ""))}`,
    `- 当前建议：${valueLabels[String(record.decision ?? "")] ?? record.decision ?? ""}`,
    "",
    "## 材料包",
    "```json",
    formatJson(record.material_pack ?? {}),
    "```",
    "",
    "## 证据包",
    "```json",
    formatJson(record.evidence_packets ?? []),
    "```",
    "",
    "## 假设账本",
    "```json",
    formatJson(record.assumptions ?? []),
    "```",
    "",
    "## 本体规则命中",
    "```json",
    formatJson(record.ontology_rule_hits ?? []),
    "```",
    "",
    "## 委员会规则链",
    "```json",
    formatJson(record.committee_rule_matrix ?? []),
    "```",
    "",
    "## 行动项",
    "```json",
    formatJson(record.action_items ?? []),
    "```",
    ""
  ].join("\n");
}

function renderRecordHtml(record: Record<string, unknown>) {
  const escaped = renderRecordMarkdown(record)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>${record.title ?? "超级董事会"}</title><style>body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:40px;color:#0f172a}pre{white-space:pre-wrap;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:16px}</style></head><body><pre>${escaped}</pre></body></html>`;
}

function evidenceRows(preview: Preview | null) {
  return preview?.evidence_packets ?? [];
}

function assumptionRows(preview: Preview | null) {
  return preview?.assumptions ?? [];
}

function ontologyRows(preview: Preview | null) {
  return preview?.ontology_rule_hits ?? [];
}

function committeeRuleRows(preview: Preview | null) {
  return preview?.committee_rule_matrix ?? [];
}

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

const toneClasses: Record<string, string> = {
  slate: "border-slate-200 bg-slate-50 text-slate-900",
  blue: "border-blue-200 bg-blue-50 text-blue-950",
  cyan: "border-cyan-200 bg-cyan-50 text-cyan-950",
  emerald: "border-emerald-200 bg-emerald-50 text-emerald-950",
  amber: "border-amber-200 bg-amber-50 text-amber-950",
  rose: "border-rose-200 bg-rose-50 text-rose-950",
  violet: "border-violet-200 bg-violet-50 text-violet-950"
};

const dotClasses: Record<string, string> = {
  slate: "bg-slate-500",
  blue: "bg-blue-500",
  cyan: "bg-cyan-500",
  emerald: "bg-emerald-500",
  amber: "bg-amber-500",
  rose: "bg-rose-500",
  violet: "bg-violet-500"
};

function VisualCardView({ card }: { card: VisualCard }) {
  const tone = toneClasses[card.tone] ?? toneClasses.slate;
  const dot = dotClasses[card.tone] ?? dotClasses.slate;
  return (
    <article className={`rounded-lg border p-4 ${tone}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${dot}`} />
            <h4 className="break-words text-sm font-semibold">{card.title}</h4>
          </div>
          {card.meta && <div className="mt-1 text-xs opacity-70">{card.meta}</div>}
        </div>
        {card.value && (
          <span className="shrink-0 rounded-md bg-white/70 px-2 py-1 text-xs font-medium shadow-sm">{card.value}</span>
        )}
      </div>
      <p className="mt-3 text-sm leading-6">{card.body}</p>
      {(card.badges?.length ?? 0) > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {card.badges?.map((badge) => (
            <span key={badge} className="rounded-md bg-white/70 px-2 py-1 text-xs">{badge}</span>
          ))}
        </div>
      )}
      <div className="mt-3 text-[11px] leading-5 opacity-70">来源：{card.source_fields.join("、")}</div>
    </article>
  );
}

function VisualSection({ title, cards, columns = "grid-cols-1 md:grid-cols-2" }: { title: string; cards: VisualCard[]; columns?: string }) {
  return (
    <section className="space-y-3">
      <h3 className="text-sm font-semibold text-slate-950">{title}</h3>
      {cards.length === 0 ? (
        <div className="rounded-md border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">暂无内容</div>
      ) : (
        <div className={`grid gap-3 ${columns}`}>
          {cards.map((card) => <VisualCardView key={card.card_id} card={card} />)}
        </div>
      )}
    </section>
  );
}

function VisualReportView({ report }: { report?: VisualReport }) {
  if (!report) {
    return (
      <div className="flex h-[690px] items-start gap-3 p-4 text-sm leading-6 text-slate-600">
        <Sparkles size={18} className="mt-1 text-slate-400" />
        <div>
          <div className="font-medium text-slate-900">暂无视觉版建议书</div>
          <div className="mt-1">生成董事会建议书后，这里会把决策摘要、委员会、本体规则、证据、假设和 AI 洞察转换为卡片化报告。</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[690px] overflow-auto p-4">
      <div className="space-y-5">
        <section className="rounded-lg border border-slate-200 bg-slate-950 p-5 text-white">
          <div className="text-xs text-slate-300">{report.hero.mode_label} · {report.hero.decision_id}</div>
          <h3 className="mt-2 text-xl font-semibold leading-7">{report.hero.title}</h3>
          <div className="mt-4 grid grid-cols-1 gap-2 text-xs sm:grid-cols-3">
            <div className="rounded-md bg-white/10 p-3">
              <div className="text-slate-300">当前建议</div>
              <div className="mt-1 text-base font-semibold">{report.hero.decision_label}</div>
            </div>
            <div className="rounded-md bg-white/10 p-3">
              <div className="text-slate-300">材料文件</div>
              <div className="mt-1 text-base font-semibold">{report.hero.material_file_count}</div>
            </div>
            <div className="rounded-md bg-white/10 p-3">
              <div className="text-slate-300">来源块</div>
              <div className="mt-1 text-base font-semibold">{report.hero.source_block_count}</div>
            </div>
          </div>
        </section>

        <VisualSection title="决策摘要卡片" cards={report.decision_cards} />
        <VisualSection title="本次参与席位" cards={report.seat_view_cards ?? []} />
        <VisualSection title="人物本体图谱" cards={report.persona_graph_cards ?? []} />
        <VisualSection title="模型制衡关系" cards={report.model_comparison_cards ?? []} />
        <VisualSection title="动作审计" cards={report.action_audit_cards ?? []} />
        <VisualSection title="AI 洞察" cards={report.insight_cards} />
        <VisualSection title="委员会卡片" cards={report.committee_cards} />
        <VisualSection title="本体规则卡片" cards={report.ontology_cards.slice(0, 6)} />
        <VisualSection title="证据与假设" cards={[...report.evidence_cards.slice(0, 3), ...report.assumption_cards.slice(0, 3)]} />

        <section className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-950">30 / 60 / 90 天路线图</h3>
          <div className="grid gap-3 md:grid-cols-3">
            {report.roadmap.map((item) => (
              <div key={item.day} className="rounded-lg border border-slate-200 bg-white p-4">
                <div className="text-lg font-semibold text-slate-950">{item.day} 天</div>
                <div className="mt-2 text-sm leading-6 text-slate-700">{item.body}</div>
                <div className="mt-3 text-xs text-slate-500">{item.evidence}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-950">结构化正文摘要</h3>
          <div className="space-y-2">
            {report.appendix_sections.slice(0, 2).map((section) => (
              <div key={section.title} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm font-semibold text-slate-900">{section.title}</div>
                <div className="mt-2 text-sm leading-6 text-slate-600">{section.body}</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export function App() {
  const [config, setConfig] = useState<Config>(fallbackConfig);
  const [modeId, setModeId] = useState("deep_board_review");
  const [material, setMaterial] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [activeTab, setActiveTab] = useState<DetailTab>("materials");
  const [status, setStatus] = useState("本地工作台就绪");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [inputFileName, setInputFileName] = useState<string | null>(null);
  const [materialPack, setMaterialPack] = useState<MaterialPack | null>(null);
  const [showCommittees, setShowCommittees] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [isMaterialDragging, setIsMaterialDragging] = useState(false);
  const [activeMemoView, setActiveMemoView] = useState<"visual" | "memo">("visual");

  useEffect(() => {
    fetch("/api/config")
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("config unavailable")))
      .then((payload: Config) => {
        setConfig(payload);
        setModeId(payload.modes[0]?.mode_id ?? "deep_board_review");
      })
      .catch(() => setConfig(fallbackConfig));
  }, []);

  const selectedMode = useMemo(
    () => config.modes.find((mode) => mode.mode_id === modeId) ?? config.modes[0],
    [config.modes, modeId]
  );

  async function generateModelMemo() {
    const llm = config.llm;
    if (!llm?.configured) {
      const message = `模型未配置：${llm?.missing?.join("，") ?? "缺少 API 配置"}`;
      setStatus(message);
      setGenerationError(message);
      return;
    }
    if (!material.trim()) {
      setStatus("请先上传或输入材料");
      setGenerationError("请先上传或输入材料，然后再生成董事会建议书。");
      return;
    }
    setIsGenerating(true);
    setStatus(`正在生成董事会建议书：${llm.model}`);
    setGenerationError(null);
    setPreview(null);
    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ material, mode_id: modeId, material_pack: materialPack })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = String(payload.error ?? "模型生成失败");
        setStatus(message);
        setGenerationError(message);
        return;
      }
      if (payload.job_id) {
        await pollGenerationJob(String(payload.job_id), llm);
        return;
      }
      setPreview(payload);
      setActiveMemoView("visual");
      setStatus(`模型建议书已生成：${payload.generation?.model ?? llm.model}`);
      setGenerationError(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : "模型请求失败";
      setStatus(message);
      setGenerationError(`模型请求失败：${message}`);
    } finally {
      setIsGenerating(false);
    }
  }

  async function pollGenerationJob(jobId: string, llm: LlmConfig) {
    const pollIntervalMs = 2000;
    const firstPollDelayMs = 800;
    const timeoutSeconds = Number(llm.timeout ?? 360);
    const continuations = Number(llm.continuations ?? 0);
    const maxWaitSeconds = Math.max(900, timeoutSeconds * (continuations + 1) + 120);
    const maxAttempts = Math.ceil((maxWaitSeconds * 1000) / pollIntervalMs);
    const startedAt = Date.now();

    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      await sleep(attempt === 0 ? firstPollDelayMs : pollIntervalMs);
      const response = await fetch(`/api/jobs/${jobId}`);
      const payload = await response.json().catch(() => ({}));
      const elapsedSeconds = Math.round((Date.now() - startedAt) / 1000);
      const elapsedLabel = elapsedSeconds < 60 ? `${elapsedSeconds} 秒` : `${Math.floor(elapsedSeconds / 60)} 分 ${elapsedSeconds % 60} 秒`;
      if (!response.ok) {
        const message = String(payload.error ?? "生成任务读取失败");
        setStatus(message);
        setGenerationError(message);
        return;
      }
      if (payload.status === "running") {
        setStatus(`生成任务已创建，等待调用 ${llm.model}（已等待 ${elapsedLabel}）`);
        continue;
      }
      if (payload.status === "calling_model") {
        setStatus(`正在调用 ${llm.model} 生成董事会建议书（已等待 ${elapsedLabel}）`);
        continue;
      }
      if (payload.status === "failed") {
        const message = String(payload.error ?? "模型生成失败");
        setStatus(message);
        setGenerationError(message);
        return;
      }
      if (payload.status === "succeeded" && payload.result) {
        setPreview(payload.result as Preview);
        setActiveMemoView("visual");
        setStatus(`模型建议书已生成：${llm.model}`);
        setGenerationError(null);
        return;
      }
    }
    const message = `前端等待已超过 ${Math.round(maxWaitSeconds / 60)} 分钟，但后端任务尚未返回最终状态。请刷新记录或稍后重试。`;
    setStatus(message);
    setGenerationError(message);
  }

  async function processMaterialFiles(files: File[]) {
    if (files.length === 0) return;

    try {
      const payloadFiles = await Promise.all(
        files.map(async (file) => ({
          name: file.name,
          size: file.size,
          type: file.type || file.name.split(".").pop() || "text",
          content: await file.text()
        }))
      );
      const response = await fetch("/api/materials/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ files: payloadFiles })
      });
      if (!response.ok) {
        throw new Error("material preview failed");
      }
      const payload = await response.json();
      const pack = payload.material_pack as MaterialPack;
      setMaterialPack(pack);
      setMaterial(
        pack.source_blocks
          .map((block) => `<!-- ${block.block_id} · ${block.source_file} -->\n${block.text}`)
          .join("\n\n")
      );
      setInputFileName(`${files.length} 个文件 · ${formatFileSize(files.reduce((total, file) => total + file.size, 0))}`);
      setPreview(null);
      setActiveTab("materials");
      setStatus("材料包已生成，文件内容只在本地工作台处理");
    } catch {
      setStatus("文件读取失败，请确认它是文本文件");
    }
  }

  async function handleMaterialFile(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    await processMaterialFiles(files);
  }

  function handleMaterialDragOver(event: DragEvent<HTMLElement>) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
    setIsMaterialDragging(true);
  }

  function handleMaterialDragLeave(event: DragEvent<HTMLElement>) {
    const nextTarget = event.relatedTarget;
    if (nextTarget instanceof Node && event.currentTarget.contains(nextTarget)) {
      return;
    }
    setIsMaterialDragging(false);
  }

  async function handleMaterialDrop(event: DragEvent<HTMLElement>) {
    event.preventDefault();
    setIsMaterialDragging(false);
    await processMaterialFiles(Array.from(event.dataTransfer.files ?? []));
  }

  async function handleRecord() {
    if (!preview) return;
    setStatus("正在写入本地记录");
    const response = await fetch("/api/record", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(preview.record)
    });
    if (!response.ok) {
      setStatus("记录写入失败");
      return;
    }
    setStatus("记录已写入 records/，默认不进入 git");
  }

  async function handleCalibration() {
    if (!preview) return;
    const record = preview.record;
    const response = await fetch("/api/calibration", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision_id: record.decision_id,
        mode_id: record.mode_id,
        signal: "manual_note",
        note: "从工作台手动记录一次待复盘校准事件。"
      })
    });
    setStatus(response.ok ? "校准事件已记录到本地" : "校准事件记录失败");
  }

  function exportRecord(format: "md" | "json" | "html") {
    if (!preview) return;
    if (format === "json") {
      downloadText("超级董事会决策记录.json", JSON.stringify(preview.record, null, 2));
      return;
    }
    if (format === "html") {
      downloadText("超级董事会决策记录.html", renderRecordHtml(preview.record));
      return;
    }
    downloadText("超级董事会决策记录.md", renderRecordMarkdown(preview.record));
  }

  function exportBoardMemo() {
    if (!preview) return;
    downloadText(boardMemoFilename(preview), preview.board_memo);
  }

  function exportVisualReport(format: "md" | "html") {
    if (!preview) return;
    if (format === "html") {
      downloadText(visualReportFilename(preview, "html"), renderVisualReportHtml(preview));
      return;
    }
    downloadText(visualReportFilename(preview), preview.visual_report_markdown ?? "");
  }

  return (
    <main className="min-h-screen bg-[#f8fafc] text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <ShieldCheck size={16} />
              本地决策审议工作台
            </div>
            <h1 className="text-2xl font-semibold tracking-normal">超级董事会</h1>
          </div>
          <div className="flex items-center gap-2">
            <Badge>{displayModel(config)}</Badge>
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl grid-cols-1 gap-4 px-5 py-5 lg:grid-cols-[360px_minmax(0,1fr)_360px]">
        <form className="space-y-5 rounded-lg border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2">
            <Layers size={18} />
            <h2 className="text-base font-semibold">审议准备</h2>
          </div>

          <section
            className={`space-y-3 rounded-md border border-dashed p-3 ${isMaterialDragging ? "border-slate-950 bg-slate-50" : "border-transparent"}`}
            onDragOver={handleMaterialDragOver}
            onDragLeave={handleMaterialDragLeave}
            onDrop={handleMaterialDrop}
          >
            <div className="text-sm font-semibold text-slate-900">1. 材料</div>
            <div className="flex items-center justify-between gap-3">
              <label className="block text-sm font-medium text-slate-700" htmlFor="material">输入材料</label>
              <label className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50">
                <Upload size={15} />
                上传文件
                <input
                  type="file"
                  accept={supportedUploadTypes}
                  multiple
                  className="sr-only"
                  onChange={handleMaterialFile}
                />
              </label>
            </div>
            {inputFileName && (
              <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-500">
                已读取：{inputFileName}
              </div>
            )}
            {materialPack && (
              <div className="rounded-md border border-slate-200 bg-white px-3 py-2 text-xs text-slate-600">
                材料包：{materialPack.title} · {materialPack.files.length} 个材料文件 · {materialPack.source_blocks.length} 个可引用来源块
              </div>
            )}
            <textarea
              id="material"
              value={material}
              onChange={(event) => setMaterial(event.target.value)}
              placeholder="粘贴审议材料，或拖入 / 上传文件。"
              className="min-h-[260px] w-full resize-y rounded-md border border-slate-300 px-3 py-2 font-mono text-sm leading-6"
            />
          </section>

          <section className="space-y-3 border-t border-slate-200 pt-4">
            <div className="text-sm font-semibold text-slate-900">2. 审议设置</div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="mode">审议模式</label>
            <select
              id="mode"
              value={modeId}
              onChange={(event) => setModeId(event.target.value)}
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
            >
              {config.modes.map((mode) => (
                <option key={mode.mode_id} value={mode.mode_id}>{mode.name}</option>
              ))}
            </select>
            <div className="rounded-md bg-slate-50 p-3 text-sm text-slate-600">{selectedMode?.description}</div>
            <button
              type="button"
              onClick={() => setShowCommittees((value) => !value)}
              className="rounded-md border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:bg-slate-50"
            >
              已启用 {(selectedMode?.enabled_committees ?? []).length} 个委员会
            </button>
            {showCommittees && (
              <div className="flex flex-wrap gap-2">
                {(selectedMode?.enabled_committees ?? []).map((committee) => <Badge key={committee}>{displayCommittee(committee)}</Badge>)}
              </div>
            )}
          </section>

          <div className="grid grid-cols-1 gap-2 border-t border-slate-200 pt-4">
            <button
              type="button"
              onClick={generateModelMemo}
              disabled={!config.llm?.configured || isGenerating}
              className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-3 py-2 text-sm font-medium text-white disabled:opacity-40"
            >
              <RefreshCw size={16} className={isGenerating ? "animate-spin" : ""} />
              {isGenerating ? "正在生成董事会建议书..." : "生成董事会建议书"}
            </button>
          </div>
          <div className={`rounded-md px-3 py-2 text-xs ${isGenerating ? "border border-blue-200 bg-blue-50 text-blue-800" : "border border-slate-200 bg-slate-50 text-slate-600"}`}>
            {isGenerating ? `正在调用 ${config.llm?.model ?? "模型"}，生成通常需要几十秒，请勿重复点击。` : status}
          </div>
        </form>

        <section className="rounded-lg border border-slate-200 bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <FileText size={18} />
                <h2 className="text-base font-semibold">董事会建议书</h2>
              </div>
              <div className="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1 text-xs">
                <button
                  type="button"
                  onClick={() => setActiveMemoView("visual")}
                  className={`rounded px-3 py-1.5 ${activeMemoView === "visual" ? "bg-slate-950 text-white" : "text-slate-600"}`}
                >
                  视觉版
                </button>
                <button
                  type="button"
                  onClick={() => setActiveMemoView("memo")}
                  className={`rounded px-3 py-1.5 ${activeMemoView === "memo" ? "bg-slate-950 text-white" : "text-slate-600"}`}
                >
                  正文版
                </button>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={!preview}
                onClick={() => exportVisualReport("md")}
                className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 disabled:opacity-40"
              >
                <Download size={15} />
                导出视觉报告
              </button>
              <button
                type="button"
                disabled={!preview}
                onClick={() => exportVisualReport("html")}
                className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 disabled:opacity-40"
              >
                <Download size={15} />
                导出 HTML
              </button>
              <button
                type="button"
                disabled={!preview}
                onClick={exportBoardMemo}
                className="inline-flex items-center gap-2 rounded-md bg-slate-950 px-3 py-2 text-sm text-white disabled:opacity-40"
              >
                <Download size={15} />
                导出建议书
              </button>
            </div>
          </div>
          {isGenerating ? (
            <div className="flex h-[690px] items-start gap-3 p-4 text-sm leading-6 text-slate-700">
              <RefreshCw size={18} className="mt-1 animate-spin text-slate-500" />
              <div>
                <div className="font-medium text-slate-900">正在生成董事会建议书</div>
                <div className="mt-1 text-slate-500">已向 {config.llm?.model ?? "模型"} 提交审议请求，等待模型返回。</div>
              </div>
            </div>
          ) : generationError ? (
            <div className="h-[690px] overflow-auto p-4 text-sm leading-6">
              <div className="rounded-md border border-red-200 bg-red-50 p-4 text-red-800">
                <div className="font-medium">生成失败</div>
                <div className="mt-1 whitespace-pre-wrap break-words">{generationError}</div>
              </div>
            </div>
          ) : (
            activeMemoView === "visual" ? (
              <VisualReportView report={preview?.visual_report} />
            ) : (
              <pre className="h-[690px] overflow-auto whitespace-pre-wrap p-4 text-sm leading-6 text-slate-700">
                {preview?.board_memo ?? "上传或输入材料后，点击“生成董事会建议书”。"}
              </pre>
            )
          )}
        </section>

        <aside className="space-y-4">
          <section className="rounded-lg border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <div>
                <h2 className="text-base font-semibold">分析详情</h2>
                <div className="mt-1 text-xs text-slate-500">
                  可引用来源块：{(preview?.material_pack?.source_blocks ?? materialPack?.source_blocks ?? []).length}
                </div>
              </div>
              <button
                type="button"
                onClick={() => setDetailsOpen((value) => !value)}
                className="rounded-md border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:bg-slate-50"
              >
                {detailsOpen ? "收起" : "展开"}
              </button>
            </div>
            {!detailsOpen ? (
              <div className="space-y-3 p-4 text-sm leading-6 text-slate-700">
                <div className="rounded-md border border-slate-200 p-3">
                  <div className="font-medium">{preview?.material_pack?.title ?? materialPack?.title ?? "暂无材料包"}</div>
                  <div className="mt-1 text-xs text-slate-500">
                    {(preview?.material_pack?.files ?? materialPack?.files ?? []).length} 个材料文件 · {(preview?.material_pack?.source_blocks ?? materialPack?.source_blocks ?? []).length} 个可引用来源块
                  </div>
                  <div className="mt-1 text-xs text-slate-500">
                    本体命中：{ontologyRows(preview).length} 条规则
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleRecord}
                  disabled={!preview}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm disabled:opacity-40"
                >
                  <Save size={16} />
                  写入记录
                </button>
              </div>
            ) : (
              <>
                <div className="flex flex-wrap gap-2 border-b border-slate-200 p-3 text-xs">
                  {detailTabs.map(([id, label]) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setActiveTab(id)}
                      className={`rounded-md px-3 py-2 ${activeTab === id ? "bg-slate-950 text-white" : "border border-slate-300 text-slate-600"}`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <div className="min-h-[320px] p-4 text-sm leading-6 text-slate-700">
                  {activeTab === "materials" && (
                    <div className="space-y-3">
                      <div className="font-medium">{preview?.material_pack?.title ?? materialPack?.title ?? "暂无材料包"}</div>
                      {(preview?.material_pack?.files ?? materialPack?.files ?? []).map((file) => (
                        <div key={file.file_id ?? file.name} className="rounded-md border border-slate-200 p-2">
                          <div className="font-medium">{file.name}</div>
                          <div className="text-xs text-slate-500">{formatFileSize(file.size)} · {valueLabels[file.status ?? "read"] ?? file.status}</div>
                        </div>
                      ))}
                      <div className="text-xs text-slate-500">
                        可引用来源块：{(preview?.material_pack?.source_blocks ?? materialPack?.source_blocks ?? []).length} 个，同一文件可拆分为多个来源块
                      </div>
                    </div>
                  )}
                  {activeTab === "ontology" && (
                    <div className="space-y-3">
                      {ontologyRows(preview).length === 0 && <div className="text-slate-500">暂无本体规则命中</div>}
                      {ontologyRows(preview).map((row, index) => (
                        <div key={`${row.persona_id}-${row.rule_id}-${index}`} className="rounded-md border border-slate-200 p-3">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="font-medium">{row.persona_name ?? row.persona_id}</span>
                            <Badge>{displayCommittee(row.committee)}</Badge>
                          </div>
                          <div className="mt-2 text-xs text-slate-500">{row.rule_id}</div>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {row.triggered_by.map((trigger) => <Badge key={trigger}>{trigger}</Badge>)}
                          </div>
                          <div className="mt-3 text-xs text-slate-600">
                            证据缺口：{(row.missing_evidence ?? []).join("、") || "未记录"}
                          </div>
                          <div className="mt-1 text-xs text-slate-600">
                            反证实验：{row.counter_test || "未记录"}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {activeTab === "rules" && (
                    <div className="space-y-3">
                      {committeeRuleRows(preview).length === 0 && <div className="text-slate-500">暂无委员会规则链</div>}
                      {committeeRuleRows(preview).map((group) => (
                        <div key={group.committee} className="rounded-md border border-slate-200 p-3">
                          <div className="font-medium">{displayCommittee(group.committee)}</div>
                          <div className="mt-3 space-y-2">
                            {group.rule_hits.map((hit, index) => (
                              <div key={`${hit.persona_id}-${hit.rule_id}-${index}`} className="rounded-md bg-slate-50 p-2 text-xs">
                                <div className="font-medium text-slate-800">{hit.persona_name ?? hit.persona_id} / {hit.rule_id}</div>
                                <div className="mt-1 text-slate-500">触发词：{hit.triggered_by.join("、") || "未记录"}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {activeTab === "evidence" && (
                    <div className="space-y-3">
                      {evidenceRows(preview).length === 0 && <div className="text-slate-500">暂无依据</div>}
                      {evidenceRows(preview).map((row, index) => (
                        <div key={index} className="rounded-md border border-slate-200 p-3">
                          <div className="font-medium">{row.claim}</div>
                          <div className="mt-1 text-xs text-slate-500">
                            {valueLabels[row.claim_type] ?? row.claim_type} · {valueLabels[row.confidence] ?? row.confidence} · {row.source_file ?? "无来源文件"} / {row.source_block_id ?? "无来源块"}
                          </div>
                          <div className="mt-2 text-xs text-slate-600">{row.source_excerpt}</div>
                        </div>
                      ))}
                    </div>
                  )}
                  {activeTab === "assumptions" && (
                    <pre className="whitespace-pre-wrap">{formatJson(assumptionRows(preview))}</pre>
                  )}
                  {activeTab === "flow" && (
                    <div className="space-y-2">
                      {(preview?.review_run?.stages ?? []).map((stage) => (
                        <div key={stage.stage_id} className="rounded-md border border-slate-200 p-3">
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-medium">{stage.name}</span>
                            <span className="rounded-md bg-slate-100 px-2 py-1 text-xs">{valueLabels[stage.status] ?? stage.status}</span>
                          </div>
                          <div className="mt-1 text-xs text-slate-500">{stage.summary}</div>
                        </div>
                      ))}
                      {!preview?.review_run && <div className="text-slate-500">暂无生成过程</div>}
                    </div>
                  )}
                  {activeTab === "record" && (
                    <div className="space-y-3">
                      <pre className="max-h-56 overflow-auto whitespace-pre-wrap rounded-md bg-slate-50 p-3">{formatJson(preview?.record ?? {})}</pre>
                      <div className="grid grid-cols-3 gap-2">
                        <button type="button" disabled={!preview} onClick={() => exportRecord("md")} className="rounded-md border border-slate-300 px-2 py-2 text-xs disabled:opacity-40">导出 MD</button>
                        <button type="button" disabled={!preview} onClick={() => exportRecord("json")} className="rounded-md border border-slate-300 px-2 py-2 text-xs disabled:opacity-40">导出 JSON</button>
                        <button type="button" disabled={!preview} onClick={() => exportRecord("html")} className="rounded-md border border-slate-300 px-2 py-2 text-xs disabled:opacity-40">导出 HTML</button>
                      </div>
                      <button type="button" disabled={!preview} onClick={handleCalibration} className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm disabled:opacity-40">记录校准事件</button>
                    </div>
                  )}
                </div>
                <div className="border-t border-slate-200 p-4">
                  <button
                    type="button"
                    disabled={!preview}
                    onClick={handleRecord}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm disabled:opacity-40"
                  >
                    <Save size={16} />
                    写入记录
                  </button>
                </div>
              </>
            )}
          </section>
        </aside>
      </section>
    </main>
  );
}
