import React from 'react';
import { GravitationalDome } from './components/GravitationalDome.jsx';
import { OperationalCube } from './components/OperationalCube.jsx';
import { ChatAxial } from './components/ChatAxial.jsx';
import { DomainGraph } from './components/DomainGraph.jsx';

export default function App() {
  return (
    <main className="casulo-workbench">
      <h1>CASULO Workbench</h1>
      <p>Estado Operacional como ancora.</p>
      <GravitationalDome />
      <OperationalCube />
      <DomainGraph />
      <ChatAxial />
    </main>
  );
}
