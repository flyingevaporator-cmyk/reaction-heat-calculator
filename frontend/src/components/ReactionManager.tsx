import { useState, useCallback } from 'react';
import type {
  MoleculeEntry,
  CalculateResponse,
  ProgressEvent,
} from '../types';
import { MoleculeEditor } from './MoleculeEditor';
import { ResultDisplay } from './ResultDisplay';
import { calculateReactionSSE } from '../api/calculate';

export function ReactionManager() {
  const [molecules, setMolecules] = useState<MoleculeEntry[]>([]);
  const [result, setResult] = useState<CalculateResponse | null>(null);
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editorMode, setEditorMode] = useState<'smiles' | 'ketcher'>('smiles');

  // --- Molecule management ---

  const handleAddMolecule = useCallback(
    (smiles: string, role: 'reactant' | 'product') => {
      const entry: MoleculeEntry = {
        id: crypto.randomUUID(),
        smiles,
        role,
        coefficient: 1,
      };
      setMolecules((prev) => [...prev, entry]);
    },
    [],
  );

  const updateCoefficient = useCallback((id: string, coeff: number) => {
    setMolecules((prev) =>
      prev.map((m) =>
        m.id === id ? { ...m, coefficient: Math.max(1, coeff) } : m,
      ),
    );
  }, []);

  const removeMolecule = useCallback((id: string) => {
    setMolecules((prev) => prev.filter((m) => m.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setMolecules([]);
    setResult(null);
    setProgress(null);
    setError(null);
  }, []);

  // --- Calculation ---

  const handleCalculate = useCallback(async () => {
    if (molecules.length === 0) return;

    setIsCalculating(true);
    setResult(null);
    setProgress(null);
    setError(null);

    try {
      await calculateReactionSSE(molecules, (event) => {
        if (event.type === 'progress') {
          setProgress(event);
        } else if (event.type === 'result') {
          setResult(event);
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setIsCalculating(false);
      setProgress(null);
    }
  }, [molecules]);

  // --- Derived data ---

  const reactants = molecules.filter((m) => m.role === 'reactant');
  const products = molecules.filter((m) => m.role === 'product');
  const canCalculate =
    !isCalculating && reactants.length > 0 && products.length > 0;

  return (
    <div className="reaction-manager">
      {/* Left panel: Editor */}
      <div className="editor-panel">
        <div className="editor-tabs">
          <button
            className={`tab-btn ${editorMode === 'smiles' ? 'tab-active' : ''}`}
            onClick={() => setEditorMode('smiles')}
          >
            SMILES Input
          </button>
          <button
            className={`tab-btn ${editorMode === 'ketcher' ? 'tab-active' : ''}`}
            onClick={() => setEditorMode('ketcher')}
          >
            Ketcher Editor
          </button>
        </div>
        {editorMode === 'smiles' ? (
          <SmilesInput onAddMolecule={handleAddMolecule} />
        ) : (
          <MoleculeEditor onAddMolecule={handleAddMolecule} />
        )}
      </div>

      {/* Right panel: Reaction scheme + results */}
      <div className="reaction-panel">
        {/* Reaction equation display */}
        <div className="reaction-equation">
          <div className="equation-side">
            <h3>Reactants</h3>
            {reactants.length === 0 ? (
              <p className="placeholder">
                Draw a molecule and click "+ Reactant"
              </p>
            ) : (
              <ul className="molecule-list">
                {reactants.map((m) => (
                  <MoleculeRow
                    key={m.id}
                    molecule={m}
                    onUpdateCoeff={updateCoefficient}
                    onRemove={removeMolecule}
                  />
                ))}
              </ul>
            )}
          </div>

          <div className="arrow-container">
            <span className="reaction-arrow">&rarr;</span>
          </div>

          <div className="equation-side">
            <h3>Products</h3>
            {products.length === 0 ? (
              <p className="placeholder">
                Draw a molecule and click "+ Product"
              </p>
            ) : (
              <ul className="molecule-list">
                {products.map((m) => (
                  <MoleculeRow
                    key={m.id}
                    molecule={m}
                    onUpdateCoeff={updateCoefficient}
                    onRemove={removeMolecule}
                  />
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="calculation-actions">
          <button
            className="btn btn-calculate"
            onClick={handleCalculate}
            disabled={!canCalculate}
          >
            {isCalculating ? 'Calculating...' : 'Calculate \u0394H'}
          </button>
          <button className="btn btn-clear" onClick={clearAll}>
            Clear All
          </button>
        </div>

        {/* Progress */}
        {progress && (
          <div className="progress-bar">
            <div className="progress-text">
              Computing molecule {progress.completed + 1} of {progress.total}
              : <code>{progress.current_smiles}</code>
            </div>
            <div className="progress-track">
              <div
                className="progress-fill"
                style={{
                  width: `${(progress.completed / progress.total) * 100}%`,
                }}
              />
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Results */}
        {result && <ResultDisplay result={result} molecules={molecules} />}
      </div>
    </div>
  );
}

// --- Sub-component: Molecule Row ---

interface MoleculeRowProps {
  molecule: MoleculeEntry;
  onUpdateCoeff: (id: string, coeff: number) => void;
  onRemove: (id: string) => void;
}

// --- Temporary SMILES text input (until Ketcher is working) ---

function SmilesInput({ onAddMolecule }: { onAddMolecule: (smiles: string, role: 'reactant' | 'product') => void }) {
  const [smiles, setSmiles] = useState('');
  return (
    <div className="molecule-editor">
      <h2>Molecule Editor</h2>
      <div style={{ padding: 16, background: 'white', borderRadius: 8, border: '1px solid #e2e8f0' }}>
        <label style={{ display: 'block', marginBottom: 8, fontSize: '0.85rem', color: '#64748b' }}>
          Enter SMILES:
        </label>
        <input
          type="text"
          value={smiles}
          onChange={(e) => setSmiles(e.target.value)}
          placeholder="e.g. O, C, [H][H], O=O, CCO"
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: 6, fontSize: '1rem', fontFamily: 'monospace' }}
        />
        <p style={{ marginTop: 8, fontSize: '0.75rem', color: '#94a3b8' }}>
          Examples: O (water), C (methane), [H][H] (H2), O=O (O2), CCO (ethanol)
        </p>
      </div>
      <div className="editor-actions">
        <button className="btn btn-reactant" onClick={() => { if (smiles.trim()) { onAddMolecule(smiles.trim(), 'reactant'); setSmiles(''); } }}>
          + Reactant
        </button>
        <button className="btn btn-product" onClick={() => { if (smiles.trim()) { onAddMolecule(smiles.trim(), 'product'); setSmiles(''); } }}>
          + Product
        </button>
      </div>
    </div>
  );
}

function MoleculeRow({ molecule, onUpdateCoeff, onRemove }: MoleculeRowProps) {
  return (
    <li className="molecule-row">
      <input
        type="number"
        className="coeff-input"
        min={1}
        max={99}
        value={molecule.coefficient}
        onChange={(e) =>
          onUpdateCoeff(molecule.id, parseInt(e.target.value, 10) || 1)
        }
      />
      <span className="molecule-smiles" title={molecule.smiles}>
        {molecule.smiles}
      </span>
      <button
        className="btn-remove"
        onClick={() => onRemove(molecule.id)}
        title="Remove"
      >
        &times;
      </button>
    </li>
  );
}
