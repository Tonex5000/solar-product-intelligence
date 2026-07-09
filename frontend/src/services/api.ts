import type {
  SimulationInput,
  SimulationOutput,
  Product,
  AIExplainRequest,
  AIExplainResponse,
  AIDiagnosisRequest,
  AIDiagnosisResponse,
  ExplanationLevel,
} from '@/types'

const API_BASE = '/api'

// Helper function for API calls
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `API Error: ${response.status}`)
  }

  return response.json()
}

// Products API
export async function getProducts(category?: string): Promise<Product[]> {
  const params = category ? `?category=${category}` : ''
  return apiCall<Product[]>(`/products${params}`)
}

export async function getProduct(id: number): Promise<Product> {
  return apiCall<Product>(`/products/${id}`)
}

// Simulation API
export async function runSimulation(input: SimulationInput): Promise<SimulationOutput> {
  return apiCall<SimulationOutput>('/simulate/', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function getSimulation(id: number): Promise<SimulationOutput> {
  return apiCall<SimulationOutput>(`/simulate/${id}`)
}

export async function validateSystem(
  batteryId: number,
  inverterId: number,
  panelId: number,
  controllerId: number
): Promise<{ valid: boolean; errors: Array<{ message: string }> }> {
  return apiCall('/simulate/validate', {
    method: 'POST',
    body: JSON.stringify({
      battery_id: batteryId,
      inverter_id: inverterId,
      panel_id: panelId,
      charge_controller_id: controllerId,
    }),
  })
}

export async function calculateSizing(
  loadWatts: number,
  dailyHours: number,
  location: string = 'default'
): Promise<{
  panel_watts_needed: number
  battery_wh_needed: number
  inverter_watts_needed: number
  daily_energy_kwh: number
}> {
  return apiCall('/simulate/sizing/calculate', {
    method: 'GET',
    body: JSON.stringify({
      load_watts: loadWatts,
      daily_usage_hours: dailyHours,
      location,
    }),
  })
}

// AI API
export async function explainSimulation(
  request: AIExplainRequest
): Promise<AIExplainResponse> {
  return apiCall<AIExplainResponse>('/ai/explain', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function diagnoseSystem(
  request: AIDiagnosisRequest
): Promise<AIDiagnosisResponse> {
  return apiCall<AIDiagnosisResponse>('/ai/diagnose', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function getRecommendations(
  simulationId: number,
  focusArea?: string,
  level: ExplanationLevel = 'intermediate'
): Promise<{
  summary: string
  product_recommendations: Array<{
    category: string
    reason: string
    expected_improvement: string
    priority: string
  }>
  configuration_changes: string[]
  reasoning: string
}> {
  const params = new URLSearchParams({
    simulation_id: simulationId.toString(),
    level,
  })
  if (focusArea) params.append('focus_area', focusArea)
  
  return apiCall(`/ai/recommend?${params}`)
}

export async function checkAIHealth(): Promise<{
  status: string
  model?: string
  available_models?: string[]
}> {
  return apiCall('/ai/health')
}
