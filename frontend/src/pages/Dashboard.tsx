import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  Zap, 
  Sun, 
  Battery, 
  AlertTriangle,
  TrendingUp,
  Clock,
  ArrowRight,
  Play,
  BarChart3,
  Shield
} from 'lucide-react'
import { useSimulationStore } from '@/stores/simulationStore'

const stats = [
  { 
    label: 'System Health', 
    value: '94%', 
    icon: Shield, 
    color: 'text-success',
    bgColor: 'bg-success/20',
    trend: '+2%'
  },
  { 
    label: 'Energy Today', 
    value: '28.5 kWh', 
    icon: Zap, 
    color: 'text-primary',
    bgColor: 'bg-primary/20',
    trend: '+12%'
  },
  { 
    label: 'Battery Level', 
    value: '78%', 
    icon: Battery, 
    color: 'text-solar',
    bgColor: 'bg-solar/20',
    trend: '+5%'
  },
  { 
    label: 'Active Alerts', 
    value: '2', 
    icon: AlertTriangle, 
    color: 'text-warning',
    bgColor: 'bg-warning/20',
    trend: '-1'
  },
]

const quickActions = [
  {
    title: 'New Simulation',
    description: 'Run a system simulation',
    icon: Play,
    href: '/simulate',
    color: 'from-primary to-blue-600',
  },
  {
    title: 'View Products',
    description: 'Browse solar components',
    icon: BarChart3,
    href: '/products',
    color: 'from-solar to-amber-600',
  },
  {
    title: 'System History',
    description: 'Past simulations',
    icon: Clock,
    href: '/history',
    color: 'from-success to-emerald-600',
  },
]

const recentSimulations = [
  { id: 1, name: 'Home System v2', health: 94, date: '2 hours ago', status: 'optimal' },
  { id: 2, name: 'Office Backup', health: 78, date: '1 day ago', status: 'warning' },
  { id: 3, name: 'Remote Cabin', health: 45, date: '3 days ago', status: 'failure' },
]

const alerts = [
  { id: 1, type: 'warning', message: 'Battery approaching end of life', time: '2h ago' },
  { id: 2, type: 'info', message: 'System balance optimized', time: '5h ago' },
  { id: 3, type: 'success', message: 'Panel cleaning completed', time: '1d ago' },
]

export function Dashboard() {
  // simulationHistory can be used for displaying recent simulations
  useSimulationStore()

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
            <span className="gradient-text">SolarFlow</span> Dashboard
          </motion.h1>
          <p className="text-muted-foreground mt-1">
            Monitor and simulate your solar energy system
          </p>
        </div>
        <Link
          to="/simulate"
          className="flex items-center gap-2 px-6 py-3 bg-primary hover:bg-primary/90 rounded-xl font-medium transition-all"
        >
          <Play className="w-5 h-5" />
          New Simulation
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card rounded-2xl p-6 hover:border-primary/30 transition-all"
          >
            <div className="flex items-start justify-between">
              <div className={`p-3 rounded-xl ${stat.bgColor}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <span className="text-xs text-success flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                {stat.trend}
              </span>
            </div>
            <div className="mt-4">
              <p className="text-3xl font-bold">{stat.value}</p>
              <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-1 space-y-6"
        >
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary" />
            Quick Actions
          </h2>
          <div className="space-y-4">
            {quickActions.map((action) => (
              <Link
                key={action.title}
                to={action.href}
                className="group block glass-card rounded-xl p-4 hover:border-primary/30 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${action.color}`}>
                    <action.icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium group-hover:text-primary transition-colors">
                      {action.title}
                    </p>
                    <p className="text-sm text-muted-foreground">{action.description}</p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                </div>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* Recent Simulations */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-2 glass-card rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Sun className="w-5 h-5 text-solar" />
              Recent Simulations
            </h2>
            <Link 
              to="/history" 
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              View All <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="space-y-4">
            {recentSimulations.map((sim) => (
              <div
                key={sim.id}
                className="flex items-center gap-4 p-4 rounded-xl bg-solar-card hover:bg-solar-card/80 transition-colors"
              >
                <div className="flex-1">
                  <p className="font-medium">{sim.name}</p>
                  <p className="text-sm text-muted-foreground">{sim.date}</p>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${
                    sim.status === 'optimal' ? 'text-success' :
                    sim.status === 'warning' ? 'text-warning' : 'text-danger'
                  }`}>
                    {sim.health}%
                  </p>
                  <p className="text-xs text-muted-foreground capitalize">{sim.status}</p>
                </div>
                <Link
                  to="/simulate/results"
                  className="p-2 rounded-lg hover:bg-primary/10 text-muted-foreground hover:text-primary transition-colors"
                >
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Alerts Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card rounded-2xl p-6"
      >
        <h2 className="text-xl font-semibold flex items-center gap-2 mb-6">
          <AlertTriangle className="w-5 h-5 text-warning" />
          System Alerts
        </h2>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-center gap-4 p-4 rounded-xl ${
                alert.type === 'warning' ? 'bg-warning/10 border border-warning/20' :
                alert.type === 'success' ? 'bg-success/10 border border-success/20' :
                'bg-primary/10 border border-primary/20'
              }`}
            >
              <div className={`w-2 h-2 rounded-full ${
                alert.type === 'warning' ? 'bg-warning' :
                alert.type === 'success' ? 'bg-success' :
                'bg-primary'
              }`} />
              <span className="flex-1">{alert.message}</span>
              <span className="text-sm text-muted-foreground">{alert.time}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* System Flow Visualization Preview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-card rounded-2xl p-6"
      >
        <h2 className="text-xl font-semibold flex items-center gap-2 mb-6">
          <TrendingUp className="w-5 h-5 text-primary" />
          System Flow Overview
        </h2>
        <div className="flex items-center justify-between overflow-x-auto py-4">
          {['Solar Panel', 'Charge Controller', 'Battery', 'Inverter', 'Load'].map((component, index) => (
            <div key={component} className="flex items-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex flex-col items-center"
              >
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-solar/20 border border-primary/30 flex items-center justify-center mb-2">
                  {index === 0 && <Sun className="w-8 h-8 text-solar" />}
                  {index === 1 && <Zap className="w-8 h-8 text-primary" />}
                  {index === 2 && <Battery className="w-8 h-8 text-success" />}
                  {index === 3 && <Zap className="w-8 h-8 text-primary" />}
                  {index === 4 && (
                    <svg className="w-8 h-8 text-solar" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  )}
                </div>
                <span className="text-xs text-center max-w-[80px]">{component}</span>
              </motion.div>
              {index < 4 && (
                <div className="w-12 h-1 mx-2 bg-gradient-to-r from-primary/50 to-solar/50 rounded-full relative overflow-hidden">
                  <motion.div
                    className="absolute inset-0 bg-white/50"
                    animate={{ x: ['-100%', '100%'] }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
