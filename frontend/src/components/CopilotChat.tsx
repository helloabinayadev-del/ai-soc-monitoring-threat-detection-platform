import React, { useState } from 'react';
import { Bot, Send, Sparkles, ShieldCheck, ExternalLink, RefreshCw, AlertCircle, CheckCircle2, HelpCircle } from 'lucide-react';
import { copilotApi } from '../services/api';
import { CopilotResponse } from '../types';

interface Message {
  id: string;
  sender: 'user' | 'copilot';
  text: string;
  data?: CopilotResponse;
}

export const CopilotChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'copilot',
      text: 'Greetings, SOC Analyst. I am your Evidence-Driven AI Security Copilot. Ask me to perform 10-point grounded triage on active security alerts or log telemetry.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const suggestedPrompts = [
    'Analyze the latest critical alert with 10-point evidence breakdown.',
    'Explain the Isolation Forest anomaly score for recent authentication logs.',
    'Provide step-by-step containment playbook for suspicious execution.',
  ];

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend,
    };
    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput('');
    setLoading(true);

    try {
      const res = await copilotApi.queryCopilot(textToSend);
      const copilotMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'copilot',
        text: res.answer,
        data: res,
      };
      setMessages((prev) => [...prev, copilotMsg]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'copilot',
          text: 'Error connecting to AI Copilot engine. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[650px] rounded-xl border border-soc-border bg-soc-card/90 glass-panel">
      {/* Header */}
      <div className="p-4 border-b border-soc-border flex items-center justify-between bg-soc-bg/50">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
              Explainable AI Security Copilot
              <span className="text-[10px] font-mono bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded border border-cyan-800">
                10-Point Evidence Framework
              </span>
            </h3>
            <p className="text-[11px] text-slate-400 font-mono">Telemetry Grounded Analysis & Non-Fabricated Evidence</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-xl p-4 text-xs ${
                m.sender === 'user'
                  ? 'bg-cyan-950 border border-cyan-800 text-cyan-100'
                  : 'bg-slate-900 border border-soc-border text-slate-200'
              }`}
            >
              <div className="whitespace-pre-line font-sans leading-relaxed">{m.text}</div>

              {/* Extended Copilot Output Details */}
              {m.data && (
                <div className="mt-3 pt-3 border-t border-slate-800 space-y-3 font-mono">
                  {/* Empirical Evidence Box */}
                  {m.data.evidence_items && m.data.evidence_items.length > 0 && (
                    <div className="p-2.5 rounded bg-slate-950 border border-slate-800 space-y-1">
                      <div className="text-[10px] text-cyan-400 font-bold uppercase flex items-center gap-1">
                        <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400" /> EMPIRICAL TELEMETRY EVIDENCE:
                      </div>
                      <ul className="list-disc list-inside space-y-0.5 text-[11px] text-slate-300">
                        {m.data.evidence_items.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Uncertainty Statement Warning */}
                  {m.data.uncertainty_statement && (
                    <div className="p-2.5 rounded bg-amber-950/40 border border-amber-800 text-amber-200 flex items-start gap-2">
                      <HelpCircle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-bold text-amber-400 uppercase text-[10px]">UNCERTAINTY & TELEMETRY GAPS:</span>
                        <div className="text-[11px] font-sans mt-0.5">{m.data.uncertainty_statement}</div>
                      </div>
                    </div>
                  )}

                  {m.data.action_items && m.data.action_items.length > 0 && (
                    <div>
                      <div className="text-[10px] text-slate-400 font-bold uppercase mb-1 flex items-center gap-1">
                        <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" /> RECOMMENDED INVESTIGATION & REMEDIATION:
                      </div>
                      <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-300">
                        {m.data.action_items.map((act, idx) => (
                          <li key={idx}>{act}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {m.data.mitre_references && m.data.mitre_references.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {m.data.mitre_references.map((ref, idx) => (
                        <span key={idx} className="text-[10px] bg-purple-950 text-purple-300 border border-purple-800 px-2 py-0.5 rounded">
                          {ref}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-900 border border-soc-border rounded-xl p-4 text-xs text-slate-400 flex items-center space-x-2">
              <RefreshCw className="h-4 w-4 animate-spin text-cyan-400" />
              <span>Running 10-point evidence analysis against SIEM telemetry...</span>
            </div>
          </div>
        )}
      </div>

      {/* Suggested Prompts */}
      <div className="px-4 py-2 bg-soc-bg/40 border-t border-soc-border flex items-center gap-2 overflow-x-auto">
        <Sparkles className="h-4 w-4 text-cyan-400 shrink-0" />
        {suggestedPrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            className="text-[11px] font-mono whitespace-nowrap px-3 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="p-3 border-t border-soc-border bg-soc-bg/60">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <input
            id="copilot-query-input"
            name="copilotQuery"
            type="text"
            autoComplete="off"
            aria-label="Ask AI Copilot for threat analysis or response playbook"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask AI Copilot for 10-point evidence triage..."
            className="flex-1 bg-soc-bg border border-soc-border rounded-lg px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
          <button
            type="submit"
            disabled={loading}
            className="p-2.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white transition disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
