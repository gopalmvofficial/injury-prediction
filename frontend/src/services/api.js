import axios from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5 * 60 * 1000, // video analysis can take a while; don't time out too eagerly
})

const TOKEN_KEY = 'sirdps_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

client.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Normalizes axios/network errors into a plain message the UI can show directly.
function friendlyError(error) {
  if (error.response) {
    const detail = error.response.data?.detail
    return typeof detail === 'string' ? detail : JSON.stringify(detail || error.response.statusText)
  }
  if (error.request) {
    return `Could not reach the backend at ${API_BASE_URL}. Is it running? (uvicorn app.main:app --reload)`
  }
  return error.message || 'Unknown error'
}

export async function healthCheck() {
  const res = await client.get('/api/health')
  return res.data
}

// --- Auth ---------------------------------------------------------------

export async function registerUser({ name, email, password }) {
  try {
    const res = await client.post('/api/auth/register', { name, email, password })
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function loginUser({ email, password }) {
  try {
    const res = await client.post('/api/auth/login', { email, password })
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function getCurrentUser() {
  try {
    const res = await client.get('/api/auth/me')
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

// --- Athletes -------------------------------------------------------------

export async function createAthlete(payload) {
  try {
    const res = await client.post('/api/athletes', payload)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function listAthletes() {
  try {
    const res = await client.get('/api/athletes')
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function getAthlete(athleteId) {
  try {
    const res = await client.get(`/api/athletes/${athleteId}`)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function updateAthlete(athleteId, payload) {
  try {
    const res = await client.put(`/api/athletes/${athleteId}`, payload)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function deleteAthlete(athleteId) {
  try {
    const res = await client.delete(`/api/athletes/${athleteId}`)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function listAthleteVideos(athleteId) {
  try {
    const res = await client.get(`/api/athletes/${athleteId}/videos`)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function listAthleteAnalyses(athleteId) {
  try {
    const res = await client.get(`/api/athletes/${athleteId}/analyses`)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

// --- Videos / Analysis ------------------------------------------------

export async function uploadVideo({ athleteId, activity, file, onUploadProgress }) {
  const form = new FormData()
  form.append('athlete_id', athleteId)
  form.append('activity', activity)
  form.append('file', file)
  try {
    const res = await client.post('/api/videos/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (evt) => {
        if (onUploadProgress && evt.total) {
          onUploadProgress(Math.round((evt.loaded / evt.total) * 100))
        }
      },
    })
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function analyzeVideo({ videoId, athleteId, activity }) {
  try {
    const res = await client.post('/api/videos/analyze', {
      video_id: videoId,
      athlete_id: athleteId,
      activity,
    })
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function getAnalysis(analysisId) {
  try {
    const res = await client.get(`/api/analysis/${analysisId}`)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

// --- Risk -----------------------------------------------------------------

export async function getRiskForAnalysis(analysisId) {
  try {
    const res = await client.get(`/api/risk/${analysisId}`)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export async function getRiskHistory(athleteId) {
  try {
    const res = await client.get(`/api/athletes/${athleteId}/risk-history`)
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

// --- Dashboard --------------------------------------------------------

export async function getDashboardSummary() {
  try {
    const res = await client.get('/api/dashboard/summary')
    return res.data
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}

export function processedVideoUrl(processedVideoPath) {
  if (!processedVideoPath) return null
  return `${API_BASE_URL}${processedVideoPath}`
}

export function reportUrl(analysisId) {
  return `${API_BASE_URL}/api/reports/${analysisId}`
}

// Report downloads now require auth (Authorization header), which a plain
// <a href> link can't send - fetch as a blob instead and trigger the
// save-as manually.
export async function downloadReport(analysisId) {
  try {
    const res = await client.get(`/api/reports/${analysisId}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${analysisId}_biomechanics_report.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    throw new Error(friendlyError(e))
  }
}
