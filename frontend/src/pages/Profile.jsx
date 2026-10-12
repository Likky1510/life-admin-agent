import { useState } from 'react'
import Layout from '../components/Layout'
import { useAuth } from '../api/AuthContext'
import { authApi } from '../api/client'
import { SkillTag } from '../components/Badges'

function TagInput({ label, values, onChange, placeholder }) {
  const [draft, setDraft] = useState('')

  function addTag(e) {
    e.preventDefault()
    if (draft.trim() && !values.includes(draft.trim())) {
      onChange([...values, draft.trim()])
      setDraft('')
    }
  }

  function removeTag(tag) {
    onChange(values.filter(v => v !== tag))
  }

  return (
    <div className="field">
      <label>{label}</label>
      <div style={{marginBottom: 8}}>
        {values.map(v => (
          <span key={v} style={{cursor: 'pointer'}} onClick={() => removeTag(v)}>
            <SkillTag skill={`${v} ×`} />
          </span>
        ))}
      </div>
      <form onSubmit={addTag} style={{display: 'flex', gap: 8}}>
        <input value={draft} onChange={e => setDraft(e.target.value)} placeholder={placeholder} />
        <button className="btn btn-small btn-secondary" type="submit">Add</button>
      </form>
    </div>
  )
}

export default function Profile() {
  const { user, updateLocalUser } = useAuth()
  const [interests, setInterests] = useState(user?.interests || [])
  const [qualifications, setQualifications] = useState(user?.qualifications || [])
  const [careerGoals, setCareerGoals] = useState(user?.career_goals || [])
  const [saved, setSaved] = useState(false)

  async function handleSave() {
    const res = await authApi.updateProfile({
      interests, qualifications, career_goals: careerGoals,
    })
    updateLocalUser(res.data)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Module 1</div>
          <h2>Profile</h2>
        </div>
      </div>

      <div className="card">
        <p className="helper-text" style={{marginBottom: 16}}>
          These details power your Opportunity Discovery matches and the AI Assistant's recommendations.
        </p>

        <TagInput label="Interests" values={interests} onChange={setInterests} placeholder="e.g. machine learning" />
        <TagInput label="Qualifications" values={qualifications} onChange={setQualifications} placeholder="e.g. B.Tech CSE" />
        <TagInput label="Career Goals" values={careerGoals} onChange={setCareerGoals} placeholder="e.g. data scientist" />

        <button className="btn" onClick={handleSave}>Save Profile</button>
        {saved && <span className="helper-text" style={{marginLeft: 10, color: 'var(--sage)'}}>Saved!</span>}
      </div>
    </Layout>
  )
}
