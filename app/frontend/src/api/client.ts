import axios from 'axios'
import type {
  AdapterStatus,
  AutomationStatus,
  DashboardPayload,
  RoiSnapshot,
  RoiUpdateRequest,
  SettingsState,
  StatusPackPreview,
  StatusPackRequest,
  StatusPackResult,
  UploadResponse,
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000/api'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
})

export async function fetchDashboard(): Promise<DashboardPayload> {
  const { data } = await client.get<DashboardPayload>('/dashboard')
  return data
}

export interface SampleOptions {
  scenario?: string
  seed?: number
}

export async function loadSampleData(options?: SampleOptions): Promise<UploadResponse> {
  const payload = options && (options.scenario || options.seed !== undefined) ? options : undefined
  const { data } = await client.post<UploadResponse>('/demo/load', payload)
  return data
}

export async function exportStatusPack(
  payload: StatusPackRequest,
): Promise<StatusPackResult> {
  const { data } = await client.post<StatusPackResult>('/export/status-pack', payload)
  return data
}

export async function fetchExportPreview(): Promise<StatusPackPreview> {
  const { data } = await client.get<StatusPackPreview>('/export/status-pack/preview')
  return data
}

export async function fetchRoi(): Promise<RoiSnapshot> {
  const { data } = await client.get<RoiSnapshot>('/roi')
  return data
}

export async function updateRoi(payload: RoiUpdateRequest): Promise<RoiSnapshot> {
  const { data } = await client.post<RoiSnapshot>('/roi', payload)
  return data
}

export async function fetchSettingsState(): Promise<SettingsState> {
  const { data } = await client.get<SettingsState>('/settings')
  return data
}

export async function updateSafeMode(safeMode: boolean): Promise<SettingsState> {
  const { data } = await client.post<SettingsState>('/settings/safe-mode', { safe_mode: safeMode })
  return data
}

export async function updateAdapterMode(
  adapter: 'jira' | 'slack' | 'servicenow',
  mode: 'mock' | 'live',
): Promise<Pick<SettingsState, 'adapter_mode' | 'adapter_modes' | 'adapters'>> {
  const { data } = await client.post<Pick<SettingsState, 'adapter_mode' | 'adapter_modes' | 'adapters'>>(
    '/settings/adapter-mode',
    { adapter, mode },
  )
  return data
}

export async function runAdapterCheck(adapter: 'jira' | 'slack' | 'servicenow'): Promise<AdapterStatus> {
  const { data } = await client.post<AdapterStatus>('/settings/adapter-check', { adapter })
  return data
}

export async function revealExportPath(path: string): Promise<void> {
  await client.post('/export/reveal', { path })
}

export async function fetchExportMarkdown(path: string): Promise<string> {
  const { data } = await client.post<{ content: string }>('/export/markdown', { path })
  return data.content
}

export async function uploadDataset(formData: FormData): Promise<UploadResponse> {
  const { data } = await client.post<UploadResponse>('/ingest', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export async function runAutomationDryRun(): Promise<AutomationStatus> {
  const { data } = await client.post<AutomationStatus>('/automation/dry-run')
  return data
}

export async function purgeLocalData(): Promise<void> {
  await client.post('/ingest/purge')
}

export default client
