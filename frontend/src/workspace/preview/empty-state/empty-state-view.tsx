import React from 'react';
import { Sparkles } from 'lucide-react';

interface EmptyStateViewProps {
  isGenerating: boolean;
}

export const EmptyStateView: React.FC<EmptyStateViewProps> = ({ isGenerating }) => (
  <div className="my-auto max-w-md text-center p-10 rounded-3xl border border-zinc-200/80 bg-white shadow-[0_4px_24px_rgba(0,0,0,0.04)] space-y-4">
    <div className="w-16 h-16 rounded-3xl bg-zinc-50 border border-zinc-200/80 flex items-center justify-center mx-auto text-zinc-900 shadow-sm"><Sparkles className="w-7 h-7 text-zinc-800" /></div>
    <div>
      <h3 className="text-base font-semibold text-zinc-900 tracking-tight mb-1.5">Không gian vẽ trống</h3>
      <p className="text-xs text-zinc-500 leading-relaxed">Nhập yêu cầu vào khung chat bên trái (ví dụ: <em>"Tạo landing page cho studio chụp ảnh tối giản"</em>). Agent sẽ lập kế hoạch và dựng giao diện trực tiếp lên màn hình này.</p>
    </div>
    {isGenerating && <div className="pt-3 flex items-center justify-center gap-2 text-xs text-zinc-700 font-medium"><span className="w-2 h-2 rounded-full bg-zinc-900 animate-ping" /><span>Agent đang dựng cấu trúc trang...</span></div>}
  </div>
);
