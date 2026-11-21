import React from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useInputBarStore, InputBarStoreProps } from './input-bar-store';

export const InputBarView: React.FC<InputBarStoreProps> = ({ onSendMessage, isGenerating }) => {
  const { input, setInput, handleSubmit, handleKeyDown, canSubmit } = useInputBarStore({
    onSendMessage,
    isGenerating,
  });

  return (
    <div className="p-4 border-t border-zinc-200/80 bg-white">
      <form onSubmit={handleSubmit} className="relative">
        <textarea
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Yêu cầu Agent tạo hoặc sửa giao diện..."
          className="w-full bg-[#f5f5f7] focus:bg-white border border-zinc-200 focus:border-zinc-400 focus:ring-4 focus:ring-zinc-100 rounded-2xl px-4 py-3 pr-12 text-xs text-zinc-900 placeholder-zinc-400 outline-none resize-none transition duration-200"
        />
        <button
          type="submit"
          disabled={!canSubmit}
          className={`absolute right-3 bottom-4 p-2 rounded-full transition-all ${
            canSubmit
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
  );
};
