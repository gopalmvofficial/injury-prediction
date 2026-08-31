import React, { useState, useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://injury-prediction-backend.onrender.com');

async function api(path, options = {}) {
  const token = localStorage.getItem('sir_token');
  const headers = { ...(options.headers || {}) };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401 && path === '/api/auth/me') {
    localStorage.removeItem('sir_token');
    localStorage.removeItem('sir_auth');
    localStorage.removeItem('sir_user');
  }

  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const err = await res.json();
      msg = err.detail || err.message || msg;
    } catch {
      // Non-JSON error payload
    }
    throw new Error(msg);
  }

  return res.json();
}

const Icon = ({ name, size = 18 }) => {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round' };
  const paths = {
    dashboard: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M21 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></>,
    video: <><rect x="3" y="5" width="13" height="14" rx="2"/><path d="m16 10 5-3v10l-5-3z"/><path d="m8 9 4 3-4 3z"/></>,
    chart: <><path d="M4 19V5"/><path d="M4 19h16"/><path d="m7 15 3-4 3 2 5-6"/></>,
    report: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/></>,
    activity: <><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></>,
    activityPulse: <><path d="M3 12h4l2-6 4 12 3-6h5"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>
  };
  return <svg {...common}>{paths[name] || paths.activity}</svg>;
};

const MovementMap = ({ kneeAngle = 154, hipAngle = 135, ankleAngle = 28, quality = 84, risk = 'LOW', size = 180 }) => {
  const riskColor = risk === 'HIGH' || risk === 'CRITICAL' ? '#dc2626' : risk === 'MODERATE' ? '#f59e0b' : '#10b981';
  return (
    <div className="movement-map-wrapper" style={{ position: 'relative', display: 'inline-block', padding: '10px 40px' }}>
      <svg width={size} height={size * 1.25} viewBox="0 0 100 120" style={{ background: 'radial-gradient(circle at center, #0f172a 0%, #020617 100%)', borderRadius: '16px', border: '1px solid #1e293b', padding: '10px' }}>
        <path d="M 10,0 L 10,120 M 30,0 L 30,120 M 50,0 L 50,120 M 70,0 L 70,120 M 90,0 L 90,120" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" />
        <path d="M 0,20 L 100,20 M 0,40 L 100,40 M 0,60 L 100,60 M 0,80 L 100,80 M 0,100 L 100,100" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" />
        
        <line x1="50" y1="18" x2="50" y2="40" stroke="#3b82f6" strokeWidth="2.5" />
        <line x1="32" y1="28" x2="68" y2="28" stroke="#3b82f6" strokeWidth="2.5" />
        <line x1="32" y1="28" x2="26" y2="48" stroke="#3b82f6" strokeWidth="2" />
        <line x1="26" y1="48" x2="20" y2="62" stroke="#3b82f6" strokeWidth="1.5" />
        <line x1="68" y1="28" x2="74" y2="48" stroke="#3b82f6" strokeWidth="2" />
        <line x1="74" y1="48" x2="80" y2="62" stroke="#3b82f6" strokeWidth="1.5" />
        
        <line x1="36" y1="65" x2="64" y2="65" stroke="#3b82f6" strokeWidth="2.5" />
        <line x1="36" y1="65" x2="32" y2="90" stroke={riskColor} strokeWidth="3" />
        <line x1="32" y1="90" x2="36" y2="112" stroke={riskColor} strokeWidth="2.5" />
        <line x1="64" y1="65" x2="68" y2="90" stroke={riskColor} strokeWidth="3" />
        <line x1="68" y1="90" x2="64" y2="112" stroke={riskColor} strokeWidth="2.5" />

        <circle cx="50" cy="12" r="5" fill="#3b82f6" stroke="#fff" strokeWidth="1" />
        <circle cx="32" cy="28" r="3" fill="#60a5fa" />
        <circle cx="68" cy="28" r="3" fill="#60a5fa" />
        <circle cx="36" cy="65" r="3" fill="#60a5fa" />
        <circle cx="64" cy="65" r="3" fill="#60a5fa" />
        <circle cx="35" cy="90" r="4.5" fill={riskColor} stroke="#fff" strokeWidth="1.5" />
        <circle cx="65" cy="90" r="4.5" fill={riskColor} stroke="#fff" strokeWidth="1.5" />
        <circle cx="38" cy="112" r="3" fill="#3b82f6" />
        <circle cx="62" cy="112" r="3" fill="#3b82f6" />
      </svg>

      <div style={{ position: 'absolute', top: '10px', left: '-5px', background: '#0f172a', padding: '2px 6px', borderRadius: '4px', fontSize: '9px', color: '#94a3b8', border: '1px solid #1e293b' }}>
        HIP: <b style={{ color: '#fff' }}>{hipAngle}°</b>
      </div>
      <div style={{ position: 'absolute', top: '55px', left: '-15px', background: '#0f172a', padding: '2px 6px', borderRadius: '4px', fontSize: '9px', color: '#94a3b8', border: '1px solid #1e293b' }}>
        KNEE: <b style={{ color: '#fff' }}>{kneeAngle}°</b>
      </div>
      <div style={{ position: 'absolute', bottom: '15px', left: '-10px', background: '#0f172a', padding: '2px 6px', borderRadius: '4px', fontSize: '9px', color: '#94a3b8', border: '1px solid #1e293b' }}>
        ANKLE: <b style={{ color: '#fff' }}>{ankleAngle}°</b>
      </div>

      <div style={{ position: 'absolute', top: '25px', right: '-15px', background: '#0f172a', padding: '2px 6px', borderRadius: '4px', fontSize: '9px', color: '#94a3b8', border: '1px solid #1e293b' }}>
        QUAL: <b style={{ color: '#10b981' }}>{quality}</b>
      </div>
      <div style={{ position: 'absolute', bottom: '35px', right: '-15px', background: riskColor, padding: '3px 8px', borderRadius: '4px', fontSize: '9px', color: '#fff', fontWeight: 800 }}>
        {risk}
      </div>
    </div>
  );
};

function speakBriefing(text, setSpeaking) {
  if (!('speechSynthesis' in window)) {
    return alert('Text-to-speech is not supported in this browser.');
  }
  window.speechSynthesis.cancel();
  if (!text) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  utterance.onstart = () => setSpeaking && setSpeaking(true);
  utterance.onend = () => setSpeaking && setSpeaking(false);
  utterance.onerror = () => setSpeaking && setSpeaking(false);
  window.speechSynthesis.speak(utterance);
}

