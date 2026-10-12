import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../api/AuthContext'

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">Life Admin Agent</div>
        <div className="brand-sub">Your AI Assistant</div>

        <nav>
          <NavLink to="/dashboard" className={({isActive}) => isActive ? 'active' : ''}>Dashboard</NavLink>
          <NavLink to="/tasks" className={({isActive}) => isActive ? 'active' : ''}>Life Admin</NavLink>
          <NavLink to="/opportunities" className={({isActive}) => isActive ? 'active' : ''}>Opportunities</NavLink>
          <NavLink to="/assistant" className={({isActive}) => isActive ? 'active' : ''}>AI Assistant</NavLink>
          <NavLink to="/notifications" className={({isActive}) => isActive ? 'active' : ''}>Notifications</NavLink>
          <NavLink to="/analytics" className={({isActive}) => isActive ? 'active' : ''}>Analytics</NavLink>
          <NavLink to="/profile" className={({isActive}) => isActive ? 'active' : ''}>Profile</NavLink>
        </nav>

        <div className="user-tag">
          <div>{user?.name}</div>
          <a href="#" onClick={handleLogout} style={{color: '#c3dac8', display: 'block', marginTop: 8}}>
            Sign out
          </a>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  )
}
