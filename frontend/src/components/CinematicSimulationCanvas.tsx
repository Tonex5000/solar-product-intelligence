import { useRef, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Sun, 
  Battery, 
  Zap, 
  Cable,
  AlertTriangle,
  CheckCircle,
  Activity,
  Thermometer
} from 'lucide-react'
import { cn } from '@/lib/utils'

// Types
export type NodeStatus = 'normal' | 'optimal' | 'warning' | 'failure' | 'offline'
export type CableStatus = 'normal' | 'heating' | 'critical' | 'offline'

export interface SimulationNode {
  id: string
  type: 'panel' | 'controller' | 'battery' | 'inverter' | 'load'
  label: string
  status: NodeStatus
  specs: {
    voltage?: number
    current?: number
    power?: number
    temperature?: number
    efficiency?: number
  }
}

export interface SimulationCable {
  id: string
  source: string
  target: string
  status: CableStatus
  current: number
  temperature: number
  maxCurrent: number
}

export interface SimulationMetrics {
  voltage: number
  current: number
  power: number
  temperature: number
  efficiency: number
}

// Node Component
function NodeComponent({ 
  node, 
  isActive,
  onClick 
}: { 
  node: SimulationNode
  isActive: boolean
  onClick: () => void 
}) {
  const statusColors = {
    normal: {
      bg: 'from-primary/20 to-primary/5',
      border: 'border-primary/40',
      icon: 'text-primary',
      glow: 'rgba(59, 130, 246, 0.4)',
    },
    optimal: {
      bg: 'from-success/20 to-success/5',
      border: 'border-success/40',
      icon: 'text-success',
      glow: 'rgba(16, 185, 129, 0.4)',
    },
    warning: {
      bg: 'from-warning/20 to-warning/5',
      border: 'border-warning/40',
      icon: 'text-warning',
      glow: 'rgba(249, 115, 22, 0.5)',
    },
    failure: {
      bg: 'from-danger/20 to-danger/5',
      border: 'border-danger/40',
      icon: 'text-danger',
      glow: 'rgba(239, 68, 68, 0.5)',
    },
    offline: {
      bg: 'from-gray-500/20 to-gray-500/5',
      border: 'border-gray-500/40',
      icon: 'text-gray-500',
      glow: 'rgba(107, 114, 128, 0.2)',
    },
  }

  const colors = statusColors[node.status]
  const shouldPulse = node.status === 'warning' || node.status === 'failure'

  const Icon = {
    panel: Sun,
    controller: Cable,
    battery: Battery,
    inverter: Zap,
    load: Activity,
  }[node.type]

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        'relative cursor-pointer',
        isActive && 'ring-2 ring-primary rounded-2xl'
      )}
    >
      {/* Glow effect */}
      <motion.div
        animate={shouldPulse ? {
          opacity: [0.3, 0.6, 0.3],
          scale: [1, 1.1, 1],
        } : {}}
        transition={{ duration: shouldPulse ? 1 : 0, repeat: Infinity }}
        className="absolute inset-0 rounded-2xl blur-xl"
        style={{ backgroundColor: colors.glow }}
      />

      {/* Node card */}
      <div className={cn(
        'relative w-36 h-44 rounded-2xl glass-card p-4 flex flex-col items-center justify-between',
        'border-2 transition-all duration-300',
        colors.border,
        node.status === 'failure' && 'animate-pulse'
      )}>
        {/* Status indicator */}
        <div className="absolute top-3 right-3">
          {node.status === 'optimal' && <CheckCircle className="w-4 h-4 text-success" />}
          {node.status === 'warning' && <AlertTriangle className="w-4 h-4 text-warning" />}
          {node.status === 'failure' && <AlertTriangle className="w-4 h-4 text-danger" />}
          {node.status === 'offline' && <Activity className="w-4 h-4 text-gray-500" />}
        </div>

        {/* Icon */}
        <div className={cn(
          'w-14 h-14 rounded-xl flex items-center justify-center',
          `bg-gradient-to-br ${colors.bg}`
        )}>
          <Icon className={cn('w-7 h-7', colors.icon)} />
        </div>

        {/* Label */}
        <p className="text-sm font-medium text-center">{node.label}</p>

        {/* Specs */}
        <div className="w-full space-y-1 text-xs">
          {node.specs.power && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Power</span>
              <span className="font-mono">{node.specs.power}W</span>
            </div>
          )}
          {node.specs.current && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Current</span>
              <span className="font-mono">{node.specs.current}A</span>
            </div>
          )}
          {node.specs.temperature && (
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground flex items-center gap-1">
                <Thermometer className="w-3 h-3" />
              </span>
              <span className={cn(
                'font-mono',
                node.specs.temperature > 60 && 'text-danger',
                node.specs.temperature > 45 && node.specs.temperature <= 60 && 'text-warning',
                node.specs.temperature <= 45 && 'text-success'
              )}>
                {node.specs.temperature}°C
              </span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

// Cable Component
function CableComponent({
  cable,
  startPos,
  endPos,
  isActive,
}: {
  cable: SimulationCable
  startPos: { x: number, y: number }
  endPos: { x: number, y: number }
  isActive: boolean
}) {
  const statusColors = {
    normal: { color: '#3B82F6', glow: 'rgba(59, 130, 246, 0.5)' },
    heating: { color: '#F97316', glow: 'rgba(249, 115, 22, 0.6)' },
    critical: { color: '#EF4444', glow: 'rgba(239, 68, 68, 0.7)' },
    offline: { color: '#6B7280', glow: 'rgba(107, 114, 128, 0.3)' },
  }

  const colors = statusColors[cable.status]
  
  // Calculate cable thickness based on current load
  const thickness = isActive ? Math.min(8, 2 + (cable.current / cable.maxCurrent) * 6) : 2

  return (
    <g className="cable-group">
      {/* Glow effect */}
      {isActive && (
        <motion.line
          x1={startPos.x}
          y1={startPos.y}
          x2={endPos.x}
          y2={endPos.y}
          stroke={colors.glow}
          strokeWidth={thickness + 8}
          strokeLinecap="round"
          filter="blur(8px)"
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: cable.status === 'critical' ? 0.5 : 2, repeat: Infinity }}
        />
      )}

      {/* Main cable */}
      <motion.line
        x1={startPos.x}
        y1={startPos.y}
        x2={endPos.x}
        y2={endPos.y}
        stroke={colors.color}
        strokeWidth={thickness}
        strokeLinecap="round"
        animate={cable.status === 'critical' ? {
          strokeDashoffset: [0, -20],
        } : {}}
        style={{
          strokeDasharray: cable.status === 'critical' ? '10 5' : undefined,
        }}
      />

      {/* Energy particles */}
      {isActive && cable.current > 0 && (
        <EnergyParticles
          startPos={startPos}
          endPos={endPos}
          color={colors.color}
          speed={cable.current / cable.maxCurrent}
        />
      )}

      {/* Temperature indicator */}
      {cable.temperature > 40 && (
        <g transform={`translate(${(startPos.x + endPos.x) / 2 - 12}, ${(startPos.y + endPos.y) / 2 - 12})`}>
          <rect
            width={24}
            height={16}
            rx={4}
            fill="rgba(0, 0, 0, 0.7)"
            stroke={cable.status === 'critical' ? '#EF4444' : '#F97316'}
            strokeWidth={1}
          />
          <text
            x={12}
            y={11}
            textAnchor="middle"
            fill={cable.status === 'critical' ? '#EF4444' : '#F97316'}
            fontSize={9}
            fontFamily="monospace"
          >
            {cable.temperature}°
          </text>
        </g>
      )}
    </g>
  )
}

