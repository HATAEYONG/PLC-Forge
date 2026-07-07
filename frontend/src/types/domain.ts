export interface User {
  id: string
  username: string
  email: string
  role: string
}

export interface Company {
  id: string
  name: string
  industry: string
}

export interface Project {
  id: string
  company: string
  name: string
  code: string
  status: string
  created_at: string
}

export type QuestionType =
  | 'TEXT'
  | 'YES_NO'
  | 'SINGLE_CHOICE'
  | 'MULTI_CHOICE'
  | 'INTEGER'
  | 'DECIMAL'
  | 'RANGE'
  | 'UNIT_VALUE'
  | 'DEVICE_LIST'
  | 'TABLE'
  | 'FILE_UPLOAD'
  | 'CONFIRMATION'

export interface AnswerOption {
  id: string
  value: string
  label: string
  order: number
}

export interface Question {
  id: string
  code: string
  text: string
  help_text: string
  category: string
  question_type: QuestionType
  criticality: string
  options: AnswerOption[]
}

export interface ProjectFact {
  id: string
  fact_key: string
  value_json: unknown
  unit: string
  status: string
  confidence: number
}

export interface NextQuestionResponse {
  complete: boolean
  question: Question | null
  selection?: {
    total_score: number
    score_breakdown: Record<string, number>
    reason: string
  }
  coverage?: Record<string, { satisfied: boolean; detail: string }>
  message?: string
}

export interface AnswerResponse {
  answer: { id: string }
  generated_facts: ProjectFact[]
}

export interface InterviewSession {
  id: string
  project: string
  status: string
}

export interface ProgressResponse {
  status: string
  answered_count: number
  known_fact_count: number
  completion: {
    complete: boolean
    criteria: Record<string, { satisfied: boolean; detail: string }>
  }
}
