import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getAthlete, listAthleteVideos, listAthleteAnalyses, getRiskHistory } from '../services/api.js'
import { StatCard, ClassificationBadge } from '../components/StatCard.jsx'

const riskBadgeMap = { LOW: 'Good', MEDIUM: 'Moderate', HIGH: 'Needs Attention' }

export default function AthleteProfile() {
  const { athleteId } = useParams()
  const [athlete, setAthlete] = useState(null)
  const [videos, setVideos] = useState([])
  const [analyses, setAnalyses] = useState([])
  const [riskHistory, setRiskHistory] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    getAthlete(athleteId).then(setAthlete).catch((e) => setError(e.message))
    listAthleteVideos(athleteId).then(setVideos).catch(() => {})
    listAthleteAnalyses(athleteId).then(setAnalyses).catch(() => {})
    getRiskHistory(athleteId).then(setRiskHistory).catch(() => {})
  }, [athleteId])

  if (error) {
    return (
      <div className="card max-w-lg">
        <p className="text-rose-600 text-sm">{error}</p>
        <Link to="/athletes" className="text-brand-600 text-sm font-medium mt-3 inline-block">
          &larr; Back to Athletes
        </Link>
      </div>
    )
  }

  if (!athlete) {
    return <p className="text-slate-500 text-sm">Loading athlete...</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">{athlete.name}</h1>
          <p className="text-slate-500 mt-1">
            {athlete.sport} {athlete.position ? `· ${athlete.position}` : ''} · Age {athlete.age}
          </p>
        </div>
        <Link to="/analyze" className="btn-primary">
          Analyze new video
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <StatCard label="Height" value={athlete.height_cm ? `${athlete.height_cm} cm` : 'N/A'} />
        <StatCard label="Weight" value={athlete.weight_kg ? `${athlete.weight_kg} kg` : 'N/A'} />
        <StatCard label="Videos" value={videos.length} />
        <StatCard label="Analyses" value={analyses.length} />
      </div>

      {athlete.injury_history && (
        <div className="card">
          <h2 className="font-semibold text-slate-900 mb-1">Injury history</h2>
          <p className="text-sm text-slate-600">{athlete.injury_history}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold text-slate-900 mb-3">Uploaded videos</h2>
          {videos.length === 0 ? (
            <p className="text-sm text-slate-400">No videos uploaded yet.</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {videos.map((v) => (
                <li key={v.video_id} className="py-2 text-sm flex justify-between">
                  <span className="text-slate-700">{v.activity}</span>
                  <span className="text-slate-400 text-xs">{v.processing_status}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card">
          <h2 className="font-semibold text-slate-900 mb-3">Risk history</h2>
          {riskHistory.length === 0 ? (
            <p className="text-sm text-slate-400">No risk results yet.</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {riskHistory.map((r) => (
                <li key={r.risk_id} className="py-2 text-sm flex justify-between items-center">
                  <span className="text-slate-400 text-xs">{new Date(r.created_at).toLocaleDateString()}</span>
                  <ClassificationBadge classification={riskBadgeMap[r.risk_level] || null} />
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="font-semibold text-slate-900 mb-3">Movement analyses</h2>
        {analyses.length === 0 ? (
          <p className="text-sm text-slate-400">No analyses yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 text-xs uppercase border-b border-slate-200">
                <th className="py-2">Activity</th>
                <th className="py-2">Status</th>
                <th className="py-2">Quality score</th>
                <th className="py-2">Date</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((a) => (
                <tr key={a.analysis_id} className="border-b border-slate-100 last:border-0">
                  <td className="py-2 text-slate-800">{a.activity}</td>
                  <td className="py-2 text-slate-600">{a.status}</td>
                  <td className="py-2 text-slate-600">
                    {a.movement_quality?.score != null ? `${a.movement_quality.score}/100` : '—'}
                  </td>
                  <td className="py-2 text-slate-400 text-xs">{new Date(a.created_at).toLocaleDateString()}</td>
                  <td className="py-2">
                    {a.status === 'completed' && (
                      <Link to={`/results/${a.analysis_id}`} className="text-brand-600 text-xs font-medium">
                        View results
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
