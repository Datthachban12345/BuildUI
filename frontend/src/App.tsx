import React from 'react';
import { WorkspaceView } from './workspace/workspace-view';
import { sendPromptToAgent, loadFixture } from './services/agent-api';

// Feature-based naming keeps the UI entry point discoverable in the IDE.

export const App: React.FC = () => {
  return (
    <WorkspaceView
      onSendPromptToBackend={sendPromptToAgent}
      onLoadFixtureData={loadFixture}
    />
  );
};

export default App;
