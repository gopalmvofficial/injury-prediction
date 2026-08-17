import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboardSummary, healthCheck } from '../services/api.js'
import { StatCard, ClassificationBadge } from '../components/StatCard.jsx'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [backendStatus, setBackendStatus] = useState('checking')
  const [error, setError] = useState(null)

  useEffect(() => {
    healthCheck()
      .then(() => setBackendStatus('online'))
      .catch(() => setBackendStatus('offline'))

    getDashboardSummary()
      .then(setSummary)
      .catch((e) => setError(e.message))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
        <p className="text-slate-500 mt-1">
          Sports Injury Risk Detection and Prevention System — Milestone 2: Pose Estimation &amp;
          Biomechanical Analysis.
        </p>
      </div>

      {backendStatus === 'offline' && (
        <div className="rounded-lg bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 text-sm">
          Backend is unreachable. Start it with <code className="font-mono">uvicorn app.main:app --reload</code>{' '}
          in the <code className="font-mono">backend/</code> folder.
        </div>
      )}
      {error && <p className="text-sm text-rose-600">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <StatCard label="Total athletes" value={summary?.total_athletes ?? '—'} />
        <StatCard label="Total videos" value={summary?.total_videos ?? '—'} />
        <StatCard label="Total analyses" value={summary?.total_analyses ?? '—'} />
        <StatCard label="High-risk athletes" value={summary?.high_risk_athletes ?? '—'} />
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card">
            <h2 className="font-semibold text-slate-900 mb-3">Risk-level distribution</h2>
            {summary.total_analyses === 0 ? (
              <p className="text-sm text-slate-400">No analyses yet.</p>
            ) : (
              <div className="space-y-2">
                {Object.entries(summary.risk_distribution || {}).map(([level, count]) => (
                  <div key={level} className="flex items-center justify-between text-sm">
                    <ClassificationBadge
                      classification={level === 'LOW' ? 'Good' : level === 'MEDIUM' ? 'Moderate' : level === 'HIGH' ? 'Needs Attention' : null}
                    />
                    <span className="text-slate-700 font-medium">{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <h2 className="font-semibold text-slate-900 mb-3">Recent athletes</h2>
            {summary.recent_athletes.length === 0 ? (
              <p className="text-sm text-slate-400">
                No athletes yet.{' '}
                <Link to="/athletes" className="text-brand-600 font-medium">
                  Add one
                </Link>
                .
              </p>
            ) : (
              <ul className="divide-y divide-slate-100">
                {summary.recent_athletes.map((a) => (
                  <li key={a.athlete_id} className="py-2 flex justify-between text-sm">
                    <Link to={`/athletes/${a.athlete_id}`} className="text-slate-700 hover:text-brand-600">
                      {a.name}
                    </Link>
                    <span className="text-slate-400">{a.sport}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      <div className="card">
        <h2 className="font-semibold text-slate-900 mb-2">Get started</h2>
        <ol className="list-decimal list-inside text-sm text-slate-600 space-y-1">
          <li>
            Create an athlete profile on the{' '}
            <Link to="/athletes" className="text-brand-600 font-medium">
              Athletes
            </Link>{' '}
            page.
          </li>
          <li>
            Upload and analyze a movement video on the{' '}
            <Link to="/analyze" className="text-brand-600 font-medium">
              Video Analysis
            </Link>{' '}
            page.
          </li>
          <li>Review biomechanics, movement quality, the risk indicator, recommendations, and the PDF report.</li>
        </ol>
      </div>
    </div>
  )
}
