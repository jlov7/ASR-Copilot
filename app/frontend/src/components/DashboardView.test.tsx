import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { DashboardView } from './DashboardView'
import type { DashboardPayload } from '../types'

const now = new Date().toISOString()

const payload: DashboardPayload = {
  evm: {
    pv: 380,
    ev: 310,
    ac: 356,
    sv: -70,
    cv: -46,
    spi: 0.816,
    cpi: 0.871,
    bac: 490,
    eac: 562.66,
    etc: 206.66,
    vac: -72.66,
    baseline_date: '2023-09-27',
  },
  risks: {
    top_risks: [
      {
        id: 'R1',
        summary: 'Vendor firmware slip could delay milestone',
        probability: 0.6,
        impact: 5,
        severity: 3,
        due_date: '2023-10-05',
        owner: 'Sophia',
        mitigation: 'Escalate to vendor',
        status: 'High',
        days_to_due: 3,
      },
    ],
    heatmap: [
      {
        id: 'R1',
        probability: 0.6,
        impact: 5,
        severity: 3,
        summary: 'Vendor firmware slip could delay milestone',
      },
    ],
    watchlist_size: 1,
  },
  changes: {
    has_changes: true,
    items: [
      {
        id: 'T1',
        entity_type: 'task',
        change_type: 'added',
        title: 'New task',
        detail: 'New entry added.',
        timestamp: new Date().toISOString(),
      },
    ],
  },
  roi: {
    annual_savings: 120000,
    monthly_savings: 10000,
    total_hours_saved: 800,
    assumptions: [
      {
        task_name: 'Status assembly',
        frequency_per_month: 4,
        hours_saved: 4,
        pm_hourly_cost: 95,
        team_size: 1,
      },
    ],
    selected_preset: 'medium',
    modifiers: {
      time_saved_multiplier: 1,
      frequency_multiplier: 1,
    },
    available_presets: [
      {
        name: 'medium',
        label: 'Medium complexity PMO',
        description: 'Test preset',
        assumptions: [
          {
            task_name: 'Status assembly',
            frequency_per_month: 4,
            hours_saved: 4,
            pm_hourly_cost: 95,
            team_size: 1,
          },
        ],
      },
    ],
  },
  automation: {
    steps: [
      {
        key: 'ingestion',
        title: 'Ingestion',
        status: 'ok',
        last_run: '2023-10-05T12:00:00Z',
        duration_ms: 1200,
        note: 'Sample dataset loaded.',
      },
      {
        key: 'analytics',
        title: 'Analytics',
        status: 'ok',
        last_run: '2023-10-05T12:00:01Z',
        duration_ms: 800,
        note: 'CPI 0.87 / SPI 0.82',
      },
      {
        key: 'narrative',
        title: 'Narrative',
        status: 'ok',
        last_run: '2023-10-05T12:00:02Z',
        duration_ms: 420,
        note: 'Narrative refreshed.',
      },
      {
        key: 'export',
        title: 'Export',
        status: 'ok',
        last_run: '2023-10-05T12:00:03Z',
        duration_ms: 600,
        note: 'Markdown saved to status_pack.md',
      },
    ],
    last_run: '2023-10-05T12:00:03Z',
    trigger: 'dry_run',
  },
  narrative: 'Status: Watch. CPI 0.871 / SPI 0.816.',
  meta: {
    dataset_hash: 'abc',
    last_updated: now,
    safe_mode: true,
  },
  data_health: {
    total: 90,
    label: 'Strong',
    summary: 'Completeness: 1 issue(s)',
    last_calculated: now,
    dimensions: [
      {
        key: 'completeness',
        label: 'Completeness',
        score: 36,
        max_score: 40,
        description: 'Required fields populated.',
        issues: ['Task T-1 missing owner.'],
        actions: ['Assign an owner to Task T-1.'],
      },
      {
        key: 'freshness',
        label: 'Freshness',
        score: 22,
        max_score: 25,
        description: 'Updates land recently for active work.',
        issues: [],
        actions: [],
      },
      {
        key: 'consistency',
        label: 'Consistency',
        score: 22,
        max_score: 25,
        description: 'Status aligns with dates and blockers.',
        issues: ['Integration task is blocked without mitigation.'],
        actions: ['Capture mitigation for Integration task.'],
      },
      {
        key: 'conformance',
        label: 'Conformance',
        score: 10,
        max_score: 10,
        description: 'Matches canonical schema.',
        issues: [],
        actions: [],
      },
    ],
  },
  chase_queue: [
    {
      gap_id: 'completeness-T-1',
      summary: 'Missing owner assignment',
      owner: 'Jess PM',
      owner_role: 'Project Manager',
      channel: 'teams',
      priority: 'medium',
      status: 'draft',
      message: 'Hi Jess, can you assign an owner to Task T-1 so we can clear the completeness gap?',
      related_entities: ['T-1'],
      dimension: 'completeness',
    },
  ],
  compliance: {
    shot_clocks: [
      {
        key: 'fcc_collocation_90',
        label: 'FCC Shot Clock – 90 days (collocation)',
        deadline: '2024-06-01',
        days_remaining: 42,
        status: 'green',
        description: 'Collocation milestones remain on track.',
      },
      {
        key: 'fcc_new_site_150',
        label: 'FCC Shot Clock – 150 days (new site)',
        deadline: '2024-08-10',
        days_remaining: 112,
        status: 'amber',
        description: 'Monitor permitting packet to avoid delays.',
      },
    ],
    checklist: [
      {
        key: 'nepa_section_106',
        label: 'NEPA / Section 106 correspondence logged',
        status: 'complete',
        owner: 'Permitting Lead',
        action: 'Upload latest SHPO letter to audit folder.',
      },
      {
        key: 'eligible_facilities',
        label: '6409(a) eligibility documented',
        status: 'pending',
        owner: 'Regulatory Counsel',
        action: 'Confirm documentation before review board.',
      },
      {
        key: 'structural',
        label: 'Structural calculations attached',
        status: 'missing',
        owner: 'Engineering',
        action: 'Provide stamped drawings for build packet.',
      },
      {
        key: 'power_service',
        label: 'Power service / inspection scheduled',
        status: 'pending',
        owner: 'Field Ops',
        action: 'Coordinate utility inspection prior to go-live.',
      },
    ],
    last_reviewed: now,
  },
}

describe('DashboardView', () => {
  it('renders RAG badge and key metrics', () => {
    render(
      <DashboardView
        data={payload}
        isLoading={false}
        exporting={false}
        onExport={vi.fn()}
        onPreview={vi.fn()}
        previewing={false}
        onSaveRoi={vi.fn()}
        roiSaving={false}
        onNotify={vi.fn()}
        onDryRun={vi.fn()}
        dryRunning={false}
      />,
    )

    expect(screen.getByText(/Overall RAG/)).toHaveTextContent('Overall RAG: At Risk')
    expect(screen.getByText(/Data Health 90/)).toBeInTheDocument()
    expect(screen.getByText(/Planned Value/)).toBeInTheDocument()
    expect(screen.getAllByText(/Vendor firmware slip/)[0]).toBeInTheDocument()
    expect(screen.getByText(/Chase queue/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Preview export/i })).toBeInTheDocument()
  })
})
