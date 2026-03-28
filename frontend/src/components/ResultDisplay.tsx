import type { CalculateResponse, MoleculeEntry } from '../types';

interface ResultDisplayProps {
  result: CalculateResponse;
  molecules: MoleculeEntry[];
}

export function ResultDisplay({ result }: ResultDisplayProps) {
  return (
    <div className="result-display">
      {/* Main result */}
      {result.reaction_enthalpy_kjmol !== null ? (
        <div
          className={`main-result ${result.is_exothermic ? 'exothermic' : 'endothermic'}`}
        >
          <h2>Reaction Enthalpy</h2>
          <p className="delta-h">
            &Delta;H = {result.reaction_enthalpy_kjmol.toFixed(2)} kJ/mol
          </p>
          <p className="delta-h-sub">
            ({result.reaction_enthalpy_hartree?.toFixed(6)} Eh)
          </p>
          <p className="reaction-type">
            {result.is_exothermic ? 'Exothermic (발열)' : 'Endothermic (흡열)'}
          </p>
        </div>
      ) : (
        <div className="main-result error">
          <h2>Calculation Error</h2>
          <p>
            Could not compute reaction enthalpy. Check individual molecule
            statuses below.
          </p>
        </div>
      )}

      {/* Breakdown table */}
      <h3>Calculation Breakdown</h3>
      <table className="breakdown-table">
        <thead>
          <tr>
            <th>SMILES</th>
            <th>Role</th>
            <th>Coeff</th>
            <th>H(T) / Eh</th>
            <th>E(total) / Eh</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {result.molecule_results.map((mr, i) => (
            <tr
              key={i}
              className={mr.status === 'error' ? 'row-error' : ''}
            >
              <td className="smiles-cell" title={mr.canonical_smiles}>
                {mr.smiles}
              </td>
              <td>
                <span
                  className={`role-badge ${mr.role === 'reactant' ? 'role-reactant' : 'role-product'}`}
                >
                  {mr.role}
                </span>
              </td>
              <td>{mr.coefficient}</td>
              <td>
                {mr.enthalpy_hartree !== null
                  ? mr.enthalpy_hartree.toFixed(6)
                  : 'N/A'}
              </td>
              <td>
                {mr.total_energy_hartree !== null
                  ? mr.total_energy_hartree.toFixed(6)
                  : 'N/A'}
              </td>
              <td>
                {mr.status === 'success' ? (
                  <span className="status-ok">OK</span>
                ) : (
                  <span className="status-error" title={mr.error}>
                    Error
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Calculation formula */}
      {result.reaction_enthalpy_kjmol !== null && (
        <div className="formula-section">
          <h3>Formula</h3>
          <p className="formula">
            &Delta;H<sub>rxn</sub> = &Sigma;(coeff &times; H(T))<sub>products</sub>
            &minus; &Sigma;(coeff &times; H(T))<sub>reactants</sub>
          </p>
          <p className="formula-detail">
            {(() => {
              const products = result.molecule_results.filter(
                (m) => m.role === 'product' && m.enthalpy_hartree !== null,
              );
              const reactants = result.molecule_results.filter(
                (m) => m.role === 'reactant' && m.enthalpy_hartree !== null,
              );

              const prodStr = products
                .map(
                  (m) =>
                    `${m.coefficient > 1 ? m.coefficient + ' \u00d7 ' : ''}(${m.enthalpy_hartree!.toFixed(6)})`,
                )
                .join(' + ');
              const reactStr = reactants
                .map(
                  (m) =>
                    `${m.coefficient > 1 ? m.coefficient + ' \u00d7 ' : ''}(${m.enthalpy_hartree!.toFixed(6)})`,
                )
                .join(' + ');

              return `= [${prodStr}] \u2212 [${reactStr}]`;
            })()}
          </p>
          <p className="formula-detail">
            = {result.reaction_enthalpy_hartree?.toFixed(6)} Eh
            = {result.reaction_enthalpy_kjmol.toFixed(2)} kJ/mol
          </p>
          <p className="method-note">
            Method: GFN2-xTB (--ohess) | 1 Eh = 2625.5 kJ/mol
          </p>
        </div>
      )}
    </div>
  );
}
