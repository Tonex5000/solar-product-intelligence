import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Settings2, 
  Sun, 
  Battery, 
  Zap, 
  Cable,
  AlertCircle,
  CheckCircle,
  ChevronRight,
  Loader2,
  Info,
  RotateCcw
} from 'lucide-react'
import { cn, getNodeGlowClass } from '@/lib/utils'
import { useSimulationStore } from '@/stores/simulationStore'
import type { RailwayNode, RailwayEdge, SimulationOutput } from '@/types'

// Mock products for selection
const mockProducts = {
  battery: [
    { id: 1, name: 'Tesla Powerwall 2', specs: { voltage: '48V', capacity: '200Ah', cycles: '4000' } },
    { id: 2, name: 'BYD PowerMax 10kWh', specs: { voltage: '48V', capacity: '210Ah', cycles: '6000' } },
    { id: 3, name: 'LG RESU 16H', specs: { voltage: '48V', capacity: '167Ah', cycles: '3000' } },
  ],
  inverter: [
    { id: 1, name: 'SolarEdge SE5000H', specs: { power: '5000W', efficiency: '99.2%', surge: '7500W' } },
    { id: 2, name: 'SMA Sunny Boy 5.0', specs: { power: '5000W', efficiency: '97%', surge: '5500W' } },
  ],
  panel: [
    { id: 1, name: 'LG NeON 2 400W', specs: { wattage: '400W', efficiency: '22.5%', Voc: '48.9V' } },
    { id: 2, name: 'LONGi Hi-MO 4 400W', specs: { wattage: '400W', efficiency: '21.8%', Voc: '49.3V' } },
  ],
  controller: [
    { id: 1, name: 'Victron SmartSolar 100/30', specs: { current: '30A', voltage: '100V', efficiency: '98%' } },
    { id: 2, name: 'Epever Tracer 40A', specs: { current: '40A', voltage: '150V', efficiency: '95%' } },
  ],
}

