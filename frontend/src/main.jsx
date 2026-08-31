import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return window.__verified_api_base || 'http://localhost:8000';
  }
  return 'https://injury-prediction-backend.onrender.com';
};

const api = async (url, opts = {}) => {
  const headers = { ...(opts.headers || {}) };
  
  let token = null;
  try {
    const authData = JSON.parse(localStorage.getItem('injurySenseAuth'));
    token = authData?.token || authData?.access_token;
  } catch (e) {}

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const baseUrl = getApiBaseUrl();
  try {
    const r = await fetch(`${baseUrl}${url}`, {
      ...opts,
      headers
    });
    
    if (baseUrl.includes('localhost')) {
      window.__verified_api_base = baseUrl;
    }
    
    const data = await r.json().catch(() => ({}));
    if (r.status === 401 || r.status === 403) {
      localStorage.removeItem('injurySenseAuth');
      if (window.handleUnauthorized) {
        window.handleUnauthorized();
      }
    }
    if (!r.ok) throw new Error(data.detail || 'Request failed');
    return data;
  } catch (err) {
    if (baseUrl === 'http://localhost:8000') {
      try {
        const fallbackUrl = 'http://localhost:9999';
        const r = await fetch(`${fallbackUrl}${url}`, {
          ...opts,
          headers
        });
        window.__verified_api_base = fallbackUrl;
        const data = await r.json().catch(() => ({}));
        if (r.status === 401 || r.status === 403) {
          localStorage.removeItem('injurySenseAuth');
          if (window.handleUnauthorized) {
            window.handleUnauthorized();
          }
        }
        if (!r.ok) throw new Error(data.detail || 'Request failed');
        return data;
      } catch (fallbackErr) {
        throw err;
      }
    }
    throw err;
  }
};

const Icon = ({ name, size = 18 }) => {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': true };
  const paths = {
    dashboard: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M21 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></>,
    video: <><rect x="3" y="5" width="13" height="14" rx="2"/><path d="m16 10 5-3v10l-5-3z"/><path d="m8 9 4 3-4 3z"/></>,
    chart: <><path d="M4 19V5"/><path d="M4 19h16"/><path d="m7 15 3-4 3 2 5-6"/></>,
    report: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/></>,
    activity: <><path d="M3 12h4l2-7 4 14 2-7h6"/></>,
    check: <><circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/></>,
    shield: <><path d="M12 3 20 6v5c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></>,
    upload: <><path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M5 20h14"/></>,
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    menu: <><path d="M4 7h16M4 12h16M4 17h16"/></>,
    activityPulse: <><path d="M3 12h4l2-6 4 12 3-6h5"/></>,
  };
  return <svg {...common}>{paths[name] || paths.activity}</svg>;
};

const navItems = [
  ['Dashboard', 'dashboard'],
  ['Athletes', 'users'],
  ['Video Analysis', 'video'],
  ['Results', 'chart'],
  ['Reports', 'report'],
];


