import { useState } from 'react'
import type { Question } from '../types/domain'

interface Props {
  question: Question
  onSubmit: (rawAnswer: unknown) => void
  busy?: boolean
}

/** 질문 유형별 입력 위젯 (PRD §8.3). rawAnswer를 백엔드 Answer Processor 형식으로 만든다. */
export function QuestionWidget({ question, onSubmit, busy }: Props) {
  const [value, setValue] = useState<string>('')
  const [multi, setMulti] = useState<string[]>([])
  const [unit, setUnit] = useState<string>('')

  const t = question.question_type

  function toggleMulti(v: string) {
    setMulti((prev) => (prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v]))
  }

  function submit() {
    if (t === 'INTEGER') return onSubmit(parseInt(value, 10))
    if (t === 'DECIMAL') return onSubmit(parseFloat(value))
    if (t === 'YES_NO' || t === 'CONFIRMATION') return onSubmit(value === 'yes')
    if (t === 'UNIT_VALUE') return onSubmit({ value: parseFloat(value), unit })
    if (t === 'MULTI_CHOICE') return onSubmit(multi)
    if (t === 'DEVICE_LIST')
      return onSubmit(
        value
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
      )
    return onSubmit(value)
  }

  const canSubmit =
    t === 'MULTI_CHOICE'
      ? multi.length > 0
      : t === 'UNIT_VALUE'
        ? value !== '' && unit !== ''
        : value !== ''

  return (
    <div>
      {(t === 'TEXT' || t === 'DEVICE_LIST') && (
        <textarea
          rows={3}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={t === 'DEVICE_LIST' ? '쉼표로 구분 (예: 펌프, 밸브, 히터)' : ''}
          aria-label="answer"
        />
      )}
      {(t === 'INTEGER' || t === 'DECIMAL') && (
        <input
          type="number"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          aria-label="answer"
        />
      )}
      {t === 'UNIT_VALUE' && (
        <div className="row">
          <input
            type="number"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="값"
            aria-label="answer-value"
            style={{ flex: 2 }}
          />
          <input
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
            placeholder="단위 (예: C, L, bar)"
            aria-label="answer-unit"
            style={{ flex: 1 }}
          />
        </div>
      )}
      {(t === 'YES_NO' || t === 'CONFIRMATION') && (
        <select value={value} onChange={(e) => setValue(e.target.value)} aria-label="answer">
          <option value="">선택…</option>
          <option value="yes">예</option>
          <option value="no">아니오</option>
        </select>
      )}
      {t === 'SINGLE_CHOICE' && (
        <select value={value} onChange={(e) => setValue(e.target.value)} aria-label="answer">
          <option value="">선택…</option>
          {question.options.map((o) => (
            <option key={o.id} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      )}
      {t === 'MULTI_CHOICE' && (
        <div>
          {question.options.map((o) => (
            <label key={o.id} className="row" style={{ margin: '0.3rem 0' }}>
              <input
                type="checkbox"
                checked={multi.includes(o.value)}
                onChange={() => toggleMulti(o.value)}
                style={{ width: 'auto' }}
              />
              <span>{o.label}</span>
            </label>
          ))}
        </div>
      )}
      <button
        className="btn"
        onClick={submit}
        disabled={busy || !canSubmit}
        style={{ marginTop: '0.8rem' }}
      >
        {busy ? '처리 중…' : '답변 제출'}
      </button>
    </div>
  )
}