export function SimulationBuilder() {
  const { 
    railwayNodes, 
    railwayEdges, 
    simulationConfig,
    updateSimulationConfig,
    setCurrentSimulation,
    setSimulationRunning,
    isSimulationRunning
  } = useSimulationStore()

  const [showConfig, setShowConfig] = useState(true)
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null)
  const [configErrors, setConfigErrors] = useState<string[]>([])

  const handleRunSimulation = async () => {
    setConfigErrors([])
    
    // Validate
    const errors: string[] = []
    if (simulationConfig.load_watts <= 0) errors.push('Load watts must be greater than 0')
    if (simulationConfig.simulation_days <= 0) errors.push('Simulation days must be greater than 0')
    if (simulationConfig.daily_usage_hours > 24) errors.push('Daily usage hours cannot exceed 24')
    
    if (errors.length > 0) {
      setConfigErrors(errors)
      return
    }

    setSimulationRunning(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock result
    const mockResult: SimulationOutput = {
      status: 'completed',
      input: simulationConfig,
      summary: {
        battery_health_final: 85.2,
        total_energy_produced_kwh: 18250,
        total_energy_consumed_kwh: 9125,
        total_energy_lost_kwh: 1500,
        system_failures: 0,
        warnings: 3,
        cycle_count_total: 2500,
        avg_daily_production_kwh: 5.0,
        avg_daily_consumption_kwh: 2.5,
        system_balance_percent: 98,
        projected_battery_lifespan_years: 12,
        max_inverter_load_percent: 85,
      },
      timeline: [],
      events: [
        { day: 120, type: 'warning', severity: 'medium', message: 'Battery approached 80% DoD', component: 'battery' },
        { day: 365, type: 'info', severity: 'low', message: 'System at year 1 milestone', component: 'system' },
        { day: 730, type: 'info', severity: 'low', message: 'System at year 2 milestone', component: 'system' },
      ],
      recommendations: [
        { category: 'battery', priority: 'medium', title: 'Consider larger battery', description: 'For daily usage of 25kWh, consider upgrading to 300Ah capacity' },
      ],
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      duration_ms: 2150,
    }

    setCurrentSimulation(mockResult)
    setSimulationRunning(false)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold"
          >
            Simulation <span className="gradient-text">Builder</span>
          </motion.h1>
          <p className="text-muted-foreground mt-1">
            Design and run your solar system simulation
          </p>
        </div>
        <button
          onClick={() => setShowConfig(!showConfig)}
          className="flex items-center gap-2 px-4 py-2 bg-solar-bg-card rounded-xl hover:bg-solar-bg-card/80 transition-colors"
        >
          <Settings2 className="w-5 h-5" />
          {showConfig ? 'Hide' : 'Show'} Config
        </button>
      </div>

      {/* Railway System Visualization */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card rounded-2xl p-8 relative overflow-hidden"
      >
        {/* Background Grid */}
        <div className="absolute inset-0 opacity-5">
          <svg width="100%" height="100%">
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5"/>
            </pattern>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        <div className="relative">
          <h2 className="text-lg font-semibold mb-8 flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary" />
            System Configuration
          </h2>

          {/* Railway Flow */}
          <div className="flex items-center justify-between py-8 overflow-x-auto">
            {railwayNodes.map((node, index) => (
              <div key={node.id} className="flex items-center">
                {/* Node */}
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  onClick={() => setSelectedComponent(selectedComponent === node.id ? null : node.id)}
                  className={cn(
                    'relative cursor-pointer group',
                    selectedComponent === node.id && 'ring-2 ring-primary rounded-2xl'
                  )}
                >
                  {/* Glow effect */}
                  <div className={cn(
                    'absolute inset-0 rounded-2xl blur-xl opacity-50',
                    node.status === 'optimal' && 'bg-success',
                    node.status === 'normal' && 'bg-primary',
                    node.status === 'warning' && 'bg-warning',
                    node.status === 'failure' && 'bg-danger'
                  )} />

                  {/* Node Card */}
                  <div className={cn(
                    'relative w-32 h-40 rounded-2xl glass-card p-4 flex flex-col items-center justify-center',
                    getNodeGlowClass(node.status)
                  )}>
                    <div className={cn(
                      'w-14 h-14 rounded-xl flex items-center justify-center mb-3',
                      node.type === 'panel' && 'bg-solar/20',
                      node.type === 'battery' && 'bg-success/20',
                      node.type === 'inverter' && 'bg-primary/20',
                      node.type === 'controller' && 'bg-info/20',
                      node.type === 'load' && 'bg-warning/20'
                    )}>
                      {node.type === 'panel' && <Sun className={cn('w-7 h-7', node.status === 'optimal' ? 'text-success' : 'text-solar')} />}
                      {node.type === 'battery' && <Battery className={cn('w-7 h-7', node.status === 'optimal' ? 'text-success' : 'text-success')} />}
                      {node.type === 'inverter' && <Zap className={cn('w-7 h-7', node.status === 'optimal' ? 'text-success' : 'text-primary')} />}
                      {node.type === 'controller' && <Cable className={cn('w-7 h-7', node.status === 'optimal' ? 'text-success' : 'text-info')} />}
                      {node.type === 'load' && <Zap className="w-7 h-7 text-warning" />}
                    </div>
                    <p className="text-sm font-medium text-center">{node.label}</p>
                    <div className="flex items-center gap-1 mt-2">
                      <div className={cn(
                        'w-2 h-2 rounded-full',
                        node.status === 'optimal' && 'bg-success',
                        node.status === 'normal' && 'bg-primary',
                        node.status === 'warning' && 'bg-warning',
                        node.status === 'failure' && 'bg-danger animate-pulse'
                      )} />
                      <span className="text-xs text-muted-foreground capitalize">{node.status}</span>
                    </div>
                  </div>

                  {/* Energy Flow Animation */}
                  {index < railwayEdges.length && (
                    <div className="absolute left-full top-1/2 w-8 h-1 -translate-y-1/2">
                      <div className="w-full h-full bg-gradient-to-r from-primary/50 to-solar/50 rounded-full relative overflow-hidden">
                        <motion.div
                          className="absolute w-3 h-3 rounded-full bg-white/80 top-1/2 -translate-y-1/2"
                          animate={{ x: [0, 32] }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        />
                      </div>
                    </div>
                  )}
                </motion.div>

                {/* Connection */}
                {index < railwayNodes.length - 1 && (
                  <div className="w-12 h-1 mx-1 relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/30 via-primary to-primary/30 rounded-full" />
                    <motion.div
                      className="absolute w-2 h-2 rounded-full bg-white/80 top-1/2 -translate-y-1/2"
                      animate={{ x: [0, 48] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: 'linear', delay: index * 0.2 }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Component Selection */}
          <div className="mt-8 pt-8 border-t border-solar-border">
            <h3 className="text-sm font-medium text-muted-foreground mb-4">Select Components</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(mockProducts).map(([type, products]) => (
                <div key={type} className="space-y-2">
                  <label className="text-sm font-medium capitalize flex items-center gap-2">
                    {type === 'battery' && <Battery className="w-4 h-4 text-success" />}
                    {type === 'inverter' && <Zap className="w-4 h-4 text-primary" />}
                    {type === 'panel' && <Sun className="w-4 h-4 text-solar" />}
                    {type === 'controller' && <Cable className="w-4 h-4 text-info" />}
                    {type.replace('_', ' ')}
                  </label>
                  <select
                    className="w-full px-3 py-2 bg-solar-bg-card border border-solar-border rounded-lg text-sm focus:outline-none focus:border-primary"
                    onChange={(e) => {
                      const key = type.replace(' ', '') as keyof typeof simulationConfig
                      if (e.target.value) {
                        updateSimulationConfig({ [key]: parseInt(e.target.value) })
                      }
                    }}
                  >
                    <option value="">Select...</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Configuration Panel */}
      <AnimatePresence>
        {showConfig && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="glass-card rounded-2xl p-6">
              <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
                <Settings2 className="w-5 h-5 text-primary" />
                Simulation Parameters
              </h2>

              {configErrors.length > 0 && (
                <div className="mb-6 p-4 bg-danger/10 border border-danger/20 rounded-xl">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-danger">Configuration Error</p>
                      <ul className="mt-1 space-y-1">
                        {configErrors.map((error, i) => (
                          <li key={i} className="text-sm text-muted-foreground">{error}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Load */}
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Zap className="w-4 h-4 text-warning" />
                      Load (Watts)
                    </span>
                    <span className="text-primary font-mono">{simulationConfig.load_watts}W</span>
                  </label>
                  <input
                    type="range"
                    min="500"
                    max="10000"
                    step="100"
                    value={simulationConfig.load_watts}
                    onChange={(e) => updateSimulationConfig({ load_watts: parseInt(e.target.value) })}
                    className="w-full accent-primary"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>500W</span>
                    <span>10kW</span>
                  </div>
                </div>

                {/* Daily Usage */}
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Info className="w-4 h-4 text-info" />
                      Daily Usage
                    </span>
                    <span className="text-primary font-mono">{simulationConfig.daily_usage_hours}h</span>
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="24"
                    step="0.5"
                    value={simulationConfig.daily_usage_hours}
                    onChange={(e) => updateSimulationConfig({ daily_usage_hours: parseFloat(e.target.value) })}
                    className="w-full accent-primary"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>1h</span>
                    <span>24h</span>
                  </div>
                </div>

                {/* Simulation Days */}
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Info className="w-4 h-4 text-solar" />
                      Duration
                    </span>
                    <span className="text-primary font-mono">{simulationConfig.simulation_days} days</span>
                  </label>
                  <input
                    type="range"
                    min="30"
                    max="3650"
                    step="30"
                    value={simulationConfig.simulation_days}
                    onChange={(e) => updateSimulationConfig({ simulation_days: parseInt(e.target.value) })}
                    className="w-full accent-solar"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>30 days</span>
                    <span>10 years</span>
                  </div>
                </div>

                {/* Sun Hours */}
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Sun className="w-4 h-4 text-solar" />
                      Avg Sun Hours
                    </span>
                    <span className="text-primary font-mono">{simulationConfig.avg_sun_hours}h</span>
                  </label>
                  <input
                    type="range"
                    min="2"
                    max="10"
                    step="0.5"
                    value={simulationConfig.avg_sun_hours ?? 5}
                    onChange={(e) => updateSimulationConfig({ avg_sun_hours: parseFloat(e.target.value) })}
                    className="w-full accent-solar"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>2h</span>
                    <span>10h</span>
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div className="mt-6 p-4 bg-solar-bg-card rounded-xl">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Daily Energy Requirement</span>
                  <span className="font-mono font-medium">
                    {((simulationConfig.load_watts * simulationConfig.daily_usage_hours) / 1000).toFixed(1)} kWh
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Action Buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => {
            updateSimulationConfig({
              load_watts: 2500,
              daily_usage_hours: 10,
              simulation_days: 365,
              avg_sun_hours: 5
            })
          }}
          className="flex items-center gap-2 px-4 py-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          Reset to Defaults
        </button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleRunSimulation}
          disabled={isSimulationRunning}
          className={cn(
            'flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-lg transition-all',
            isSimulationRunning
              ? 'bg-primary/50 cursor-not-allowed'
              : 'bg-gradient-to-r from-primary to-blue-600 hover:shadow-lg hover:shadow-primary/25'
          )}
        >
          {isSimulationRunning ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Running Simulation...
            </>
          ) : (
            <>
              <Play className="w-6 h-6" />
              Run Simulation
              <ChevronRight className="w-5 h-5" />
            </>
          )}
        </motion.button>
      </div>
    </div>
  )
}
