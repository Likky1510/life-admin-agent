import { useEffect, useState, useRef } from 'react'
import Layout from '../components/Layout'
import { assistantApi } from '../api/client'

export default function Assistant() {
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const chatWindowRef = useRef(null)

  useEffect(() => {
    assistantApi.history().then(res => setMessages(res.data))
  }, [])

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight
    }
  }, [messages])

  async function handleSend(e) {
    e.preventDefault()
    if (!draft.trim()) return
    const userMessage = draft
    setDraft('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage, created_at: new Date().toISOString() }])
    setSending(true)
    try {
      const res = await assistantApi.chat(userMessage)
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply, created_at: new Date().toISOString() }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.', created_at: new Date().toISOString() }])
    } finally {
      setSending(false)
    }
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Module 5</div>
          <h2>AI Assistant</h2>
        </div>
      </div>

      <div className="card">
        <div className="chat-window" ref={chatWindowRef}>
          {messages.length === 0 && (
            <p className="helper-text">Ask me anything -- about your tasks, deadlines, or what to focus on today.</p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.role}`}>{m.content}</div>
          ))}
          {sending && <div className="chat-bubble assistant">Thinking…</div>}
        </div>

        <form onSubmit={handleSend} style={{display: 'flex', gap: 10}}>
          <input
            value={draft} onChange={e => setDraft(e.target.value)}
            placeholder="Type a message…" disabled={sending}
          />
          <button className="btn" type="submit" disabled={sending}>Send</button>
        </form>
      </div>
    </Layout>
  )
}
