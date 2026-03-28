import type { MoleculeEntry, SSEEvent } from '../types';

/**
 * Calculate reaction enthalpy via SSE streaming endpoint.
 *
 * Sends the molecule list to the backend and reads SSE events
 * for progress updates and the final result.
 *
 * @param molecules - List of molecules with roles and coefficients.
 * @param onEvent - Callback fired for each SSE event (progress or result).
 */
export async function calculateReactionSSE(
  molecules: MoleculeEntry[],
  onEvent: (event: SSEEvent) => void,
): Promise<void> {
  const response = await fetch('/api/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      molecules: molecules.map((m) => ({
        smiles: m.smiles,
        role: m.role,
        coefficient: m.coefficient,
      })),
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Parse SSE lines: "data: {...}\n\n"
    const lines = buffer.split('\n\n');
    buffer = lines.pop() ?? '';

    for (const block of lines) {
      const line = block.trim();
      if (line.startsWith('data: ')) {
        const json = line.slice(6);
        try {
          const event: SSEEvent = JSON.parse(json);
          onEvent(event);
        } catch {
          console.warn('Failed to parse SSE event:', json);
        }
      }
    }
  }
}
