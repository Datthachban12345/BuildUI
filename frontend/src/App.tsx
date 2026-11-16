import React from 'react';
import { WorkspaceLayout } from './workspace/WorkspaceLayout';
import { sendPromptToAgent, loadFixture } from './services/agentApi';

export const App: React.FC = () => {
  return (
    <WorkspaceLayout
      onSendPromptToBackend={sendPromptToAgent}
      onLoadFixtureData={loadFixture}
    />
  );
};

export default App;
