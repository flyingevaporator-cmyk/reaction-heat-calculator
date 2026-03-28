import { useRef, useCallback, useState, lazy, Suspense } from 'react';
import type { Ketcher } from 'ketcher-core';
import { ErrorBoundary } from './ErrorBoundary';

// Lazy load Ketcher to prevent it from blocking initial render
const KetcherEditor = lazy(async () => {
  const [{ Editor }, { StandaloneStructServiceProvider }] = await Promise.all([
    import('ketcher-react'),
    import('ketcher-standalone'),
  ]);
  await import('ketcher-react/dist/index.css');

  const structServiceProvider = new StandaloneStructServiceProvider();

  return {
    default: function KetcherWrapper(props: {
      onInit: (ketcher: Ketcher) => void;
    }) {
      return (
        <Editor
          staticResourcesUrl=""
          structServiceProvider={structServiceProvider}
          onInit={props.onInit}
          errorHandler={console.error}
        />
      );
    },
  };
});

interface MoleculeEditorProps {
  onAddMolecule: (smiles: string, role: 'reactant' | 'product') => void;
}

export function MoleculeEditor({ onAddMolecule }: MoleculeEditorProps) {
  const ketcherRef = useRef<Ketcher | null>(null);
  const [ketcherReady, setKetcherReady] = useState(false);

  const handleInit = useCallback((ketcher: Ketcher) => {
    ketcherRef.current = ketcher;
    setKetcherReady(true);
    (window as Record<string, unknown>).ketcher = ketcher;
  }, []);

  const handleAdd = useCallback(
    async (role: 'reactant' | 'product') => {
      if (!ketcherRef.current) return;
      try {
        const smiles = await ketcherRef.current.getSmiles();
        if (smiles && smiles.trim()) {
          onAddMolecule(smiles.trim(), role);
        }
      } catch (err) {
        console.error('Failed to get SMILES from Ketcher:', err);
      }
    },
    [onAddMolecule],
  );

  return (
    <div className="molecule-editor">
      <h2>Molecule Editor (Ketcher)</h2>
      <div className="ketcher-container">
        <ErrorBoundary>
          <Suspense
            fallback={
              <div className="ketcher-loading">Loading Ketcher editor...</div>
            }
          >
            <KetcherEditor onInit={handleInit} />
          </Suspense>
        </ErrorBoundary>
      </div>
      <div className="editor-actions">
        <button
          className="btn btn-reactant"
          onClick={() => handleAdd('reactant')}
          disabled={!ketcherReady}
          title="Add drawn molecule as a reactant"
        >
          + Reactant
        </button>
        <button
          className="btn btn-product"
          onClick={() => handleAdd('product')}
          disabled={!ketcherReady}
          title="Add drawn molecule as a product"
        >
          + Product
        </button>
      </div>
    </div>
  );
}
