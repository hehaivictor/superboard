import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { Download, FileText, Layers, RefreshCw, Save, ShieldCheck, Upload } from "lucide-react";

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
};

type Preview = {
  record: Record<string, unknown>;
  prompt_bundle: string;
  evidence_packets: Array<Record<string, string>>;
  assumptions: Array<Record<string, unknown>>;
  material_pack?: MaterialPack;
  review_run?: ReviewRun;
  action_items?: Array<Record<string, unknown>>;
  calibration_events?: Array<Record<string, unknown>>;
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
  modes: [
    {
      mode_id: "deep_board_review",
      name: "深度董事会审议",
      description: "完整五委员会审议，适合可转发建议书。",
      recommended_for: ["产品需求", "项目计划", "商业计划"],
      enabled_committees: ["business-leaders", "startup-mentors", "investment-masters", "consulting-elite", "product-users"],
      required_sections: ["Evidence Packet", "Assumption Ledger", "Decision Log Entry"],
      depth: "deep",
      include_persona_appendix: true
    }
  ]
};

const committeeLabels: Record<string, string> = {
  "business-leaders": "商业领袖组",
  "startup-mentors": "创业导师组",
  "investment-masters": "投资大师组",
  "consulting-elite": "咨询精英组",
  "product-users": "产品与用户组"
  , "synthetic-users": "用户模拟组"
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
  assumptions: "假设账本",
  evidence_packets: "证据包",
  follow_up_checkpoints: "复盘检查点",
  material_pack: "材料包",
  source_blocks: "来源块",
  source_file: "来源文件",
  source_block_id: "来源块",
  source_excerpt: "来源摘录",
  action_items: "行动项",
  review_run: "审议流程",
  calibration_events: "校准事件",
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

const sampleMaterial = `# AI 会议复盘助手

目标：两周内把单场会议整理时间从 45 分钟降到 20 分钟以内。

用户：一线产品经理和产品负责人。

约束：第一版只支持手动上传会议转写文本，不接 IM、日历、CRM 或任务系统。

风险：行动项负责人经常不明确，用户担心 AI 编造结论。`;

const supportedUploadTypes = ".md,.markdown,.txt,.json,.csv,.yaml,.yml";

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function Badge({ children }: { children: string }) {
  return <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-600">{children}</span>;
}

function displayBoard(boardId: string) {
  return boardId === "default" ? "默认董事会" : boardId;
}

function displayTemplate(version: string) {
  return version === "local-fallback" ? "本地模板" : `模板版本 ${version}`;
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

export function App() {
  const [config, setConfig] = useState<Config>(fallbackConfig);
  const [modeId, setModeId] = useState("deep_board_review");
  const [material, setMaterial] = useState(sampleMaterial);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [records, setRecords] = useState<Array<Record<string, string>>>([]);
  const [activeTab, setActiveTab] = useState<"materials" | "evidence" | "assumptions" | "flow" | "record">("materials");
  const [status, setStatus] = useState("本地工作台就绪");
  const [inputFileName, setInputFileName] = useState<string | null>(null);
  const [materialPack, setMaterialPack] = useState<MaterialPack | null>(null);

  useEffect(() => {
    fetch("/api/config")
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("config unavailable")))
      .then((payload: Config) => {
        setConfig(payload);
        setModeId(payload.modes[0]?.mode_id ?? "deep_board_review");
      })
      .catch(() => setConfig(fallbackConfig));
    refreshRecords();
  }, []);

  const selectedMode = useMemo(
    () => config.modes.find((mode) => mode.mode_id === modeId) ?? config.modes[0],
    [config.modes, modeId]
  );

  function refreshRecords() {
    fetch("/api/records")
      .then((response) => response.ok ? response.json() : { records: [] })
      .then((payload) => setRecords(payload.records ?? []))
      .catch(() => setRecords([]));
  }

  async function handlePreview(event: FormEvent) {
    event.preventDefault();
    setStatus("正在生成本地提示包");
    const response = await fetch("/api/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ material, mode_id: modeId, material_pack: materialPack })
    });
    if (!response.ok) {
      setStatus("预览失败，请检查本地 API");
      return;
    }
    const payload = await response.json();
    setPreview(payload);
    setStatus("预览已生成，未调用外部模型");
  }

  async function handleMaterialFile(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
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
    refreshRecords();
  }

  async function handleLoadRecord(decisionId: string) {
    const response = await fetch(`/api/records/${decisionId}`);
    if (!response.ok) {
      setStatus("记录读取失败");
      return;
    }
    const record = await response.json();
    setPreview({
      record,
      prompt_bundle: "已加载本地决策记录。可从右侧查看材料、证据、假设、流程和行动项。",
      evidence_packets: record.evidence_packets ?? [],
      assumptions: record.assumptions ?? [],
      material_pack: record.material_pack,
      review_run: record.review_run,
      action_items: record.action_items ?? [],
      calibration_events: record.calibration_events ?? []
    });
    setMaterialPack(record.material_pack ?? null);
    setActiveTab("record");
    setStatus("已加载本地决策记录");
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
            <Badge>{displayBoard(config.board_id)}</Badge>
            <Badge>{displayTemplate(config.template_version)}</Badge>
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl grid-cols-1 gap-4 px-5 py-5 lg:grid-cols-[360px_minmax(0,1fr)_360px]">
        <form onSubmit={handlePreview} className="space-y-4 rounded-lg border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2">
            <Layers size={18} />
            <h2 className="text-base font-semibold">材料与模式</h2>
          </div>
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
          <div className="flex flex-wrap gap-2">
            {(selectedMode?.enabled_committees ?? []).map((committee) => <Badge key={committee}>{displayCommittee(committee)}</Badge>)}
          </div>
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
              材料包：{materialPack.title} · {materialPack.files.length} 个文件 · {materialPack.source_blocks.length} 个来源块
            </div>
          )}
          <textarea
            id="material"
            value={material}
            onChange={(event) => setMaterial(event.target.value)}
            className="min-h-[420px] w-full resize-y rounded-md border border-slate-300 px-3 py-2 font-mono text-sm leading-6"
          />
          <button className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-3 py-2 text-sm font-medium text-white">
            <RefreshCw size={16} />
            生成预览
          </button>
        </form>

        <section className="rounded-lg border border-slate-200 bg-white">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
            <div className="flex items-center gap-2">
              <FileText size={18} />
              <h2 className="text-base font-semibold">审议预览</h2>
            </div>
            <button
              type="button"
              disabled={!preview}
              onClick={() => preview && downloadText("超级董事会提示包.md", preview.prompt_bundle)}
              className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm disabled:opacity-40"
            >
              <Download size={15} />
              导出
            </button>
          </div>
          <pre className="h-[690px] overflow-auto whitespace-pre-wrap p-4 text-sm leading-6 text-slate-700">
            {preview?.prompt_bundle ?? "生成预览后，这里会显示本地提示包。"}
          </pre>
        </section>

        <aside className="space-y-4">
          <section className="rounded-lg border border-slate-200 bg-white">
            <div className="grid grid-cols-5 border-b border-slate-200 text-xs">
              {[
                ["materials", "材料"],
                ["evidence", "证据"],
                ["assumptions", "假设账本"],
                ["flow", "流程"],
                ["record", "决策记录"]
              ].map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => setActiveTab(id as typeof activeTab)}
                  className={`px-3 py-2 ${activeTab === id ? "bg-slate-950 text-white" : "text-slate-600"}`}
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
                    来源块：{(preview?.material_pack?.source_blocks ?? materialPack?.source_blocks ?? []).length}
                  </div>
                </div>
              )}
              {activeTab === "evidence" && (
                <div className="space-y-3">
                  {evidenceRows(preview).length === 0 && <div className="text-slate-500">暂无证据包</div>}
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
                  {!preview?.review_run && <div className="text-slate-500">生成预览后显示审议流程。</div>}
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
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-4">
            <h2 className="text-base font-semibold">历史记录</h2>
            <p className="mt-1 text-sm text-slate-500">{status}</p>
            <div className="mt-4 space-y-2">
              {records.length === 0 && <div className="text-sm text-slate-500">暂无本地记录</div>}
              {records.map((record) => (
                <div key={record.decision_id} className="rounded-md border border-slate-200 p-3 text-sm">
                  <button type="button" onClick={() => handleLoadRecord(record.decision_id)} className="w-full text-left">
                    <div className="font-medium">{record.title}</div>
                    <div className="mt-1 text-xs text-slate-500">{record.decision_id} · {displayMode(record.mode_id)}</div>
                  </button>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </section>
    </main>
  );
}
