import React from 'react';

export function ChatAxial({ state }) {
  return (
    <section>
      <h2>Chat Axial</h2>
      <p>Intencoes permitidas: {state.chat_axial.allowed_intents.join(', ')}</p>
      <p>Fonte da verdade: {state.chat_axial.source_of_truth.join(', ')}</p>
    </section>
  );
}
