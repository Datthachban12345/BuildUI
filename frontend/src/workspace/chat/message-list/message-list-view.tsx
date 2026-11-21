import React from 'react';
import { Bot, User, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react';
import { ChatMessage } from '../../workspace-store';
import { useMessageListStore } from './message-list-store';

export interface MessageListViewProps {
  messages: ChatMessage[];
  onSendMessage: (prompt: string) => void;
}

export const MessageListView: React.FC<MessageListViewProps> = ({ messages, onSendMessage }) => {
  const { messagesEndRef, starterPrompts } = useMessageListStore(messages);

  return (
    <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-[#fbfbfd]">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col justify-center text-center px-4 py-8 space-y-5">
          <div className="w-14 h-14 rounded-3xl bg-white border border-zinc-200/80 shadow-[0_4px_16px_rgba(0,0,0,0.04)] flex items-center justify-center mx-auto text-zinc-800">
            <Bot className="w-7 h-7 text-zinc-900" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-zinc-900 tracking-tight mb-1.5">Trợ lý Thiết kế AI</h3>
            <p className="text-xs text-zinc-500 leading-relaxed max-w-xs mx-auto">
              Nhập yêu cầu bằng ngôn ngữ tự nhiên. Agent sẽ tự động lập kế hoạch và dựng giao diện tương tác trực tiếp lên canvas bên phải.
            </p>
          </div>
          <div className="space-y-2 pt-2 text-left">
            <div className="text-[11px] uppercase tracking-wider text-zinc-400 font-semibold px-1">Gợi ý bắt đầu:</div>
            {starterPrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => onSendMessage(prompt)}
                className="w-full text-left p-3.5 rounded-2xl bg-white hover:bg-zinc-50 border border-zinc-200/80 text-xs text-zinc-700 hover:text-zinc-950 shadow-sm transition-all flex items-center justify-between group hover:border-zinc-300"
              >
                <span className="line-clamp-2 leading-relaxed">{prompt}</span>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-400 group-hover:text-zinc-900 shrink-0 ml-2 transition-transform group-hover:translate-x-0.5" />
              </button>
            ))}
          </div>
        </div>
      ) : (
        messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 text-xs ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'agent' && (
              <div className="w-7 h-7 rounded-full bg-zinc-900 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-sm">
                <Bot className="w-3.5 h-3.5 text-white" />
              </div>
            )}
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                msg.sender === 'user'
                  ? 'bg-zinc-900 text-white font-normal shadow-[0_2px_8px_rgba(0,0,0,0.08)]'
                  : 'bg-white border border-zinc-200/90 text-zinc-800 shadow-[0_2px_8px_rgba(0,0,0,0.03)]'
              }`}
            >
              <div className="whitespace-pre-wrap leading-relaxed text-xs">{msg.content}</div>

              {msg.console && msg.console.length > 0 && (
                <section
                  aria-label="Agent console"
                  className="mt-3 overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950 text-[10px] text-zinc-200"
                >
                  <div className="flex items-center gap-2 border-b border-zinc-800 px-3 py-2 font-semibold tracking-wide text-zinc-300">
                    <span className="text-emerald-400">&gt;_</span>
                    AGENT CONSOLE
                  </div>
                  <div className="max-h-64 space-y-2 overflow-auto px-3 py-2">
                    {msg.console.map((entry, idx) => (
                      <div key={idx} className="space-y-1">
                        <div
                          className={
                            entry.level === 'error'
                              ? 'text-rose-300'
                              : entry.level === 'warning'
                                ? 'text-amber-300'
                                : entry.level === 'success'
                                  ? 'text-emerald-300'
                                  : 'text-zinc-300'
                          }
                        >
                          {entry.message}
                        </div>
                        {entry.provider && <div className="text-zinc-400">Provider: {entry.provider}</div>}
                        {entry.model && <div className="text-zinc-400">Model: {entry.model}</div>}
                        {entry.data !== undefined && (
                          <details open className="rounded-lg bg-black/40 p-2">
                            <summary className="cursor-pointer text-zinc-400">Xem dữ liệu phản hồi</summary>
                            <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-words text-[9px] leading-relaxed text-zinc-200">
                              {typeof entry.data === 'string'
                                ? entry.data
                                : JSON.stringify(entry.data, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Agent Steps / Planning Breakdown */}
              {msg.steps && msg.steps.length > 0 && (
                <div className="mt-3 pt-3 border-t border-zinc-100 space-y-2 text-[11px]">
                  <div className="text-[10px] uppercase text-zinc-400 font-semibold tracking-wider">Tiến trình triển khai:</div>
                  {msg.steps.map((step: string, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 text-zinc-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span className="leading-tight">{step}</span>
                    </div>
                  ))}
                </div>
              )}

              {msg.isStreaming && (
                <div className="mt-2.5 flex items-center gap-1.5 text-[11px] text-amber-600 font-medium">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-600" />
                  <span>Đang render các khối A2UI...</span>
                </div>
              )}
            </div>
            {msg.sender === 'user' && (
              <div className="w-7 h-7 rounded-full bg-zinc-200 flex items-center justify-center text-zinc-700 shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        ))
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};
