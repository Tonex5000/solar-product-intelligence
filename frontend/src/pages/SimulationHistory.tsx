import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  History, 
  Search, 
  Calendar,
  Battery,
  AlertTriangle,
  Zap,
  ChevronRight,
  Trash2,
  Eye,
  BarChart3
} from 'lucide-react'
import { cn, formatDate, formatDuration } from '@/lib/utils'
import type { SimulationOutput } from '@/types'

// Mock history data
const mockHistory: (SimulationOutput & { id: number })[] = [
  {
    id: 1,
    status: 'completed',
    input: {
      battery_id: 1, inverter_id: 2, panel_id: 3, charge_controller_id: 4,
      load_watts: 2500, daily_usage_hours: 10, simulation_days: 365
    },
    summary: {
      battery_health_final: 85.2,
      total_energy_produced_kwh: 9125,
      total_energy_consumed_kwh: 9125,
      total_energy_lost_kwh: 750,
      system_failures: 0,
      warnings: 3,
      cycle_count_total: 1825,
      avg_daily_production_kwh: 5.0,
      avg_daily_consumption_kwh: 2.5,
      system_balance_percent: 98,
      projected_battery_lifespan_years: 12,
      max_inverter_load_percent: 85,
    },
    timeline: [],
    events: [
      { day: 120, type: 'warning', severity: 'medium', message: 'Battery approached 80% DoD', component: 'battery' },
    ],
    recommendations: [],
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 2,
    status: 'completed',
    input: {
      battery_id: 1, inverter_id: 2, panel_id: 3, charge_controller_id: 4,
      load_watts: 4000, daily_usage_hours: 8, simulation_days: 730
    },
    summary: {
      battery_health_final: 62.5,
      total_energy_produced_kwh: 18250,
      total_energy_consumed_kwh: 23360,
      total_energy_lost_kwh: 2000,
      system_failures: 1,
      warnings: 12,
      cycle_count_total: 3650,
      avg_daily_production_kwh: 5.0,
      avg_daily_consumption_kwh: 3.2,
      system_balance_percent: 78,
      projected_battery_lifespan_years: 6,
      max_inverter_load_percent: 105,
    },
    timeline: [],
    events: [
      { day: 180, type: 'failure', severity: 'critical', message: 'Inverter overload shutdown', component: 'inverter' },
      { day: 300, type: 'damage', severity: 'high', message: 'Battery deep discharge damage', component: 'battery' },
    ],
    recommendations: [],
    created_at: new Date(Date.now() - 604800000).toISOString(),
  },
  {
    id: 3,
    status: 'completed',
    input: {
      battery_id: 2, inverter_id: 1, panel_id: 2, charge_controller_id: 1,
      load_watts: 1500, daily_usage_hours: 12, simulation_days: 1825
    },
    summary: {
      battery_health_final: 78.3,
      total_energy_produced_kwh: 45625,
      total_energy_consumed_kwh: 32850,
      total_energy_lost_kwh: 5000,
      system_failures: 0,
      warnings: 5,
      cycle_count_total: 4500,
      avg_daily_production_kwh: 5.0,
      avg_daily_consumption_kwh: 1.8,
      system_balance_percent: 92,
      projected_battery_lifespan_years: 15,
      max_inverter_load_percent: 65,
    },
    timeline: [],
    events: [],
    recommendations: [],
    created_at: new Date(Date.now() - 2592000000).toISOString(),
  },
]

