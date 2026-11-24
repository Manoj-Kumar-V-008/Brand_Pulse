import React, { useMemo, useState } from "react";
import { ExternalLink, Filter, MessageSquareQuote } from "lucide-react";
import { MentionItem } from "../types";

interface MentionsFeedProps {
  mentions: MentionItem[];
  selectedMentionId: string | null;
  onSelectMention: (m: MentionItem) => void;
}

export const MentionsFeed: React.FC<MentionsFeedProps> = ({ mentions, selectedMentionId, onSelectMention }) => {
  const [filter, setFilter] = useState<"ALL" | "Positive" | "Neutral" | "Negative">("ALL");
  const filtered = useMemo(() => (filter === "ALL" ? mentions : mentions.filter((m) => m.sentiment_label === filter)), [mentions, filter]);
  const selectedMention = useMemo(() => mentions.find((m) => m.id === selectedMentionId) || null, [mentions, selectedMentionId]);

  return (
    <section className="glass-panel rounded-2xl p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <MessageSquareQuote className="h-5 w-5 text-cyan-400" />
          <h3 className="text-base font-bold text-white">Analyzed Brand Mentions & Per-Post Reasoning ({filtered.length})</h3>
        </div>
        <div className="flex items-center gap-1.5 rounded-xl border border-slate-800 bg-obsidian-950/80 p-1">
          <Filter className="ml-1.5 h-3.5 w-3.5 text-slate-400" />
          {(["ALL", "Positive", "Neutral", "Negative"] as const).map((f) => (
            <button key={f} onClick={() => setFilter(f)} className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition ${filter === f ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"}`}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {selectedMention && (
        <div className="mt-4 rounded-xl border border-cyan-400/50 bg-cyan-500/10 p-3.5">
          <div className="flex items-center justify-between text-xs text-cyan-300">
            <span className="font-mono font-bold uppercase">Selected 3D Node Inspection</span>
            <span>{selectedMention.source} • {selectedMention.author}</span>
          </div>
          <p className="mt-1 text-sm font-semibold text-white">{selectedMention.title}</p>
          <p className="mt-1 text-xs text-slate-300">{selectedMention.clean_text}</p>
          <p className="mt-2 font-mono text-xs text-cyan-200">{selectedMention.reason_snippet}</p>
        </div>
      )}

      <div className="mt-4 grid max-h-[520px] gap-3 overflow-y-auto pr-1 md:grid-cols-2">
        {filtered.map((m) => {
          const isSel = m.id === selectedMentionId;
          const badgeCls =
            m.sentiment_label === "Positive" ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-300" :
            m.sentiment_label === "Negative" ? "border-rose-500/40 bg-rose-500/15 text-rose-300" :
            "border-amber-500/40 bg-amber-500/15 text-amber-300";

          return (
            <div key={m.id} onClick={() => onSelectMention(m)} className={`cursor-pointer rounded-xl border p-4 transition ${isSel ? "border-cyan-400 bg-obsidian-800/90 shadow-lg shadow-cyan-500/10" : "border-slate-800/90 bg-obsidian-900/70 hover:border-slate-700"}`}>
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] font-semibold text-cyan-300">{m.source}</span>
                  <span className="max-w-[140px] truncate">{m.author}</span>
                </div>
                <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${badgeCls}`}>
                  {m.sentiment_label} ({m.ensemble_score >= 0 ? "+" : ""}{m.ensemble_score.toFixed(2)})
                </span>
              </div>

              <h4 className="mt-2 line-clamp-2 text-sm font-semibold text-white">{m.title}</h4>
              <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-400">{m.clean_text}</p>

              <div className="mt-3 flex flex-wrap items-center gap-3 rounded-lg bg-obsidian-950/75 px-2.5 py-1.5 font-mono text-[11px]">
                <span className="text-slate-400">VADER: <strong className={m.vader_score >= 0 ? "text-emerald-300" : "text-rose-300"}>{m.vader_score >= 0 ? "+" : ""}{m.vader_score.toFixed(2)}</strong></span>
                <span className="text-slate-600">|</span>
                <span className="text-slate-400">BERT/ML: <strong className={m.bert_score >= 0 ? "text-emerald-300" : "text-rose-300"}>{m.bert_score >= 0 ? "+" : ""}{m.bert_score.toFixed(2)}</strong></span>
                <span className="ml-auto text-slate-500">Conf {Math.round(m.confidence * 100)}%</span>
              </div>

              <p className="mt-2 text-[11px] italic text-cyan-200/90">{m.reason_snippet}</p>

              <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2">
                <div className="flex flex-wrap gap-1.5">
                  {m.aspects.map((asp) => (
                    <span key={asp} className="rounded-md border border-indigo-500/30 bg-indigo-500/10 px-2 py-0.5 text-[10px] font-medium text-indigo-200">{asp}</span>
                  ))}
                </div>
                {m.url && (
                  <a href={m.url} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()} className="inline-flex items-center gap-1 text-[11px] font-medium text-cyan-400 hover:underline">
                    Source <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
