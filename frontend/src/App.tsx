import { ReactionManager } from './components/ReactionManager'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Reaction Heat Energy Calculator</h1>
        <p className="subtitle">
          Draw molecules with Ketcher, assign as reactants/products, and compute
          &Delta;H using GFN2-xTB.
        </p>
      </header>
      <main>
        <ReactionManager />
      </main>
    </div>
  )
}

export default App
