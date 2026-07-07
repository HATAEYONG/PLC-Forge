import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { QuestionWidget } from '../QuestionWidget'
import type { Question } from '../../types/domain'

function makeQuestion(overrides: Partial<Question>): Question {
  return {
    id: 'q1',
    code: 'Q-1',
    text: '질문',
    help_text: '',
    category: 'DEVICE',
    question_type: 'TEXT',
    criticality: 'MEDIUM',
    options: [],
    ...overrides,
  }
}

describe('QuestionWidget', () => {
  it('INTEGER 답변을 숫자로 제출한다', () => {
    const onSubmit = vi.fn()
    render(
      <QuestionWidget question={makeQuestion({ question_type: 'INTEGER' })} onSubmit={onSubmit} />,
    )
    fireEvent.change(screen.getByLabelText('answer'), { target: { value: '3' } })
    fireEvent.click(screen.getByText('답변 제출'))
    expect(onSubmit).toHaveBeenCalledWith(3)
  })

  it('YES_NO 답변을 boolean으로 제출한다', () => {
    const onSubmit = vi.fn()
    render(
      <QuestionWidget question={makeQuestion({ question_type: 'YES_NO' })} onSubmit={onSubmit} />,
    )
    fireEvent.change(screen.getByLabelText('answer'), { target: { value: 'yes' } })
    fireEvent.click(screen.getByText('답변 제출'))
    expect(onSubmit).toHaveBeenCalledWith(true)
  })

  it('UNIT_VALUE 답변을 {value, unit} 객체로 제출한다', () => {
    const onSubmit = vi.fn()
    render(
      <QuestionWidget
        question={makeQuestion({ question_type: 'UNIT_VALUE' })}
        onSubmit={onSubmit}
      />,
    )
    fireEvent.change(screen.getByLabelText('answer-value'), { target: { value: '80' } })
    fireEvent.change(screen.getByLabelText('answer-unit'), { target: { value: 'C' } })
    fireEvent.click(screen.getByText('답변 제출'))
    expect(onSubmit).toHaveBeenCalledWith({ value: 80, unit: 'C' })
  })

  it('MULTI_CHOICE 답변을 선택 배열로 제출한다', () => {
    const onSubmit = vi.fn()
    const q = makeQuestion({
      question_type: 'MULTI_CHOICE',
      options: [
        { id: 'a', value: 'LEVEL', label: '레벨', order: 0 },
        { id: 'b', value: 'TEMP', label: '온도', order: 1 },
      ],
    })
    render(<QuestionWidget question={q} onSubmit={onSubmit} />)
    fireEvent.click(screen.getByText('레벨'))
    fireEvent.click(screen.getByText('답변 제출'))
    expect(onSubmit).toHaveBeenCalledWith(['LEVEL'])
  })

  it('빈 답변은 제출 버튼이 비활성화된다', () => {
    render(<QuestionWidget question={makeQuestion({})} onSubmit={vi.fn()} />)
    expect(screen.getByText('답변 제출')).toBeDisabled()
  })
})
