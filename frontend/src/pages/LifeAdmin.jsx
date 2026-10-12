import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import { lifeItemsApi } from '../api/client'
import { TypeBadge, UrgencyBadge } from '../components/Badges'

const ITEM_TYPES = ['task', 'bill', 'subscription', 'appointment', 'document']
const RECURRENCE_OPTIONS = ['none', 'daily', 'weekly', 'monthly', 'yearly']

export default function LifeAdmin() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterType, setFilterType] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    item_type: 'task', title: '', description: '', due_date: '', amount: '', recurrence: 'none',
  })

  useEffect(() => { loadItems() }, [filterType])

  function loadItems() {
    setLoading(true)
    lifeItemsApi.list(filterType ? { item_type: filterType } : {})
      .then(res => setItems(res.data))
      .finally(() => setLoading(false))
  }

  async function handleCreate(e) {
    e.preventDefault()
    setError('')
    try {
      const payload = {
        ...form,
        due_date: new Date(form.due_date).toISOString(),
        amount: form.amount ? parseFloat(form.amount) : null,
      }
      await lifeItemsApi.create(payload)
      setShowForm(false)
      setForm({ item_type: 'task', title: '', description: '', due_date: '', amount: '', recurrence: 'none' })
      loadItems()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create item.')
    }
  }

  async function toggleComplete(item) {
    await lifeItemsApi.update(item.id, { is_completed: !item.is_completed })
    loadItems()
  }

  async function handleDelete(id) {
    await lifeItemsApi.delete(id)
    loadItems()
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Module 2</div>
          <h2>Life Admin</h2>
        </div>
        <button className="btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Item'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <form onSubmit={handleCreate}>
            <div className="grid grid-2">
              <div className="field">
                <label>Type</label>
                <select value={form.item_type} onChange={e => setForm({...form, item_type: e.target.value})}>
                  {ITEM_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Title</label>
                <input value={form.title} onChange={e => setForm({...form, title: e.target.value})} required />
              </div>
            </div>
            <div className="field">
              <label>Description (optional)</label>
              <textarea rows={2} value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
            </div>
            <div className="grid grid-3">
              <div className="field">
                <label>Due date</label>
                <input type="datetime-local" value={form.due_date} onChange={e => setForm({...form, due_date: e.target.value})} required />
              </div>
              <div className="field">
                <label>Amount (if bill/subscription)</label>
                <input type="number" step="0.01" value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} />
              </div>
              <div className="field">
                <label>Recurrence</label>
                <select value={form.recurrence} onChange={e => setForm({...form, recurrence: e.target.value})}>
                  {RECURRENCE_OPTIONS.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
            </div>
            {error && <div className="error-text">{error}</div>}
            <button className="btn" type="submit">Save</button>
          </form>
        </div>
      )}

      <div className="card" style={{marginBottom: 16}}>
        <div style={{display: 'flex', gap: 8}}>
          <button className={`btn btn-small ${filterType === '' ? '' : 'btn-secondary'}`} onClick={() => setFilterType('')}>All</button>
          {ITEM_TYPES.map(t => (
            <button key={t} className={`btn btn-small ${filterType === t ? '' : 'btn-secondary'}`} onClick={() => setFilterType(t)}>
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        {loading && <p className="helper-text">Loading…</p>}
        {!loading && items.length === 0 && <div className="empty-state">Nothing here yet.</div>}
        {items.map(item => (
          <div className="life-item-row" key={item.id}>
            <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
              <div
                className={`checkbox-circle ${item.is_completed ? 'checked' : ''}`}
                onClick={() => toggleComplete(item)}
              >
                {item.is_completed && '✓'}
              </div>
              <div>
                <div style={{textDecoration: item.is_completed ? 'line-through' : 'none', opacity: item.is_completed ? 0.5 : 1}}>
                  {item.title}
                </div>
                <div className="helper-text">
                  {new Date(item.due_date).toLocaleString()}
                  {item.amount ? ` · ${item.amount}` : ''}
                  {item.recurrence !== 'none' ? ` · repeats ${item.recurrence}` : ''}
                </div>
              </div>
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
              <TypeBadge type={item.item_type} />
              <UrgencyBadge dueDate={item.due_date} isCompleted={item.is_completed} />
              <button className="btn btn-small btn-danger" onClick={() => handleDelete(item.id)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  )
}
