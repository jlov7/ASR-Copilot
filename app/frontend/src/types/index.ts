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

export interface AutomationStepStatus {
  key: 'ingestion' | 'analytics' | 'narrative' | 'export'
  title: string
  status: 'ok' | 'pending' | 'error' | 'mock'
  last_run: string | null
  duration_ms: number | null
  note?: string | null
}

export interface AutomationStatus {
  steps: AutomationStepStatus[]
  last_run: string | null
  trigger: 'unknown' | 'upload' | 'dry_run' | 'seed'
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

export type DataHealthKey = 'completeness' | 'freshness' | 'consistency' | 'conformance'

export interface DataHealthDimension {
  key: DataHealthKey
  label: string
  score: number
  max_score: number
  description: string
  issues: string[]
  actions: string[]
}

export type DataHealthLabel = 'Excellent' | 'Strong' | 'Fair' | 'Weak'

export interface DataHealthScore {
  total: number
  label: DataHealthLabel
  summary: string
  dimensions: DataHealthDimension[]
  last_calculated: string
}

export type ChaseChannel = 'email' | 'teams'
export type ChasePriority = 'low' | 'medium' | 'high'

export interface ChaseQueueItem {
  gap_id: string
  summary: string
  owner: string
  owner_role?: string | null
  channel: ChaseChannel
  priority: ChasePriority
  status: 'draft' | 'ready' | 'sent'
  message: string
  related_entities: string[]
  dimension: DataHealthKey
}

export interface ComplianceCountdown {
  key: 'fcc_collocation_90' | 'fcc_new_site_150'
  label: string
  deadline: string
  days_remaining: number
  status: 'green' | 'amber' | 'red'
  description: string
}

export interface ComplianceChecklistItem {
  key: 'nepa_section_106' | 'eligible_facilities' | 'structural' | 'power_service'
  label: string
  status: 'complete' | 'pending' | 'missing'
  owner?: string | null
  action?: string | null
}

export interface CompliancePanel {
  shot_clocks: ComplianceCountdown[]
  checklist: ComplianceChecklistItem[]
  last_reviewed: string
}

export interface DashboardPayload {
  evm: EvmMetrics
  risks: RiskSummary
  changes: ChangesSummary
  roi: RoiSnapshot
  narrative: string
  meta: DashboardMeta
  automation: AutomationStatus
  data_health: DataHealthScore
  chase_queue: ChaseQueueItem[]
  compliance: CompliancePanel
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

export interface StatusPackChartPreview {
  name: string
  description?: string | null
  data_uri: string
}

export interface StatusPackPreview {
  markdown: string
  charts: StatusPackChartPreview[]
  dataset_hash: string
}

export interface AdapterStatus {
  key: 'jira' | 'slack' | 'servicenow'
  name: string
  mode: 'mock' | 'live'
  safe_mode_blocked: boolean
  live_configured: boolean
  status: 'ok' | 'error' | 'mock' | 'unconfigured' | 'pending'
  detail: string
  last_checked: string | null
}

export interface SettingsState {
  safe_mode: boolean
  adapter_mode: 'mock' | 'live'
  adapter_modes?: Record<'jira' | 'slack' | 'servicenow', 'mock' | 'live'>
  adapters?: AdapterStatus[]
}

export interface DashboardState {
  data?: DashboardPayload
  loading: boolean
  error?: string
}
