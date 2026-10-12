import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import { opportunitiesApi } from '../api/client'
import { SkillTag } from '../components/Badges'

const TYPES = [
  { value: '', label: 'All' },
  { value: 'job', label: 'Jobs' },
  { value: 'internship', label: 'Internships' },
  { value: 'scholarship', label: 'Scholarships' },
  { value: 'government_scheme', label: 'Gov Schemes' },
  { value: 'course', label: 'Courses' },
  { value: 'hackathon', label: 'Hackathons' },
]

export default function Opportunities() {
  const [matches, setMatches] = useState([])
  const [summary, setSummary] = useState('')
  const [filterType, setFilterType] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadMatches() }, [filterType])

  useEffect(() => {
    opportunitiesApi.summary().then(res => setSummary(res.data.summary)).catch(() => {})
  }, [])

  function loadMatches() {
    setLoading(true)
    opportunitiesApi.matches(filterType || undefined)
      .then(res => setMatches(res.data))
      .finally(() => setLoading(false))
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Module 4</div>
          <h2>Opportunity Discovery</h2>
        </div>
      </div>

      {summary && (
        <div className="card" style={{borderLeft: '3px solid var(--sage)', marginBottom: 16}}>
          <div className="eyebrow" style={{marginBottom: 6}}>AI Summary</div>
          <p style={{margin: 0}}>{summary}</p>
        </div>
      )}

      <div className="card" style={{marginBottom: 16}}>
        <div style={{display: 'flex', gap: 8, flexWrap: 'wrap'}}>
          {TYPES.map(t => (
            <button
              key={t.value}
              className={`btn btn-small ${filterType === t.value ? '' : 'btn-secondary'}`}
              onClick={() => setFilterType(t.value)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {loading && <p>Finding matches…</p>}
      {!loading && matches.length === 0 && <div className="empty-state">No opportunities found yet.</div>}

      {matches.map(m => (
        <div className="card" key={m.opportunity.id}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
            <div style={{flex: 1}}>
              <h3 style={{fontSize: '1.02rem', marginBottom: 4}}>{m.opportunity.title}</h3>
              <div className="helper-text" style={{marginBottom: 8}}>
                {m.opportunity.organization} · {m.opportunity.source}
                {m.opportunity.deadline && ` · deadline ${new Date(m.opportunity.deadline).toLocaleDateString()}`}
              </div>
              <p style={{fontSize: '0.88rem', margin: '8px 0'}}>{m.opportunity.description}</p>
              <div style={{marginTop: 8}}>
                {m.opportunity.tags.map(t => <SkillTag key={t} skill={t} />)}
              </div>
              <p className="helper-text" style={{marginTop: 8}}>{m.match_reason}</p>
            </div>
            <div style={{textAlign: 'center', minWidth: 100, marginLeft: 16}}>
              <div className="relevance-pill">{m.relevance_score}%</div>
              <div className="helper-text">match</div>
            </div>
          </div>
        </div>
      ))}
    </Layout>
  )
}
