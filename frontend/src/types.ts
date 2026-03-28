/** A molecule entry in the reaction scheme. */
export interface MoleculeEntry {
  id: string;
  smiles: string;
  role: 'reactant' | 'product';
  coefficient: number;
}

/** Single molecule result from the backend. */
export interface MoleculeResult {
  smiles: string;
  canonical_smiles: string;
  role: 'reactant' | 'product';
  coefficient: number;
  enthalpy_hartree: number | null;
  total_energy_hartree: number | null;
  status: 'success' | 'error';
  error?: string;
}

/** Full calculation response from the backend. */
export interface CalculateResponse {
  type: 'result';
  status: 'success' | 'partial_failure' | 'error';
  reaction_enthalpy_hartree: number | null;
  reaction_enthalpy_kjmol: number | null;
  is_exothermic: boolean | null;
  molecule_results: MoleculeResult[];
}

/** Progress event from SSE stream. */
export interface ProgressEvent {
  type: 'progress';
  completed: number;
  total: number;
  current_smiles: string;
}

/** Union of all SSE event types. */
export type SSEEvent = ProgressEvent | CalculateResponse;
