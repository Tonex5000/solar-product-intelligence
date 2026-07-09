import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Products } from './pages/Products'
import { SimulationBuilder } from './pages/SimulationBuilder'
import { SimulationResults } from './pages/SimulationResults'
import { SimulationHistory } from './pages/SimulationHistory'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="products" element={<Products />} />
        <Route path="simulate" element={<SimulationBuilder />} />
        <Route path="simulate/results" element={<SimulationResults />} />
        <Route path="history" element={<SimulationHistory />} />
      </Route>
    </Routes>
  )
}

export default App
