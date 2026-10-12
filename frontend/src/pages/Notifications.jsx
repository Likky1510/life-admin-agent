import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import { notificationsApi } from '../api/client'

export default function Notifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadNotifications() }, [])

  function loadNotifications() {
    setLoading(true)
    notificationsApi.list().then(res => setNotifications(res.data)).finally(() => setLoading(false))
  }

  async function handleMarkRead(id) {
    await notificationsApi.markRead(id)
    loadNotifications()
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Module 3</div>
          <h2>Notifications</h2>
        </div>
      </div>

      <div className="card">
        {loading && <p className="helper-text">Loading…</p>}
        {!loading && notifications.length === 0 && (
          <div className="empty-state">No notifications yet -- they'll show up here as deadlines approach.</div>
        )}
        {notifications.map(n => (
          <div className="life-item-row" key={n.id} style={{opacity: n.is_read ? 0.55 : 1}}>
            <div>
              <div style={{fontWeight: n.is_read ? 400 : 600}}>{n.title}</div>
              <div className="helper-text">{n.message}</div>
              <div className="helper-text">
                via {n.channel} · {new Date(n.sent_at).toLocaleString()}
              </div>
            </div>
            {!n.is_read && (
              <button className="btn btn-small btn-secondary" onClick={() => handleMarkRead(n.id)}>
                Mark read
              </button>
            )}
          </div>
        ))}
      </div>
    </Layout>
  )
}
