import React, { useRef, useEffect } from 'react';
import { Sparkles, Send, Bot, User, ArrowRight, Loader2, Code2, CheckCircle2 } from 'lucide-react';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: string;
  steps?: string[];
  isStreaming?: boolean;
}

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (prompt: string) => void;
  isGenerating: boolean;
  onLoadFixture: (fixtureName: string) => void;
}

const STARTER_PROMPTS = [
  "Tạo landing page cho studio chụp ảnh phong cách tối giản có bảng giá và form đặt lịch",
  "Tạo SaaS dashboard thống kê doanh thu với bảng dữ liệu dự án và metrics cards",
  "Đổi tiêu đề hero sang phong cách sang trọng và thêm nút Đăng ký ngay"
];

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  onSendMessage,
  isGenerating,
  onLoadFixture
}) => {
  const [input, setInput] = React.useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;
    onSendMessage(input.trim());
    setInput('');
  };

  return (
    <aside className="w-96 flex flex-col h-full bg-zinc-950 border-r border-zinc-800/80 shrink-0 select-none">
      {/* Header */}
      <div className="h-14 px-4 border-b border-zinc-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-white shadow-inner">
            <Sparkles className="w-4 h-4 text-zinc-100" />
          </div>
          <div>
            <h2 className="text-xs font-semibold text-white tracking-wide uppercase">AI Agent Copilot</h2>
            <div className="flex items-center gap-1.5 text-[10px] text-zinc-400">
              <span className={`w-1.5 h-1.5 rounded-full ${isGenerating ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'}`} />
              {isGenerating ? 'Agent đang tạo UI...' : 'Sẵn sàng nhận lệnh'}
            </div>
          </div>
        </div>

        {/* Fixture Test Dropdown for deterministic check */}
        <div className="relative group">
          <button
            title="Load Deterministic Fixture"
            className="p-1.5 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-900 transition flex items-center gap-1 text-[11px]"
          >
            <Code2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Fixtures</span>
          </button>
          <div className="absolute right-0 top-full mt-1 w-52 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl p-1.5 hidden group-hover:block z-50">
            <div className="text-[10px] font-semibold text-zinc-500 uppercase px-2 py-1">Test Fixtures (Offline)</div>
            <button
              onClick={() => onLoadFixture('landing_page')}
              className="w-full text-left px-2 py-1.5 rounded text-xs text-zinc-300 hover:text-white hover:bg-zinc-800 transition"
            >
              📷 Minimalist Studio
            </button>
            <button
              onClick={() => onLoadFixture('data_table')}
              className="w-full text-left px-2 py-1.5 rounded text-xs text-zinc-300 hover:text-white hover:bg-zinc-800 transition"
            >
              📊 Analytics Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col justify-center text-center px-4 py-8 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-zinc-900/80 border border-zinc-800 flex items-center justify-center mx-auto text-zinc-400">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-white mb-1">Figma Make AI Studio</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Trò chuyện với Agent để tạo website tương tác trực tiếp lên canvas bên phải.
              </p>
            </div>
            <div className="space-y-2 pt-2">
              <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold text-left">Gợi ý yêu cầu:</div>
              {STARTER_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => onSendMessage(prompt)}
                  className="w-full text-left p-2.5 rounded-lg bg-zinc-900/40 hover:bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-white transition flex items-center justify-between group"
                >
                  <span className="line-clamp-2">{prompt}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-zinc-500 group-hover:text-zinc-200 shrink-0 ml-2" />
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
                <div className="w-6 h-6 rounded-md bg-zinc-800 border border-zinc-700 flex items-center justify-center text-white shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5 text-blue-400" />
                </div>
              )}
              <div
                className={`max-w-[85%] rounded-xl px-3.5 py-2.5 ${
                  msg.sender === 'user'
                    ? 'bg-zinc-100 text-zinc-950 font-medium'
                    : 'bg-zinc-900/80 border border-zinc-800 text-zinc-200'
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>

                {/* Agent Steps / Planning Breakdown */}
                {msg.steps && msg.steps.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-zinc-800/80 space-y-1.5 font-mono text-[11px]">
                    <div className="text-[10px] uppercase text-zinc-500 font-semibold">Tiến trình Agent:</div>
                    {msg.steps.map((step, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 text-zinc-400">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                )}

                {msg.isStreaming && (
                  <div className="mt-2 flex items-center gap-1.5 text-[11px] text-amber-400 font-mono">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Đang stream A2UI messages...</span>
                  </div>
                )}
              </div>
              {msg.sender === 'user' && (
                <div className="w-6 h-6 rounded-md bg-zinc-200 flex items-center justify-center text-zinc-900 shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 border-t border-zinc-800/80 bg-zinc-950/80">
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Yêu cầu Agent tạo hoặc sửa website..."
            className="w-full bg-zinc-900 border border-zinc-800 focus:border-zinc-500 rounded-xl px-3.5 py-2.5 pr-10 text-xs text-zinc-100 placeholder-zinc-500 outline-none resize-none transition"
          />
          <button
            type="submit"
            disabled={!input.trim() || isGenerating}
            className={`absolute right-2.5 bottom-3.5 p-1.5 rounded-lg transition ${
              input.trim() && !isGenerating
                ? 'bg-zinc-100 text-zinc-900 hover:bg-white cursor-pointer shadow-sm'
                : 'text-zinc-600 bg-zinc-800/50 cursor-not-allowed'
            }`}
          >
            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </form>
        <div className="text-[10px] text-zinc-500 text-center mt-2">
          Shift + Enter để xuống dòng · Nhấn Enter để gửi
        </div>
      </div>
    </aside>
  );
};
