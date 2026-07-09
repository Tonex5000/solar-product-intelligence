// Product Types
export interface Product {
  id: number
  model_name: string
  product_name: string
  company: string
  category: string
  is_verified: boolean
  validation_status: string
}

export interface ProductSpec {
  key: string
  value: string
  unit?: string
}

// Simulation Types
export interface SimulationInput {
  battery_id: number
  inverter_id: number
  panel_id: number
  charge_controller_id: number
  load_watts: number
  daily_usage_hours: number
  simulation_days: number
  location?: string
  avg_sun_hours?: number
}

export interface SimulationSummary {
  battery_health_final: number
  total_energy_produced_kwh: number
  total_energy_consumed_kwh: number
  total_energy_lost_kwh: number
  system_failures: number
  warnings: number
  cycle_count_total: number
  avg_daily_production_kwh: number
  avg_daily_consumption_kwh: number
  system_balance_percent: number
  projected_battery_lifespan_years: number
  first_failure_day?: number
  max_inverter_load_percent: number
}

export interface SimulationEvent {
  day: number
  type: 'warning' | 'damage' | 'failure' | 'info' | 'milestone'
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  component: string
  details?: Record<string, unknown>
}

export interface TimelineEntry {
  day: number
  date: string
  battery_soc: number
  battery_health: number
  daily_production_kwh: number
  daily_consumption_kwh: number
  cycle_count: number
  inverter_load_percent: number
  events: SimulationEvent[]
}

export interface SimulationOutput {
  id?: number
  status: string
  input: SimulationInput
  summary: SimulationSummary
  timeline: TimelineEntry[]
  events: SimulationEvent[]
  recommendations: Recommendation[]
  created_at?: string
  completed_at?: string
  duration_ms?: number
}

export interface Recommendation {
  category: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  component?: string
  expected_improvement?: string
}

// AI Types
export type ExplanationLevel = 'beginner' | 'intermediate' | 'engineer'

export interface AIExplainRequest {
  simulation_id: number
  question: string
  level: ExplanationLevel
}

export interface AIExplainResponse {
  answer: string
  key_factors: string[]
  referenced_specs: ReferencedSpec[]
  events_used: SimulationEvent[]
  confidence: number
}

export interface ReferencedSpec {
  product_id: number
  product_name: string
  spec_key: string
  spec_value: string
  unit?: string
}

export interface AIDiagnosisRequest {
  simulation_id: number
  level: ExplanationLevel
}

export interface DiagnosisProblem {
  component: string
  problem: string
  cause: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  evidence: string[]
}

export interface AIDiagnosisResponse {
  summary: string
  problems: DiagnosisProblem[]
  overall_health_score: number
  critical_issues: string[]
  warnings: string[]
  confidence: number
}

export interface AIChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

// Railway System Types
export type NodeStatus = 'normal' | 'optimal' | 'warning' | 'failure' | 'offline'
export type CableStatus = 'normal' | 'heating' | 'critical' | 'offline'

export interface RailwayNode {
  id: string
  type: 'panel' | 'controller' | 'battery' | 'inverter' | 'load'
  label: string
  status: NodeStatus
  specs: Record<string, string | number>
  position: { x: number; y: number }
}

export interface RailwayEdge {
  id: string
  source: string
  target: string
  flow: number // 0-100 percentage
  status: 'active' | 'warning' | 'stopped'
  current?: number
  temperature?: number
  maxCurrent?: number
}

// Real-time simulation metrics
export interface SimulationMetrics {
  voltage: number
  current: number
  power: number
  temperature: number
  efficiency: number
}

// Cinematic simulation state
export interface CinematicNode {
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

export interface CinematicCable {
  id: string
  source: string
  target: string
  status: CableStatus
  current: number
  temperature: number
  maxCurrent: number
}

// Alert system types
export type AlertSeverity = 'info' | 'warning' | 'critical' | 'success'

export interface Alert {
  id: string
  type: 'info' | 'warning' | 'damage' | 'failure' | 'milestone' | 'recommendation'
  severity: AlertSeverity
  title: string
  message: string
  component?: string
  day?: number
  explanation?: string
  cause?: string
  recommendation?: string
  timestamp: Date
  isRead: boolean
}

// Component Selection
export interface SelectedComponents {
  battery: Product | null
  inverter: Product | null
  panel: Product | null
  chargeController: Product | null
}
