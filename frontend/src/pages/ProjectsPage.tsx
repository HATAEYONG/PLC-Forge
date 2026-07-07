import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { Paginated } from '../types/api'
import type { Company, Project } from '../types/domain'

export default function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [companies, setCompanies] = useState<Company[]>([])
  const [error, setError] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [code, setCode] = useState('')
  const [companyId, setCompanyId] = useState('')

  async function load() {
    try {
      const [p, c] = await Promise.all([
        api.get<Paginated<Project>>('/api/projects/'),
        api.get<Paginated<Company>>('/api/companies/'),
      ])
      setProjects(p.results)
      setCompanies(c.results)
      if (c.results[0]) setCompanyId((prev) => prev || c.results[0].id)
    } catch (err) {
      setError(err instanceof Error ? err.message : '불러오기 실패')
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function createCompany() {
    const created = await api.post<Company>('/api/companies/', {
      name: `신규회사 ${new Date().toISOString().slice(11, 19)}`,
      industry: '식품',
    })
    setCompanies((prev) => [...prev, created])
    setCompanyId(created.id)
  }

  async function onCreate(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      const created = await api.post<Project>('/api/projects/', {
        company: companyId,
        name,
        code,
      })
      setName('')
      setCode('')
      navigate(`/projects/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : '프로젝트 생성 실패')
    }
  }

  return (
    <div className="container">
      <div className="panel">
        <h2>새 프로젝트</h2>
        <form onSubmit={onCreate}>
          <label htmlFor="company">회사</label>
          <div className="row">
            <select
              id="company"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              style={{ flex: 1 }}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.industry})
                </option>
              ))}
            </select>
            <button type="button" className="btn secondary" onClick={createCompany}>
              + 회사
            </button>
          </div>
          <label htmlFor="pname">프로젝트명</label>
          <input id="pname" value={name} onChange={(e) => setName(e.target.value)} />
          <label htmlFor="pcode">코드</label>
          <input id="pcode" value={code} onChange={(e) => setCode(e.target.value)} />
          {error && <p className="error-text">{error}</p>}
          <button className="btn" type="submit" disabled={!companyId || !name || !code}>
            생성하고 인터뷰 시작
          </button>
        </form>
      </div>

      <div className="panel">
        <h2>프로젝트 ({projects.length})</h2>
        <table>
          <thead>
            <tr>
              <th>코드</th>
              <th>이름</th>
              <th>상태</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {projects.map((p) => (
              <tr key={p.id}>
                <td>{p.code}</td>
                <td>{p.name}</td>
                <td>
                  <span className="badge">{p.status}</span>
                </td>
                <td>
                  <button className="btn secondary" onClick={() => navigate(`/projects/${p.id}`)}>
                    열기
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
