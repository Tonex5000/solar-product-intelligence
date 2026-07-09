import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar
} from 'recharts'
import { 
  Activity,
  AlertTriangle, 
  Battery, 
  Zap, 
  TrendingUp,
  TrendingDown,
  Sun,
  MessageSquare,
  ChevronRight,
  Download,
  RefreshCw,
  Lightbulb,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react'
import { cn, formatNumber, formatDuration } from '@/lib/utils'
import { useSimulationStore } from '@/stores/simulationStore'
import { AIChatPanel } from '@/components/AIChatPanel'

// Generate mock timeline data
const generateTimelineData = (days: number) => {
  const data = []
  let health = 100
  let soc = 100
  
  for (let day = 0; day <= days; day += Math.max(1, Math.floor(days / 100))) {
    // Simulate degradation
    health = Math.max(0, 100 - (day * 0.015) - (Math.random() * 0.5))
    soc = 50 + (Math.sin(day / 30) * 30) + (Math.random() * 10)
    
    data.push({
      day,
      health: Math.round(health * 10) / 10,
      soc: Math.round(soc * 10) / 10,
      production: 5 + Math.sin(day / 365 * Math.PI) * 2 + (Math.random() - 0.5),
      consumption: 2.5 + (Math.random() - 0.5) * 0.5,
      cycles: Math.floor(day / 1.5),
    })
  }
  return data
}

const mockTimelineData = generateTimelineData(365)

export function SimulationResults() {
  const { currentSimulation } = useSimulationStore()
  const [showAI, setShowAI] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'timeline' | 'events' | 'recommendations'>('overview')

  if (!currentSimulation) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <Activity className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <p className="text-xl font-medium">No simulation results</p>
          <p className="text-muted-foreground mt-1">Run a simulation to see results here</p>
        </div>
      </div>
    )
  }

  const { summary, events } = currentSimulation

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
            Simulation <span className="gradient-text">Results</span>
          </motion.h1>
          <p className="text-muted-foreground mt-1">
            {summary.battery_health_final > 80 ? 'Excellent' : summary.battery_health_final > 50 ? 'Good' : 'Needs Attention'} System Performance
            {' · '}{formatDuration(summary.cycle_count_total / 365)} simulated
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowAI(!showAI)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl transition-all',
              showAI 
                ? 'bg-primary text-white' 
                : 'bg-solar-bg-card hover:bg-solar-bg-card/80'
            )}
          >
            <MessageSquare className="w-5 h-5" />
            AI Assistant
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-solar-bg-card rounded-xl hover:bg-solar-bg-card/80 transition-colors">
            <Download className="w-5 h-5" />
            Export
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-solar-bg-card rounded-xl hover:bg-solar-bg-card/80 transition-colors">
            <RefreshCw className="w-5 h-5" />
            Re-run
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className={cn('space-y-6', showAI && 'lg:col-span-2')}>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                'glass-card rounded-2xl p-5',
                summary.battery_health_final > 80 && 'border-success/30',
                summary.battery_health_final <= 80 && summary.battery_health_final > 50 && 'border-warning/30',
                summary.battery_health_final <= 50 && 'border-danger/30'
              )}
            >
              <div className="flex items-center justify-between mb-3">
                <Battery className={cn(
                  'w-5 h-5',
                  summary.battery_health_final > 80 && 'text-success',
                  summary.battery_health_final <= 80 && summary.battery_health_final > 50 && 'text-warning',
                  summary.battery_health_final <= 50 && 'text-danger'
                )} />
                {summary.battery_health_final > 80 ? (
                  <TrendingUp className="w-4 h-4 text-success" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-danger" />
                )}
              </div>
              <p className="text-3xl font-bold">
                {formatNumber(summary.battery_health_final)}%
              </p>
              <p className="text-sm text-muted-foreground mt-1">Battery Health</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass-card rounded-2xl p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <Zap className="w-5 h-5 text-solar" />
                <span className="text-xs text-muted-foreground">Total</span>
              </div>
              <p className="text-3xl font-bold">{formatNumber(summary.total_energy_produced_kwh)}</p>
              <p className="text-sm text-muted-foreground mt-1">kWh Produced</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card rounded-2xl p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <AlertTriangle className="w-5 h-5 text-warning" />
                <span className="text-xs text-muted-foreground">Events</span>
              </div>
              <p className="text-3xl font-bold">{summary.warnings + summary.system_failures}</p>
              <p className="text-sm text-muted-foreground mt-1">Warnings + Failures</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass-card rounded-2xl p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <Activity className="w-5 h-5 text-primary" />
                <span className="text-xs text-muted-foreground">Efficiency</span>
              </div>
              <p className="text-3xl font-bold">{formatNumber(summary.system_balance_percent)}%</p>
              <p className="text-sm text-muted-foreground mt-1">System Balance</p>
            </motion.div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 bg-solar-bg-card rounded-xl p-1">
            {(['overview', 'timeline', 'events', 'recommendations'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={cn(
                  'flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize',
                  activeTab === tab 
                    ? 'bg-primary text-white' 
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card rounded-2xl p-6 space-y-6"
            >
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Sun className="w-5 h-5 text-solar" />
                Energy Overview
              </h3>
              
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={mockTimelineData}>
                    <defs>
                      <linearGradient id="productionGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="consumptionGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E2A3A" />
                    <XAxis 
                      dataKey="day" 
                      stroke="#6B7280"
                      tick={{ fill: '#9CA3AF', fontSize: 12 }}
                      tickFormatter={(value) => `Day ${value}`}
                    />
                    <YAxis 
                      stroke="#6B7280"
                      tick={{ fill: '#9CA3AF', fontSize: 12 }}
                      tickFormatter={(value) => `${value} kWh`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#161D27', 
                        border: '1px solid #1E2A3A',
                        borderRadius: '8px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="production"
                      stroke="#F59E0B"
                      fill="url(#productionGradient)"
                      strokeWidth={2}
                      name="Production"
                    />
                    <Area
                      type="monotone"
                      dataKey="consumption"
                      stroke="#3B82F6"
                      fill="url(#consumptionGradient)"
                      strokeWidth={2}
                      name="Consumption"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-success/10 rounded-xl">
                  <div className="flex items-center gap-2 text-success mb-2">
                    <TrendingUp className="w-4 h-4" />
                    <span className="font-medium">Surplus</span>
                  </div>
                  <p className="text-2xl font-bold">{formatNumber(summary.total_energy_produced_kwh - summary.total_energy_consumed_kwh)} kWh</p>
                  <p className="text-xs text-muted-foreground mt-1">Net energy generated</p>
                </div>
                <div className="p-4 bg-primary/10 rounded-xl">
                  <div className="flex items-center gap-2 text-primary mb-2">
                    <Activity className="w-4 h-4" />
                    <span className="font-medium">Avg Daily</span>
                  </div>
                  <p className="text-2xl font-bold">{formatNumber(summary.avg_daily_production_kwh)} kWh</p>
                  <p className="text-xs text-muted-foreground mt-1">Average daily production</p>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'timeline' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card rounded-2xl p-6 space-y-6"
            >
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Battery className="w-5 h-5 text-success" />
                Battery Health Over Time
              </h3>
              
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={mockTimelineData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E2A3A" />
                    <XAxis 
                      dataKey="day" 
                      stroke="#6B7280"
                      tick={{ fill: '#9CA3AF', fontSize: 12 }}
                      tickFormatter={(value) => `Day ${value}`}
                    />
                    <YAxis 
                      stroke="#6B7280"
                      tick={{ fill: '#9CA3AF', fontSize: 12 }}
                      domain={[0, 100]}
                      tickFormatter={(value) => `${value}%`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#161D27', 
                        border: '1px solid #1E2A3A',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number) => [`${formatNumber(value)}%`, 'Health']}
                    />
                    <Line
                      type="monotone"
                      dataKey="health"
                      stroke="#10B981"
                      strokeWidth={3}
                      dot={false}
                      name="Battery Health"
                    />
                    <Line
                      type="monotone"
                      dataKey="soc"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      dot={false}
                      name="State of Charge"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-1 bg-success rounded-full" />
                  <span className="text-muted-foreground">Battery Health</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-1 bg-primary rounded-full" style={{ backgroundImage: 'repeating-linear-gradient(90deg, #3B82F6, #3B82F6 4px, transparent 4px, transparent 8px)' }} />
                  <span className="text-muted-foreground">State of Charge</span>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'events' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card rounded-2xl p-6 space-y-4"
            >
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-warning" />
                Event Timeline
              </h3>

              <div className="space-y-3">
                {events.map((event, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={cn(
                      'flex items-start gap-4 p-4 rounded-xl',
                      event.severity === 'critical' && 'bg-danger/10 border border-danger/20',
                      event.severity === 'high' && 'bg-warning/10 border border-warning/20',
                      event.severity === 'medium' && 'bg-primary/10 border border-primary/20',
                      event.severity === 'low' && 'bg-success/10 border border-success/20'
                    )}
                  >
                    <div className={cn(
                      'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                      event.type === 'failure' && 'bg-danger/20 text-danger',
                      event.type === 'warning' && 'bg-warning/20 text-warning',
                      event.type === 'info' && 'bg-primary/20 text-primary',
                      event.type === 'milestone' && 'bg-success/20 text-success'
                    )}>
                      {event.type === 'failure' && <XCircle className="w-4 h-4" />}
                      {event.type === 'warning' && <AlertTriangle className="w-4 h-4" />}
                      {event.type === 'info' && <Info className="w-4 h-4" />}
                      {event.type === 'milestone' && <CheckCircle className="w-4 h-4" />}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium capitalize">{event.type}</span>
                        <span className="text-sm text-muted-foreground">Day {event.day}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">{event.message}</p>
                      <span className="inline-block mt-2 px-2 py-0.5 bg-solar-bg rounded text-xs capitalize">
                        {event.component}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'recommendations' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card rounded-2xl p-6 space-y-4"
            >
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-solar" />
                Recommendations
              </h3>

              {currentSimulation.recommendations.map((rec, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-solar-bg-card rounded-xl hover:bg-solar-bg-card/80 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className={cn(
                      'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                      rec.priority === 'high' && 'bg-danger/20 text-danger',
                      rec.priority === 'medium' && 'bg-warning/20 text-warning',
                      rec.priority === 'low' && 'bg-success/20 text-success'
                    )}>
                      <Lightbulb className="w-4 h-4" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium">{rec.title}</span>
                        <span className={cn(
                          'px-2 py-0.5 rounded text-xs uppercase',
                          rec.priority === 'high' && 'bg-danger/20 text-danger',
                          rec.priority === 'medium' && 'bg-warning/20 text-warning',
                          rec.priority === 'low' && 'bg-success/20 text-success'
                        )}>
                          {rec.priority}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{rec.description}</p>
                      {rec.expected_improvement && (
                        <p className="text-sm text-success mt-2 flex items-center gap-1">
                          <TrendingUp className="w-4 h-4" />
                          {rec.expected_improvement}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>

        {/* AI Chat Panel */}
        {showAI && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <AIChatPanel />
          </motion.div>
        )}
      </div>
    </div>
  )
}
