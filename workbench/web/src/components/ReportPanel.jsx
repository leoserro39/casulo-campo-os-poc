import React from 'react';

export function ReportPanel({ state }) {
  return (
    <section>
      <h2>Relatorio</h2>
      <p>{state.case.title} — {state.case.vertical}</p>
      <p>Dominios: {state.summary.domains} | Gates: {state.summary.gates}</p>
    </section>
  );
}
