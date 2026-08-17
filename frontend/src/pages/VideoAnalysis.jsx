import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listAthletes, uploadVideo, analyzeVideo } from '../services/api.js'

const ACTIVITIES = [
  { value: 'squat', label: 'Squatting' },
  { value: 'running', label: 'Running' },
  { value: 'jumping_landing', label: 'Jumping / Landing' },
]

export default function VideoAnalysis() {
  const navigate = useNavigate()
  const [athletes, setAthletes] = useState([])
  const [athleteId, setAthleteId] = useState('')
  const [activity, setActivity] = useState('squat')
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [dragActive, setDragActive] = useState(false)

  const [uploadProgress, setUploadProgress] = useState(0)
  const [stage, setStage] = useState('idle') // idle | uploading | processing | error
  const [errorMsg, setErrorMsg] = useState(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    listAthletes().then(setAthletes).catch(() => {})
  }, [])

  function handleFile(selected) {
    if (!selected) return
    setFile(selected)
    setPreviewUrl(URL.createObjectURL(selected))
    setErrorMsg(null)
  }

  function onDrop(e) {
    e.preventDefault()
    setDragActive(false)
    const dropped = e.dataTransfer.files?.[0]
    handleFile(dropped)
  }

  async function handleAnalyze() {
    setErrorMsg(null)
    if (!athleteId) {
      setErrorMsg('Select an athlete first.')
      return
    }
    if (!file) {
      setErrorMsg('Choose a video file to upload.')
      return
    }

    try {
      setStage('uploading')
      setUploadProgress(0)
      const uploadResult = await uploadVideo({
        athleteId,
        activity,
        file,
        onUploadProgress: setUploadProgress,
      })

      setStage('processing')
      const analysis = await analyzeVideo({
        videoId: uploadResult.video_id,
        athleteId,
        activity,
      })

      navigate(`/results/${analysis.analysis_id}`)
    } catch (e) {
      setErrorMsg(e.message)
      setStage('error')
    }
  }

  const isBusy = stage === 'uploading' || stage === 'processing'

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Video Analysis</h1>
        <p className="text-slate-500 mt-1">Upload a movement video to run pose estimation and biomechanical analysis.</p>
      </div>

      <div className="card space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Athlete</label>
            <select className="input" value={athleteId} onChange={(e) => setAthleteId(e.target.value)}>
              <option value="">Select athlete...</option>
              {athletes.map((a) => (
                <option key={a.athlete_id} value={a.athlete_id}>
                  {a.name} ({a.sport})
                </option>
              ))}
            </select>
            {athletes.length === 0 && (
              <p className="text-xs text-amber-600 mt-1">No athletes found — create one on the Athletes page first.</p>
            )}
          </div>
          <div>
            <label className="label">Activity</label>
            <select className="input" value={activity} onChange={(e) => setActivity(e.target.value)}>
              {ACTIVITIES.map((a) => (
                <option key={a.value} value={a.value}>
                  {a.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="label">Video file</label>
          <div
            onDragOver={(e) => {
              e.preventDefault()
              setDragActive(true)
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-colors ${
              dragActive ? 'border-brand-500 bg-brand-50' : 'border-slate-300 hover:border-slate-400'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/quicktime,video/x-msvideo,video/webm,.mp4,.mov,.avi,.mkv,.webm"
              className="hidden"
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
            {file ? (
              <p className="text-sm text-slate-700">
                <span className="font-medium">{file.name}</span> ({(file.size / (1024 * 1024)).toFixed(1)} MB)
              </p>
            ) : (
              <p className="text-sm text-slate-500">
                Drag and drop a video here, or <span className="text-brand-600 font-medium">click to browse</span>
                <br />
                <span className="text-xs text-slate-400">MP4, MOV, AVI, MKV, WEBM — up to 300 MB</span>
              </p>
            )}
          </div>
        </div>

        {previewUrl && (
          <video src={previewUrl} controls className="w-full rounded-lg max-h-80 bg-black" />
        )}

        {errorMsg && (
          <p className="text-sm text-rose-600 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">{errorMsg}</p>
        )}

        {stage === 'uploading' && (
          <div>
            <p className="text-xs text-slate-500 mb-1">Uploading... {uploadProgress}%</p>
            <div className="w-full bg-slate-100 rounded-full h-2">
              <div className="bg-brand-600 h-2 rounded-full transition-all" style={{ width: `${uploadProgress}%` }} />
            </div>
          </div>
        )}

        {stage === 'processing' && (
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <span className="w-4 h-4 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
            Processing video — running pose estimation and biomechanical analysis. This can take a
            while depending on video length.
          </div>
        )}

        <button className="btn-primary w-full" disabled={isBusy} onClick={handleAnalyze}>
          {isBusy ? 'Working...' : 'Analyze video'}
        </button>
      </div>
    </div>
  )
}
