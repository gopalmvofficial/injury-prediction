export function StatCard({ label, value, sub }) {
  return (
    <div className="card">
      <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-semibold text-slate-900 mt-1">{value ?? 'N/A'}</p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </div>
  )
}

const classificationColors = {
  Excellent: 'bg-emerald-100 text-emerald-700',
  Good: 'bg-blue-100 text-blue-700',
  Moderate: 'bg-amber-100 text-amber-700',
  'Needs Attention': 'bg-rose-100 text-rose-700',
}

export function ClassificationBadge({ classification }) {
  if (!classification) {
    return <span className="px-2 py-1 rounded-full text-xs bg-slate-100 text-slate-500">Not available</span>
  }
  const cls = classificationColors[classification] || 'bg-slate-100 text-slate-600'
  return <span className={`px-2 py-1 rounded-full text-xs font-medium ${cls}`}>{classification}</span>
}

export function JointAngleRow({ label, joint }) {
  if (!joint || joint.available === false || joint.range_of_motion == null) {
    return (
      <tr className="border-b border-slate-100 last:border-0">
        <td className="py-2 text-sm text-slate-600">{label}</td>
        <td className="py-2 text-sm text-slate-400 text-center" colSpan={3}>
          Not available
        </td>
      </tr>
    )
  }
  return (
    <tr className="border-b border-slate-100 last:border-0">
      <td className="py-2 text-sm text-slate-600">{label}</td>
      <td className="py-2 text-sm text-slate-900 text-center">{joint.min_angle}°</td>
      <td className="py-2 text-sm text-slate-900 text-center">{joint.max_angle}°</td>
      <td className="py-2 text-sm font-medium text-brand-700 text-center">{joint.range_of_motion}°</td>
    </tr>
  )
}
