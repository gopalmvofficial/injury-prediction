import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { createAthlete, listAthletes, deleteAthlete } from '../services/api.js'

const emptyForm = {
  name: '', age: '', sport: '', position: '', height_cm: '', weight_kg: '',
  injury_history: '', training_load: '',
}

export default function Athletes() {
  const [athletes, setAthletes] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)
  const [showForm, setShowForm] = useState(false)

  function refresh() {
    listAthletes().then(setAthletes).catch((e) => setError(e.message))
  }

  useEffect(refresh, [])

  function updateField(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setSuccessMsg(null)

    if (!form.name.trim() || !form.age || !form.sport.trim()) {
      setError('Name, age, and sport are required.')
      return
    }

    setSubmitting(true)
    try {
      const payload = {
        name: form.name.trim(),
        age: Number(form.age),
        sport: form.sport.trim(),
        position: form.position.trim() || null,
        height_cm: form.height_cm ? Number(form.height_cm) : null,
        weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
        injury_history: form.injury_history.trim() || null,
        training_load: form.training_load.trim() || null,
      }
      const created = await createAthlete(payload)
      setSuccessMsg(`Athlete "${created.name}" created.`)
      setForm(emptyForm)
      setShowForm(false)
      refresh()
    } catch (e) {
      setError(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(athleteId, name) {
    if (!window.confirm(`Delete athlete "${name}"? This also removes their videos and analyses.`)) return
    try {
      await deleteAthlete(athleteId)
      refresh()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Athlete Profiles</h1>
          <p className="text-slate-500 mt-1">Create and manage athlete profiles used for video analysis.</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Cancel' : 'Add Athlete'}
        </button>
      </div>

      {error && <p className="text-sm text-rose-600 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">{error}</p>}
      {successMsg && (
        <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">{successMsg}</p>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-4">
          <h2 className="font-semibold text-slate-900">New athlete</h2>
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="label">Athlete name *</label>
              <input className="input" value={form.name} onChange={(e) => updateField('name', e.target.value)} />
            </div>
            <div>
              <label className="label">Age *</label>
              <input type="number" className="input" value={form.age} onChange={(e) => updateField('age', e.target.value)} />
            </div>
            <div>
              <label className="label">Sport *</label>
              <input className="input" value={form.sport} onChange={(e) => updateField('sport', e.target.value)} />
            </div>
            <div>
              <label className="label">Position</label>
              <input className="input" value={form.position} onChange={(e) => updateField('position', e.target.value)} />
            </div>
            <div>
              <label className="label">Training load</label>
              <input className="input" value={form.training_load} onChange={(e) => updateField('training_load', e.target.value)} placeholder="e.g. Moderate" />
            </div>
            <div>
              <label className="label">Height (cm)</label>
              <input type="number" className="input" value={form.height_cm} onChange={(e) => updateField('height_cm', e.target.value)} />
            </div>
            <div>
              <label className="label">Weight (kg)</label>
              <input type="number" className="input" value={form.weight_kg} onChange={(e) => updateField('weight_kg', e.target.value)} />
            </div>
            <div className="col-span-2">
              <label className="label">Injury history</label>
              <textarea className="input" rows={2} value={form.injury_history} onChange={(e) => updateField('injury_history', e.target.value)} />
            </div>
          </div>
          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? 'Creating...' : 'Create athlete'}
          </button>
        </form>
      )}

      <div className="card">
        <h2 className="font-semibold text-slate-900 mb-3">All athletes ({athletes.length})</h2>
        {athletes.length === 0 ? (
          <p className="text-sm text-slate-400">No athletes yet — click "Add Athlete" above.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-400 text-xs uppercase border-b border-slate-200">
                  <th className="py-2 pr-2">ID</th>
                  <th className="py-2 pr-2">Athlete</th>
                  <th className="py-2 pr-2">Age</th>
                  <th className="py-2 pr-2">Sport</th>
                  <th className="py-2 pr-2">Weight</th>
                  <th className="py-2 pr-2">Injury History</th>
                  <th className="py-2 pr-2">Created</th>
                  <th className="py-2 pr-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {athletes.map((a) => (
                  <tr key={a.athlete_id} className="border-b border-slate-100 last:border-0">
                    <td className="py-2 pr-2 font-mono text-xs text-slate-500">{a.athlete_id}</td>
                    <td className="py-2 pr-2 text-slate-800">{a.name}</td>
                    <td className="py-2 pr-2 text-slate-600">{a.age}</td>
                    <td className="py-2 pr-2 text-slate-600">{a.sport}</td>
                    <td className="py-2 pr-2 text-slate-600">{a.weight_kg ? `${a.weight_kg} kg` : '—'}</td>
                    <td className="py-2 pr-2 text-slate-600 max-w-[160px] truncate">{a.injury_history || '—'}</td>
                    <td className="py-2 pr-2 text-slate-400 text-xs">{new Date(a.created_at).toLocaleDateString()}</td>
                    <td className="py-2 pr-2">
                      <div className="flex gap-2">
                        <Link to={`/athletes/${a.athlete_id}`} className="text-brand-600 text-xs font-medium">
                          View
                        </Link>
                        <button
                          onClick={() => handleDelete(a.athlete_id, a.name)}
                          className="text-rose-600 text-xs font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
