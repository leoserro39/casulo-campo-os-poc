import React from 'react';

export function DomainGraph({ state }) {
  const graph = state.graph_projection;
  return (
    <section>
      <h2>Grafo de Dominios</h2>
      <p>Nos: {graph.nodes.length}</p>
      <p>Arestas: {graph.edges.length}</p>
    </section>
  );
}
