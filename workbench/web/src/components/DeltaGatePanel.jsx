import React from 'react';

export function DeltaGatePanel({ state }) {
  const gates = state.operational_cube.faces.gates || [];
  return (
    <section>
      <h2>Deltas e Gates</h2>
      <ul>
        {gates.map((gate) => (
          <li key={gate.delta_id}>
            {gate.gate_status} — {gate.delta_title} → {gate.solution_package}
          </li>
        ))}
      </ul>
    </section>
  );
}
