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
    <aside className="w-[400px] flex flex-col h-full bg-white border-r border-zinc-200/80 shrink-0 select-none shadow-[2px_0_12px_rgba(0,0,0,0.02)] z-10">
      {/* Header - Apple frosted styling */}
      <div className="h-16 px-5 border-b border-zinc-200/80 flex items-center justify-between bg-white/90 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-zinc-950 flex items-center justify-center text-white shadow-sm">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-xs font-semibold text-zinc-900 tracking-tight">A2UI Copilot</h2>
            <div className="flex items-center gap-1.5 text-[11px] text-zinc-500 font-normal">
              <span className={`w-1.5 h-1.5 rounded-full ${isGenerating ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`} />
              {isGenerating ? 'Đang tạo giao diện...' : 'Sẵn sàng nhận lệnh'}
            </div>
          </div>
        </div>

        {/* Fixture Test Dropdown */}
        <div className="relative group">
          <button
            title="Load Deterministic Fixture"
            className="px-2.5 py-1.5 rounded-full bg-zinc-100 hover:bg-zinc-200/70 text-zinc-700 transition flex items-center gap-1.5 text-xs font-medium border border-zinc-200/60"
          >
            <Code2 className="w-3.5 h-3.5 text-zinc-600" />
            <span>Mẫu thử</span>
          </button>
          <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-zinc-200 rounded-2xl shadow-xl p-1.5 hidden group-hover:block z-50">
            <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider px-2.5 py-1.5">Offline Fixtures</div>
            <button
              onClick={() => onLoadFixture('landing_page')}
              className="w-full text-left px-2.5 py-2 rounded-xl text-xs text-zinc-800 hover:bg-zinc-100 transition flex items-center gap-2"
            >
              <span>📷</span>
              <span>Minimalist Studio</span>
            </button>
            <button
              onClick={() => onLoadFixture('data_table')}
              className="w-full text-left px-2.5 py-2 rounded-xl text-xs text-zinc-800 hover:bg-zinc-100 transition flex items-center gap-2"
            >
              <span>📊</span>
              <span>Analytics Dashboard</span>
            </button>
          </div>
        </div>
      </div>

      {/* Messages Scroll Area */}
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
              {STARTER_PROMPTS.map((prompt, i) => (
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

                {/* Agent Steps / Planning Breakdown */}
                {msg.steps && msg.steps.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-zinc-100 space-y-2 text-[11px]">
                    <div className="text-[10px] uppercase text-zinc-400 font-semibold tracking-wider">Tiến trình triển khai:</div>
                    {msg.steps.map((step, idx) => (
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

      {/* Input Area - Apple search/input style */}
      <div className="p-4 border-t border-zinc-200/80 bg-white">
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
            placeholder="Yêu cầu Agent tạo hoặc sửa giao diện..."
            className="w-full bg-[#f5f5f7] focus:bg-white border border-zinc-200 focus:border-zinc-400 focus:ring-4 focus:ring-zinc-100 rounded-2xl px-4 py-3 pr-12 text-xs text-zinc-900 placeholder-zinc-400 outline-none resize-none transition duration-200"
          />
          <button
            type="submit"
            disabled={!input.trim() || isGenerating}
            className={`absolute right-3 bottom-4 p-2 rounded-full transition-all ${
              input.trim() && !isGenerating
                ? 'bg-zinc-950 text-white hover:bg-black cursor-pointer shadow-sm hover:scale-105 active:scale-95'
                : 'text-zinc-400 bg-zinc-200/60 cursor-not-allowed'
            }`}
          >
            {isGenerating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          </button>
        </form>
        <div className="text-[10px] text-zinc-400 text-center mt-2 font-normal">
          Nhấn Enter để gửi · Shift + Enter để xuống dòng
        </div>
      </div>
    </aside>
  );
};
