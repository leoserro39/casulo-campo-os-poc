import React from 'react';

export function GravitationalDome({ state }) {
  const domains = state.gravitational_dome.domains || [];
  return (
    <section>
      <h2>Cupula Gravitacional</h2>
      <ul>
        {domains.map((domain) => (
          <li key={domain.id}>
            {domain.name} — peso {domain.gravity_weight} — {domain.priority}
          </li>
        ))}
      </ul>
    </section>
  );
}
