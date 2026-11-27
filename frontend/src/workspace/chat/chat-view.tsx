import React from 'react';
import { Sparkles, Code2 } from 'lucide-react';
import { ChatMessage } from '../workspace-store';
import { MessageListView } from './message-list/message-list-view';
import { InputBarView } from './input-bar/input-bar-view';
import { useChatStore } from './chat-store';

export interface ChatViewProps {
  messages: ChatMessage[];
  onSendMessage: (prompt: string) => void;
  isGenerating: boolean;
  onLoadFixture: (fixtureName: string) => void;
}

export const ChatView: React.FC<ChatViewProps> = ({
  messages,
  onSendMessage,
  isGenerating,
  onLoadFixture,
}) => {
  const { isFixtureMenuOpen, setIsFixtureMenuOpen } = useChatStore();

  return (
    <aside className="w-[400px] flex flex-col h-full bg-white border-r border-zinc-200/80 shrink-0 shadow-[2px_0_12px_rgba(0,0,0,0.02)] z-10">
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
            onClick={() => setIsFixtureMenuOpen(!isFixtureMenuOpen)}
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
      <MessageListView messages={messages} onSendMessage={onSendMessage} />

      {/* Input Area */}
      <InputBarView onSendMessage={onSendMessage} isGenerating={isGenerating} />
    </aside>
  );
};
