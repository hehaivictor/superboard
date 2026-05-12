import { FormEvent, useEffect, useMemo, useState } from "react";
import { Download, FileText, Layers, RefreshCw, Save, ShieldCheck } from "lucide-react";

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
};

const modeLabels: Record<string, string> = {
  quick_triage: "快速审议",
  deep_board_review: "深度董事会审议",
  red_team: "红队反证审查",
  pre_mortem: "事前验尸",
  investment_committee: "投资委员会",
  product_discovery: "产品发现审议",
  go_to_market_review: "市场进入审议"
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
};

const sampleMaterial = `# AI 会议复盘助手

目标：两周内把单场会议整理时间从 45 分钟降到 20 分钟以内。

用户：一线产品经理和产品负责人。

约束：第一版只支持手动上传会议转写文本，不接 IM、日历、CRM 或任务系统。

风险：行动项负责人经常不明确，用户担心 AI 编造结论。`;

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

export function App() {
  const [config, setConfig] = useState<Config>(fallbackConfig);
  const [modeId, setModeId] = useState("deep_board_review");
  const [material, setMaterial] = useState(sampleMaterial);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [records, setRecords] = useState<Array<Record<string, string>>>([]);
  const [activeTab, setActiveTab] = useState<"evidence" | "assumptions" | "record">("evidence");
  const [status, setStatus] = useState("本地工作台就绪");

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
      body: JSON.stringify({ material, mode_id: modeId })
    });
    if (!response.ok) {
      setStatus("预览失败，请检查本地 API");
      return;
    }
    const payload = await response.json();
    setPreview(payload);
    setStatus("预览已生成，未调用外部模型");
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
          <label className="block text-sm font-medium text-slate-700" htmlFor="material">输入材料</label>
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
            <div className="grid grid-cols-3 border-b border-slate-200 text-sm">
              {[
                ["evidence", "证据包"],
                ["assumptions", "假设账本"],
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
              {activeTab === "evidence" && (
                <pre className="whitespace-pre-wrap">{formatJson(preview?.evidence_packets ?? [])}</pre>
              )}
              {activeTab === "assumptions" && (
                <pre className="whitespace-pre-wrap">{formatJson(preview?.assumptions ?? [])}</pre>
              )}
              {activeTab === "record" && (
                <pre className="whitespace-pre-wrap">{formatJson(preview?.record ?? {})}</pre>
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
                  <div className="font-medium">{record.title}</div>
                  <div className="mt-1 text-xs text-slate-500">{record.decision_id} · {displayMode(record.mode_id)}</div>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </section>
    </main>
  );
}
