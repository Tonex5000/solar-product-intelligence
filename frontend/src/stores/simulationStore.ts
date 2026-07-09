import { create } from 'zustand'
import type {
  Product,
  SimulationInput,
  SimulationOutput,
  SelectedComponents,
  RailwayNode,
  RailwayEdge,
  AIChatMessage,
  SimulationMetrics,
  Alert,
  CinematicNode,
  CinematicCable,
} from '@/types'

interface SimulationState {
  // Selected products
  selectedComponents: SelectedComponents
  setSelectedComponent: (type: keyof SelectedComponents, product: Product | null) => void
  clearSelectedComponents: () => void

  // Simulation config
  simulationConfig: SimulationInput
  updateSimulationConfig: (config: Partial<SimulationInput>) => void
  resetSimulationConfig: () => void

  // Simulation results
  currentSimulation: SimulationOutput | null
  setCurrentSimulation: (result: SimulationOutput | null) => void
  simulationHistory: SimulationOutput[]
  addToHistory: (result: SimulationOutput) => void

  // Railway visualization state
  railwayNodes: RailwayNode[]
  railwayEdges: RailwayEdge[]
  updateRailwayState: (nodes: RailwayNode[], edges: RailwayEdge[]) => void

  // AI Chat
  chatMessages: AIChatMessage[]
  addChatMessage: (message: AIChatMessage) => void
  clearChatMessages: () => void

  // UI State
  isSimulationRunning: boolean
  setSimulationRunning: (running: boolean) => void
  activePanel: 'builder' | 'results' | 'history'
  setActivePanel: (panel: 'builder' | 'results' | 'history') => void

  // Cinematic Simulation State
  cinematicNodes: CinematicNode[]
  cinematicCables: CinematicCable[]
  updateCinematicState: (nodes: CinematicNode[], cables: CinematicCable[]) => void
  
  // Real-time metrics
  realTimeMetrics: SimulationMetrics
  updateRealTimeMetrics: (metrics: Partial<SimulationMetrics>) => void
  
  // Alerts
  alerts: Alert[]
  addAlert: (alert: Alert) => void
  dismissAlert: (id: string) => void
  markAlertRead: (id: string) => void
  clearAlerts: () => void
  
  // Sound
  soundEnabled: boolean
  setSoundEnabled: (enabled: boolean) => void
  
  // Selected node for details
  selectedNodeId: string | null
  setSelectedNodeId: (id: string | null) => void
}

const defaultComponents: SelectedComponents = {
  battery: null,
  inverter: null,
  panel: null,
  chargeController: null,
}

const defaultConfig: SimulationInput = {
  battery_id: 0,
  inverter_id: 0,
  panel_id: 0,
  charge_controller_id: 0,
  load_watts: 2500,
  daily_usage_hours: 10,
  simulation_days: 365,
  location: 'default',
  avg_sun_hours: 5.0,
}

const defaultRailwayNodes: RailwayNode[] = [
  { id: 'panel', type: 'panel', label: 'Solar Panel', status: 'normal', specs: {}, position: { x: 0, y: 150 } },
  { id: 'controller', type: 'controller', label: 'Charge Controller', status: 'normal', specs: {}, position: { x: 200, y: 150 } },
  { id: 'battery', type: 'battery', label: 'Battery', status: 'normal', specs: {}, position: { x: 400, y: 150 } },
  { id: 'inverter', type: 'inverter', label: 'Inverter', status: 'normal', specs: {}, position: { x: 600, y: 150 } },
  { id: 'load', type: 'load', label: 'Load', status: 'normal', specs: {}, position: { x: 800, y: 150 } },
]

const defaultRailwayEdges: RailwayEdge[] = [
  { id: 'panel-controller', source: 'panel', target: 'controller', flow: 100, status: 'active' },
  { id: 'controller-battery', source: 'controller', target: 'battery', flow: 80, status: 'active' },
  { id: 'battery-inverter', source: 'battery', target: 'inverter', flow: 60, status: 'active' },
  { id: 'inverter-load', source: 'inverter', target: 'load', flow: 100, status: 'active' },
]

