import React from 'react';

export function LedgerPanel({ state }) {
  return (
    <section>
      <h2>Ledger / Snapshot</h2>
      <p>Contrato: {state.contract_version}</p>
      <p>Gerado em: {state.generated_at}</p>
    </section>
  );
}