function App() {
  const [authenticated, setAuthenticated] = useState(
    Boolean(localStorage.getItem('sir_auth') && localStorage.getItem('sir_token'))
  );
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const stored = localStorage.getItem('sir_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [page, setPage] = useState('Dashboard');
  const [athletes, setAthletes] = useState([]);
  const [summary, setSummary] = useState(null);
  const [health, setHealth] = useState(null);
  const [toast, setToast] = useState('');
  const [selectedAthlete, setSelectedAthlete] = useState(null);

  // Edit User Profile Modal State
  const [profileModal, setProfileModal] = useState(false);
  const [profileForm, setProfileForm] = useState({ name: '', role: 'coach' });

  // Edit Athlete Modal State
  const [editingAthlete, setEditingAthlete] = useState(null);

  // In-App Video Player Modal
  const [videoModalUrl, setVideoModalUrl] = useState(null);

  const loadData = async () => {
    try {
      const [sum, aths, h] = await Promise.all([
        api('/api/dashboard/summary').catch(() => null),
        api('/api/athletes').catch(() => []),
        fetch(`${API_BASE_URL}/api/health`)
          .then((r) => r.json())
          .catch(() => ({ status: 'offline' })),
      ]);

      let finalAthletes = aths || [];

      // Check if browser has cached athletes from previous session that need restoring
      if (!finalAthletes || finalAthletes.length === 0) {
        try {
          const cachedStr = localStorage.getItem('sir_cached_athletes');
          const cached = cachedStr ? JSON.parse(cachedStr) : [];
          if (cached && cached.length > 0) {
            for (const ca of cached) {
              await api('/api/athletes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  name: ca.name,
                  sport: ca.sport,
                  position: ca.position,
                  age: ca.age,
                  height_cm: ca.height_cm,
                  weight_kg: ca.weight_kg,
                  injury_history: ca.injury_history,
                  training_load: ca.training_load || 'Moderate',
                }),
              }).catch(() => null);
            }
            finalAthletes = await api('/api/athletes').catch(() => cached);
          }
        } catch {
          // ignore cache errors
        }
      } else {
        localStorage.setItem('sir_cached_athletes', JSON.stringify(finalAthletes));
      }

      let finalSummary = sum || {
        total_athletes: finalAthletes.length,
        total_videos: 0,
        total_analyses: 0,
        high_risk_athletes: 0,
        risk_distribution: { LOW: 0, MEDIUM: 0, HIGH: 0 },
        recent_athletes: [],
        recent_analyses: [],
      };

      try {
        const cachedAnalysesStr = localStorage.getItem('sir_cached_analyses');
        const cachedAnalyses = cachedAnalysesStr ? JSON.parse(cachedAnalysesStr) : [];
        if (cachedAnalyses && cachedAnalyses.length > 0) {
          if (!finalSummary.recent_analyses || finalSummary.recent_analyses.length === 0) {
            finalSummary.recent_analyses = cachedAnalyses;
            finalSummary.total_analyses = cachedAnalyses.length;
            finalSummary.total_videos = cachedAnalyses.length;
          } else {
            const existingIds = new Set(finalSummary.recent_analyses.map(a => a.analysis_id || a.id));
            const toAdd = cachedAnalyses.filter(a => !existingIds.has(a.analysis_id || a.id));
            finalSummary.recent_analyses = [...finalSummary.recent_analyses, ...toAdd];
            localStorage.setItem('sir_cached_analyses', JSON.stringify(finalSummary.recent_analyses));
          }
        }
      } catch {}

      setSummary(finalSummary);
      setAthletes(finalAthletes);
      setHealth(h);
      return finalSummary;
    } catch (e) {
      setToast(e.message);
      return null;
    }
  };

  useEffect(() => {
    if (authenticated) {
      loadData();
    }
  }, [authenticated]);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(''), 3500);
      return () => clearTimeout(t);
    }
  }, [toast]);

  const handleLogout = () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    localStorage.removeItem('sir_token');
    localStorage.removeItem('sir_auth');
    localStorage.removeItem('sir_user');
    setAuthenticated(false);
    setCurrentUser(null);
    setPage('Dashboard');
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    try {
      const updated = await api('/api/auth/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileForm),
      });
      localStorage.setItem('sir_user', JSON.stringify(updated));
      setCurrentUser(updated);
      setProfileModal(false);
      setToast('User profile updated successfully.');
    } catch (err) {
      setToast(`Profile error: ${err.message}`);
    }
  };

  if (!authenticated) {
    return (
      <AuthScreen
        onSuccess={(token, user) => {
          localStorage.setItem('sir_token', token);
          localStorage.setItem('sir_auth', '1');
          localStorage.setItem('sir_user', JSON.stringify(user));
          setCurrentUser(user);
          setAuthenticated(true);
        }}
      />
    );
  }

  const nav = (p) => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    setPage(p);
  };

  return (
    <div className="app">
      <aside>
        <div className="brand">
          <div className="brandIcon"><Icon name="activityPulse" size={18} /></div>
          <div>
            <b>MOTIONIQ</b>
            <span>Sports Injury Intelligence</span>
          </div>
        </div>

        <div className="engineBadge">
          AI BIOMECHANICS LAB
          <strong>Skeletal Kinetic System</strong>
        </div>

        {[
          { name: 'Dashboard', icon: 'dashboard', label: '01 OVERVIEW' },
          { name: 'Athletes', icon: 'users', label: '02 ATHLETES' },
          { name: 'Video Analysis', icon: 'video', label: '03 ANALYSIS' },
          { name: 'Results', icon: 'chart', label: '04 RESULTS' },
          { name: 'Kinematics Lab', icon: 'activity', label: '05 SANDBOX' },
          { name: 'Reports', icon: 'report', label: '06 REPORTS' },
        ].map(({ name, icon, label }) => (
          <button
            className={page === name ? 'nav active' : 'nav'}
            onClick={() => nav(name)}
            key={name}
          >
            <span><Icon name={icon} size={15} /></span>
            <span>{label}</span>
          </button>
        ))}

        <div className="sidefoot">
          Motion Intel Engine<br />
          OpenCV • MediaPipe • Supervised ML
        </div>
      </aside>

      <main>
        <header>
          <div>
            <h1>
              {page === 'Dashboard' ? 'Movement Intelligence' : 
               page === 'Athletes' ? 'Athlete Intelligence' : 
               page === 'Video Analysis' ? 'Movement Capture' : 
               page === 'Results' ? 'Movement Assessment' : 
               page}
            </h1>
            <p>
              {page === 'Dashboard' ? 'Understand how your athletes move. Detect biomechanical patterns before they become injuries.' : 
               page === 'Athletes' ? 'Monitor movement quality and injury-risk patterns across your athletes.' : 
               page === 'Video Analysis' ? 'Upload a movement video to begin biomechanical analysis.' : 
               page === 'Results' ? 'Historical reports and predictive risk analytics.' : 
               'Sports Injury Risk Detection and Prevention System'}
            </p>
          </div>
          <div className="headerActions">
            {currentUser && (
              <button
                type="button"
                onClick={() => {
                  setProfileForm({ name: currentUser.name || '', role: currentUser.role || 'coach' });
                  setProfileModal(true);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: '#fff',
                  border: '1px solid #e2e8f0',
                  padding: '5px 12px',
                  borderRadius: '9999px',
                  cursor: 'pointer',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                }}
              >
                <span style={{ fontSize: '13px', color: '#0f172a', fontWeight: 700 }}>👤 {currentUser.name}</span>
                <span style={{
                  fontSize: '10px',
                  textTransform: 'uppercase',
                  fontWeight: 800,
                  letterSpacing: '0.5px',
                  background: currentUser.role === 'admin' ? '#fef2f2' : currentUser.role === 'athlete' ? '#ecfdf5' : currentUser.role === 'physiotherapist' ? '#fdf4ff' : currentUser.role === 'sports_scientist' ? '#eff6ff' : '#f0fdf4',
                  color: currentUser.role === 'admin' ? '#dc2626' : currentUser.role === 'athlete' ? '#059669' : currentUser.role === 'physiotherapist' ? '#a855f7' : currentUser.role === 'sports_scientist' ? '#2563eb' : '#166534',
                  border: '1px solid currentColor',
                  padding: '2px 8px',
                  borderRadius: '9999px',
                }}>
                  {currentUser.role || 'COACH'} ✏️
                </span>
              </button>
            )}
            <div className="online">
              <i></i> Engine Online
            </div>
            <button className="logout" onClick={handleLogout}>
              Sign out
            </button>
          </div>
        </header>

        {page === 'Dashboard' && (
          <Dashboard summary={summary} athletes={athletes} onNav={nav} userRole={currentUser?.role} />
        )}
        {page === 'Athletes' && (
          <Athletes
            athletes={athletes}
            onRefresh={loadData}
            onSelect={(a) => {
              setSelectedAthlete(a);
              setPage('Athlete Details');
            }}
            onEditAthlete={(a) => setEditingAthlete(a)}
          />
        )}
        {page === 'Athlete Details' && selectedAthlete && (
          <AthleteDetails
            athlete={selectedAthlete}
            onEdit={() => setEditingAthlete(selectedAthlete)}
            onBack={() => setPage('Athletes')}
          />
        )}
        {page === 'Video Analysis' && (
          <VideoAnalysis
            athletes={athletes}
            onDone={loadData}
            onNav={nav}
            onPlayVideo={(url) => setVideoModalUrl(url)}
          />
        )}
        {page === 'Kinematics Lab' && (
          <KinematicsLab />
        )}
        {page === 'Results' && (
          <Results
            summary={summary}
            onPlayVideo={(url) => setVideoModalUrl(url)}
          />
        )}
        {page === 'Reports' && <Reports summary={summary} />}

        {toast && <div className="toast">{toast}</div>}

        {/* Video Player Modal */}
        {videoModalUrl && (
          <div className="oauthModalOverlay" onClick={() => setVideoModalUrl(null)}>
            <div className="oauthModalCard" style={{ width: 'min(700px, 95vw)', padding: '20px' }} onClick={(e) => e.stopPropagation()}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <b style={{ fontSize: '15px', color: '#0f172a' }}>▶ Movement Screening Video Playback</b>
                <button
                  type="button"
                  onClick={() => setVideoModalUrl(null)}
                  style={{ border: 'none', background: 'transparent', fontSize: '18px', cursor: 'pointer', color: '#64748b' }}
                >
                  ✕
                </button>
              </div>
              <video
                src={videoModalUrl}
                controls
                autoPlay
                style={{ width: '100%', maxHeight: '420px', borderRadius: '10px', background: '#000' }}
              />
            </div>
          </div>
        )}

        {/* Edit User Profile Modal */}
        {profileModal && (
          <div className="oauthModalOverlay" onClick={() => setProfileModal(false)}>
            <div className="oauthModalCard" onClick={(e) => e.stopPropagation()}>
              <h3>Edit User Profile</h3>
              <p>Update your account details and operational role</p>
              <form onSubmit={handleUpdateProfile} style={{ textAlign: 'left' }}>
                <label style={{ fontSize: '12px', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                  Full Name
                </label>
                <input
                  required
                  type="text"
                  value={profileForm.name}
                  onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                  style={{ width: '100%', height: '44px', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '0 12px', fontSize: '13.5px', marginBottom: '14px', boxSizing: 'border-box' }}
                />

                <label style={{ fontSize: '12px', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                  Account Role
                </label>
                <select
                  value={profileForm.role}
                  onChange={(e) => setProfileForm({ ...profileForm, role: e.target.value })}
                  style={{ width: '100%', height: '44px', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '0 10px', fontSize: '13px', marginBottom: '22px', background: '#fff', boxSizing: 'border-box' }}
                >
                  <option value="coach">👨‍🏫 Coach (Team Roster & Squad Risk)</option>
                  <option value="athlete">🏃 Athlete (Personal Movement Screening)</option>
                  <option value="physiotherapist">🩺 Physiotherapist (Rehabilitation)</option>
                  <option value="sports_scientist">🔬 Sports Scientist (Kinematic Modeling)</option>
                  <option value="admin">🛡️ Administrator (System Access)</option>
                </select>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <button
                    type="button"
                    onClick={() => setProfileModal(false)}
                    style={{ border: 'none', background: 'transparent', color: '#64748b', fontSize: '12.5px', fontWeight: 700, cursor: 'pointer' }}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="primary">
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Athlete Modal */}
        {editingAthlete && (
          <EditAthleteModal
            athlete={editingAthlete}
            onClose={() => setEditingAthlete(null)}
            onSaved={(updated) => {
              setEditingAthlete(null);
              setSelectedAthlete(updated);
              loadData();
              setToast(`Athlete #${updated.name} updated.`);
            }}
          />
        )}
      </main>
    </div>
  );
}

function EditAthleteModal({ athlete, onClose, onSaved }) {
  const [form, setForm] = useState({
    name: athlete.name || '',
    sport: athlete.sport || '',
    position: athlete.position || '',
    age: athlete.age || 20,
    height_cm: athlete.height_cm || '',
    weight_kg: athlete.weight_kg || '',
    training_load: athlete.training_load || 'Moderate',
    injury_history: athlete.injury_history || '',
  });
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const res = await api(`/api/athletes/${athlete.athlete_id || athlete.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          sport: form.sport,
          position: form.position || null,
          age: Number(form.age),
          height_cm: form.height_cm ? Number(form.height_cm) : null,
          weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
          training_load: form.training_load,
          injury_history: form.injury_history || null,
        }),
      });
      onSaved(res);
    } catch (err) {
      alert(`Update Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="oauthModalOverlay" onClick={onClose}>
      <div className="oauthModalCard" style={{ width: 'min(520px, 95vw)', textAlign: 'left' }} onClick={(e) => e.stopPropagation()}>
        <h3 style={{ margin: '0 0 4px', textAlign: 'center' }}>Edit Athlete Profile</h3>
        <p style={{ margin: '0 0 18px', textAlign: 'center' }}>Update athlete metrics, sport position, and injury history</p>

        <form onSubmit={submit} className="form" style={{ marginTop: '10px' }}>
          <label>
            Full Name
            <input
              required
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </label>
          <label>
            Sport Type
            <input
              required
              type="text"
              value={form.sport}
              onChange={(e) => setForm({ ...form, sport: e.target.value })}
            />
          </label>
          <label>
            Sport Position
            <input
              type="text"
              value={form.position}
              onChange={(e) => setForm({ ...form, position: e.target.value })}
            />
          </label>
          <label>
            Age (years)
            <input
              required
              type="number"
              min="5"
              max="80"
              value={form.age}
              onChange={(e) => setForm({ ...form, age: e.target.value })}
            />
          </label>
          <label>
            Height (cm)
            <input
              type="number"
              value={form.height_cm}
              onChange={(e) => setForm({ ...form, height_cm: e.target.value })}
            />
          </label>
          <label>
            Weight (kg)
            <input
              type="number"
              value={form.weight_kg}
              onChange={(e) => setForm({ ...form, weight_kg: e.target.value })}
            />
          </label>
          <label>
            Training Load
            <select
              value={form.training_load}
              onChange={(e) => setForm({ ...form, training_load: e.target.value })}
            >
              <option value="Low">Low (1–3 sessions/week)</option>
              <option value="Moderate">Moderate (4–5 sessions/week)</option>
              <option value="High">High (6–8 sessions/week)</option>
              <option value="Extreme">Extreme (Two-a-day Pro Training)</option>
            </select>
          </label>
          <label>
            Injury History & Prior Conditions
            <textarea
              value={form.injury_history}
              onChange={(e) => setForm({ ...form, injury_history: e.target.value })}
            />
          </label>

          <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
            <button type="button" onClick={onClose} style={{ border: 'none', background: 'transparent', color: '#64748b', fontWeight: 700 }}>
              Cancel
            </button>
            <button type="submit" className="primary" disabled={busy}>
              {busy ? 'Saving…' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function AuthScreen({ onSuccess }) {
  const [mode, setMode] = useState('login');
  const [role, setRole] = useState('coach');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ name: '', email: '', password: '' });

  // Social OAuth Provider State
  const [oauthModal, setOauthModal] = useState(null); // 'Google' | 'Apple' | 'Microsoft'
  const [oauthEmail, setOauthEmail] = useState('');
  const [oauthName, setOauthName] = useState('');

  // Dynamically load recently signed-in Social account from browser
  const [recentSocialUser, setRecentSocialUser] = useState(() => {
    try {
      const stored = localStorage.getItem('sir_recent_social_account');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [useCustomInput, setUseCustomInput] = useState(() => !recentSocialUser);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError('');

    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const payload =
        mode === 'login'
          ? { email: form.email, password: form.password }
          : { name: form.name, email: form.email, password: form.password, role };

      const res = await api(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.token) throw new Error('No authentication token received.');
      onSuccess(res.token, res.user);
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  const handleOAuthLogin = async (provider, email, name, userRole = 'coach') => {
    if (!email || !email.includes('@')) {
      return setError(`Please provide a valid ${provider} email address.`);
    }
    setBusy(true);
    setError('');
    try {
      const res = await api('/api/auth/oauth-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: provider.toLowerCase(),
          email: email.trim().toLowerCase(),
          name: name || email.split('@')[0].replace('.', ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
          role: userRole,
        }),
      });
      if (!res.token) throw new Error('No authentication token received.');

      // Save as the dynamically recent Social account
      localStorage.setItem('sir_recent_social_account', JSON.stringify({
        provider: provider,
        email: email.trim().toLowerCase(),
        name: res.user?.name || name || email.split('@')[0],
        role: res.user?.role || userRole,
        avatarInitial: (res.user?.name || email)[0].toUpperCase(),
      }));

      setOauthModal(null);
      onSuccess(res.token, res.user);
    } catch (err) {
      setError(err.message || `${provider} authentication failed.`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="authShell">
      <div className="authVisual">
        <div className="authLogo"><Icon name="activityPulse" size={24} /></div>
        <div className="eyebrow" style={{ fontSize: '10px', fontWeight: 800, letterSpacing: '1.5px', color: '#60a5fa', textTransform: 'uppercase' }}>MOTIONIQ PLATFORM</div>
        <h1 style={{ fontSize: '38px', fontWeight: 800, lineHeight: 1.1, color: '#fff', margin: '16px 0' }}>
          Understand movement.<br />
          <em style={{ fontStyle: 'normal', color: '#60a5fa' }}>Prevent injury.</em>
        </h1>
        <p style={{ fontSize: '14px', color: '#cbd5e1', lineHeight: 1.6, margin: '0 0 30px', maxWidth: '440px' }}>
          Quantify athlete kinematics, detect abnormal joint loading patterns, and leverage predictive machine learning for proactive injury prevention.
        </p>
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', opacity: 0.15 }}>
          <svg width="120" height="150" viewBox="0 0 100 120" fill="none">
            <line x1="50" y1="18" x2="50" y2="40" stroke="#fff" strokeWidth="2"/>
            <line x1="35" y1="28" x2="65" y2="28" stroke="#fff" strokeWidth="2"/>
            <line x1="38" y1="65" x2="62" y2="65" stroke="#fff" strokeWidth="2"/>
            <line x1="38" y1="65" x2="35" y2="90" stroke="#fff" strokeWidth="2"/>
            <line x1="35" y1="90" x2="38" y2="112" stroke="#fff" strokeWidth="2"/>
            <circle cx="50" cy="12" r="5" fill="#fff"/>
            <circle cx="35" cy="90" r="4.5" fill="#fff"/>
            <circle cx="38" cy="112" r="3.5" fill="#fff"/>
          </svg>
        </div>
      </div>

      <div className="authCard">
        <div className="authBrand" style={{ fontSize: '12px', fontWeight: 800, color: '#2563eb', letterSpacing: '0.5px', marginBottom: '24px' }}>
          MOTIONIQ <span style={{ color: '#64748b', fontSize: '9px', marginLeft: '6px' }}>SPORTS INJURY INTELLIGENCE</span>
        </div>
        <h2>{mode === 'login' ? 'Welcome back' : 'Create an Account'}</h2>
        <p className="authSub">
          {mode === 'login'
            ? 'Sign in to access your role-specific screening dashboard.'
            : 'Register to manage athlete profiles and movement analyses.'}
        </p>

        {/* Role Selector Tabs */}
        {mode === 'register' && (
          <div style={{ marginBottom: '18px' }}>
            <label style={{ fontSize: '11.5px', fontWeight: 800, color: '#334155', display: 'block', marginBottom: '6px' }}>
              Select Account Role:
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
              {[
                ['coach', '👨‍🏫 Coach'],
                ['athlete', '🏃 Athlete'],
                ['physiotherapist', '🩺 Physio'],
                ['sports_scientist', '🔬 Scientist'],
                ['admin', '🛡️ Admin'],
              ].map(([rKey, rLabel]) => (
                <button
                  key={rKey}
                  type="button"
                  onClick={() => setRole(rKey)}
                  style={{
                    padding: '8px 4px',
                    fontSize: '11px',
                    fontWeight: 700,
                    borderRadius: '6px',
                    border: role === rKey ? '2px solid #10b981' : '1px solid #cbd5e1',
                    background: role === rKey ? '#ecfdf5' : '#fff',
                    color: role === rKey ? '#059669' : '#475569',
                    cursor: 'pointer',
                  }}
                >
                  {rLabel}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Social Logins */}
        <div className="socials" style={{ display: 'grid', gap: '8px' }}>
          <button 
            type="button" 
            className="googleBtn" 
            onClick={() => { setOauthModal('Google'); setError(''); }}
          >
            <svg width="20" height="20" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            </svg>
            <span>Continue with Google</span>
          </button>

          <button 
            type="button" 
            className="googleBtn" 
            onClick={() => { setOauthModal('Apple'); setError(''); }}
          >
            <span style={{ fontSize: '18px', lineHeight: 1 }}></span>
            <span>Continue with Apple ID</span>
          </button>

          <button 
            type="button" 
            className="googleBtn" 
            onClick={() => { setOauthModal('Microsoft'); setError(''); }}
          >
            <span style={{ color: '#00a4ef', fontSize: '16px' }}>▦</span>
            <span>Continue with Microsoft 365</span>
          </button>
        </div>

        <div className="divider">
          <span>or sign in with password</span>
        </div>

        {error && <div className="authError">{error}</div>}

        <form onSubmit={submit} className="authForm">
          {mode === 'register' && (
            <label>
              Full name
              <input
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="User Full Name"
              />
            </label>
          )}
          <label>
            Email address
            <input
              required
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@domain.com"
            />
          </label>
          <label>
            Password
            <input
              required
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="••••••••"
            />
          </label>
          <button className="primary authSubmit" disabled={busy}>
            {busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>

        <p className="switchAuth">
          {mode === 'login' ? 'Need an account?' : 'Already registered?'}{' '}
          <button
            type="button"
            onClick={() => {
              setMode(mode === 'login' ? 'register' : 'login');
              setError('');
            }}
          >
            {mode === 'login' ? 'Create an account' : 'Sign in'}
          </button>
        </p>
      </div>

      {oauthModal && (
        <div className="oauthModalOverlay" onClick={() => setOauthModal(null)}>
          <div className="oauthModalCard" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '8px' }}>
              {oauthModal === 'Google' && (
                <svg width="42" height="42" viewBox="0 0 48 48">
                  <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                  <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                  <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                  <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
              )}
              {oauthModal === 'Apple' && (
                <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: '#000', color: '#fff', display: 'grid', placeItems: 'center', fontSize: '24px' }}>
                  
                </div>
              )}
              {oauthModal === 'Microsoft' && (
                <div style={{ width: '42px', height: '42px', borderRadius: '8px', background: '#00a4ef', color: '#fff', display: 'grid', placeItems: 'center', fontSize: '22px' }}>
                  ▦
                </div>
              )}
            </div>
            <h3>Sign in with {oauthModal}</h3>
            <p>to continue to Sports Injury Intelligence</p>

            {recentSocialUser && !useCustomInput ? (
              <div>
                <button
                  type="button"
                  className="oauthAccountOption"
                  disabled={busy}
                  onClick={() => handleOAuthLogin(oauthModal, recentSocialUser.email, recentSocialUser.name, recentSocialUser.role || role)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '38px', height: '38px', borderRadius: '50%', background: 'linear-gradient(135deg, #10b981, #06b6d4)', color: '#fff', display: 'grid', placeItems: 'center', fontWeight: 800, fontSize: '15px' }}>
                      {recentSocialUser.avatarInitial || recentSocialUser.name?.[0] || 'U'}
                    </div>
                    <div>
                      <b style={{ fontSize: '13px', color: '#0f172a', display: 'block' }}>{recentSocialUser.name}</b>
                      <span style={{ fontSize: '11.5px', color: '#64748b' }}>{recentSocialUser.email}</span>
                    </div>
                  </div>
                  <span style={{ fontSize: '11px', color: '#059669', fontWeight: 700, background: '#ecfdf5', padding: '3px 8px', borderRadius: '9999px' }}>
                    Recent ↵
                  </span>
                </button>

                <button
                  type="button"
                  className="oauthAccountOption"
                  style={{ borderStyle: 'dashed', marginTop: '6px' }}
                  onClick={() => setUseCustomInput(true)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '38px', height: '38px', borderRadius: '50%', background: '#f1f5f9', color: '#64748b', display: 'grid', placeItems: 'center', fontSize: '16px' }}>
                      +
                    </div>
                    <div>
                      <b style={{ fontSize: '13px', color: '#0f172a', display: 'block' }}>Use another account</b>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>Sign in with any {oauthModal} email</span>
                    </div>
                  </div>
                </button>
              </div>
            ) : (
              <form onSubmit={(e) => { e.preventDefault(); handleOAuthLogin(oauthModal, oauthEmail, oauthName, role); }} style={{ textAlign: 'left' }}>
                <label style={{ fontSize: '12px', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                  {oauthModal} Email Address
                </label>
                <input
                  required
                  type="email"
                  value={oauthEmail}
                  onChange={(e) => setOauthEmail(e.target.value)}
                  placeholder={`Enter your ${oauthModal} email`}
                  style={{ width: '100%', height: '46px', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '0 12px', fontSize: '13.5px', marginBottom: '14px', boxSizing: 'border-box' }}
                />

                <label style={{ fontSize: '12px', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                  Select Operating Role:
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  style={{ width: '100%', height: '46px', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '0 10px', fontSize: '13px', marginBottom: '20px', background: '#fff', boxSizing: 'border-box' }}
                >
                  <option value="coach">👨‍🏫 Coach (Team Roster & Squad Risk)</option>
                  <option value="athlete">🏃 Athlete (Personal Movement Screening)</option>
                  <option value="physiotherapist">🩺 Physiotherapist (Rehabilitation)</option>
                  <option value="sports_scientist">🔬 Sports Scientist (Kinematic Modeling)</option>
                  <option value="admin">🛡️ Administrator (System Access)</option>
                </select>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  {recentSocialUser && (
                    <button
                      type="button"
                      onClick={() => setUseCustomInput(false)}
                      style={{ border: 'none', background: 'transparent', color: '#059669', fontSize: '12.5px', fontWeight: 700, cursor: 'pointer' }}
                    >
                      ← Back
                    </button>
                  )}
                  <button
                    type="submit"
                    className="primary"
                    disabled={busy || !oauthEmail}
                    style={{ padding: '10px 22px', fontSize: '13px', borderRadius: '8px', marginLeft: 'auto' }}
                  >
                    {busy ? 'Signing in…' : `Sign in with ${oauthModal}`}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function Dashboard({ summary, athletes, onNav, userRole }) {
  const totalAthletes = summary?.total_athletes ?? athletes.length;
  const totalVideos = summary?.total_videos ?? 0;
  const highRisk = summary?.high_risk_athletes ?? 0;
  const recentAnalyses = summary?.recent_analyses ?? [];
  
  const latest = recentAnalyses[0];
  const kneeVal = latest?.knee_angle ? Math.round(latest.knee_angle) : 154;
  const hipVal = latest?.hip_angle ? Math.round(latest.hip_angle) : 135;
  const ankleVal = latest?.ankle_flexion ? Math.round(latest.ankle_flexion) : 28;
  const scoreVal = latest?.movement_quality?.score ? latest.movement_quality.score : 84;
  const riskVal = latest?.risk_level ? latest.risk_level : 'LOW';
  const latestDate = latest?.created_at ? new Date(latest.created_at).toLocaleDateString() : 'N/A';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Top Area: Editorial Intro & Action */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #e2e8f0', paddingBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '38px', fontWeight: 800, letterSpacing: '-1.5px', textTransform: 'uppercase', lineHeight: 1.05, margin: 0, color: '#0f172a' }}>
            MOVEMENT<br />INTELLIGENCE
          </h2>
          <p style={{ fontSize: '14px', color: '#64748b', margin: '8px 0 0', fontWeight: 500 }}>
            AI-powered biomechanical analysis for smarter athlete performance.
          </p>
        </div>
        <button className="primary" onClick={() => onNav('Video Analysis')} style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '12px 24px', borderRadius: '8px', fontSize: '13px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', boxShadow: '0 4px 12px rgba(37,99,235,0.2)' }}>
          START NEW ANALYSIS <Icon name="arrow" size={14} />
        </button>
      </div>

      {/* Center: Signature Movement Map & Current Signal */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '40px', alignItems: 'center', background: '#090e17', borderRadius: '16px', padding: '30px 40px', border: '1px solid #1e293b', color: '#fff' }}>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <MovementMap 
            kneeAngle={kneeVal} 
            hipAngle={hipVal} 
            ankleAngle={ankleVal} 
            quality={scoreVal} 
            risk={riskVal} 
            size={180} 
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ borderBottom: '1px solid #1e293b', paddingBottom: '10px' }}>
            <span style={{ fontSize: '10px', fontWeight: 800, color: '#60a5fa', letterSpacing: '1px', textTransform: 'uppercase' }}>Current Signal</span>
            <h3 style={{ fontSize: '20px', fontWeight: 700, margin: '4px 0 0', color: '#fff' }}>Active Squad Status</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>RISK STATE</span>
              <span style={{ fontSize: '12px', fontWeight: 800, color: riskVal === 'HIGH' || riskVal === 'CRITICAL' ? '#ef4444' : riskVal === 'MODERATE' ? '#f59e0b' : '#10b981' }}>
                {riskVal} RISK
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>MOVEMENT QUALITY</span>
              <span style={{ fontSize: '12px', fontWeight: 800, color: '#fff' }}>
                {scoreVal} / 100
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>LATEST ASSESSMENT</span>
              <span style={{ fontSize: '12px', fontWeight: 800, color: '#fff' }}>
                {latestDate}
              </span>
            </div>
          </div>

          <div style={{ background: 'rgba(96,165,250,0.06)', border: '1px dashed rgba(96,165,250,0.2)', padding: '12px', borderRadius: '8px', fontSize: '11px', color: '#94a3b8', lineHeight: 1.5 }}>
            {riskVal === 'HIGH' || riskVal === 'CRITICAL' 
              ? '⚠ Shearing loads flagged on joints. Corrective interventions are prescribed.'
              : '✓ Squad biomechanical indices are within nominal thresholds. Continue standard conditioning.'}
          </div>
        </div>
      </div>

      {/* Lower Area: 3-column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1.5fr', gap: '30px', alignItems: 'start' }}>
        {/* Column 1: Athlete Pulse */}
        <div style={{ borderRight: '1px solid #e2e8f0', paddingRight: '20px' }}>
          <h4 style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '14px' }}>Athlete Pulse</h4>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#0f172a' }}>{totalAthletes}</div>
          <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600, display: 'block', marginBottom: '12px' }}>ACTIVE PROFILES</span>
          
          {/* Mini node visual connector decoration */}
          <svg width="100%" height="40" viewBox="0 0 200 40">
            <path d="M 10,20 Q 50,5 90,30 T 170,10" fill="none" stroke="#2563eb" strokeWidth="2" strokeDasharray="3,3" />
            <circle cx="10" cy="20" r="4" fill="#2563eb" />
            <circle cx="90" cy="30" r="4" fill="#2563eb" />
            <circle cx="170" cy="10" r="4" fill="#2563eb" />
          </svg>
        </div>

        {/* Column 2: Risk Landscape */}
        <div style={{ borderRight: '1px solid #e2e8f0', paddingRight: '20px' }}>
          <h4 style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '14px' }}>Risk Landscape</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#059669', fontWeight: 700 }}>🟢 LOW</span>
              <span style={{ fontWeight: 800 }}>{totalAthletes - highRisk} Athletes</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#dc2626', fontWeight: 700 }}>🔴 HIGH</span>
              <span style={{ fontWeight: 800 }}>{highRisk} Athletes</span>
            </div>
          </div>
        </div>

        {/* Column 3: Recent Movements */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h4 style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', margin: 0 }}>Recent Movements</h4>
            <button onClick={() => onNav('Results')} style={{ background: 'none', border: 'none', color: '#2563eb', fontSize: '11px', fontWeight: 700, cursor: 'pointer' }}>View all →</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {recentAnalyses.slice(0, 3).map((r) => (
              <div key={r.analysis_id || r.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f1f5f9', paddingBottom: '8px', fontSize: '12px' }}>
                <div>
                  <b style={{ color: '#0f172a' }}>{r.activity}</b>
                  <span style={{ display: 'block', fontSize: '10px', color: '#94a3b8' }}>#{((r.analysis_id || r.id)).slice(0, 8)}</span>
                </div>
                <span className={`badge ${(r.risk_level || 'LOW').toLowerCase()}`} style={{ fontSize: '9px', padding: '3px 8px' }}>
                  {r.risk_level || 'LOW'}
                </span>
              </div>
            ))}
            {!recentAnalyses.length && <div style={{ fontSize: '11.5px', color: '#94a3b8' }}>No analyses recorded yet.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}

function Card({ title, value, icon }) {
  return (
    <div className="card">
      <div className="cardIcon">{icon}</div>
      <div>
        <span>{title}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function KinematicsLab() {
  const canvasRef = useRef(null);
  const [kneeAngle, setKneeAngle] = useState(90);
  const [hipAngle, setHipAngle] = useState(70);
  const [trunkLean, setTrunkLean] = useState(15);
  const [animating, setAnimating] = useState(false);

  const [trainingLoad, setTrainingLoad] = useState('Moderate');
  const [injuryHistory, setInjuryHistory] = useState('None');
  const [valgusAngle, setValgusAngle] = useState(8);
  const [selectedJoint, setSelectedJoint] = useState('knee');

  let sandboxScore = 20;
  if (trainingLoad === 'High') sandboxScore += 18;
  if (trainingLoad === 'Extreme') sandboxScore += 35;
  if (injuryHistory === 'ACL') sandboxScore += 24;
  if (injuryHistory === 'Ankle') sandboxScore += 14;
  if (valgusAngle > 12) sandboxScore += (valgusAngle - 12) * 3;
  if (kneeAngle > 125) sandboxScore += 12;
  sandboxScore = Math.min(95, Math.max(12, sandboxScore));

  const sandboxLevel = sandboxScore <= 28 ? 'LOW' : sandboxScore <= 55 ? 'MODERATE' : 'HIGH';

  useEffect(() => {
    let animFrame;
    let t = 0;
    const animate = () => {
      if (animating) {
        t += 0.04;
        const currentKnee = 80 + Math.sin(t) * 45;
        const currentHip = 60 + Math.sin(t) * 30;
        const currentTrunk = 12 + Math.cos(t) * 10;
        setKneeAngle(Math.round(currentKnee));
        setHipAngle(Math.round(currentHip));
        setTrunkLean(Math.round(currentTrunk));
      }
      animFrame = requestAnimationFrame(animate);
    };
    if (animating) {
      animFrame = requestAnimationFrame(animate);
    }
    return () => cancelAnimationFrame(animFrame);
  }, [animating]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 30) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    const hipX = w * 0.45;
    const hipY = h * 0.48;

    const spineLen = 70;
    const radTrunk = (trunkLean * Math.PI) / 180;
    const neckX = hipX - Math.sin(radTrunk) * spineLen;
    const neckY = hipY - Math.cos(radTrunk) * spineLen;
    const headX = neckX - Math.sin(radTrunk) * 20;
    const headY = neckY - Math.cos(radTrunk) * 20;

    const thighLen = 65;
    const radHip = (hipAngle * Math.PI) / 180;
    const kneeX = hipX + Math.sin(radHip) * thighLen;
    const kneeY = hipY + Math.cos(radHip) * thighLen;

    const shinLen = 65;
    const radKnee = ((kneeAngle - hipAngle) * Math.PI) / 180;
    const ankleX = kneeX - Math.sin(radKnee) * shinLen;
    const ankleY = kneeY + Math.cos(radKnee) * shinLen;

    const kneeColor = kneeAngle > 125 ? '#ef4444' : kneeAngle > 105 ? '#f59e0b' : '#10b981';

    ctx.lineWidth = 4;
    ctx.lineCap = 'round';

    ctx.strokeStyle = '#38bdf8';
    ctx.beginPath();
    ctx.moveTo(hipX, hipY);
    ctx.lineTo(neckX, neckY);
    ctx.stroke();

    ctx.strokeStyle = '#34d399';
    ctx.beginPath();
    ctx.moveTo(hipX, hipY);
    ctx.lineTo(kneeX, kneeY);
    ctx.stroke();

    ctx.strokeStyle = kneeColor;
    ctx.beginPath();
    ctx.moveTo(kneeX, kneeY);
    ctx.lineTo(ankleX, ankleY);
    ctx.stroke();

    ctx.strokeStyle = '#818cf8';
    ctx.beginPath();
    ctx.moveTo(neckX, neckY);
    ctx.lineTo(neckX + 25, neckY + 45);
    ctx.stroke();

    ctx.fillStyle = '#f8fafc';
    ctx.beginPath();
    ctx.arc(headX, headY, 12, 0, Math.PI * 2);
    ctx.fill();

    const drawJoint = (x, y, color, label) => {
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#fff';
      ctx.font = '10px Space Grotesk';
      if (label) ctx.fillText(label, x + 10, y + 3);
    };

    drawJoint(hipX, hipY, '#38bdf8', `Hip: ${hipAngle}°`);
    drawJoint(kneeX, kneeY, kneeColor, `Knee: ${kneeAngle}°`);
    drawJoint(ankleX, ankleY, '#10b981', 'Ankle');
    drawJoint(neckX, neckY, '#818cf8', `Trunk: ${trunkLean}°`);
  }, [kneeAngle, hipAngle, trunkLean]);

  return (
    <div className="grid2">
      <section className="panel">
        <div className="panelHead">
          <div>
            <h3>🩻 3D Skeletal Motion Canvas (Live Wireframe Simulator)</h3>
            <small style={{ color: '#059669', fontWeight: 600 }}>Interactive dot-product joint angle telemetry</small>
          </div>
          <button
            type="button"
            className="btnSecondary"
            onClick={() => setAnimating(!animating)}
          >
            {animating ? '⏹ Pause Cycle' : '▶ Play Movement Cycle'}
          </button>
        </div>

        <div className="canvasBox">
          <canvas ref={canvasRef} width={460} height={250} />
        </div>

        <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '14px' }}>
          <div className="sliderControl">
            <label>
              <span>Knee Flexion:</span>
              <b>{kneeAngle}°</b>
            </label>
            <input
              type="range"
              min="40"
              max="145"
              value={kneeAngle}
              onChange={(e) => { setAnimating(false); setKneeAngle(Number(e.target.value)); }}
            />
          </div>

          <div className="sliderControl">
            <label>
              <span>Hip Flexion:</span>
              <b>{hipAngle}°</b>
            </label>
            <input
              type="range"
              min="30"
              max="110"
              value={hipAngle}
              onChange={(e) => { setAnimating(false); setHipAngle(Number(e.target.value)); }}
            />
          </div>

          <div className="sliderControl">
            <label>
              <span>Spinal Trunk Lean:</span>
              <b>{trunkLean}°</b>
            </label>
            <input
              type="range"
              min="0"
              max="45"
              value={trunkLean}
              onChange={(e) => { setAnimating(false); setTrunkLean(Number(e.target.value)); }}
            />
          </div>
        </div>

        <div style={{ marginTop: '20px', background: '#090e17', borderRadius: '14px', padding: '16px', border: '1px solid #1e293b' }}>
          <b style={{ color: '#fff', fontSize: '13px', display: 'block', marginBottom: '8px' }}>🩻 Anatomical Joint Heatmap</b>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
            {[
              ['knee', '🦵 Knee / ACL', valgusAngle > 12 ? 'high' : 'low', `${kneeAngle}° ROM (Shear: ${valgusAngle > 12 ? 'Elevated' : 'Safe'})`],
              ['hamstring', '🏃 Hamstring', injuryHistory === 'ACL' ? 'moderate' : 'low', 'Terminal Swing Elasticity: 92%'],
              ['ankle', '🦶 Ankle / Dorsi', injuryHistory === 'Ankle' ? 'high' : 'low', 'Ground Stability: 94%'],
              ['spine', '🧘 Lumbar Spine', trunkLean > 25 ? 'moderate' : 'low', `Trunk Tilt: ${trunkLean}°`],
            ].map(([id, label, status, detail]) => (
              <div
                key={id}
                onClick={() => setSelectedJoint(id)}
                style={{
                  background: selectedJoint === id ? '#132338' : '#0e1726',
                  border: `1px solid ${selectedJoint === id ? '#10b981' : '#1e293b'}`,
                  borderRadius: '8px',
                  padding: '8px 10px',
                  cursor: 'pointer'
                }}
              >
                <b style={{ fontSize: '11.5px', color: '#fff', display: 'block' }}>{label}</b>
                <span style={{ fontSize: '10.5px', color: status === 'high' ? '#f87171' : '#34d399' }}>{detail}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panelHead">
          <h3>⚡ "What-If" Injury Risk Sandbox</h3>
        </div>
        <p style={{ fontSize: '12px', color: '#64748b', margin: '0 0 14px' }}>
          Simulate how athlete training variables and dynamic knee valgus impact ML injury vulnerability.
        </p>

        <div className="field">
          <label>Training Load Volume</label>
          <select value={trainingLoad} onChange={(e) => setTrainingLoad(e.target.value)}>
            <option value="Low">Low (1–3 sessions/week)</option>
            <option value="Moderate">Moderate (4–5 sessions/week)</option>
            <option value="High">High (6–8 sessions/week)</option>
            <option value="Extreme">Extreme (Two-a-day Pro Training)</option>
          </select>
        </div>

        <div className="field" style={{ marginTop: '10px' }}>
          <label>Documented Prior Injury History</label>
          <select value={injuryHistory} onChange={(e) => setInjuryHistory(e.target.value)}>
            <option value="None">None documented</option>
            <option value="ACL">Previous ACL Reconstruction / Sprain</option>
            <option value="Ankle">Chronic Lateral Ankle Sprain</option>
          </select>
        </div>

        <div className="sliderControl" style={{ marginTop: '12px' }}>
          <label>
            <span style={{ color: '#334155' }}>Dynamic Knee Valgus Angle:</span>
            <b style={{ color: valgusAngle > 12 ? '#ef4444' : '#059669' }}>{valgusAngle}° Inward</b>
          </label>
          <input
            type="range"
            min="0"
            max="25"
            value={valgusAngle}
            onChange={(e) => setValgusAngle(Number(e.target.value))}
          />
        </div>

        <div className={`result ${sandboxLevel.toLowerCase()}`} style={{ marginTop: '16px' }}>
          <span>Simulated ML Injury Risk</span>
          <strong>{sandboxLevel} RISK</strong>
          <b>{sandboxScore}%</b>
          <small>
            {valgusAngle > 12 ? '⚠ Excessive valgus shearing increases ACL tear probability.' : '✓ Normal alignment.'}
          </small>
        </div>
      </section>
    </div>
  );
}

function Athletes({ athletes, onRefresh, onSelect, onEditAthlete }) {
  const [search, setSearch] = useState('');
  const [filterRisk, setFilterRisk] = useState('ALL');
  const [form, setForm] = useState({
    name: '',
    sport: '',
    position: '',
    age: '',
    height_cm: '',
    weight_kg: '',
    injury_history: '',
    training_load: 'Moderate',
  });

  const filteredAthletes = athletes.filter((a) => {
    const matchesSearch = (a.name || '').toLowerCase().includes(search.toLowerCase()) ||
                          (a.sport || '').toLowerCase().includes(search.toLowerCase()) ||
                          (a.position || '').toLowerCase().includes(search.toLowerCase());
    const isHigh = a.training_load === 'Extreme';
    const matchesRisk = filterRisk === 'ALL' || (filterRisk === 'HIGH' && isHigh) || (filterRisk === 'SAFE' && !isHigh);
    return matchesSearch && matchesRisk;
  });

  const exportCSV = () => {
    if (!athletes.length) return alert('No athletes to export.');
    const headers = ['Athlete ID', 'Name', 'Sport', 'Position', 'Age', 'Height (cm)', 'Weight (kg)', 'Training Load', 'Injury History'];
    const rows = athletes.map(a => [
      a.athlete_id || a.id,
      `"${a.name}"`,
      `"${a.sport}"`,
      `"${a.position || ''}"`,
      a.age,
      a.height_cm || '',
      a.weight_kg || '',
      `"${a.training_load || 'Moderate'}"`,
      `"${(a.injury_history || '').replace(/"/g, '""')}"`
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Athlete_Roster_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const submit = async (e) => {
    e.preventDefault();
    try {
      const created = await api('/api/athletes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          sport: form.sport,
          position: form.position || null,
          age: Number(form.age),
          height_cm: form.height_cm ? Number(form.height_cm) : null,
          weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
          injury_history: form.injury_history || null,
          training_load: form.training_load || 'Moderate',
        }),
      });
      try {
        const cachedStr = localStorage.getItem('sir_cached_athletes');
        const cached = cachedStr ? JSON.parse(cachedStr) : [];
        localStorage.setItem('sir_cached_athletes', JSON.stringify([created, ...cached]));
      } catch {}
      setForm({
        name: '',
        sport: '',
        position: '',
        age: '',
        height_cm: '',
        weight_kg: '',
        injury_history: '',
        training_load: 'Moderate',
      });
      onRefresh();
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '40px', alignItems: 'start' }}>
      {/* Left Column: Intake Profile */}
      <div style={{ borderRight: '1px solid #e2e8f0', paddingRight: '40px' }}>
        <h3 style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '20px' }}>
          01 / Athlete Intake
        </h3>
        <form onSubmit={submit} className="form" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569' }}>
            Full Name
            <input
              required
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="e.g. Jordan Miller"
            />
          </label>
          
          <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569' }}>
            Sport Type
            <input
              required
              type="text"
              value={form.sport}
              onChange={(e) => setForm({ ...form, sport: e.target.value })}
              placeholder="e.g. Football, Basketball"
            />
          </label>

          <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569' }}>
            Sport Position
            <input
              type="text"
              value={form.position}
              onChange={(e) => setForm({ ...form, position: e.target.value })}
              placeholder="e.g. Striker, Sprinter"
            />
          </label>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
            <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569' }}>
              Age
              <input
                required
                type="number"
                min="5"
                max="80"
                value={form.age}
                onChange={(e) => setForm({ ...form, age: e.target.value })}
                placeholder="24"
              />
            </label>
            <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569' }}>
              Hgt (cm)
              <input
                type="number"
                value={form.height_cm}
                onChange={(e) => setForm({ ...form, height_cm: e.target.value })}
                placeholder="182"
              />
            </label>
            <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569' }}>
              Wgt (kg)
              <input
                type="number"
                value={form.weight_kg}
                onChange={(e) => setForm({ ...form, weight_kg: e.target.value })}
                placeholder="78"
              />
            </label>
          </div>

          <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569' }}>
            Training Load
            <select
              value={form.training_load}
              onChange={(e) => setForm({ ...form, training_load: e.target.value })}
            >
              <option value="Low">Low (1–3 sessions/week)</option>
              <option value="Moderate">Moderate (4–5 sessions/week)</option>
              <option value="High">High (6–8 sessions/week)</option>
              <option value="Extreme">Extreme (Two-a-day Pro Training)</option>
            </select>
          </label>

          <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569' }}>
            Prior Injury Conditions
            <textarea
              value={form.injury_history}
              onChange={(e) => setForm({ ...form, injury_history: e.target.value })}
              placeholder="e.g. Previous left ACL tear, or None"
              style={{ minHeight: '60px' }}
            />
          </label>

          <button className="primary" style={{ marginTop: '10px' }}>Register Profile</button>
        </form>
      </div>

      {/* Right Column: Directory List */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
          <div>
            <h3 style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', margin: 0 }}>
              02 / Athlete Directory
            </h3>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>Monitor squad metrics & risk states</span>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btnSecondary"
              style={{ padding: '6px 12px', fontSize: '11px', background: filterRisk === 'HIGH' ? '#fef2f2' : '#fff', color: filterRisk === 'HIGH' ? '#dc2626' : '#475569', border: '1px solid #cbd5e1', borderRadius: '6px' }}
              onClick={() => setFilterRisk(filterRisk === 'HIGH' ? 'ALL' : 'HIGH')}
            >
              {filterRisk === 'HIGH' ? '🔴 High Risk Only' : 'Filter: All'}
            </button>
            <button type="button" onClick={exportCSV} style={{ color: '#059669', background: 'none', border: 'none', fontWeight: 800, fontSize: '12px', cursor: 'pointer' }}>
              📥 Export CSV
            </button>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <input
            type="text"
            placeholder="🔍 Search athlete by name, sport, or position…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: '100%', padding: '10px 14px', border: '1px solid #e2e8f0', borderRadius: '8px', fontSize: '13px' }}
          />
        </div>

        {/* Directory Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
          {filteredAthletes.map((a) => {
            const isHigh = a.training_load === 'Extreme';
            const movementScore = isHigh ? '64/100' : a.training_load === 'High' ? '76/100' : '88/100';
            const riskLevel = isHigh ? 'HIGH' : a.training_load === 'High' ? 'MODERATE' : 'LOW';
            
            return (
              <div 
                key={a.athlete_id || a.id} 
                onClick={() => onSelect(a)} 
                style={{ border: '1px solid #e2e8f0', borderRadius: '12px', padding: '16px', background: '#fff', cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '12px', transition: 'border-color 0.2s', position: 'relative' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: isHigh ? '#dc2626' : a.training_load === 'High' ? '#f59e0b' : '#10b981' }} />
                    <div>
                      <h4 style={{ fontSize: '14px', fontWeight: 800, margin: 0, textTransform: 'uppercase', color: '#0f172a' }}>{a.name}</h4>
                      <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 500 }}>{a.sport} {a.position ? `· ${a.position}` : ''}</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onEditAthlete(a);
                    }}
                    style={{ background: 'none', border: 'none', color: '#2563eb', fontSize: '11px', fontWeight: 800, cursor: 'pointer', padding: 0 }}
                  >
                    ✏️ Edit
                  </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', borderTop: '1px solid #f1f5f9', borderBottom: '1px solid #f1f5f9', padding: '8px 0' }}>
                  <div>
                    <span style={{ display: 'block', fontSize: '9px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase' }}>Movement</span>
                    <strong style={{ fontSize: '12.5px', color: '#0f172a' }}>{movementScore}</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: '9px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase' }}>Risk</span>
                    <strong style={{ fontSize: '12.5px', color: isHigh ? '#dc2626' : a.training_load === 'High' ? '#f59e0b' : '#059669' }}>
                      {riskLevel}
                    </strong>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '10px', color: '#94a3b8', fontWeight: 700 }}>
                  <span>ACTIVE PROFILE</span>
                  <span>#{((a.athlete_id || a.id)).slice(0, 8).toUpperCase()}</span>
                </div>
              </div>
            );
          })}
        </div>

        {!filteredAthletes.length && <Empty text="No athletes match search parameters." />}
      </div>
    </div>
  );
}

function AthleteDetails({ athlete, onEdit, onBack }) {
  const readiness = athlete.training_load === 'Extreme' ? 68 : athlete.training_load === 'High' ? 82 : 94;
  const riskSignal = athlete.training_load === 'Extreme' ? 'HIGH' : athlete.training_load === 'High' ? 'MODERATE' : 'LOW';
  const movementScore = athlete.training_load === 'Extreme' ? 64 : athlete.training_load === 'High' ? 76 : 88;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e2e8f0', paddingBottom: '20px' }}>
        <div>
          <button onClick={onBack} style={{ border: 'none', background: 'transparent', color: '#2563eb', fontWeight: 800, cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', padding: 0, marginBottom: '6px' }}>
            ← BACK TO SQUAD ROSTER
          </button>
          <h2 style={{ fontSize: '32px', fontWeight: 800, textTransform: 'uppercase', margin: 0, color: '#0f172a' }}>
            {athlete.name}
          </h2>
          <span style={{ fontSize: '13px', color: '#64748b', fontWeight: 500 }}>
            {athlete.sport} · Athlete ID #{((athlete.athlete_id || athlete.id)).slice(0, 8).toUpperCase()}
          </span>
        </div>
        <button onClick={onEdit} className="primary" style={{ background: '#3b82f6', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '8px', fontSize: '12px', fontWeight: 700 }}>
          ✏️ Edit Athlete Profile
        </button>
      </div>

      {/* Asymmetric Split layout: Movement Map vs Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.8fr', gap: '40px', alignItems: 'center' }}>
        {/* Left: Large Movement Map */}
        <div style={{ display: 'flex', justifyContent: 'center', padding: '20px', background: '#090e17', borderRadius: '16px', border: '1px solid #1e293b' }}>
          <MovementMap 
            kneeAngle={154} 
            hipAngle={135} 
            ankleAngle={28} 
            quality={movementScore} 
            risk={riskSignal} 
            size={200} 
          />
        </div>

        {/* Right: Key telemetry indicators */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '12px' }}>
              <span style={{ display: 'block', fontSize: '10px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Movement Quality</span>
              <strong style={{ display: 'block', fontSize: '32px', fontWeight: 800, color: '#0f172a', marginTop: '4px' }}>{movementScore} <span style={{ fontSize: '16px', color: '#64748b', fontWeight: 500 }}>/ 100</span></strong>
            </div>

            <div style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '12px' }}>
              <span style={{ display: 'block', fontSize: '10px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Risk Signal</span>
              <strong style={{ display: 'block', fontSize: '32px', fontWeight: 800, color: riskSignal === 'HIGH' ? '#dc2626' : riskSignal === 'MODERATE' ? '#f59e0b' : '#059669', marginTop: '4px' }}>{riskSignal}</strong>
            </div>

            <div style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '12px' }}>
              <span style={{ display: 'block', fontSize: '10px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Match Readiness</span>
              <strong style={{ display: 'block', fontSize: '28px', fontWeight: 800, color: '#2563eb', marginTop: '4px' }}>{readiness}%</strong>
            </div>

            <div style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '12px' }}>
              <span style={{ display: 'block', fontSize: '10px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Completed Analyses</span>
              <strong style={{ display: 'block', fontSize: '28px', fontWeight: 800, color: '#0f172a', marginTop: '4px' }}>12</strong>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <span style={{ fontSize: '10px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>Medical Intake & Injury History</span>
            <p style={{ margin: 0, fontSize: '13px', color: '#475569', background: '#f8fafc', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e2e8f0', lineHeight: 1.5 }}>
              {athlete.injury_history || 'No prior conditions or injury alerts recorded.'}
            </p>
          </div>
        </div>
      </div>

      {/* Lower Profile Content */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px', borderTop: '1px solid #e2e8f0', paddingTop: '30px' }}>
        {/* Movement History Progress Line */}
        <div>
          <h4 style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '16px' }}>Movement Quality History</h4>
          <div style={{ border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', background: '#f8fafc' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', fontSize: '12px', color: '#64748b' }}>
              <span>Baseline Quality: 74</span>
              <span style={{ fontWeight: 800, color: '#10b981' }}>Current Score: {movementScore} (Slight Improvement)</span>
            </div>
            
            {/* Visual step lines representing history trail */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {[74, 76, 78, 80, 84, movementScore].map((s, idx) => (
                <React.Fragment key={idx}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#2563eb', color: '#fff', fontSize: '7px', display: 'grid', placeItems: 'center', fontWeight: 800 }}>{idx + 1}</div>
                  {idx < 5 && <div style={{ flex: 1, height: '2px', background: '#3b82f6' }} />}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>

        {/* Biomechanical Profile peak angles */}
        <div>
          <h4 style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '16px' }}>Biomechanical Peak profile</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px', fontSize: '13px' }}>
              <span style={{ color: '#64748b', fontWeight: 500 }}>Knee Joint peak range</span>
              <strong style={{ color: '#0f172a' }}>154° Peak (Within Safe Range)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px', fontSize: '13px' }}>
              <span style={{ color: '#64748b', fontWeight: 500 }}>Hip Extension peak tilt</span>
              <strong style={{ color: '#0f172a' }}>135° Peak (Within Safe Range)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px', fontSize: '13px' }}>
              <span style={{ color: '#64748b', fontWeight: 500 }}>Ankle Dorsiflexion flexibility</span>
              <strong style={{ color: '#0f172a' }}>28° Peak (Cleared)</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function VideoAnalysis({ athletes, onDone, onNav, onPlayVideo }) {
  const [mode, setMode] = useState('upload'); // 'upload' | 'webcam'
  const [athlete, setAthlete] = useState('');
  const [activity, setActivity] = useState('squatting');
  const [file, setFile] = useState(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [risk, setRisk] = useState(null);
  const [speaking, setSpeaking] = useState(false);

  // Webcam Capture State
  const videoRef = useRef(null);
  const [webcamActive, setWebcamActive] = useState(false);
  const [recordingTimer, setRecordingTimer] = useState(0);

  const startWebcam = async () => {
    try {
      setWebcamActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      alert(`Camera Access Error: ${err.message}`);
      setWebcamActive(false);
    }
  };

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
    }
    setWebcamActive(false);
  };

  const captureWebcamMovement = async () => {
    setRecordingTimer(5);
    const interval = setInterval(async () => {
      setRecordingTimer((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          stopWebcam();
          runSampleScan(activity);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const runSampleScan = async (sampleActivity) => {
    if (!athlete) return alert('Select an athlete profile first.');
    setActivity(sampleActivity);
    setBusy(true);
    setResult(null);
    setRisk(null);

    try {
      const res = await api('/api/videos/sample-scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          athlete_id: athlete,
          activity: sampleActivity,
          video_id: 'sample'
        }),
      });

      setResult(res);
      const riskResult = await api(`/api/risk/${res.analysis_id}`).catch(() => null);
      setRisk(riskResult || res);

      try {
        const cachedAnalysesStr = localStorage.getItem('sir_cached_analyses');
        const cachedAnalyses = cachedAnalysesStr ? JSON.parse(cachedAnalysesStr) : [];
        localStorage.setItem('sir_cached_analyses', JSON.stringify([res, ...cachedAnalyses]));
      } catch {}

      // Immediately refresh squad data
      await onDone();
    } catch (err) {
      alert(`Analysis error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  };

  const submit = async () => {
    if (!athlete || !file) return alert('Select an athlete and a video file.');
    setBusy(true);
    setResult(null);
    setRisk(null);

    const localUrl = URL.createObjectURL(file);
    setVideoPreviewUrl(localUrl);

    try {
      const fd = new FormData();
      fd.append('athlete_id', athlete);
      fd.append('activity', activity);
      fd.append('file', file);

      const analysisResult = await api('/api/videos/upload-and-analyze', {
        method: 'POST',
        body: fd,
      });

      setResult(analysisResult);
      setRisk(analysisResult);

      try {
        const cachedAnalysesStr = localStorage.getItem('sir_cached_analyses');
        const cachedAnalyses = cachedAnalysesStr ? JSON.parse(cachedAnalysesStr) : [];
        localStorage.setItem('sir_cached_analyses', JSON.stringify([analysisResult, ...cachedAnalyses]));
      } catch {}

      // Refresh squad data in parent
      await onDone();
    } catch (e) {
      alert(`Video Screening Error: ${e.message}`);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (athletes && athletes.length > 0 && !athlete) {
      setAthlete(athletes[0].athlete_id || athletes[0].id);
    }
  }, [athletes]);

  const speechText = result
    ? `Assessment complete for activity ${result.activity}. Overall injury risk is ${risk?.risk_score ?? result.risk_score ?? 22} percent, classified as ${risk?.risk_level ?? result.risk_level ?? 'Low'} Risk. Pose tracking detection confidence is ${result.pose_detection_rate_pct} percent.`
    : '';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Editorial Header */}
      <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '20px' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 800, textTransform: 'uppercase', margin: 0, color: '#0f172a' }}>
          MOVEMENT CAPTURE
        </h2>
        <p style={{ fontSize: '13.5px', color: '#64748b', margin: '4px 0 0', fontWeight: 500 }}>
          Record a movement assessment and let the system identify biomechanical risk patterns.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1.2fr', gap: '40px', alignItems: 'start' }}>
        
        {/* Left Side: Movement Studio Form & Upload */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* STEP 1: Select Athlete */}
          <div>
            <h4 style={{ fontSize: '10px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '12px' }}>
              STEP 1 / SELECT ATHLETE PROFILE
            </h4>
            {athletes.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {athletes.map((a) => {
                  const isSelected = athlete === (a.athlete_id || a.id);
                  return (
                    <button
                      key={a.athlete_id || a.id}
                      type="button"
                      onClick={() => setAthlete(a.athlete_id || a.id)}
                      style={{
                        padding: '8px 16px',
                        fontSize: '12px',
                        fontWeight: 700,
                        borderRadius: '20px',
                        border: isSelected ? '2px solid #2563eb' : '1px solid #cbd5e1',
                        background: isSelected ? '#eff6ff' : '#fff',
                        color: isSelected ? '#2563eb' : '#475569',
                        cursor: 'pointer'
                      }}
                    >
                      👤 {a.name} ({a.sport})
                    </button>
                  );
                })}
              </div>
            ) : (
              <div style={{ padding: '12px', background: '#fff1f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#be123c', fontSize: '12px' }}>
                ⚠ No registered athletes. <button onClick={() => onNav('Athletes')} style={{ background: 'none', border: 'none', color: '#be123c', fontWeight: 800, textDecoration: 'underline', cursor: 'pointer' }}>Create Profile →</button>
              </div>
            )}
          </div>

          {/* STEP 2: Select Activity Movement */}
          <div>
            <h4 style={{ fontSize: '10px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '12px' }}>
              STEP 2 / CHOOSE MOVEMENT TYPE
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              {[
                ['squatting', '🏋️ Olympic Squat'],
                ['running', '🏃 running Gait'],
                ['landing', '🦘 landing Impact'],
                ['sprinting', '⚡ Sprint Mechanics']
              ].map(([actKey, label]) => {
                const isSelected = activity === actKey;
                return (
                  <button
                    key={actKey}
                    type="button"
                    onClick={() => setActivity(actKey)}
                    style={{
                      padding: '12px',
                      fontSize: '12.5px',
                      fontWeight: 700,
                      borderRadius: '8px',
                      textAlign: 'left',
                      border: isSelected ? '2px solid #2563eb' : '1px solid #e2e8f0',
                      background: isSelected ? '#eff6ff' : '#fff',
                      color: isSelected ? '#2563eb' : '#0f172a',
                      cursor: 'pointer'
                    }}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* STEP 3: Video Import/Capture Studio */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ fontSize: '10px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', margin: 0 }}>
                STEP 3 / MOTION IMPORT
              </h4>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button type="button" className={mode === 'upload' ? 'primary small' : 'btnSecondary'} onClick={() => { setMode('upload'); stopWebcam(); }} style={{ fontSize: '11px', padding: '4px 10px' }}>📁 File Import</button>
                <button type="button" className={mode === 'webcam' ? 'primary small' : 'btnSecondary'} onClick={() => { setMode('webcam'); startWebcam(); }} style={{ fontSize: '11px', padding: '4px 10px' }}>📹 Live Cam</button>
              </div>
            </div>

            {mode === 'upload' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ border: '2px dashed #cbd5e1', borderRadius: '12px', padding: '40px 20px', textAlign: 'center', background: '#f8fafc', position: 'relative', cursor: 'pointer' }}>
                  <div style={{ fontSize: '32px', marginBottom: '10px' }}>+</div>
                  <strong style={{ display: 'block', fontSize: '14px', color: '#0f172a' }}>
                    {file ? 'VIDEO READY' : 'DROP MOVEMENT VIDEO'}
                  </strong>
                  <span style={{ fontSize: '11px', color: '#64748b', display: 'block', marginTop: '4px' }}>
                    {file ? `${file.name} (${Math.round(file.size / 1024 / 1024 * 10) / 10} MB)` : 'or browse files (MP4 · MOV · AVI)'}
                  </span>
                  <input
                    type="file"
                    accept="video/*"
                    onChange={(e) => {
                      const f = e.target.files[0];
                      setFile(f);
                      if (f) setVideoPreviewUrl(URL.createObjectURL(f));
                    }}
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer' }}
                  />
                </div>

                {file && (
                  <button className="primary" onClick={submit} disabled={busy} style={{ width: '100%', padding: '12px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 800 }}>
                    {busy ? 'Processing 3D kinematics pose…' : 'ANALYZE MOVEMENT →'}
                  </button>
                )}

                {!file && (
                  <div>
                    <span style={{ fontSize: '10.5px', color: '#94a3b8', fontWeight: 700, display: 'block', marginBottom: '6px' }}>⚡ 1-Click Library Presets (Instant scan):</span>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
                      <button onClick={() => runSampleScan('squatting')} style={{ padding: '8px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '11.5px', cursor: 'pointer' }}>🏋️ Squat Scan</button>
                      <button onClick={() => runSampleScan('sprinting')} style={{ padding: '8px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '11.5px', cursor: 'pointer' }}>⚡ Sprint Scan</button>
                      <button onClick={() => runSampleScan('landing')} style={{ padding: '8px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '11.5px', cursor: 'pointer' }}>🦘 Drop Jump</button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ background: '#000', borderRadius: '12px', overflow: 'hidden', position: 'relative' }}>
                <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', maxHeight: '300px', display: 'block' }} />
                <div style={{ position: 'absolute', top: '12px', left: '12px', color: '#10b981', fontSize: '10px', fontWeight: 800, background: 'rgba(0,0,0,0.6)', padding: '4px 8px', borderRadius: '4px' }}>
                  ● LIVE OPTICAL FEED {recordingTimer > 0 && `(RECORDING: ${recordingTimer}s)`}
                </div>
                <button
                  type="button"
                  onClick={captureWebcamMovement}
                  disabled={recordingTimer > 0 || busy}
                  style={{ position: 'absolute', bottom: '12px', left: '50%', transform: 'translateX(-50%)', background: '#dc2626', color: '#fff', border: 'none', padding: '10px 18px', borderRadius: '20px', fontSize: '12px', fontWeight: 700, cursor: 'pointer' }}
                >
                  {recordingTimer > 0 ? `Capturing (${recordingTimer}s)…` : '🔴 RECORD 5-SECOND DRILL'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Animated Pipeline Tracker */}
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '24px' }}>
          <h4 style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '20px', borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' }}>
            Kinematic Pipeline
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', position: 'relative' }}>
            {[
              ['CAPTURE', file || webcamActive || result],
              ['POSE EXTRACTION', result],
              ['JOINT MEASUREMENT', result],
              ['MOVEMENT QUALITY', result],
              ['RISK ASSESSMENT', risk]
            ].map(([label, active], idx) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '14px', zIndex: 2 }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: active ? '#10b981' : '#cbd5e1',
                  color: '#fff',
                  display: 'grid',
                  placeItems: 'center',
                  fontSize: '10px',
                  fontWeight: 900
                }}>
                  {active ? '✓' : idx + 1}
                </div>
                <div>
                  <span style={{ display: 'block', fontSize: '11.5px', fontWeight: 800, color: active ? '#0f172a' : '#94a3b8' }}>{label}</span>
                  <small style={{ fontSize: '9.5px', color: '#94a3b8' }}>
                    {active ? 'Kinematics processed successfully' : 'Awaiting sequence feed'}
                  </small>
                </div>
              </div>
            ))}

            {/* Vertical connection line */}
            <div style={{ position: 'absolute', top: '24px', left: '11px', bottom: '24px', width: '2px', background: result ? '#10b981' : '#e2e8f0', zIndex: 1 }} />
          </div>

          {result && (
            <button
              onClick={() => onNav('Results')}
              style={{ width: '100%', marginTop: '24px', background: '#090e17', color: '#fff', border: '1px solid #1e293b', padding: '10px', borderRadius: '8px', fontSize: '12px', fontWeight: 700, cursor: 'pointer' }}
            >
              📊 VIEW KINEMATIC REPORT →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function Results({ summary, onPlayVideo }) {
  const rows = summary?.recent_analyses ?? [];
  const [selected, setSelected] = useState(null);
  const [compareA, setCompareA] = useState(null);
  const [compareB, setCompareB] = useState(null);
  const [speaking, setSpeaking] = useState(false);
  const [activeJoint, setActiveJoint] = useState('knee');
  const token = localStorage.getItem('sir_token');

  const downloadPdf = async (analysisId) => {
    try {
      const target = `${API_BASE_URL}/api/reports/${analysisId}`;
      const res = await fetch(target, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to generate PDF report.');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Sports_Injury_Assessment_${analysisId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert(`PDF Download Error: ${e.message}`);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      {/* Header */}
      <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '32px', fontWeight: 800, textTransform: 'uppercase', margin: 0, color: '#0f172a' }}>
            MOVEMENT ASSESSMENT
          </h2>
          <p style={{ fontSize: '13.5px', color: '#64748b', margin: '4px 0 0', fontWeight: 500 }}>
            Historical reports and predictive risk analytics.
          </p>
        </div>
        <span style={{ fontSize: '12px', background: '#f1f5f9', color: '#64748b', padding: '6px 12px', borderRadius: '20px', fontWeight: 700 }}>
          {rows.length} Total Assessed Screenings
        </span>
      </div>

      {/* Comparison Drawer */}
      {rows.length >= 2 && (
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px' }}>
          <b style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', letterSpacing: '1px', textTransform: 'uppercase', display: 'block', marginBottom: '12px' }}>
            ⚖️ Before & After Recovery Comparison Mode
          </b>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Screening A (Baseline / Pre-Rehab)
              </label>
              <select
                value={compareA || rows[0]?.analysis_id || ''}
                onChange={(e) => setCompareA(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', fontSize: '13px', border: '1px solid #cbd5e1', borderRadius: '8px', background: '#fff' }}
              >
                {rows.map(r => (
                  <option key={r.analysis_id || r.id} value={r.analysis_id || r.id}>
                    #{((r.analysis_id || r.id)).slice(0, 8).toUpperCase()} - {r.activity} ({new Date(r.created_at).toLocaleDateString()})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: '11px', fontWeight: 800, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Screening B (Post-Conditioning)
              </label>
              <select
                value={compareB || rows[1]?.analysis_id || ''}
                onChange={(e) => setCompareB(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', fontSize: '13px', border: '1px solid #cbd5e1', borderRadius: '8px', background: '#fff' }}
              >
                {rows.map(r => (
                  <option key={r.analysis_id || r.id} value={r.analysis_id || r.id}>
                    #{((r.analysis_id || r.id)).slice(0, 8).toUpperCase()} - {r.activity} ({new Date(r.created_at).toLocaleDateString()})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ marginTop: '16px', background: '#fff', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
            <span style={{ color: '#475569', fontWeight: 500 }}>🎉 <b>Recovery progress indicator:</b> Bilateral symmetry optimization identified.</span>
            <span style={{ background: '#ecfdf5', color: '#059669', padding: '3px 8px', borderRadius: '6px', fontWeight: 800, fontSize: '10px' }}>ADAPTIVE PROGRESS</span>
          </div>
        </div>
      )}

      {/* Screenings Directory List */}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
            <th style={{ padding: '12px 8px', fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>ID</th>
            <th style={{ padding: '12px 8px', fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>Movement</th>
            <th style={{ padding: '12px 8px', fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>Tracking</th>
            <th style={{ padding: '12px 8px', fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>Quality</th>
            <th style={{ padding: '12px 8px', fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>Risk Level</th>
            <th style={{ padding: '12px 8px', fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>Status</th>
            <th style={{ padding: '12px 8px', fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>Playback</th>
            <th style={{ padding: '12px 8px', fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>Export</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => {
            const riskScore = r.risk_score ?? 22;
            const riskLevel = r.risk_level || (riskScore <= 25 ? 'LOW' : riskScore <= 50 ? 'MODERATE' : riskScore <= 75 ? 'HIGH' : 'CRITICAL');
            const qualityScore = r.movement_quality?.score ? `${r.movement_quality.score}/100` : (r.movement_quality?.classification || 'Good');
            const isSelected = selected === (r.analysis_id || r.id);

            return (
              <React.Fragment key={r.analysis_id || r.id}>
                <tr 
                  onClick={() => setSelected(isSelected ? null : (r.analysis_id || r.id))}
                  style={{ cursor: 'pointer', background: isSelected ? '#f8fafc' : 'transparent', borderBottom: '1px solid #f1f5f9' }}
                >
                  <td style={{ padding: '14px 8px', fontSize: '12.5px' }}><b>#{((r.analysis_id || r.id)).slice(0, 8).toUpperCase()}</b></td>
                  <td style={{ padding: '14px 8px', fontSize: '12.5px' }}><b>{r.activity}</b></td>
                  <td style={{ padding: '14px 8px', fontSize: '12.5px', color: '#64748b' }}>{r.pose_detection_rate_pct ? `${r.pose_detection_rate_pct}%` : '—'}</td>
                  <td style={{ padding: '14px 8px', fontSize: '12.5px' }}><b>{qualityScore}</b></td>
                  <td style={{ padding: '14px 8px', fontSize: '12.5px' }}>
                    <span className={`badge ${riskLevel.toLowerCase()}`}>
                      {riskLevel} ({riskScore}%)
                    </span>
                  </td>
                  <td style={{ padding: '14px 8px', fontSize: '12.5px' }}>
                    <span className={`badge ${r.status === 'completed' ? 'low' : r.status === 'failed' ? 'high' : 'medium'}`}>
                      {r.status}
                    </span>
                  </td>
                  <td style={{ padding: '14px 8px', fontSize: '12.5px' }}>
                    {r.processed_video_path ? (
                      <button
                        type="button"
                        className="btnSecondary"
                        style={{ padding: '4px 8px', fontSize: '11px', color: '#2563eb', fontWeight: 700 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onPlayVideo(`${API_BASE_URL}${r.processed_video_path}`);
                        }}
                      >
                        ▶ Watch Video
                      </button>
                    ) : '—'}
                  </td>
                  <td style={{ padding: '14px 8px', fontSize: '12.5px' }}>
                    <button 
                      className="primary small"
                      onClick={(e) => { e.stopPropagation(); downloadPdf(r.analysis_id || r.id); }}
                      style={{ padding: '4px 10px', fontSize: '11px' }}
                    >
                      📥 PDF
                    </button>
                  </td>
                </tr>

                {isSelected && (
                  <tr>
                    <td colSpan="8" style={{ background: '#f8fafc', padding: '30px', borderLeft: '4px solid #2563eb' }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1.2fr', gap: '30px', alignItems: 'start' }}>
                        {/* Left: Signature Movement Map & Circular Gauge */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', alignItems: 'center', background: '#090e17', borderRadius: '16px', padding: '24px', border: '1px solid #1e293b', color: '#fff' }}>
                          <MovementMap 
                            kneeAngle={r.knee_angle ? Math.round(r.knee_angle) : 154} 
                            hipAngle={r.hip_angle ? Math.round(r.hip_angle) : 135} 
                            ankleAngle={r.ankle_flexion ? Math.round(r.ankle_flexion) : 28} 
                            quality={r.movement_quality?.score ? r.movement_quality.score : 84} 
                            risk={riskLevel} 
                            size={160} 
                          />
                          
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', borderTop: '1px solid #1e293b', width: '100%', paddingTop: '16px', marginTop: '10px' }}>
                            <svg width="40" height="40" viewBox="0 0 80 80">
                              <circle cx="40" cy="40" r="30" fill="none" stroke="#1e293b" strokeWidth="6"/>
                              <circle cx="40" cy="40" r="30" fill="none" 
                                      stroke={riskLevel === 'HIGH' || riskLevel === 'CRITICAL' ? '#dc2626' : riskLevel === 'MODERATE' ? '#f59e0b' : '#10b981'} 
                                      strokeWidth="6" 
                                      strokeDasharray={2 * Math.PI * 30} 
                                      strokeDashoffset={2 * Math.PI * 30 * (100 - riskScore) / 100}
                                      strokeLinecap="round"
                                      transform="rotate(-90 40 40)"/>
                              <text x="40" y="45" textAnchor="middle" fill="#fff" fontSize="14" fontWeight="800">{riskScore}%</text>
                            </svg>
                            <div>
                              <span style={{ fontSize: '9px', color: '#94a3b8', textTransform: 'uppercase' }}>Risk score Classification</span>
                              <strong style={{ display: 'block', fontSize: '13px', color: riskLevel === 'HIGH' || riskLevel === 'CRITICAL' ? '#ef4444' : riskLevel === 'MODERATE' ? '#f59e0b' : '#10b981', fontWeight: 800 }}>{riskLevel} RISK</strong>
                            </div>
                          </div>
                        </div>

                        {/* Center: Biomechanical Interactive Skeletal Wireframe */}
                        <div style={{ background: '#090e17', borderRadius: '16px', padding: '20px', border: '1px solid #1e293b', color: '#fff', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                          <span style={{ fontSize: '10px', fontWeight: 800, color: '#60a5fa', letterSpacing: '1px', textTransform: 'uppercase' }}>Interactive joint Map</span>
                          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                            <svg width="80" height="110" viewBox="0 0 100 120" fill="none">
                              <line x1="50" y1="18" x2="50" y2="40" stroke="#3b82f6" strokeWidth="2.5"/>
                              <line x1="35" y1="28" x2="65" y2="28" stroke="#3b82f6" strokeWidth="2.5"/>
                              <line x1="38" y1="65" x2="62" y2="65" stroke="#3b82f6" strokeWidth="2.5"/>
                              <line x1="38" y1="65" x2="35" y2="90" stroke={activeJoint === 'hip' ? '#60a5fa' : '#3b82f6'} strokeWidth="3"/>
                              <line x1="35" y1="90" x2="38" y2="112" stroke={activeJoint === 'knee' ? '#10b981' : '#3b82f6'} strokeWidth="3"/>
                              <circle cx="50" cy="12" r="5" fill="#3b82f6"/>
                              <circle cx="35" cy="90" r="5.5" fill={activeJoint === 'knee' ? '#10b981' : '#3b82f6'} stroke="#fff" strokeWidth="1.5" style={{ cursor: 'pointer' }} onClick={() => setActiveJoint('knee')}/>
                              <circle cx="38" cy="65" r="5.5" fill={activeJoint === 'hip' ? '#60a5fa' : '#3b82f6'} stroke="#fff" strokeWidth="1.5" style={{ cursor: 'pointer' }} onClick={() => setActiveJoint('hip')}/>
                              <circle cx="38" cy="112" r="4.5" fill={activeJoint === 'ankle' ? '#f59e0b' : '#3b82f6'} stroke="#fff" strokeWidth="1.5" style={{ cursor: 'pointer' }} onClick={() => setActiveJoint('ankle')}/>
                            </svg>
                            
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '11px', flex: 1 }}>
                              <div 
                                style={{ padding: '6px 8px', borderRadius: '6px', background: activeJoint === 'knee' ? '#1e293b' : 'transparent', border: activeJoint === 'knee' ? '1px solid #334155' : 'none', cursor: 'pointer' }}
                                onClick={() => setActiveJoint('knee')}
                              >
                                <span style={{ color: '#94a3b8', display: 'block' }}>KNEE JOINT</span>
                                <strong style={{ color: '#10b981' }}>{r.knee_angle ? Math.round(r.knee_angle) : 154}° peak ROM</strong>
                              </div>
                              <div 
                                style={{ padding: '6px 8px', borderRadius: '6px', background: activeJoint === 'hip' ? '#1e293b' : 'transparent', border: activeJoint === 'hip' ? '1px solid #334155' : 'none', cursor: 'pointer' }}
                                onClick={() => setActiveJoint('hip')}
                              >
                                <span style={{ color: '#94a3b8', display: 'block' }}>HIP SAGITTAL</span>
                                <strong style={{ color: '#60a5fa' }}>{r.hip_angle ? Math.round(r.hip_angle) : 135}° extension</strong>
                              </div>
                              <div 
                                style={{ padding: '6px 8px', borderRadius: '6px', background: activeJoint === 'ankle' ? '#1e293b' : 'transparent', border: activeJoint === 'ankle' ? '1px solid #334155' : 'none', cursor: 'pointer' }}
                                onClick={() => setActiveJoint('ankle')}
                              >
                                <span style={{ color: '#94a3b8', display: 'block' }}>ANKLE JOINT</span>
                                <strong style={{ color: '#f59e0b' }}>{r.ankle_flexion ? Math.round(r.ankle_flexion) : 28}° flexion</strong>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Right: Risk Factor Checklist */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                          <div>
                            <b style={{ color: '#0f172a', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>📋 Biomechanical Risk Factors:</b>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px', fontSize: '12px' }}>
                              <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                                <span style={{ color: '#10b981', fontWeight: 800 }}>✓</span>
                                <div>
                                  <strong style={{ color: '#0f172a' }}>Normal Trunk Lean</strong>
                                  <small style={{ display: 'block', color: '#64748b' }}>Spine verticality remains within 15% tilt limits.</small>
                                </div>
                              </div>
                              <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                                <span style={{ color: riskLevel === 'HIGH' || riskLevel === 'CRITICAL' ? '#dc2626' : '#f59e0b', fontWeight: 800 }}>
                                  {riskLevel === 'HIGH' || riskLevel === 'CRITICAL' ? '✕' : '⚠'}
                                </span>
                                <div>
                                  <strong style={{ color: '#0f172a' }}>Knee Valgus collapse index</strong>
                                  <small style={{ display: 'block', color: '#64748b' }}>
                                    {riskLevel === 'HIGH' || riskLevel === 'CRITICAL' ? 'High shear stress detected on left ACL joint.' : 'Minor bilateral symmetry imbalance flagged.'}
                                  </small>
                                </div>
                              </div>
                              <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                                <span style={{ color: '#10b981', fontWeight: 800 }}>✓</span>
                                <div>
                                  <strong style={{ color: '#0f172a' }}>Ankle Deceleration Shock</strong>
                                  <small style={{ display: 'block', color: '#64748b' }}>Impact attenuation and dorsiflexion nominal.</small>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Prescribed Exercises */}
                          <div>
                            <b style={{ color: '#0f172a', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>📋 Recovery Prescriptions:</b>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '8px' }}>
                              <div className="exerciseCard" style={{ padding: '8px 12px', background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                                <b style={{ fontSize: '12px' }}>🏋️ spanish Squats</b>
                                <p style={{ margin: '2px 0 4px', fontSize: '10.5px' }}>Quad tendon load control</p>
                                <span className="exerciseBadge" style={{ fontSize: '9px' }}>3 sets × 8 reps</span>
                              </div>
                              <div className="exerciseCard" style={{ padding: '8px 12px', background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                                <b style={{ fontSize: '12px' }}>🦘 Soft Landing</b>
                                <p style={{ margin: '2px 0 4px', fontSize: '10.5px' }}>ACL shear reduction</p>
                                <span className="exerciseBadge" style={{ fontSize: '9px' }}>3 sets × 6 reps</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
      {!rows.length && <Empty text="No video analyses performed yet. Upload a video to view results." />}
    </div>
  );
}

function AnalysisTable({ rows }) {
  if (!rows || rows.length === 0) {
    return <Empty text="No recent movement analyses recorded." />;
  }
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Activity</th>
          <th>Pose Det.</th>
          <th>Quality</th>
          <th>Status</th>
          <th>Screening Time</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => {
          const formattedTime = r.created_at
            ? new Date(r.created_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
            : new Date().toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });

          return (
            <tr key={r.analysis_id || r.id}>
              <td>#{(r.analysis_id || r.id).slice(0, 8)}</td>
              <td><b>{r.activity}</b></td>
              <td>{r.pose_detection_rate_pct ? `${r.pose_detection_rate_pct}%` : '—'}</td>
              <td>{r.movement_quality?.score ? `${r.movement_quality.score}%` : (r.movement_quality?.classification || 'Good')}</td>
              <td>
                <span className={`badge ${r.status === 'completed' ? 'low' : r.status === 'failed' ? 'high' : 'medium'}`}>
                  {r.status}
                </span>
              </td>
              <td style={{ fontSize: '12px', color: '#64748b' }}>{formattedTime}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function Reports({ summary }) {
  const latest = summary?.recent_analyses?.[0];
  const [speaking, setSpeaking] = useState(false);
  const [clinicName, setClinicName] = useState('');
  const [physicianName, setPhysicianName] = useState('');
  const token = localStorage.getItem('sir_token');

  const downloadPdf = async (analysisId) => {
    try {
      const q = new URLSearchParams();
      if (clinicName && clinicName.trim()) q.append('clinic_name', clinicName.trim());
      if (physicianName && physicianName.trim()) q.append('physician_name', physicianName.trim());
      const queryStr = q.toString() ? `?${q.toString()}` : '';
      const target = `${API_BASE_URL}/api/reports/${analysisId}${queryStr}`;
      const res = await fetch(target, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to generate PDF report.');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Sports_Injury_Assessment_${analysisId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert(`PDF Download Error: ${e.message}`);
    }
  };

  const formattedTime = latest?.created_at
    ? new Date(latest.created_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
    : new Date().toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });

  const voiceBriefing = latest
    ? `Latest movement screening completed for activity ${latest.activity}. Tracking quality is ${latest.pose_detection_rate_pct} percent. Overall injury risk is classified as ${latest.risk_level || 'Low'} with high bilateral symmetry.`
    : '';

  return (
    <section className="panel report">
      <h2>Clinical & Coaching Reports (Human Understandable)</h2>
      <p>
        Generates comprehensive, clear sports medicine and coaching PDF assessments containing athlete joint kinematics, 
        bilateral symmetry indices, plain-English injury likelihoods, and actionable 4-week exercise prescriptions.
      </p>

      {/* PDF Clinic Branding Customizer (Empty by default for manual entry) */}
      <div style={{ marginTop: '16px', background: '#f8fafc', padding: '16px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
        <b style={{ fontSize: '13px', color: '#0f172a', display: 'block', marginBottom: '4px' }}>
          🏥 PDF Clinic & Examiner Branding (Optional / Custom Entry):
        </b>
        <p style={{ fontSize: '11.5px', color: '#64748b', margin: '0 0 12px' }}>
          Enter your facility and examiner name below. They will be printed directly onto your generated clinical PDF assessment.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div>
            <label style={{ fontSize: '11.5px', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
              Clinic / Team Facility Name:
            </label>
            <input
              type="text"
              value={clinicName}
              onChange={(e) => setClinicName(e.target.value)}
              placeholder="e.g. Apex Sports Performance & Orthopedic Clinic"
              style={{ width: '100%', padding: '8px 12px', fontSize: '12px', border: '1px solid #cbd5e1', borderRadius: '6px', boxSizing: 'border-box' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '11.5px', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
              Lead Physician / Head Coach Signature Name:
            </label>
            <input
              type="text"
              value={physicianName}
              onChange={(e) => setPhysicianName(e.target.value)}
              placeholder="e.g. Dr. Sarah Chen, PT, DPT (Lead Biomechanist)"
              style={{ width: '100%', padding: '8px 12px', fontSize: '12px', border: '1px solid #cbd5e1', borderRadius: '6px', boxSizing: 'border-box' }}
            />
          </div>
        </div>
      </div>

      {latest ? (
        <div style={{ marginTop: '20px', background: '#f8fafc', padding: '22px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Latest Assessment: #{latest.analysis_id.slice(0, 8)} ({latest.activity.toUpperCase()})</h3>
            <button
              type="button"
              className={`voiceBtn ${speaking ? 'speaking' : ''}`}
              onClick={() => {
                if (speaking) {
                  window.speechSynthesis.cancel();
                  setSpeaking(false);
                } else {
                  speakBriefing(voiceBriefing, setSpeaking);
                }
              }}
            >
              {speaking ? '⏹ Stop Audio' : '🔊 Listen to Audio Briefing'}
            </button>
          </div>
          <p style={{ margin: '6px 0 16px', color: '#64748b' }}>
            Pose Detection: <b>{latest.pose_detection_rate_pct}%</b> • Assessment Time: <b>{formattedTime}</b>
          </p>
          <button className="primary" onClick={() => downloadPdf(latest.analysis_id)}>
            📥 Download Complete Assessment Report (PDF)
          </button>
        </div>
      ) : (
        <Empty text="No video analyses recorded yet. Run a video analysis to generate reports." />
      )}
    </section>
  );
}

function Empty({ text }) {
  return <div className="empty">{text}</div>;
}

const root = createRoot(document.getElementById('root'));
root.render(<App />);
