import React from 'react';
import cockpitState from './data/cockpit_state.demo.json';
import { GravitationalDome } from './components/GravitationalDome.jsx';
import { OperationalCube } from './components/OperationalCube.jsx';
import { ChatAxial } from './components/ChatAxial.jsx';
import { DomainGraph } from './components/DomainGraph.jsx';
import { DataQualityPanel } from './components/DataQualityPanel.jsx';
import { DeltaGatePanel } from './components/DeltaGatePanel.jsx';
import { LedgerPanel } from './components/LedgerPanel.jsx';
import { ReportPanel } from './components/ReportPanel.jsx';

export default function App() {
  return (
    <main className="casulo-workbench">
      <h1>CASULO Workbench</h1>
      <p>Estado Operacional como ancora.</p>
      <DataQualityPanel state={cockpitState} />
      <GravitationalDome state={cockpitState} />
      <OperationalCube state={cockpitState} />
      <DomainGraph state={cockpitState} />
      <DeltaGatePanel state={cockpitState} />
      <ChatAxial state={cockpitState} />
      <LedgerPanel state={cockpitState} />
      <ReportPanel state={cockpitState} />
    </main>
  );
}