export function SimulationHistory() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | 'good' | 'warning' | 'critical'>('all')

  const filteredHistory = mockHistory.filter((sim) => {
    const matchesSearch = sim.created_at?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sim.input.load_watts.toString().includes(searchQuery)
    
    const health = sim.summary.battery_health_final
    const matchesFilter = 
      filterStatus === 'all' ||
      (filterStatus === 'good' && health > 80) ||
      (filterStatus === 'warning' && health > 50 && health <= 80) ||
      (filterStatus === 'critical' && health <= 50)
    
    return matchesSearch && matchesFilter
  })

  const getStatusBadge = (health: number) => {
    if (health > 80) return { label: 'Good', class: 'bg-success/20 text-success' }
    if (health > 50) return { label: 'Warning', class: 'bg-warning/20 text-warning' }
    return { label: 'Critical', class: 'bg-danger/20 text-danger' }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold"
        >
          Simulation <span className="gradient-text">History</span>
        </motion.h1>
        <p className="text-muted-foreground mt-1">
          View and analyze past simulation results
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by date or configuration..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-solar-card border border-solar rounded-xl focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2">
          {[
            { value: 'all', label: 'All' },
            { value: 'good', label: 'Good', color: 'success' },
            { value: 'warning', label: 'Warning', color: 'warning' },
            { value: 'critical', label: 'Critical', color: 'danger' },
          ].map((filter) => (
            <button
              key={filter.value}
              onClick={() => setFilterStatus(filter.value as typeof filterStatus)}
              className={cn(
                'px-4 py-2 rounded-xl text-sm font-medium transition-all',
                filterStatus === filter.value
                  ? filter.color 
                    ? `bg-${filter.color}/20 text-${filter.color} border border-${filter.color}/30`
                    : 'bg-primary text-white'
                  : 'bg-solar-card text-muted-foreground hover:text-foreground'
              )}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card rounded-xl p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{mockHistory.length}</p>
              <p className="text-xs text-muted-foreground">Total Simulations</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card rounded-xl p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-success/20 flex items-center justify-center">
              <Battery className="w-5 h-5 text-success" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {formatDuration(mockHistory.reduce((acc, s) => acc + s.input.simulation_days, 0))}
              </p>
              <p className="text-xs text-muted-foreground">Total Simulated</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card rounded-xl p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-warning/20 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-warning" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {mockHistory.reduce((acc, s) => acc + s.summary.warnings, 0)}
              </p>
              <p className="text-xs text-muted-foreground">Total Warnings</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card rounded-xl p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-danger/20 flex items-center justify-center">
              <Zap className="w-5 h-5 text-danger" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {mockHistory.reduce((acc, s) => acc + s.summary.system_failures, 0)}
              </p>
              <p className="text-xs text-muted-foreground">Total Failures</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* History List */}
      <div className="space-y-4">
        {filteredHistory.map((simulation, index) => {
          const status = getStatusBadge(simulation.summary.battery_health_final)
          return (
            <motion.div
              key={simulation.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass-card rounded-2xl p-6 hover:border-primary/30 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Header */}
                  <div className="flex items-center gap-4 mb-4">
                    <div>
                      <h3 className="font-semibold text-lg">
                        Simulation #{simulation.id}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                        <Calendar className="w-4 h-4" />
                        {simulation.created_at && formatDate(simulation.created_at)}
                      </div>
                    </div>
                    <span className={cn('px-3 py-1 rounded-full text-xs font-medium', status.class)}>
                      {status.label}
                    </span>
                  </div>

                  {/* Configuration */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="p-3 bg-solar-card rounded-xl">
                      <p className="text-xs text-muted-foreground mb-1">Load</p>
                      <p className="font-mono font-medium">{simulation.input.load_watts}W</p>
                    </div>
                    <div className="p-3 bg-solar-card rounded-xl">
                      <p className="text-xs text-muted-foreground mb-1">Duration</p>
                      <p className="font-mono font-medium">{formatDuration(simulation.input.simulation_days)}</p>
                    </div>
                    <div className="p-3 bg-solar-card rounded-xl">
                      <p className="text-xs text-muted-foreground mb-1">Battery Health</p>
                      <p className={cn(
                        'font-mono font-medium',
                        simulation.summary.battery_health_final > 80 && 'text-success',
                        simulation.summary.battery_health_final <= 80 && simulation.summary.battery_health_final > 50 && 'text-warning',
                        simulation.summary.battery_health_final <= 50 && 'text-danger'
                      )}>
                        {simulation.summary.battery_health_final.toFixed(1)}%
                      </p>
                    </div>
                    <div className="p-3 bg-solar-card rounded-xl">
                      <p className="text-xs text-muted-foreground mb-1">Energy Produced</p>
                      <p className="font-mono font-medium">{simulation.summary.total_energy_produced_kwh.toLocaleString()} kWh</p>
                    </div>
                  </div>

                  {/* Events Summary */}
                  {(simulation.summary.warnings > 0 || simulation.summary.system_failures > 0) && (
                    <div className="flex items-center gap-4 text-sm">
                      {simulation.summary.warnings > 0 && (
                        <div className="flex items-center gap-2 text-warning">
                          <AlertTriangle className="w-4 h-4" />
                          {simulation.summary.warnings} warnings
                        </div>
                      )}
                      {simulation.summary.system_failures > 0 && (
                        <div className="flex items-center gap-2 text-danger">
                          <Zap className="w-4 h-4" />
                          {simulation.summary.system_failures} failures
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 ml-4">
                  <button className="p-3 rounded-xl bg-primary/10 text-primary hover:bg-primary/20 transition-colors">
                    <Eye className="w-5 h-5" />
                  </button>
                  <button className="p-3 rounded-xl bg-solar-card text-muted-foreground hover:text-danger hover:bg-danger/10 transition-colors">
                    <Trash2 className="w-5 h-5" />
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary/90 transition-colors">
                    View Details
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Empty State */}
      {filteredHistory.length === 0 && (
        <div className="text-center py-16">
          <History className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <p className="text-lg font-medium">No simulations found</p>
          <p className="text-muted-foreground mt-1">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  )
}
