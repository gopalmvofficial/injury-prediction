import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getAnalysis, getRiskForAnalysis, processedVideoUrl, downloadReport } from '../services/api.js'
import { StatCard, ClassificationBadge, JointAngleRow } from '../components/StatCard.jsx'

const riskBadgeMap = { LOW: 'Good', MEDIUM: 'Moderate', HIGH: 'Needs Attention' }

export default function Results() {
  const { analysisId } = useParams()
  const [analysis, setAnalysis] = useState(null)
  const [risk, setRisk] = useState(null)
  const [error, setError] = useState(null)
  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState(null)

  useEffect(() => {
    getAnalysis(analysisId).then(setAnalysis).catch((e) => setError(e.message))
    getRiskForAnalysis(analysisId).then(setRisk).catch(() => {})
  }, [analysisId])

  async function handleDownload() {
    setDownloading(true)
    setDownloadError(null)
    try {
      await downloadReport(analysisId)
    } catch (e) {
      setDownloadError(e.message)
    } finally {
      setDownloading(false)
    }
  }

  if (error) {
    return (
      <div className="card max-w-lg">
        <p className="text-rose-600 text-sm">{error}</p>
        <Link to="/analyze" className="text-brand-600 text-sm font-medium mt-3 inline-block">
          &larr; Back to Video Analysis
        </Link>
      </div>
    )
  }

  if (!analysis) {
    return <p className="text-slate-500 text-sm">Loading results...</p>
  }

  const bio = analysis.biomechanics || {}
  const quality = analysis.movement_quality || {}
  const videoSrc = processedVideoUrl(analysis.processed_video_path)

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Analysis Results</h1>
          <p className="text-slate-500 mt-1">
            Activity: <span className="font-medium">{analysis.activity}</span> &middot; Analysis ID:{' '}
            <span className="font-mono text-xs">{analysis.analysis_id}</span>
          </p>
        </div>
        <div className="text-right">
          <button className="btn-primary" onClick={handleDownload} disabled={downloading}>
            {downloading ? 'Preparing PDF...' : 'Download PDF report'}
          </button>
          {downloadError && <p className="text-xs text-rose-600 mt-1">{downloadError}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <StatCard label="Movement quality" value={quality.score != null ? `${quality.score}/100` : 'N/A'} />
        <div className="card flex flex-col justify-center items-start">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-2">Classification</p>
          <ClassificationBadge classification={quality.classification} />
        </div>
        <StatCard label="Frames processed" value={analysis.frames_total} />
        <StatCard
          label="Pose detection rate"
          value={analysis.pose_detection_rate_pct != null ? `${analysis.pose_detection_rate_pct}%` : 'N/A'}
        />
      </div>

      {risk && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-slate-900">Injury Risk Indicator</h2>
            <ClassificationBadge classification={riskBadgeMap[risk.risk_level] || null} />
          </div>
          <p className="text-xs text-slate-400 mb-3">
            Rule-based placeholder — not a trained ML model, not a medical diagnosis.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">Risk score</p>
              <p className="text-xl font-semibold text-slate-900">
                {risk.risk_score != null ? `${risk.risk_score}/100` : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">Contributing factors</p>
              <ul className="text-sm text-slate-700 space-y-1">
                {risk.contributing_factors.map((f, i) => (
                  <li key={i}>• {f}</li>
                ))}
              </ul>
            </div>
          </div>
          {risk.recommendations?.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-2">Preventive recommendations</p>
              <ul className="text-sm text-slate-700 space-y-1">
                {risk.recommendations.map((r, i) => (
                  <li key={i}>• {r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold text-slate-900 mb-3">Joint angles &amp; range of motion</h2>
          <table className="w-full">
            <thead>
              <tr className="text-left text-slate-400 text-xs uppercase border-b border-slate-200">
                <th className="py-2">Joint</th>
                <th className="py-2 text-center">Min</th>
                <th className="py-2 text-center">Max</th>
                <th className="py-2 text-center">ROM</th>
              </tr>
            </thead>
            <tbody>
              <JointAngleRow label="Left knee" joint={bio.left_knee} />
              <JointAngleRow label="Right knee" joint={bio.right_knee} />
              <JointAngleRow label="Left hip" joint={bio.left_hip} />
              <JointAngleRow label="Right hip" joint={bio.right_hip} />
              <JointAngleRow label="Left elbow" joint={bio.left_elbow} />
              <JointAngleRow label="Right elbow" joint={bio.right_elbow} />
            </tbody>
          </table>
        </div>

        <div className="card space-y-3">
          <h2 className="font-semibold text-slate-900">Symmetry &amp; posture</h2>
          <div className="grid grid-cols-2 gap-3">
            <StatCard label="Knee symmetry" value={bio.knee_symmetry_pct != null ? `${bio.knee_symmetry_pct}%` : 'N/A'} />
            <StatCard label="Hip symmetry" value={bio.hip_symmetry_pct != null ? `${bio.hip_symmetry_pct}%` : 'N/A'} />
            <StatCard
              label="Trunk lean (avg)"
              value={bio.trunk?.mean_lean_angle != null ? `${bio.trunk.mean_lean_angle}°` : 'N/A'}
            />
            <StatCard
              label="Movement consistency"
              value={bio.movement_consistency_pct != null ? `${bio.movement_consistency_pct}%` : 'N/A'}
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold text-slate-900 mb-3">Processed video (skeleton overlay)</h2>
          {videoSrc ? (
            <video src={videoSrc} controls className="w-full rounded-lg bg-black max-h-96" />
          ) : (
            <p className="text-sm text-slate-400">Processed video not available.</p>
          )}
        </div>

        <div className="card">
          <h2 className="font-semibold text-slate-900 mb-3">Observations</h2>
          {analysis.observations?.length ? (
            <ul className="space-y-2">
              {analysis.observations.map((o, i) => (
                <li key={i} className="text-sm text-slate-700 flex gap-2">
                  <span className="text-brand-500 mt-0.5">&bull;</span>
                  <span>{o}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-400">No observations available.</p>
          )}
          <p className="text-xs text-slate-400 mt-4 border-t border-slate-100 pt-3">
            This is a movement-quality assessment prototype. It is not a medical diagnosis.
          </p>
        </div>
      </div>
    </div>
  )
}
