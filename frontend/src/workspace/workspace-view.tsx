import React from 'react';
import { SurfaceState, A2UIMessage } from '../a2ui/protocol/a2ui-types';
import type { StreamChunk } from '../services/agent-api';
import { useWorkspaceStore } from './workspace-store';
import { ChatView } from './chat/chat-view';
import { PreviewView } from './preview/preview-view';
import { InspectorDrawer } from './inspector/inspector-drawer';

export interface WorkspaceViewProps {
  onSendPromptToBackend: (
    prompt: string,
    currentSurface: SurfaceState | null,
    onStreamChunk: (chunk: StreamChunk) => void
  ) => Promise<void>;
  onLoadFixtureData: (fixtureName: string) => Promise<A2UIMessage | null>;
}

export const WorkspaceView: React.FC<WorkspaceViewProps> = ({
  onSendPromptToBackend,
  onLoadFixtureData,
}) => {
  const {
    surface,
    selectedId,
    setSelectedId,
    messages,
    isGenerating,
    handleSendMessage,
    handleUpdateComponent,
    handleUpdateDataModel,
    handleLoadFixture,
  } = useWorkspaceStore({
    onSendPromptToBackend,
    onLoadFixtureData,
  });

  return (
    <div className="flex w-screen h-screen overflow-hidden bg-[#f5f5f7] text-zinc-900 font-sans">
      {/* 1. Left Chat Copilot Panel */}
      <ChatView
        messages={messages}
        onSendMessage={handleSendMessage}
        isGenerating={isGenerating}
        onLoadFixture={handleLoadFixture}
      />

      {/* 2. Center Live Canvas Artboard */}
      <PreviewView
        surface={surface}
        selectedId={selectedId}
        onSelectComponent={setSelectedId}
        onUpdateDataModel={handleUpdateDataModel}
        isGenerating={isGenerating}
      />

      {/* 3. Right Property Inspector Drawer */}
      {selectedId && (
        <InspectorDrawer
          surface={surface}
          selectedId={selectedId}
          onClose={() => setSelectedId(null)}
          onUpdateComponent={handleUpdateComponent}
        />
      )}
    </div>
  );
};

export default WorkspaceView;