// Energy Particles Component
function EnergyParticles({
  startPos,
  endPos,
  color,
  speed,
}: {
  startPos: { x: number, y: number }
  endPos: { x: number, y: number }
  color: string
  speed: number
}) {
  const particleCount = Math.max(3, Math.floor(speed * 8))
  const duration = Math.max(0.5, 2 - speed * 1.5)

  return (
    <>
      {Array.from({ length: particleCount }).map((_, i) => (
        <motion.circle
          key={i}
          r={2 + speed * 2}
          fill={color}
          filter="url(#particleGlow)"
        >
          <animateMotion
            dur={`${duration}s`}
            repeatCount="indefinite"
            begin={`${i * (duration / particleCount)}s`}
            path={`M${startPos.x},${startPos.y} L${endPos.x},${endPos.y}`}
          />
          <animate
            attributeName="opacity"
            values="0;1;1;0"
            dur={`${duration}s`}
            repeatCount="indefinite"
            begin={`${i * (duration / particleCount)}s`}
          />
        </motion.circle>
      ))}
    </>
  )
}

// Metrics Panel Component
function MetricsPanel({ metrics }: { metrics: SimulationMetrics }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-card rounded-2xl p-6 w-72"
    >
      <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
        <Activity className="w-4 h-4 text-primary" />
        Real-time Metrics
      </h3>

      <div className="space-y-4">
        {/* Power */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Power</span>
            <span className="font-mono font-medium">{metrics.power.toFixed(0)}W</span>
          </div>
          <div className="h-2 bg-solar-card rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary to-solar"
              animate={{ width: `${Math.min(100, (metrics.power / 5000) * 100)}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Current */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Current</span>
            <span className="font-mono font-medium">{metrics.current.toFixed(1)}A</span>
          </div>
          <div className="h-2 bg-solar-card rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-primary"
              animate={{ width: `${Math.min(100, (metrics.current / 100) * 100)}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Voltage */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Voltage
          </span>
          <span className="font-mono font-medium">{metrics.voltage.toFixed(1)}V</span>
        </div>

        {/* Temperature */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground flex items-center gap-2">
            <Thermometer className="w-4 h-4" />
            Temperature
          </span>
          <span className={cn(
            'font-mono font-medium',
            metrics.temperature > 60 && 'text-danger',
            metrics.temperature > 45 && metrics.temperature <= 60 && 'text-warning',
            metrics.temperature <= 45 && 'text-success'
          )}>
            {metrics.temperature}°C
          </span>
        </div>

        {/* Efficiency */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">Efficiency</span>
          <span className="font-mono font-medium text-success">{metrics.efficiency.toFixed(1)}%</span>
        </div>
      </div>
    </motion.div>
  )
}

// Main Cinematic Simulation Canvas
export function CinematicSimulationCanvas({
  nodes,
  cables,
  metrics,
  isRunning,
  onNodeClick,
  selectedNodeId,
  soundEnabled: _soundEnabled = true,
}: {
  nodes: SimulationNode[]
  cables: SimulationCable[]
  metrics: SimulationMetrics
  isRunning: boolean
  onNodeClick?: (nodeId: string) => void
  selectedNodeId?: string
  soundEnabled?: boolean
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  // Calculate node positions in a horizontal line
  const nodePositions = useMemo(() => {
    const spacing = 220
    const startX = 100
    const y = 200
    return nodes.map((node, index) => ({
      node,
      x: startX + index * spacing,
      y,
    }))
  }, [nodes])

  // SVG path for cables
  const cablePaths = useMemo(() => {
    return cables.map(cable => {
      const sourceIndex = nodes.findIndex(n => n.id === cable.source)
      const targetIndex = nodes.findIndex(n => n.id === cable.target)
      
      if (sourceIndex === -1 || targetIndex === -1) return null

      const sourcePos = nodePositions[sourceIndex]
      const targetPos = nodePositions[targetIndex]

      return {
        cable,
        startPos: { x: sourcePos.x + 68, y: sourcePos.y },
        endPos: { x: targetPos.x - 68, y: targetPos.y },
      }
    }).filter(Boolean) as Array<{
      cable: SimulationCable
      startPos: { x: number, y: number }
      endPos: { x: number, y: number }
    }>
  }, [cables, nodes, nodePositions])

  return (
    <div ref={containerRef} className="relative w-full h-full min-h-[500px]">
      {/* Background grid */}
      <div className="absolute inset-0 opacity-5">
        <svg width="100%" height="100%">
          <defs>
            <pattern id="cinematicGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <circle cx="20" cy="20" r="1" fill="currentColor" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#cinematicGrid)" />
        </svg>
      </div>

      {/* SVG for cables and particles */}
      <svg
        ref={svgRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ overflow: 'visible' }}
      >
        <defs>
          <filter id="particleGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="nodeGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Cables */}
        {cablePaths.map(({ cable, startPos, endPos }) => (
          <CableComponent
            key={cable.id}
            cable={cable}
            startPos={startPos}
            endPos={endPos}
            isActive={isRunning && cable.status !== 'offline'}
          />
        ))}
      </svg>

      {/* Nodes */}
      <div className="relative z-10 flex items-center justify-center gap-8 pt-20">
        {nodePositions.map(({ node, x, y }) => (
          <div
            key={node.id}
            style={{ position: 'absolute', left: x - 68, top: y - 100 }}
          >
            <NodeComponent
              node={node}
              isActive={selectedNodeId === node.id}
              onClick={() => onNodeClick?.(node.id)}
            />
          </div>
        ))}
      </div>

      {/* Metrics Panel */}
      <div className="absolute top-4 right-4">
        <MetricsPanel metrics={metrics} />
      </div>

      {/* Running indicator */}
      <AnimatePresence>
        {isRunning && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute bottom-4 left-4 flex items-center gap-2 px-4 py-2 glass-card rounded-xl"
          >
            <motion.div
              className="w-3 h-3 rounded-full bg-success"
              animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
            <span className="text-sm font-medium">Simulation Running</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 glass-card rounded-xl p-4">
        <h4 className="text-xs font-semibold mb-3 text-muted-foreground">Cable Status</h4>
        <div className="space-y-2">
          {[
            { color: '#3B82F6', label: 'Normal' },
            { color: '#F97316', label: 'Heating' },
            { color: '#EF4444', label: 'Critical' },
          ].map(item => (
            <div key={item.label} className="flex items-center gap-2">
              <div className="w-6 h-1 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="text-xs">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
