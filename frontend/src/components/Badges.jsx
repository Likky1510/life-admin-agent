export function TypeBadge({ type }) {
  if (!type) return null
  return <span className={`badge badge-${type}`}>{type}</span>
}

export function UrgencyBadge({ dueDate, isCompleted }) {
  if (isCompleted) return null
  const now = new Date()
  const due = new Date(dueDate)
  const hoursLeft = (due - now) / (1000 * 60 * 60)

  if (hoursLeft < 0) return <span className="badge badge-overdue">overdue</span>
  if (hoursLeft <= 48) return <span className="badge badge-soon">due soon</span>
  return null
}

export function SkillTag({ skill }) {
  return <span className="skill-tag">{skill}</span>
}
