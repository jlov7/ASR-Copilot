export type RAGState = 'On Track' | 'Watch' | 'At Risk'

export interface EvmMetrics {
  pv: number
  ev: number
  ac: number
  sv: number
  cv: number
  spi: number | null
  cpi: number | null
  bac: number
  eac: number | null
  etc: number | null
  vac: number | null
  baseline_date: string
}

export interface RiskListItem {
  id: string
  summary: string
  probability: number
  impact: number
  severity: number
  due_date: string
  owner: string
  mitigation?: string | null
  status: 'High' | 'Medium' | 'Low'
  days_to_due: number
}

export interface RiskMatrixPoint {
  id: string
  probability: number
  impact: number
  severity: number
  summary: string
}

export interface RiskSummary {
  top_risks: RiskListItem[]
  heatmap: RiskMatrixPoint[]
  watchlist_size: number
}

export interface ChangeItem {
  id: string
  entity_type: 'task' | 'risk' | 'note'
  change_type: 'added' | 'updated' | 'removed'
  title: string
  detail: string
  timestamp: string
}

export interface ChangesSummary {
  items: ChangeItem[]
  has_changes: boolean
}

export interface RoiAssumption {
  task_name: string
  frequency_per_month: number
  hours_saved: number
  pm_hourly_cost: number
  team_size: number
}

export interface RoiModifiers {
  time_saved_multiplier: number
  frequency_multiplier: number
}

export interface RoiPreset {
  name: string
  label: string
  description: string
  assumptions: RoiAssumption[]
}

export interface RoiSnapshot {
  annual_savings: number
  monthly_savings: number
  total_hours_saved: number
  assumptions: RoiAssumption[]
  selected_preset: string
  modifiers: RoiModifiers
  available_presets: RoiPreset[]
}

export interface RoiUpdateRequest {
  preset: string
  modifiers: RoiModifiers
  assumptions: RoiAssumption[]
}

export interface DashboardMeta {
  dataset_hash: string
  last_updated: string
  safe_mode: boolean
}

export interface DashboardPayload {
  evm: EvmMetrics
  risks: RiskSummary
  changes: ChangesSummary
  roi: RoiSnapshot
  narrative: string
  meta: DashboardMeta
}

export interface UploadResponse {
  dataset_hash: string
  task_count: number
  risk_count: number
  note_dates: string[]
  baseline_points: number
  last_updated: string
}

export interface StatusPackRequest {
  include_markdown: boolean
  include_png: boolean
}

export interface StatusPackResult {
  markdown_path: string | null
  chart_paths: string[]
  posted_to_slack: boolean
  dataset_hash: string
}

export interface SettingsState {
  safe_mode: boolean
  adapter_mode: 'mock' | 'live'
}

export interface DashboardState {
  data?: DashboardPayload
  loading: boolean
  error?: string
}
