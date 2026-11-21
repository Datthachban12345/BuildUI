import { useState, useCallback } from 'react';

export interface InputBarStoreProps {
  onSendMessage: (prompt: string) => void;
  isGenerating: boolean;
}

export function useInputBarStore({ onSendMessage, isGenerating }: InputBarStoreProps) {
  const [input, setInput] = useState('');

  const handleSubmit = useCallback(
    (e?: React.FormEvent) => {
      if (e) e.preventDefault();
      if (!input.trim() || isGenerating) return;
      onSendMessage(input.trim());
      setInput('');
    },
    [input, isGenerating, onSendMessage]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return {
    input,
    setInput,
    handleSubmit,
    handleKeyDown,
    canSubmit: Boolean(input.trim()) && !isGenerating,
  };
}
