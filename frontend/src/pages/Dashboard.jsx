import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { useAuth } from '../api/AuthContext'
import { lifeItemsApi, notificationsApi, assistantApi } from '../api/client'
import { TypeBadge, UrgencyBadge } from '../components/Badges'

export default function Dashboard() {
  const { user } = useAuth()
  const [upcoming, setUpcoming] = useState([])
  const [notifications, setNotifications] = useState([])
  const [schedule, setSchedule] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      lifeItemsApi.upcoming(),
      notificationsApi.list(),
      assistantApi.dailySchedule(),
    ]).then(([itemsRes, notifRes, scheduleRes]) => {
      setUpcoming(itemsRes.data)
      setNotifications(notifRes.data)
      setSchedule(scheduleRes.data)
    }).finally(() => setLoading(false))
  }, [])

  const overdueCount = upcoming.filter(i => new Date(i.due_date) < new Date()).length

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Good to see you</div>
          <h2>{user?.name}</h2>
        </div>
      </div>

      <div className="grid grid-4" style={{marginBottom: 20}}>
        <div className="card stat-card">
          <div className="stat-value">{upcoming.length}</div>
          <div className="stat-label">Upcoming Items</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{overdueCount}</div>
          <div className="stat-label">Overdue</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{notifications.filter(n => !n.is_read).length}</div>
          <div className="stat-label">Unread Alerts</div>
        </div>
      </div>

      {schedule && (
        <div className="card" style={{borderLeft: '3px solid var(--sage)', marginBottom: 16}}>
          <div className="eyebrow" style={{marginBottom: 8}}>Today's Plan</div>
          <p style={{margin: '0 0 10px 0'}}>{schedule.summary}</p>
          {schedule.schedule.length > 0 && (
            <ul style={{margin: 0, paddingLeft: 20}}>
              {schedule.schedule.map((s, i) => <li key={i} style={{fontSize: '0.9rem', marginBottom: 4}}>{s}</li>)}
            </ul>
          )}
        </div>
      )}

      <div className="card">
        <h3 style={{fontSize: '1.05rem', marginBottom: 12}}>Upcoming</h3>
        {loading && <p className="helper-text">Loading…</p>}
        {!loading && upcoming.length === 0 && (
          <p className="helper-text">Nothing tracked yet. <Link to="/tasks">Add your first item</Link>.</p>
        )}
        {upcoming.slice(0, 6).map(item => (
          <div className="life-item-row" key={item.id}>
            <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
              <TypeBadge type={item.item_type} />
              <span>{item.title}</span>
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
              <UrgencyBadge dueDate={item.due_date} isCompleted={item.is_completed} />
              <span className="helper-text">{new Date(item.due_date).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  )
}
