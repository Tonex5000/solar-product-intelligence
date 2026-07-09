import { create } from 'zustand'
import type {
  Product,
  SimulationInput,
  SimulationOutput,
  SelectedComponents,
  RailwayNode,
  RailwayEdge,
  AIChatMessage,
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
}))
