import { useState } from 'react';
import type { ConsoleEventPayload } from '../../services/agent-api';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: string;
  steps?: string[];
  console?: ConsoleEventPayload[];
  isStreaming?: boolean;
}

export function useChatStore() {
  const [isFixtureMenuOpen, setIsFixtureMenuOpen] = useState(false);

  return {
    isFixtureMenuOpen,
    setIsFixtureMenuOpen,
  };
}