const defaultCinematicNodes: CinematicNode[] = [
  { id: 'panel', type: 'panel', label: 'Solar Panel', status: 'normal', specs: { power: 2000, current: 8.3, temperature: 35 } },
  { id: 'controller', type: 'controller', label: 'Charge Controller', status: 'normal', specs: { current: 30, voltage: 48, temperature: 38 } },
  { id: 'battery', type: 'battery', label: 'Battery Bank', status: 'normal', specs: { voltage: 48, power: 9600, temperature: 32 } },
  { id: 'inverter', type: 'inverter', label: 'Inverter', status: 'normal', specs: { power: 5000, efficiency: 97, temperature: 42 } },
  { id: 'load', type: 'load', label: 'Load', status: 'normal', specs: { power: 2500, current: 10.4 } },
]

const defaultCinematicCables: CinematicCable[] = [
  { id: 'panel-controller', source: 'panel', target: 'controller', status: 'normal', current: 8.3, temperature: 28, maxCurrent: 30 },
  { id: 'controller-battery', source: 'controller', target: 'battery', status: 'normal', current: 20, temperature: 35, maxCurrent: 50 },
  { id: 'battery-inverter', source: 'battery', target: 'inverter', status: 'normal', current: 52, temperature: 40, maxCurrent: 100 },
  { id: 'inverter-load', source: 'inverter', target: 'load', status: 'normal', current: 10.4, temperature: 32, maxCurrent: 30 },
]

const defaultMetrics: SimulationMetrics = {
  voltage: 48,
  current: 52,
  power: 2500,
  temperature: 38,
  efficiency: 96.5,
}

export const useSimulationStore = create<SimulationState>((set) => ({
  // Selected products
  selectedComponents: defaultComponents,
  setSelectedComponent: (type, product) =>
    set((state) => ({
      selectedComponents: { ...state.selectedComponents, [type]: product },
    })),
  clearSelectedComponents: () => set({ selectedComponents: defaultComponents }),

  // Simulation config
  simulationConfig: defaultConfig,
  updateSimulationConfig: (config) =>
    set((state) => ({
      simulationConfig: { ...state.simulationConfig, ...config },
    })),
  resetSimulationConfig: () => set({ simulationConfig: defaultConfig }),

  // Simulation results
  currentSimulation: null,
  setCurrentSimulation: (result) => set({ currentSimulation: result }),
  simulationHistory: [],
  addToHistory: (result) =>
    set((state) => ({
      simulationHistory: [result, ...state.simulationHistory].slice(0, 20),
    })),

  // Railway visualization
  railwayNodes: defaultRailwayNodes,
  railwayEdges: defaultRailwayEdges,
  updateRailwayState: (nodes, edges) => set({ railwayNodes: nodes, railwayEdges: edges }),

  // AI Chat
  chatMessages: [],
  addChatMessage: (message) =>
    set((state) => ({
      chatMessages: [...state.chatMessages, message],
    })),
  clearChatMessages: () => set({ chatMessages: [] }),

  // UI State
  isSimulationRunning: false,
  setSimulationRunning: (running) => set({ isSimulationRunning: running }),
  activePanel: 'builder',
  setActivePanel: (panel) => set({ activePanel: panel }),

  // Cinematic Simulation State
  cinematicNodes: defaultCinematicNodes,
  cinematicCables: defaultCinematicCables,
  updateCinematicState: (nodes, cables) => 
    set({ cinematicNodes: nodes, cinematicCables: cables }),
  
  // Real-time metrics
  realTimeMetrics: defaultMetrics,
  updateRealTimeMetrics: (metrics) =>
    set((state) => ({
      realTimeMetrics: { ...state.realTimeMetrics, ...metrics },
    })),
  
  // Alerts
  alerts: [],
  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 50),
    })),
  dismissAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
    })),
  markAlertRead: (id) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === id ? { ...a, isRead: true } : a
      ),
    })),
  clearAlerts: () => set({ alerts: [] }),
  
  // Sound
  soundEnabled: true,
  setSoundEnabled: (enabled) => set({ soundEnabled: enabled }),
  
  // Selected node
  selectedNodeId: null,
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
}))
