"""Pydantic models shared across the backend."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, confloat, conint


class Task(BaseModel):
    """Represents a single backlog item."""

    id: str
    title: str
    owner: str = Field(default="Unassigned")
    status: Literal["Not Started", "In Progress", "Complete", "Blocked"]
    start_date: date
    finish_date: date
    planned_hours: float = Field(ge=0)
    actual_hours: float = Field(default=0.0, ge=0)
    blocked: bool = False
    dependency_ids: List[str] = Field(default_factory=list)


class Risk(BaseModel):
    """Represents a risk entry."""

    id: str
    summary: str
    probability: confloat(ge=0.0, le=1.0)
    impact: conint(ge=1, le=5)
    owner: str
    due_date: date
    mitigation: Optional[str] = None


class StatusNote(BaseModel):
    """Markdown notes keyed by date."""

    date: date
    author: Optional[str] = None
    content: str


class EvmBaselinePoint(BaseModel):
    """Baseline PV/EV/AC snapshot."""

    date: date
    pv: float = Field(ge=0)
    ev: float = Field(ge=0)
    ac: float = Field(ge=0)


class DatasetSnapshot(BaseModel):
    """Cached dataset used for analytics + diffing."""

    tasks: List[Task]
    risks: List[Risk]
    status_notes: List[StatusNote]
    baseline: List[EvmBaselinePoint]
    dataset_hash: str
    last_updated: datetime


class UploadResponse(BaseModel):
    dataset_hash: str
    task_count: int
    risk_count: int
    note_dates: List[date]
    baseline_points: int
    last_updated: datetime


class EvmMetrics(BaseModel):
    pv: float
    ev: float
    ac: float
    sv: float
    cv: float
    spi: Optional[float]
    cpi: Optional[float]
    bac: float
    eac: Optional[float]
    etc: Optional[float]
    vac: Optional[float]
    baseline_date: date


class RiskListItem(BaseModel):
    id: str
    summary: str
    probability: float
    impact: int
    severity: float
    due_date: date
    owner: str
    mitigation: Optional[str]
    status: Literal["High", "Medium", "Low"]
    days_to_due: int


class RiskMatrixPoint(BaseModel):
    id: str
    probability: float
    impact: int
    severity: float
    summary: str


class RiskSummary(BaseModel):
    top_risks: List[RiskListItem]
    heatmap: List[RiskMatrixPoint]
    watchlist_size: int


class ChangeItem(BaseModel):
    id: str
    entity_type: Literal["task", "risk", "note"]
    change_type: Literal["added", "updated", "removed"]
    title: str
    detail: str
    timestamp: datetime


class ChangesSummary(BaseModel):
    items: List[ChangeItem]
    has_changes: bool


class RoiAssumption(BaseModel):
    task_name: str
    frequency_per_month: float = Field(ge=0)
    hours_saved: float = Field(ge=0)
    pm_hourly_cost: float = Field(ge=0)
    team_size: int = Field(default=1, ge=1)


class RoiModifiers(BaseModel):
    time_saved_multiplier: float = Field(default=1.0, ge=0.0)
    frequency_multiplier: float = Field(default=1.0, ge=0.0)


class RoiPreset(BaseModel):
    name: str
    label: str
    description: str
    assumptions: List[RoiAssumption]


class RoiSnapshot(BaseModel):
    annual_savings: float
    monthly_savings: float
    total_hours_saved: float
    assumptions: List[RoiAssumption]
    selected_preset: str
    modifiers: RoiModifiers
    available_presets: List[RoiPreset]


class RoiUpdateRequest(BaseModel):
    preset: str
    modifiers: RoiModifiers
    assumptions: List[RoiAssumption]


class AutomationStepStatus(BaseModel):
    key: Literal["ingestion", "analytics", "narrative", "export"]
    title: str
    status: Literal["ok", "pending", "error", "mock"]
    last_run: Optional[datetime]
    duration_ms: Optional[int]
    note: Optional[str] = None


class AutomationStatus(BaseModel):
    steps: List[AutomationStepStatus]
    last_run: Optional[datetime]
    trigger: Literal["unknown", "upload", "dry_run", "seed"]


class AdapterStatus(BaseModel):
    key: Literal["jira", "slack", "servicenow"]
    name: str
    mode: Literal["mock", "live"]
    safe_mode_blocked: bool
    live_configured: bool
    status: Literal["ok", "error", "mock", "unconfigured", "pending"]
    detail: str
    last_checked: Optional[datetime]


class DashboardMeta(BaseModel):
    dataset_hash: str
    last_updated: datetime
    safe_mode: bool


class DashboardPayload(BaseModel):
    evm: EvmMetrics
    risks: RiskSummary
    changes: ChangesSummary
    roi: RoiSnapshot
    narrative: str
    meta: DashboardMeta
    automation: AutomationStatus


class StatusPackRequest(BaseModel):
    include_png: bool = True
    include_markdown: bool = True


class StatusPackResult(BaseModel):
    markdown_path: Optional[str]
    chart_paths: List[str]
    posted_to_slack: bool
    dataset_hash: str


class StatusPackChartPreview(BaseModel):
    name: str
    description: Optional[str] = None
    data_uri: str


class StatusPackPreview(BaseModel):
    markdown: str
    charts: List[StatusPackChartPreview]
    dataset_hash: str
