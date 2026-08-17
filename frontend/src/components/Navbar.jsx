import { NavLink, useNavigate } from 'react-router-dom'
import { clearToken } from '../services/api.js'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/athletes', label: 'Athletes' },
  { to: '/analyze', label: 'Video Analysis' },
]

export default function Navbar() {
  const navigate = useNavigate()

  function handleLogout() {
    clearToken()
    navigate('/login')
  }

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold">
            S
          </div>
          <div>
            <p className="font-semibold text-slate-900 leading-tight">Sports Injury Risk Detection</p>
            <p className="text-xs text-slate-400 leading-tight">Milestone 2 &middot; Pose &amp; Biomechanics</p>
          </div>
        </div>
        <nav className="flex items-center gap-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/'}
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:bg-slate-100'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
          <button
            onClick={handleLogout}
            className="ml-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-100 transition-colors"
          >
            Log out
          </button>
        </nav>
      </div>
    </header>
  )
}
