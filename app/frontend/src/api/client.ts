import axios from 'axios'
import type {
  DashboardPayload,
  RoiSnapshot,
  RoiUpdateRequest,
  SettingsState,
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

export async function loadSampleData(): Promise<UploadResponse> {
  const { data } = await client.post<UploadResponse>('/demo/load')
  return data
}

export async function exportStatusPack(
  payload: StatusPackRequest,
): Promise<StatusPackResult> {
  const { data } = await client.post<StatusPackResult>('/export/status-pack', payload)
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

export async function uploadDataset(formData: FormData): Promise<UploadResponse> {
  const { data } = await client.post<UploadResponse>('/ingest', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export default client