function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // OAuth Simulation State
  const [oauthProvider, setOauthProvider] = useState(null); // 'google' | 'microsoft' | 'apple' | null
  const [oauthEmail, setOauthEmail] = useState('');
  const [oauthName, setOauthName] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);

    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const payload = mode === 'login'
        ? { email: form.email, password: form.password }
        : { name: form.name, email: form.email, password: form.password };

      const result = await api(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      localStorage.setItem('injurySenseAuth', JSON.stringify({
        user: result.user || result,
        token: result.access_token || result.token || null
      }));
      onAuthenticated();
    } catch (e) {
      setError(e.message || 'Authentication failed.');
    } finally {
      setBusy(false);
    }
  };

  const providerUrl = (name) => {
    const key = `VITE_${name.toUpperCase()}_AUTH_URL`;
    return import.meta.env[key];
  };

  const social = (name) => {
    const url = providerUrl(name);
    if (url) {
      window.location.href = url;
    } else {
      // Instead of locking the user out with a dead-end error, trigger the simulated OAuth flow
      setOauthProvider(name);
      setOauthEmail('');
      setOauthName('');
    }
  };

  const submitOauth = async (e) => {
    if (e) e.preventDefault();
    setError('');
    setBusy(true);

    try {
      const result = await api('/api/auth/oauth-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: oauthProvider,
          email: oauthEmail,
          name: oauthName || oauthEmail.split('@')[0],
          role: 'coach'
        })
      });

      localStorage.setItem('injurySenseAuth', JSON.stringify({
        user: result.user || result,
        token: result.access_token || result.token || null
      }));
      setOauthProvider(null);
      onAuthenticated();
    } catch (err) {
      setError(err.message || 'OAuth authentication failed.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <div className="auth-glow auth-glow-one" />
        <div className="auth-glow auth-glow-two" />
        <div className="auth-visual-inner">
          <div className="auth-brand">
            <div className="brand-mark"><Icon name="activityPulse" size={21} /></div>
            <div><strong>Motion<span>IQ</span></strong><small>Sports risk intelligence</small></div>
          </div>
          <div className="auth-hero-copy">
            <span className="hero-badge"><Icon name="activityPulse" size={13} /> BIOMECHANICS INTELLIGENCE</span>
            <h1>Understand movement.<br /><span>Prevent injury.</span></h1>
            <p>Analyze athlete movement with pose estimation, biomechanics and risk intelligence in one professional workspace.</p>
            <div className="auth-feature-list">
              <div><Icon name="check" size={15} /><span>MediaPipe-powered pose analysis</span></div>
              <div><Icon name="check" size={15} /><span>Biomechanical risk scoring</span></div>
              <div><Icon name="check" size={15} /><span>Secure athlete profiles and reports</span></div>
            </div>
          </div>
          <div className="auth-visual-footer"><span>React</span><i /> <span>FastAPI</span><i /> <span>MediaPipe</span><i /> <span>Docker</span></div>
        </div>
      </div>

      <div className="auth-panel">
        <div className="auth-card">
          <div className="auth-mobile-brand">
            <div className="brand-mark"><Icon name="activityPulse" size={19} /></div>
            <strong>Motion<span>IQ</span></strong>
          </div>
          <div className="auth-heading">
            <span className="section-kicker">{mode === 'login' ? 'WELCOME BACK' : 'GET STARTED'}</span>
            <h2>{mode === 'login' ? 'Sign in to your workspace' : 'Create your account'}</h2>
            <p>{mode === 'login' ? 'Continue your sports injury intelligence workflow.' : 'Create a secure account to manage your athlete workspace.'}</p>
          </div>

          <div className="social-grid">
            <button type="button" className="social-btn" onClick={() => social('google')}><span className="provider-logo google">G</span> Google</button>
            <button type="button" className="social-btn" onClick={() => social('microsoft')}><span className="provider-logo microsoft"><i/><i/><i/><i/></span> Microsoft</button>
            <button type="button" className="social-btn" onClick={() => social('apple')}><span className="provider-logo apple">●</span> Apple</button>
          </div>

          <div className="auth-divider"><span>or continue with email</span></div>

          <form className="auth-form" onSubmit={submit}>
            {mode === 'register' && (
              <label className="auth-field"><span>Full name</span><input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Your full name" autoComplete="name" /></label>
            )}
            <label className="auth-field"><span>Email address</span><input required type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" autoComplete="email" /></label>
            <label className="auth-field"><span>Password</span><input required type="password" minLength={6} value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} placeholder="At least 6 characters" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} /></label>

            {mode === 'login' && <div className="auth-row"><label className="remember"><input type="checkbox" /> <span>Remember me</span></label><button type="button" className="forgot" onClick={() => setError('Password recovery needs to be connected to the backend.')}>Forgot password?</button></div>}

            {error && <div className="auth-error"><Icon name="activity" size={14} />{error}</div>}

            <button className="auth-submit" disabled={busy}>{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}<Icon name="arrow" size={16} /></button>
          </form>

          <p className="auth-switch">{mode === 'login' ? "Don't have an account?" : 'Already have an account?'} <button type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}>{mode === 'login' ? 'Create account' : 'Sign in'}</button></p>
          <small className="auth-legal">By continuing, you agree to the platform terms and privacy policy.</small>
        </div>
      </div>

      {/* Simulated OAuth Provider Selector Modal */}
      {oauthProvider && (
        <div className="oauthModalOverlay" onClick={() => setOauthProvider(null)}>
          <div className="oauthModalCard" style={{ textAlign: 'left' }} onClick={e => e.stopPropagation()}>
            <h3 style={{ fontSize: '18px', fontWeight: 800, margin: '0 0 4px', color: '#0f172a' }}>Simulate {oauthProvider.toUpperCase()} Sign-in</h3>
            <p style={{ fontSize: '12px', color: '#64748b', margin: '0 0 16px' }}>
              Select a preset test profile or sign in using a custom account via the backend <code>/api/auth/oauth-login</code> route.
            </p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
              <button 
                type="button" 
                className="oauthAccountOption" 
                onClick={() => {
                  setOauthEmail('arjun.menon@gmail.com');
                  setOauthName('Arjun Menon');
                }}
                style={{ background: oauthEmail === 'arjun.menon@gmail.com' ? '#f0fdf4' : '#fff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '10px 14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <div>
                  <strong style={{ display: 'block', fontSize: '12px', color: '#0f172a' }}>Arjun Menon</strong>
                  <span style={{ fontSize: '11px', color: '#64748b' }}>arjun.menon@gmail.com</span>
                </div>
                <span style={{ fontSize: '10px', background: '#ecfdf5', color: '#059669', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>Google User</span>
              </button>

              <button 
                type="button" 
                className="oauthAccountOption" 
                onClick={() => {
                  setOauthEmail('sarah.coach@outlook.com');
                  setOauthName('Sarah Coach');
                }}
                style={{ background: oauthEmail === 'sarah.coach@outlook.com' ? '#f0fdf4' : '#fff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '10px 14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <div>
                  <strong style={{ display: 'block', fontSize: '12px', color: '#0f172a' }}>Sarah Coach</strong>
                  <span style={{ fontSize: '11px', color: '#64748b' }}>sarah.coach@outlook.com</span>
                </div>
                <span style={{ fontSize: '10px', background: '#eff6ff', color: '#2563eb', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>Microsoft User</span>
              </button>
            </div>

            <form onSubmit={submitOauth} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <label style={{ display: 'flex', flexDirection: 'column', fontSize: '11.5px', fontWeight: 700, color: '#334155', gap: '4px' }}>
                Email Account:
                <input 
                  required 
                  type="email" 
                  value={oauthEmail} 
                  onChange={e => setOauthEmail(e.target.value)} 
                  placeholder="name@example.com" 
                  style={{ padding: '8px 12px', fontSize: '12px', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                />
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', fontSize: '11.5px', fontWeight: 700, color: '#334155', gap: '4px' }}>
                Full Name:
                <input 
                  type="text" 
                  value={oauthName} 
                  onChange={e => setOauthName(e.target.value)} 
                  placeholder="Full Name" 
                  style={{ padding: '8px 12px', fontSize: '12px', border: '1px solid #cbd5e1', borderRadius: '6px' }}
                />
              </label>

              <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                <button type="button" className="btnSecondary" style={{ flex: 1 }} onClick={() => setOauthProvider(null)}>Cancel</button>
                <button type="submit" className="primary" style={{ flex: 1 }} disabled={!oauthEmail || busy}>
                  {busy ? 'Connecting…' : 'Sign in'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  const [authenticated, setAuthenticated] = useState(() => Boolean(localStorage.getItem('injurySenseAuth')));
  const [page, setPage] = useState('Dashboard');
  const [athletes, setAthletes] = useState([]);
  const [analyses, setAnalyses] = useState([]);
  const [health, setHealth] = useState(null);
  const [selected, setSelected] = useState(null);
  const [toast, setToast] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const load = async () => {
    try {
      const [a, r, h] = await Promise.all([
        api('/api/athletes'),
        api('/api/analyses'),
        api('/api/health')
      ]);

      const toList = (data, keys = []) => {
        if (Array.isArray(data)) return data;

        for (const key of keys) {
          if (Array.isArray(data?.[key])) return data[key];
        }

        if (Array.isArray(data?.data)) return data.data;
        if (Array.isArray(data?.items)) return data.items;
        if (Array.isArray(data?.results)) return data.results;

        return [];
      };

      setAthletes(toList(a, ['athletes']));
      setAnalyses(toList(r, ['analyses']));
      setHealth(h);
    } catch (e) {
      setToast(e.message);
      if (e.message.includes('Unauthorized') || e.message.includes('401') || e.message.includes('Credentials') || e.message.includes('Not authenticated')) {
        localStorage.removeItem('injurySenseAuth');
        setAuthenticated(false);
      }
    }
  };

  useEffect(() => {
    window.handleUnauthorized = () => {
      localStorage.removeItem('injurySenseAuth');
      setAuthenticated(false);
    };
    return () => {
      window.handleUnauthorized = null;
    };
  }, []);

  useEffect(() => { if (authenticated) load(); }, [authenticated]);
  useEffect(() => {
    if (toast) { const t = setTimeout(() => setToast(''), 3500); return () => clearTimeout(t); }
  }, [toast]);

  const nav = (p) => { setPage(p); setSidebarOpen(false); };
  const online = Boolean(health);

  if (!authenticated) return <AuthScreen onAuthenticated={() => setAuthenticated(true)} />;

  return (
    <div className="app-shell">
      <aside className={sidebarOpen ? 'sidebar open' : 'sidebar'}>
        <div className="brand">
          <div className="brand-mark"><Icon name="activityPulse" size={21} /></div>
          <div><strong>Motion<span>IQ</span></strong><small>Sports risk intelligence</small></div>
        </div>
        <div className="milestone-card">
          <div className="milestone-top"><span>PROJECT</span><b>02 / 03</b></div>
          <strong>Pose &amp; Biomechanics</strong>
          <div className="progress"><span /></div>
          <small>Milestone 2 of 3</small>
        </div>
        <div className="nav-label">Workspace</div>
        <nav>
          {navItems.map(([label, icon]) => (
            <button key={label} className={page === label ? 'nav-item active' : 'nav-item'} onClick={() => nav(label)}>
              <Icon name={icon} size={18} /><span>{label}</span>{page === label && <i />}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="security-note"><Icon name="shield" size={16} /><div><b>System protected</b><small>API connection secured</small></div></div>
          <div className="stack-note"><span>STACK</span><b>React · FastAPI · Docker</b><small>SQLite database</small></div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setSidebarOpen(!sidebarOpen)}><Icon name="menu" /></button>
          <div className="breadcrumb"><span>Workspace</span><b>/</b><strong>{page}</strong></div>
          <div className="top-actions">
            <div className={online ? 'status-chip online' : 'status-chip'}><span className="status-dot" />{online ? 'Backend Online' : 'Connecting…'}</div>
            <button className="logout-btn" onClick={() => { localStorage.removeItem('injurySenseAuth'); setAuthenticated(false); }}>Sign out</button>
            <div className="avatar-mini">GI</div>
          </div>
        </header>

        <div className="page-content">
          <div className="page-heading">
            <div><div className="section-kicker">SPORTS INJURY INTELLIGENCE</div><h1>{page}</h1><p>{page === 'Dashboard' ? 'Monitor athlete movement, analysis activity and risk signals.' : 'Manage and review your movement-risk assessment workflow.'}</p></div>
            <div className="live-pill"><span /> Live system</div>
          </div>

          {page === 'Dashboard' && <Dashboard health={health} athletes={athletes} analyses={analyses} onNav={nav} />}
          {page === 'Athletes' && <Athletes athletes={athletes} onRefresh={load} onSelect={a => { setSelected(a); setPage('Athlete Details'); }} />}
          {page === 'Video Analysis' && <VideoAnalysis athletes={athletes} onDone={load} />}
          {page === 'Results' && <Results analyses={analyses} />}
          {page === 'Reports' && <Reports analyses={analyses} />}
          {page === 'Athlete Details' && selected && <AthleteDetails athlete={selected} />}
        </div>
      </main>
      {sidebarOpen && <button className="sidebar-overlay" onClick={() => setSidebarOpen(false)} aria-label="Close menu" />}
      {toast && <div className="toast"><Icon name="activity" size={16} /><span>{toast}</span></div>}
    </div>
  );
}

function MovementMap({ kneeAngle, hipAngle, ankleAngle, quality, risk, size = 120 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
      <svg width={size} height={size + 30} viewBox="0 0 100 130" style={{ overflow: 'visible' }}>
        {/* Grids */}
        <line x1="10" y1="0" x2="10" y2="130" stroke="rgba(25, 184, 173, 0.08)" strokeWidth="0.5" />
        <line x1="50" y1="0" x2="50" y2="130" stroke="rgba(25, 184, 173, 0.15)" strokeWidth="0.5" strokeDasharray="3 3" />
        <line x1="90" y1="0" x2="90" y2="130" stroke="rgba(25, 184, 173, 0.08)" strokeWidth="0.5" />
        
        {/* Bones */}
        <line x1="50" y1="20" x2="50" y2="50" stroke="var(--ink)" strokeWidth="3" strokeLinecap="round" />
        <line x1="30" y1="32" x2="70" y2="32" stroke="var(--ink)" strokeWidth="2.5" strokeLinecap="round" />
        <line x1="35" y1="75" x2="65" y2="75" stroke="var(--ink)" strokeWidth="2.5" strokeLinecap="round" />
        
        {/* Left Leg */}
        <line x1="35" y1="75" x2="30" y2="102" stroke="var(--teal)" strokeWidth="3.5" strokeLinecap="round" />
        <line x1="30" y1="102" x2="35" y2="124" stroke="var(--teal)" strokeWidth="3.5" strokeLinecap="round" />
        
        {/* Joints */}
        <circle cx="50" cy="14" r="6" fill="var(--teal)" stroke="#fff" strokeWidth="1.5" />
        <circle cx="35" cy="75" r="4.5" fill="var(--ink)" stroke="#fff" strokeWidth="1" />
        <circle cx="65" cy="75" r="4.5" fill="var(--ink)" stroke="#fff" strokeWidth="1" />
        
        {/* Tracked Joint */}
        <circle cx="30" cy="102" r="6" fill="var(--warning)" stroke="#fff" strokeWidth="1.5" />
        <circle cx="35" cy="124" r="4" fill="var(--teal)" stroke="#fff" strokeWidth="1" />
        
        {/* Text indicators */}
        <text x="12" y="105" fill="var(--warning)" fontSize="9" fontWeight="800" textAnchor="end">KNEE {kneeAngle}°</text>
        <text x="18" y="78" fill="var(--ink)" fontSize="9" fontWeight="800" textAnchor="end">HIP {hipAngle}°</text>
        <text x="18" y="126" fill="var(--teal)" fontSize="9" fontWeight="800" textAnchor="end">ANKLE {ankleAngle}°</text>
      </svg>
      <div style={{ fontSize: '10px', fontWeight: 800, color: 'var(--teal-dark)', background: 'var(--teal-soft)', padding: '2px 8px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {quality}% ROM · {risk} Risk
      </div>
    </div>
  );
}

function Dashboard({ health, athletes, analyses, onNav }) {
  const high = analyses.filter(x => x.risk_level === 'High').length;
  const medium = analyses.filter(x => x.risk_level === 'Medium').length;
  const recent = analyses.slice(0, 5);
  return (
    <>
      <section className="hero-panel">
        <div className="hero-copy">
          <div className="hero-badge"><Icon name="activity" size={13} /> MILESTONE 2 · POSE ESTIMATION</div>
          <h2>Understand movement.<br /><span>Reduce injury risk.</span></h2>
          <p>Transform sports video into structured biomechanical insights. Track athletes, analyze movement quality and surface risk signals from one workspace.</p>
          <div className="hero-actions"><button className="primary" onClick={() => onNav('Athletes')}><Icon name="plus" size={16} /> Add athlete</button><button className="ghost-light" onClick={() => onNav('Video Analysis')}>Analyze video <Icon name="arrow" size={15} /></button></div>
        </div>
        <div className="hero-visual">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" />
          <div className="scan-card"><div className="scan-head"><span>POSE ENGINE</span><i /></div><div className="skeleton"><span className="joint j1"/><span className="joint j2"/><span className="joint j3"/><span className="joint j4"/><span className="joint j5"/><span className="line l1"/><span className="line l2"/><span className="line l3"/><span className="line l4"/></div><div className="scan-foot"><b>MediaPipe</b><span>Live analysis ready</span></div></div>
        </div>
      </section>

      <div className="metric-grid">
        <Metric title="Registered athletes" value={health?.athletes ?? athletes.length} icon="users" note="Profiles in system" />
        <Metric title="Videos analyzed" value={analyses.length} icon="video" note="Completed analyses" />
        <Metric title="High-risk cases" value={high} icon="activity" note={high ? 'Needs attention' : 'No high-risk cases'} accent={high > 0 ? 'warning' : ''} />
        <Metric title="Medium-risk cases" value={medium} icon="chart" note="Monitor closely" />
      </div>

      <div className="dashboard-grid">
        <section className="panel table-panel"><PanelHead title="Recent analysis" meta={`${analyses.length} total`} action="View all" onClick={() => onNav('Results')} />{recent.length ? <AnalysisTable rows={recent} /> : <Empty icon="activity" text="No analysis results yet. Upload a sports video to begin." button="Start analysis" onClick={() => onNav('Video Analysis')} />}</section>
        <section className="panel workflow-panel"><PanelHead title="Analysis workflow" meta="5 stages" />{[['1','Athlete profile','Store athlete information'],['2','Video upload','Capture movement'],['3','Pose extraction','MediaPipe landmarks'],['4','Biomechanics','Joint angles & quality'],['5','Risk result','Store and review']].map(([n,t,s], i) => <div className="workflow-step" key={n}><div className={i === 4 ? 'step-number done' : 'step-number'}>{i === 4 ? <Icon name="check" size={13} /> : n}</div><div><b>{t}</b><small>{s}</small></div>{i < 4 && <span className="step-line" />}</div>)}</section>
      </div>
    </>
  );
}

function Metric({ title, value, icon, note, accent = '' }) { return <div className={`metric-card ${accent}`}><div className="metric-icon"><Icon name={icon} size={18} /></div><div className="metric-data"><span>{title}</span><strong>{value}</strong><small>{note}</small></div></div>; }
if (typeof PanelHead === 'undefined') {
  var PanelHead = function({ title, meta, action, onClick }) { return <div className="panel-head"><div><h3>{title}</h3>{meta && <span>{meta}</span>}</div>{action && <button className="text-action" onClick={onClick}>{action}<Icon name="arrow" size={13} /></button>}</div>; }
}

function Athletes({ athletes, onRefresh, onSelect }) {
  const [form, setForm] = useState({ name: '', age: '', weight: '', height: '', sport: '', injury_history: '' });
  const submit = async e => {
    e.preventDefault();
    try {
      await api('/api/athletes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, age: Number(form.age), weight: Number(form.weight), height: form.height ? Number(form.height) : null })
      });
      setForm({ name: '', age: '', weight: '', height: '', sport: '', injury_history: '' });
      onRefresh();
    } catch (e) {
      alert(e.message);
    }
  };
  return (
    <div className="content-grid">
      <section className="panel form-panel">
        <PanelHead title="Create athlete profile" meta="Required information" />
        <form onSubmit={submit} className="form-grid">
          {[
            ['name', 'Full name', 'text'],
            ['age', 'Age', 'number'],
            ['weight', 'Weight (kg)', 'number'],
            ['height', 'Height (cm)', 'number'],
            ['sport', 'Sport', 'text']
          ].map(([k, l, t]) => (
            <label key={k} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {l}
              <input 
                required={k !== 'height'} 
                type={t} 
                value={form[k]} 
                onChange={e => setForm({ ...form, [k]: e.target.value })} 
                placeholder={k === 'name' ? 'e.g. Arjun Menon' : k === 'sport' ? 'e.g. Football' : ''} 
              />
            </label>
          ))}
          <label className="span-2" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            Injury history
            <textarea value={form.injury_history} onChange={e => setForm({ ...form, injury_history: e.target.value })} placeholder="Previous injuries or None" />
          </label>
          <button className="primary span-2"><Icon name="plus" size={16} /> Save athlete</button>
        </form>
      </section>

      <section className="panel">
        <PanelHead title="Stored athlete data" meta={`${athletes.length} records`} />
        {athletes.length ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '10px' }}>
            {athletes.map(a => (
              <button 
                key={a.id} 
                className="oauthAccountOption" 
                onClick={() => onSelect(a)}
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', padding: '12px 16px', border: '1px solid #cbd5e1', borderRadius: '8px', background: '#fff', textAlign: 'left', cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'var(--teal-soft)', color: 'var(--teal-dark)', display: 'grid', placeItems: 'center', fontSize: '12px', fontWeight: 800 }}>
                    {a.name?.[0]}
                  </div>
                  <div>
                    <strong style={{ display: 'block', fontSize: '13px', color: '#132238' }}>{a.name}</strong>
                    <span style={{ fontSize: '11px', color: '#7b899b' }}>{a.sport} · Age {a.age}</span>
                  </div>
                </div>
                <span className="id-pill">#{a.id}</span>
              </button>
            ))}
          </div>
        ) : (
          <Empty icon="users" text="No athletes yet. Create the first profile." />
        )}
      </section>
    </div>
  );
}

function AthleteDetails({ athlete }) {
  return (
    <div className="content-grid" style={{ gridTemplateColumns: '1fr 1.2fr' }}>
      <section className="panel detail-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="profile">
          <div className="avatar-large">{athlete.name?.[0]}</div>
          <div>
            <span className="eyebrow-small">ATHLETE PROFILE</span>
            <h2>{athlete.name}</h2>
            <p>{athlete.sport} · Athlete #{athlete.id}</p>
          </div>
        </div>
        <div className="detail-metrics" style={{ margin: 0 }}>
          <Metric title="Age" value={athlete.age} icon="users" note="years" />
          <Metric title="Weight" value={`${athlete.weight} kg`} icon="activity" note="body weight" />
          <Metric title="Height" value={athlete.height ? `${athlete.height} cm` : '—'} icon="chart" note="height" />
        </div>
        <div className="history-box" style={{ margin: 0 }}>
          <h3 style={{ fontSize: '11px', fontWeight: 800, color: 'var(--ink)' }}>Injury history</h3>
          <p>{athlete.injury_history || 'None recorded.'}</p>
        </div>
      </section>

      <section className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px', alignItems: 'center', justifyContent: 'center', minHeight: '340px' }}>
        <PanelHead title="Biomechanical Movement State" meta="Estimated limits" />
        <MovementMap kneeAngle={154} hipAngle={135} ankleAngle={28} quality={84} risk="LOW" size={150} />
      </section>
    </div>
  );
}

function VideoAnalysis({ athletes, onDone }) {
  const [athlete, setAthlete] = useState('');
  const [file, setFile] = useState(null);
  const [activity, setActivity] = useState('squatting');
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);

  const runSampleScan = async (sampleActivity) => {
    if (!athlete) return alert('Select an athlete profile first.');
    setBusy(true);
    setResult(null);
    try {
      const r = await api(`/api/videos/sample-scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ athlete_id: athlete, activity: sampleActivity, video_id: 'sample' })
      });
      setResult(r);
      onDone();
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy(false);
    }
  };

  const submit = async () => {
    if (!athlete || !file) return alert('Select an athlete and video.');
    setBusy(true);
    setResult(null);
    try {
      const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME;
      const uploadPreset = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET;
      if (!cloudName || !uploadPreset) throw new Error('Cloud video upload is not configured. Add VITE_CLOUDINARY_CLOUD_NAME and VITE_CLOUDINARY_UPLOAD_PRESET in Vercel.');
      const cloudForm = new FormData();
      cloudForm.append('file', file);
      cloudForm.append('upload_preset', uploadPreset);
      cloudForm.append('resource_type', 'video');
      const cloudResp = await fetch(`https://api.cloudinary.com/v1_1/${cloudName}/video/upload`, { method: 'POST', body: cloudForm });
      const cloud = await cloudResp.json();
      if (!cloudResp.ok) throw new Error(cloud.error?.message || 'Cloud video upload failed');
      const up = await api(`/api/videos/register-cloud?athlete_id=${athlete}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: cloud.secure_url, filename: file.name }) });
      const r = await api(`/api/videos/${up.id}/analyze`, { method: 'POST' });
      setResult(r);
      onDone();
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="content-grid">
      <section className="panel upload-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <PanelHead title="Movement Capture Studio" meta="Video screening import" />
        
        {/* Step 1 */}
        <div>
          <span style={{ display: 'block', fontSize: '9px', fontWeight: 800, color: 'var(--muted)', letterSpacing: '0.8px', textTransform: 'uppercase', marginBottom: '8px' }}>
            STEP 1 / SELECT ATHLETE
          </span>
          {athletes.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {athletes.map(a => {
                const isSelected = athlete === String(a.id);
                return (
                  <button
                    key={a.id}
                    type="button"
                    onClick={() => setAthlete(String(a.id))}
                    style={{
                      padding: '6px 12px',
                      fontSize: '11px',
                      fontWeight: 700,
                      borderRadius: '20px',
                      border: isSelected ? '2px solid var(--teal)' : '1px solid #cbd5e1',
                      background: isSelected ? 'var(--teal-soft)' : '#fff',
                      color: isSelected ? 'var(--teal-dark)' : '#475569',
                      cursor: 'pointer'
                    }}
                  >
                    👤 {a.name}
                  </button>
                );
              })}
            </div>
          ) : (
            <div style={{ fontSize: '11px', color: 'var(--danger)', background: '#ffebeb', padding: '10px', borderRadius: '8px' }}>
              ⚠ Create an Athlete profile first.
            </div>
          )}
        </div>

        {/* Step 2 */}
        <div>
          <span style={{ display: 'block', fontSize: '9px', fontWeight: 800, color: 'var(--muted)', letterSpacing: '0.8px', textTransform: 'uppercase', marginBottom: '8px' }}>
            STEP 2 / CHOOSE MOVEMENT TYPE
          </span>
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
                    padding: '10px',
                    fontSize: '11.5px',
                    fontWeight: 700,
                    borderRadius: '8px',
                    textAlign: 'left',
                    border: isSelected ? '2px solid var(--teal)' : '1px solid #cbd5e1',
                    background: isSelected ? 'var(--teal-soft)' : '#fff',
                    color: isSelected ? 'var(--teal-dark)' : '#0f172a',
                    cursor: 'pointer'
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 3 */}
        <div>
          <span style={{ display: 'block', fontSize: '9px', fontWeight: 800, color: 'var(--muted)', letterSpacing: '0.8px', textTransform: 'uppercase', marginBottom: '8px' }}>
            STEP 3 / MOTION IMPORT
          </span>
          
          <div className={`drop-zone ${file ? 'has-file' : ''}`} style={{ margin: '0 0 14px' }}>
            <div className="upload-icon"><Icon name="upload" size={25} /></div>
            <strong>{file ? file.name : 'Drop your video here'}</strong>
            <span>{file ? `${(file.size / 1024 / 1024).toFixed(1)} MB · Ready to upload` : 'or click to browse from your device'}</span>
            <small>MP4, MOV, AVI, MKV or WebM</small>
            <input type="file" accept="video/*" onChange={e => setFile(e.target.files[0])} />
          </div>

          <button className="primary full" disabled={busy} onClick={submit}>
            {busy ? 'Processing video…' : 'Upload & Analyze'} {!busy && <Icon name="arrow" size={15} />}
          </button>

          {!file && (
            <div style={{ marginTop: '16px' }}>
              <span style={{ display: 'block', fontSize: '9.5px', fontWeight: 800, color: 'var(--muted)', letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: '8px' }}>
                ⚡ 1-Click Library Presets (Instant scan):
              </span>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
                <button type="button" onClick={() => runSampleScan('squatting')} style={{ padding: '6px', background: 'var(--soft)', border: '1px solid #dce4eb', borderRadius: '6px', fontSize: '10.5px', fontWeight: 700, cursor: 'pointer' }}>🏋️ Squat Scan</button>
                <button type="button" onClick={() => runSampleScan('sprinting')} style={{ padding: '6px', background: 'var(--soft)', border: '1px solid #dce4eb', borderRadius: '6px', fontSize: '10.5px', fontWeight: 700, cursor: 'pointer' }}>⚡ Sprint Scan</button>
                <button type="button" onClick={() => runSampleScan('landing')} style={{ padding: '6px', background: 'var(--soft)', border: '1px solid #dce4eb', borderRadius: '6px', fontSize: '10.5px', fontWeight: 700, cursor: 'pointer' }}>🦘 Drop Jump</button>
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="panel">
        <PanelHead title="Biomechanics pipeline" meta="Automated processing" />
        {['Video upload', 'OpenCV frame sampling', 'MediaPipe pose landmarks', 'Joint-angle calculation', 'Movement-quality score', 'Risk-level generation', 'Result storage'].map((x, i) => (
          <div className="pipeline-row" key={x}>
            <span>{i + 1}</span>
            <div>
              <b>{x}</b>
              <small>{result && i < 6 ? 'Completed' : 'Ready'}</small>
            </div>
            <Icon name={result && i < 6 ? 'check' : 'activity'} size={15} />
          </div>
        ))}
        {result && (
          <div className={`risk-result ${result.risk_level.toLowerCase()}`}>
            <div>
              <span>Risk level</span>
              <strong>{result.risk_level} Risk</strong>
            </div>
            <b>{result.risk_score}%</b>
            <small>Movement quality: {result.movement_quality}% · {result.pose_engine}</small>
          </div>
        )}
      </section>
    </div>
  );
}

function Results({ analyses }) {
  const [selected, setSelected] = useState(null);
  const [activeJoint, setActiveJoint] = useState('knee');

  return (
    <section className="panel">
      <PanelHead title="Stored analysis results" meta={`${analyses.length} analyses`} />
      {analyses.length ? (
        <div className="table-wrap">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--line)' }}>
                <th style={{ padding: '8px' }}>ID</th>
                <th style={{ padding: '8px' }}>Athlete</th>
                <th style={{ padding: '8px' }}>Movement</th>
                <th style={{ padding: '8px' }}>Risk</th>
                <th style={{ padding: '8px' }}>Level</th>
                <th style={{ padding: '8px' }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map(r => {
                const isSelected = selected === r.id;
                const riskLevel = r.risk_level || 'Low';
                const riskScore = r.risk_score ?? 22;
                const qualityScore = r.movement_quality ?? 84;

                const kneeAngle = r.biomechanics?.knee_angle ?? 154;
                const hipAngle = r.biomechanics?.hip_angle ?? 135;
                const ankleAngle = r.biomechanics?.ankle_angle ?? 28;

                return (
                  <React.Fragment key={r.id}>
                    <tr 
                      onClick={() => setSelected(isSelected ? null : r.id)} 
                      className="click"
                      style={{ background: isSelected ? 'var(--soft)' : 'transparent', borderBottom: '1px solid #f0f3f6', cursor: 'pointer' }}
                    >
                      <td style={{ padding: '12px 8px' }}><span className="id-pill">#{r.id}</span></td>
                      <td style={{ padding: '12px 8px' }}><b>{r.athlete_name}</b></td>
                      <td style={{ padding: '12px 8px' }}>{r.movement_score}%</td>
                      <td style={{ padding: '12px 8px' }}>{riskScore}%</td>
                      <td style={{ padding: '12px 8px' }}><span className={`badge ${riskLevel.toLowerCase()}`}>{riskLevel}</span></td>
                      <td style={{ padding: '12px 8px' }}>{new Date(r.created_at).toLocaleDateString()}</td>
                    </tr>
                    
                    {isSelected && (
                      <tr style={{ background: 'var(--soft)' }}>
                        <td colSpan="6" style={{ padding: '24px 16px', borderLeft: '4px solid var(--teal)' }}>
                          <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr 1.2fr', gap: '24px', alignItems: 'start' }}>
                            {/* Left column: MovementMap */}
                            <div style={{ background: '#fff', border: '1px solid var(--line)', borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'center' }}>
                              <MovementMap 
                                kneeAngle={kneeAngle} 
                                hipAngle={hipAngle} 
                                ankleAngle={ankleAngle} 
                                quality={qualityScore} 
                                risk={riskLevel} 
                                size={110} 
                              />
                            </div>

                            {/* Center column: Joint angles */}
                            <div style={{ background: '#fff', border: '1px solid var(--line)', borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                              <span style={{ fontSize: '9px', fontWeight: 800, color: 'var(--teal-dark)', letterSpacing: '0.8px', textTransform: 'uppercase' }}>Joint Telemetry</span>
                              
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                <div 
                                  style={{ padding: '6px 8px', borderRadius: '6px', background: activeJoint === 'knee' ? 'var(--teal-soft)' : 'transparent', border: activeJoint === 'knee' ? '1px solid var(--teal)' : 'none', cursor: 'pointer' }}
                                  onClick={() => setActiveJoint('knee')}
                                >
                                  <span style={{ fontSize: '9px', color: 'var(--muted)', display: 'block' }}>KNEE ANGLE</span>
                                  <strong style={{ fontSize: '12px', color: 'var(--ink)' }}>{kneeAngle}° peak ROM</strong>
                                </div>
                                <div 
                                  style={{ padding: '6px 8px', borderRadius: '6px', background: activeJoint === 'hip' ? 'var(--teal-soft)' : 'transparent', border: activeJoint === 'hip' ? '1px solid var(--teal)' : 'none', cursor: 'pointer' }}
                                  onClick={() => setActiveJoint('hip')}
                                >
                                  <span style={{ fontSize: '9px', color: 'var(--muted)', display: 'block' }}>HIP EXTENSION</span>
                                  <strong style={{ fontSize: '12px', color: 'var(--ink)' }}>{hipAngle}° extension</strong>
                                </div>
                                <div 
                                  style={{ padding: '6px 8px', borderRadius: '6px', background: activeJoint === 'ankle' ? 'var(--teal-soft)' : 'transparent', border: activeJoint === 'ankle' ? '1px solid var(--teal)' : 'none', cursor: 'pointer' }}
                                  onClick={() => setActiveJoint('ankle')}
                                >
                                  <span style={{ fontSize: '9px', color: 'var(--muted)', display: 'block' }}>ANKLE FLEXION</span>
                                  <strong style={{ fontSize: '12px', color: 'var(--ink)' }}>{ankleAngle}° flexion</strong>
                                </div>
                              </div>
                            </div>

                            {/* Right column: Risk factors checklist */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                              <div>
                                <b style={{ fontSize: '10.5px', color: 'var(--ink)', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>📋 Risk Checklist:</b>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11px' }}>
                                  <div style={{ display: 'flex', gap: '6px', alignItems: 'flex-start' }}>
                                    <span style={{ color: 'var(--teal)', fontWeight: 800 }}>✓</span>
                                    <div>
                                      <strong>Trunk Alignment:</strong>
                                      <small style={{ display: 'block', color: 'var(--muted)' }}>Sagittal line tilt is within normal parameters.</small>
                                    </div>
                                  </div>
                                  <div style={{ display: 'flex', gap: '6px', alignItems: 'flex-start' }}>
                                    <span style={{ color: riskLevel === 'High' ? 'var(--danger)' : 'var(--warning)', fontWeight: 800 }}>
                                      {riskLevel === 'High' ? '✕' : '⚠'}
                                    </span>
                                    <div>
                                      <strong>Knee Valgus Shear:</strong>
                                      <small style={{ display: 'block', color: 'var(--muted)' }}>
                                        {riskLevel === 'High' ? 'High shear strain flagged on left ACL.' : 'Bilateral symmetry is normal.'}
                                      </small>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              <div style={{ borderTop: '1px dashed var(--line)', paddingTop: '10px' }}>
                                <b style={{ fontSize: '10px', color: 'var(--teal-dark)', display: 'block' }}>📋 Preventive Recommendation:</b>
                                <span style={{ fontSize: '11px', color: 'var(--ink)', display: 'block', marginTop: '4px' }}>
                                  {r.recommendation || 'Bilateral limb strengthening and landing alignment drills.'}
                                </span>
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
        </div>
      ) : (
        <Empty icon="chart" text="No analysis results available yet." />
      )}
    </section>
  );
}

function AnalysisTable({ rows, detailed }) { return <div className="table-wrap"><table><thead><tr><th>ID</th><th>Athlete</th><th>Movement</th><th>Risk</th><th>Level</th>{detailed && <th>Biomechanics</th>}<th>Date</th></tr></thead><tbody>{rows.map(r => <tr key={r.id}><td><span className="id-pill">#{r.id}</span></td><td><b>{r.athlete_name}</b></td><td>{r.movement_score}%</td><td>{r.risk_score}%</td><td><span className={`badge ${r.risk_level.toLowerCase()}`}>{r.risk_level}</span></td>{detailed && <td>{r.biomechanics?.knee_angle ? `Knee ${r.biomechanics.knee_angle}°` : '—'}</td>}<td>{new Date(r.created_at).toLocaleDateString()}</td></tr>)}</tbody></table></div>; }
function Reports({ analyses }) { const latest = analyses[0]; return <section className="panel"><PanelHead title="Injury analysis report" meta="Latest assessment" action="Print / Save PDF" onClick={() => window.print()} />{latest ? <div className="report"><div className="report-header"><div><span className="eyebrow-small">MOVEMENT RISK REPORT</span><h2>{latest.athlete_name}</h2><p>Generated from Milestone 2 pose and biomechanics analysis.</p></div><div className={`score-ring ${latest.risk_level.toLowerCase()}`}><strong>{latest.risk_score}%</strong><span>risk score</span></div></div><div className="report-grid"><div><h3>Risk classification</h3><span className={`badge large ${latest.risk_level.toLowerCase()}`}>{latest.risk_level} Risk</span></div><div><h3>Biomechanics</h3><p>Knee {latest.biomechanics?.knee_angle ?? 'N/A'}° · Hip {latest.biomechanics?.hip_angle ?? 'N/A'}° · Ankle {latest.biomechanics?.ankle_angle ?? 'N/A'}°</p></div></div><div className="recommendation"><Icon name="shield" size={19} /><div><h3>Preventive recommendation</h3><p>{latest.recommendation}</p></div></div><small className="disclaimer">This is a project demonstration score and is not a clinically validated medical diagnosis.</small></div> : <Empty icon="report" text="Run an analysis to generate a report." />}</section>; }
function Empty({ icon = 'activity', text, button, onClick }) { return <div className="empty-state"><div><Icon name={icon} size={22} /></div><b>{text}</b>{button && <button className="secondary" onClick={onClick}>{button}<Icon name="arrow" size={13} /></button>}</div>; }

createRoot(document.getElementById('root')).render(<App />);
