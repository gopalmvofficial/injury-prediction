import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Athletes from './pages/Athletes.jsx'
import AthleteProfile from './pages/AthleteProfile.jsx'
import VideoAnalysis from './pages/VideoAnalysis.jsx'
import Results from './pages/Results.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import { getToken } from './services/api.js'

function RequireAuth({ children }) {
  if (!getToken()) {
    return <Navigate to="/login" replace />
  }
  return children
}

function AppLayout({ children }) {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/"
        element={
          <RequireAuth>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/athletes"
        element={
          <RequireAuth>
            <AppLayout>
              <Athletes />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/athletes/:athleteId"
        element={
          <RequireAuth>
            <AppLayout>
              <AthleteProfile />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/analyze"
        element={
          <RequireAuth>
            <AppLayout>
              <VideoAnalysis />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/results/:analysisId"
        element={
          <RequireAuth>
            <AppLayout>
              <Results />
            </AppLayout>
          </RequireAuth>
        }
      />
    </Routes>
  )
}
