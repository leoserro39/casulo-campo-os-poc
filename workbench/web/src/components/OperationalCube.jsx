import React from 'react';

export function OperationalCube({ state }) {
  const faces = state.operational_cube.faces;
  return (
    <section>
      <h2>Cubo Operacional</h2>
      <p><strong>Objetivo:</strong> {faces.objective}</p>
      <p><strong>Evidencia:</strong> DQ {faces.evidence.data_quality} / {faces.evidence.label}</p>
      <p><strong>Risco:</strong> {faces.risks.decision}</p>
      <p><strong>Gates:</strong> {faces.gates.length}</p>
    </section>
  );
}
