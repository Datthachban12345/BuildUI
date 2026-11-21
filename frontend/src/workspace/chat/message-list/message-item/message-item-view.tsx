import React from 'react';
import { Bot, User, Loader2 } from 'lucide-react';
import { ChatMessage } from '../../chat-store';
import { StepBreakdownView } from './step-breakdown/step-breakdown-view';

interface MessageItemViewProps {
  message: ChatMessage;
}

export const MessageItemView: React.FC<MessageItemViewProps> = ({ message }) => (
  <div className={`flex gap-3 text-xs ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
    {message.sender === 'agent' && (
      <div className="w-7 h-7 rounded-full bg-zinc-900 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-sm">
        <Bot className="w-3.5 h-3.5 text-white" />
      </div>
    )}
    <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${message.sender === 'user' ? 'bg-zinc-900 text-white font-normal shadow-[0_2px_8px_rgba(0,0,0,0.08)]' : 'bg-white border border-zinc-200/90 text-zinc-800 shadow-[0_2px_8px_rgba(0,0,0,0.03)]'}`}>
      <div className="whitespace-pre-wrap leading-relaxed text-xs">{message.content}</div>
      {message.steps && message.steps.length > 0 && <StepBreakdownView steps={message.steps} />}
      {message.isStreaming && (
        <div className="mt-2.5 flex items-center gap-1.5 text-[11px] text-amber-600 font-medium">
          <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-600" />
          <span>Đang render các khối A2UI...</span>
        </div>
      )}
    </div>
    {message.sender === 'user' && (
      <div className="w-7 h-7 rounded-full bg-zinc-200 flex items-center justify-center text-zinc-700 shrink-0 mt-0.5">
        <User className="w-3.5 h-3.5" />
      </div>
    )}
  </div>
);
