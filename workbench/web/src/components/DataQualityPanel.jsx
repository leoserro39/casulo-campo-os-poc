import React from 'react';

export function DataQualityPanel({ state }) {
  const summary = state.summary;
  return (
    <section>
      <h2>Estado Operacional</h2>
      <p>DQ: {summary.data_quality} ({summary.data_quality_label})</p>
      <p>H_pre: {summary.h_pre} | H_post: {summary.h_post} | Delta_L: {summary.delta_l}</p>
      <p>Decisao: {summary.decision}</p>
    </section>
  );
}
