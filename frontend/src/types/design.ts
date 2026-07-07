export interface SensorRequirement {
  id: string
  measurement_type: string
  measurement_principle: string
  signal_type: string
  environmental_rating: string
  material_compatibility: string
  communication_requirements: string
}

export interface IOPoint {
  id: string
  tag: string
  signal_type: string
  description: string
  source_type: string
}

export interface PLCCandidate {
  id: string
  vendor: string
  family: string
  accepted: boolean
  reason: string
}

export interface PLCSizing {
  id: string
  di_count: number
  do_count: number
  ai_count: number
  ao_count: number
  spare_margin_percent: number
  required_class: string
  selection_reason: string
  candidates: PLCCandidate[]
}

export interface Alarm {
  id: string
  code: string
  condition: string
  priority: string
  reset_type: string
}

export interface Interlock {
  id: string
  code: string
  protected_device: string
  effect: string
  safety_related: boolean
  bypass_allowed: boolean
  bypass_permission: string
}

export interface SequenceStep {
  id: string
  step_no: number
  name: string
  completion_condition: string
  timeout_seconds: number | null
  timeout_alarm: string
}

export interface Sequence {
  id: string
  code: string
  name: string
  steps: SequenceStep[]
}

export interface DesignDecision {
  id: string
  decision_type: string
  subject_type: string
  subject_id: string
  reason: string
  confidence: number
  risk_level: string
  approval_required: boolean
  override_allowed: boolean
  input_facts: string[]
  rules: string[]
  knowledge_items: string[]
}

export interface ValidationFinding {
  id: string
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  code: string
  title: string
  description: string
  recommended_action: string
  status: string
}

export interface Approval {
  id: string
  target: string
  status: string
  reason: string
  history: { from_status: string; to_status: string; reason: string; created_at: string }[]
}

export interface CauseEffectMatrix {
  causes: string[]
  effects: string[]
  matrix: { cause: string; condition: string; effects: Record<string, boolean> }[]
}
