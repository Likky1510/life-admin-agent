import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import Layout from '../components/Layout'
import { analyticsApi } from '../api/client'

const COLORS = ['#3f6b4f', '#c4791f', '#b3473f', '#2f6b8f']

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    analyticsApi.summary()
      .then(res => setData(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Could not load analytics.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Layout><p>Loading…</p></Layout>
  if (error) return <Layout><div className="error-text">{error}</div></Layout>
  if (!data) return null

  const pieData = [
    { name: 'Completed', value: data.completed_tasks },
    { name: 'Upcoming', value: data.upcoming_deadlines },
    { name: 'Overdue', value: data.overdue_items },
  ].filter(d => d.value > 0)

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Module 6</div>
          <h2>Analytics</h2>
        </div>
      </div>

      <div className="grid grid-4" style={{marginBottom: 20}}>
        <div className="card stat-card">
          <div className="stat-value">{data.upcoming_deadlines}</div>
          <div className="stat-label">Upcoming</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{data.completed_tasks}</div>
          <div className="stat-label">Completed</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{data.overdue_items}</div>
          <div className="stat-label">Overdue</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{data.completion_rate_pct}%</div>
          <div className="stat-label">Completion Rate</div>
        </div>
      </div>

      {data.productivity_tip && (
        <div className="card" style={{borderLeft: '3px solid var(--sage)', marginBottom: 16}}>
          <div className="eyebrow" style={{marginBottom: 6}}>Productivity Tip</div>
          <p style={{margin: 0}}>{data.productivity_tip}</p>
        </div>
      )}

      {pieData.length > 0 && (
        <div className="card">
          <h3 style={{marginBottom: 12, fontSize: '1.05rem'}}>Task Breakdown</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90} label>
                {pieData.map((entry, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card stat-card">
        <div className="stat-value">{data.opportunities_available}</div>
        <div className="stat-label">Opportunities Available</div>
      </div>
    </Layout>
  )
}
