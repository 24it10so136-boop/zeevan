import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, ArrowRight, BarChart2, Brain, Check,
  CircleUserRound, Database, HeartPulse, Info, LogIn, LogOut,
  Menu, Mic, Moon, ShieldCheck, Sparkles, Sun, ThumbsDown, ThumbsUp,
  UserPlus, X, Zap
} from "lucide-react";
import { api } from "./api";
import "./index.css";

// ── Symptom Chips Library ─────────────────────────────────────────────────────
const SYMPTOM_CHIPS = [
  "Headache","Fever","Nausea","Fatigue","Cough","Cold","Pain","Breathlessness",
  "Vomiting","Dizziness","Rash","Itching","Diarrhoea","Chest pain","Sore throat",
  "Back pain","Joint pain","Swelling","Anxiety","Constipation","Acne","Chills",
  "Sweating","Blurred vision","Palpitations","Indigestion","Hair loss","Numbness",
];

// Presentation order requested for common respiratory pattern matches.
// This is not a clinical severity ranking.
const CONDITION_DISPLAY_ORDER = new Map([
  ["common cold", 0],
  ["pneumonia", 1],
  ["tuberculosis", 2],
  ["bronchial asthma", 3],
]);

// ── Auth Context ──────────────────────────────────────────────────────────────
const AuthCtx = React.createContext(null);
function useAuth() { return React.useContext(AuthCtx); }
function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("zeevan_user") || "null"); } catch { return null; }
  });
  const signIn = (userData, token) => {
    localStorage.setItem("zeevan_token", token);
    localStorage.setItem("zeevan_user", JSON.stringify(userData));
    setUser(userData);
  };
  const signOut = () => {
    localStorage.removeItem("zeevan_token");
    localStorage.removeItem("zeevan_user");
    setUser(null);
  };
  return <AuthCtx.Provider value={{ user, signIn, signOut }}>{children}</AuthCtx.Provider>;
}

// ── Router ────────────────────────────────────────────────────────────────────
function useRouter() {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const fn = () => setPath(window.location.pathname);
    window.addEventListener("popstate", fn);
    return () => window.removeEventListener("popstate", fn);
  }, []);
  const go = (to) => { window.history.pushState({}, "", to); setPath(to); window.scrollTo(0, 0); };
  return [path, go];
}
function Link({ href, children, className = "", onClick }) {
  return (
    <a href={href} className={className} onClick={e => {
      e.preventDefault();
      if (onClick) onClick();
      window.history.pushState({}, "", href);
      window.dispatchEvent(new PopStateEvent("popstate"));
      window.scrollTo(0, 0);
    }}>{children}</a>
  );
}

// ── Shared UI Components ──────────────────────────────────────────────────────
function BrandOrb({ size = 28 }) {
  return <div className="brand-orb" style={{ width: size, height: size }} />;
}
function Logo() {
  return (
    <Link href="/" className="brand">
      <BrandOrb /> <span>Zeevan</span>
    </Link>
  );
}

function Header({ path, go, theme, toggleTheme }) {
  const { user, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const nav = [
    ["Home", "/"],
    ["Check symptoms", "/check"],
    ["Health journey", "/journey"],
  ];
  const handleSignOut = () => { signOut(); go("/"); setOpen(false); };
  return (
    <header className="site-header">
      <div className="container navbar">
        <Logo />
        <nav className={`nav-links${open ? " open" : ""}`}>
          {nav.map(([label, href]) => (
            <Link key={href} href={href} className={`nav-link${path === href ? " active" : ""}`} onClick={() => setOpen(false)}>{label}</Link>
          ))}
        </nav>
        <div className="nav-actions">
          <button className="btn btn-ghost btn-sm theme-toggle" onClick={toggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}>
            {theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
            <span>{theme === "dark" ? "Light" : "Dark"}</span>
          </button>
          {user ? (
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <Link href="/profile" className="profile-pill">
                <span className="avatar"><CircleUserRound size={13} /></span>
                <span>{user.full_name?.split(" ")[0]}</span>
              </Link>
              <button className="btn btn-ghost btn-sm btn-icon" onClick={handleSignOut} title="Sign out"><LogOut size={15} /></button>
            </div>
          ) : (
            <div className="nav-auth-links">
              <Link href="/login" className="btn btn-ghost btn-sm"><LogIn size={14} /> Sign in</Link>
              <Link href="/register" className="btn btn-primary btn-sm"><UserPlus size={14} /> Register</Link>
            </div>
          )}
          <button className="menu-button" onClick={() => setOpen(!open)}>
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-inner">
        <span>© 2026 Zeevan · AI health companion. Not a substitute for professional medical advice.</span>
        <div className="footer-links">
          <Link href="/about">About</Link>
        </div>
      </div>
    </footer>
  );
}

function Layout({ path, children, go, theme, toggleTheme }) {
  return (
    <div className="zeevan-root">
      <Header path={path} go={go} theme={theme} toggleTheme={toggleTheme} />
      <div className="page-content">{children}</div>
      <Footer />
    </div>
  );
}

function AIOrb({ state = "idle" }) {
  const label = state === "idle" ? "Listening for what matters"
    : state === "analyzing" ? "Analysing symptom patterns"
    : "Ready with clarity";
  return (
    <div className="orb-stage">
      <div className="orb-wrap">
        <div className="orb-ring r1" />
        <div className="orb-ring r2" />
        <div className="orb-ring r3" />
        <span className="orb-particle p1" />
        <span className="orb-particle p2" />
        <span className="orb-particle p3" />
        <span className="orb-particle p4" />
        <div className="orb-core" />
        <div className="orb-state"><span className="state-dot" />{label}</div>
      </div>
    </div>
  );
}

function VoiceButton({ onText }) {
  const [listening, setListening] = useState(false);
  const start = () => {
    const R = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!R) return alert("Voice input is not supported in this browser.");
    const r = new R(); r.lang = "en-IN";
    r.onstart  = () => setListening(true);
    r.onend    = () => setListening(false);
    r.onresult = e => onText(e.results[0][0].transcript);
    r.start();
  };
  return (
    <button className={`voice-btn${listening ? " listening" : ""}`} onClick={start} title="Voice input">
      <Mic size={14} />
    </button>
  );
}

function Chips({ selected, setSelected, pool = SYMPTOM_CHIPS }) {
  return (
    <div className="chips">
      {pool.map(chip => {
        const sel = selected.includes(chip);
        return (
          <button key={chip} className={`chip${sel ? " selected" : ""}`}
            onClick={() => setSelected(sel ? selected.filter(x => x !== chip) : [...selected, chip])}>
            {sel ? <Check size={10} /> : "+"} {chip}
          </button>
        );
      })}
    </div>
  );
}

function PrivacyNote() {
  return (
    <div className="privacy-note">
      <ShieldCheck size={18} />
      <span>Zeevan provides health awareness guidance, not medical diagnosis. Your data is stored only on your own device's local database. If symptoms feel urgent, contact emergency services immediately.</span>
    </div>
  );
}

// ── Home Page ─────────────────────────────────────────────────────────────────
function HomePage({ go }) {
  const { user } = useAuth();
  const [text, setText] = useState("");
  const [selected, setSelected] = useState([]);
  const quickSubmit = () => {
    if (!text.trim() && !selected.length) return;
    sessionStorage.setItem("zeevan_draft", JSON.stringify({ text, selected }));
    go("/check");
  };
  return (
    <main>
      <div className="container">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><span className="eyebrow-dot" /> AI-powered health companion</div>
            <h1>Your health questions <em>deserve clarity.</em></h1>
            <p className="hero-sub">
              Describe how you're feeling in your own words — English, Hindi, or Hinglish.
              Zeevan helps you make sense of your symptoms and decide on a sensible next step.
            </p>
            <div className="hero-actions">
              <button className="btn btn-primary" onClick={() => go("/check")}>
                Start a check <ArrowRight size={15} />
              </button>
            </div>
          </div>
          <AIOrb />
        </section>

        {/* Quick compose */}
        <div className="composer" style={{ marginBottom: 80 }}>
          <div className="composer-card">
            <div>
              <textarea value={text} onChange={e => setText(e.target.value)}
                placeholder="I've had a dull headache since morning and feel slightly tired..." />
              <Chips selected={selected} setSelected={setSelected} pool={SYMPTOM_CHIPS.slice(0, 14)} />
              <div className="composer-footer">
                <span>English · Hindi · Hinglish supported</span>
                <VoiceButton onText={t => setText(prev => `${prev} ${t}`.trim())} />
              </div>
            </div>
            <button className="btn btn-primary composer-submit" onClick={quickSubmit}>
              Check <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Journey band */}
      {user && (
        <section className="section" style={{ paddingTop: 24 }}>
          <div className="container">
            <div className="journey-band">
              <div>
                <span className="kicker mono">Your health journey</span>
                <h2>Notice what changes over time.</h2>
                <p>All your symptom checks are saved privately in your local database.</p>
                <button className="btn btn-primary" style={{ marginTop: 22 }} onClick={() => go("/journey")}>
                  View journey <ArrowRight size={14} />
                </button>
              </div>
              <div className="journey-list">
                {[
                  { title: "Recent symptom check", detail: "Powered by AI · 41 diseases covered", status: "analyzed" },
                  { title: "Health pattern tracking", detail: "Personal timeline · Privately stored", status: "saved" },
                ].map((item, i) => (
                  <div className="journey-item" key={i}>
                    <span className="journey-icon"><HeartPulse size={14} /></span>
                    <div><strong>{item.title}</strong><span>{item.detail}</span></div>
                    <span className={`journey-status ${item.status}`}>{item.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}
      <div className="container"><PrivacyNote /></div>
    </main>
  );
}

// ── Login Page ─────────────────────────────────────────────────────────────────
function LoginPage({ go }) {
  const { signIn, user } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { if (user) go("/journey"); }, [user]);

  const submit = async e => {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      const r = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: form.email, password: form.password }),
      });
      signIn(r.user, r.access_token);
      go("/journey");
    } catch (err) {
      setError(err.message || "Invalid email or password.");
    } finally { setLoading(false); }
  };
  const set = field => e => setForm(f => ({ ...f, [field]: e.target.value }));

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo"><BrandOrb size={36} /><span>Zeevan</span></div>
        <h1>Welcome back</h1>
        <p className="sub">Sign in to access your health journey</p>
        {error && <div style={{ padding: "10px 14px", borderRadius: 10, background: "rgba(255,92,122,.1)", border: "1px solid rgba(255,92,122,.2)", color: "var(--danger)", fontSize: ".78rem", marginBottom: 8 }}>{error}</div>}
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Email address</label>
            <input id="login-email" className="auth-input" type="email" placeholder="you@example.com"
              value={form.email} onChange={set("email")} required autoComplete="email" />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input id="login-password" className="auth-input" type="password" placeholder="••••••••"
              value={form.password} onChange={set("password")} required autoComplete="current-password" />
          </div>
          <button id="login-submit" className="btn btn-primary auth-submit" disabled={loading}>
            {loading ? "Signing in…" : <><LogIn size={15} /> Sign in</>}
          </button>
        </form>
        <div className="auth-divider"><span>or</span></div>
        <p className="auth-switch">Don't have an account? <Link href="/register">Create one →</Link></p>
        <div className="db-info-card">
          <strong>🔒 Where is your data stored?</strong>
          Your email and hashed password are stored locally in <code style={{ color: "var(--primary)", fontSize: ".68rem" }}>backend/zeevan.db</code> (SQLite) in the <code style={{ color: "var(--primary)", fontSize: ".68rem" }}>users</code> table on your own machine. No data leaves your device.
        </div>
      </div>
    </div>
  );
}

// ── Register Page ──────────────────────────────────────────────────────────────
function RegisterPage({ go }) {
  const { signIn, user } = useAuth();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { if (user) go("/journey"); }, [user]);

  const submit = async e => {
    e.preventDefault(); setError("");
    if (form.password !== form.confirm) { setError("Passwords do not match."); return; }
    if (form.password.length < 8) { setError("Password must be at least 8 characters."); return; }
    setLoading(true);
    try {
      const r = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ full_name: form.full_name, email: form.email, password: form.password }),
      });
      signIn(r.user, r.access_token);
      go("/journey");
    } catch (err) {
      setError(err.message || "Could not create account.");
    } finally { setLoading(false); }
  };
  const set = field => e => setForm(f => ({ ...f, [field]: e.target.value }));

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo"><BrandOrb size={36} /><span>Zeevan</span></div>
        <h1>Create account</h1>
        <p className="sub">Start tracking your health journey</p>
        {error && <div style={{ padding: "10px 14px", borderRadius: 10, background: "rgba(255,92,122,.1)", border: "1px solid rgba(255,92,122,.2)", color: "var(--danger)", fontSize: ".78rem", marginBottom: 8 }}>{error}</div>}
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Full name</label>
            <input id="reg-name" className="auth-input" type="text" placeholder="Arjun Sharma"
              value={form.full_name} onChange={set("full_name")} required autoComplete="name" />
          </div>
          <div className="form-group">
            <label>Email address</label>
            <input id="reg-email" className="auth-input" type="email" placeholder="you@example.com"
              value={form.email} onChange={set("email")} required autoComplete="email" />
          </div>
          <div className="form-group">
            <label>Password (min. 8 characters)</label>
            <input id="reg-password" className="auth-input" type="password" placeholder="Create a strong password"
              value={form.password} onChange={set("password")} required autoComplete="new-password" />
          </div>
          <div className="form-group">
            <label>Confirm password</label>
            <input id="reg-confirm" className="auth-input" type="password" placeholder="Repeat your password"
              value={form.confirm} onChange={set("confirm")} required autoComplete="new-password" />
          </div>
          <button id="reg-submit" className="btn btn-primary auth-submit" disabled={loading}>
            {loading ? "Creating account…" : <><UserPlus size={15} /> Create account</>}
          </button>
        </form>
        <div className="auth-divider"><span>or</span></div>
        <p className="auth-switch">Already have an account? <Link href="/login">Sign in →</Link></p>
        <div className="db-info-card">
          <strong>🔒 Where is your data stored?</strong>
          Your account is stored in <code style={{ color: "var(--primary)", fontSize: ".68rem" }}>backend/zeevan.db</code> → <code style={{ color: "var(--primary)", fontSize: ".68rem" }}>users</code> table. Passwords are hashed with PBKDF2-SHA256 (120,000 rounds). No data leaves your device.
        </div>
      </div>
    </div>
  );
}

// ── Check Page ─────────────────────────────────────────────────────────────────
function CheckPage({ go }) {
  const draft = (() => { try { return JSON.parse(sessionStorage.getItem("zeevan_draft") || "{}"); } catch { return {}; } })();
  const [text, setText] = useState(draft.text || "");
  const [selected, setSelected] = useState(draft.selected || []);
  const [step, setStep] = useState(1);
  const [checkId, setCheckId] = useState(null);
  const [result, setResult] = useState(null);
  const [moreSymptoms, setMoreSymptoms] = useState("");
  const [conversation, setConversation] = useState([]);
  const [busy, setBusy] = useState(false);

  const analyzeText = async (desc, isFollowUp = false) => {
    if (!desc) return alert("Please describe your symptoms first.");
    try {
      setBusy(true);
      if (!isFollowUp) setStep(3);
      const r = await api("/api/symptoms/check", {
        method: "POST",
        body: JSON.stringify({ description: desc, selected: isFollowUp ? [] : selected }),
      });
      const analyzed = await api(`/api/symptoms/check/${r.id}/analyze`, {
        method: "POST",
        body: JSON.stringify({ answers: {} }),
      });
      setCheckId(r.id);
      setResult(analyzed);
      setConversation(prev => [...prev, { patient: isFollowUp ? moreSymptoms.trim() : desc, response: analyzed }]);
      setStep(4);
      if (isFollowUp) setMoreSymptoms("");
    } catch (e) { alert(e.message); if (!isFollowUp) setStep(1); }
    finally { setBusy(false); }
  };

  const submit = () => analyzeText(`${text} ${selected.join(" ")}`.trim());
  const continueConversation = () => {
    const addition = moreSymptoms.trim();
    if (!addition) return;
    const previous = conversation.map(turn => turn.patient).join(". ");
    analyzeText(`${previous}. ${addition}`, true);
  };

  return (
    <main className="container">
      <div className="page-top">
        <div className="eyebrow"><span className="eyebrow-dot" /> Symptom checker</div>
        <h1>Let's understand what's happening.</h1>
        <p>Describe your symptoms. Zeevan's AI will analyse patterns and surface your clearest next step.</p>
      </div>

      {step === 1 && (
        <div className="check-grid">
          <div className="card check-main">
            <h2>What symptoms are you having?</h2>
            <label className="input-label">Your symptoms (English, Hindi, or Hinglish)</label>
            <textarea value={text} onChange={e => setText(e.target.value)}
              placeholder="I have a dull headache since morning and feel slightly tired... (or: mujhe sar dard hai aur thakaan lag rahi hai)" />
            <div style={{ marginTop: 12 }}>
              <label className="input-label">Quick-add symptoms</label>
              <Chips selected={selected} setSelected={setSelected} />
            </div>
            <div className="composer-footer" style={{ marginTop: 12 }}>
              <span>Tip: the more detail, the better the AI analysis</span>
              <VoiceButton onText={t => setText(p => `${p} ${t}`.trim())} />
            </div>
            <button className="btn btn-primary" style={{ width: "100%", marginTop: 22 }} onClick={submit}>
              {busy ? "Analysing…" : "Send symptoms"} <ArrowRight size={15} />
            </button>
          </div>
          <div className="card check-side">
            <Sparkles size={20} color="var(--primary)" />
            <h3 style={{ marginTop: 12 }}>How AI analysis works</h3>
            <p>Your symptoms are processed through two stages:</p>
            <ul className="side-points">
              <li><Brain size={14} />NLP extracts symptom keywords from your text</li>
              <li><Activity size={14} />Reported symptoms are compared with condition patterns in the training dataset</li>
              <li><BarChart2 size={14} />See the symptoms shared with each condition pattern</li>
              <li><ShieldCheck size={14} />Emergency flags checked independently</li>
            </ul>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="analyze-loading">
          <AIOrb state="analyzing" />
          <h2>Analysing your symptoms…</h2>
          <p>Comparing reported symptoms with condition patterns and checking safety guidance.</p>
        </div>
      )}

      {step === 4 && result && (
        <>
          <ResultView result={result} checkId={checkId} go={go} onNew={() => { setStep(1); setResult(null); setText(""); setSelected([]); setConversation([]); }} />
          <div className="flow-card card followup-card">
            <div className="followup-heading">
              <span className="followup-icon"><Sparkles size={17} /></span>
              <div>
                <span className="followup-eyebrow">Continue your check-in</span>
                <h3>Is anything else bothering you?</h3>
                <p>Share another symptom or change, and I’ll add it to this analysis.</p>
              </div>
            </div>
            {conversation.map((turn, i) => <div key={i} style={{ padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
              <p><strong>You:</strong> {turn.patient}</p><p style={{ color: "var(--text-muted)" }}><strong>Zeevan:</strong> {turn.response.follow_up_prompt || "Any other symptoms or changes?"}</p>
            </div>)}
            <div className="followup-entry">
              <textarea className="followup-input" value={moreSymptoms} onChange={e => setMoreSymptoms(e.target.value)} placeholder="Tell me what else you’re experiencing…" aria-label="Additional symptoms or concerns" />
              <button className="btn btn-primary followup-submit" onClick={continueConversation} disabled={busy || !moreSymptoms.trim()}>{busy ? "Updating…" : "Add to my analysis"} <ArrowRight size={14} /></button>
            </div>
          </div>
        </>
      )}
    </main>
  );
}

// ── Result View ───────────────────────────────────────────────────────────────
function ResultView({ result, checkId, go, onNew }) {
  const { user } = useAuth();
  const [saved, setSaved] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const saveJourney = async () => {
    try {
      await api(`/api/symptoms/${checkId}/save`, { method: "POST" });
      setSaved(true);
    } catch (e) {
      if (!user) { go("/login"); } else { alert(e.message); }
    }
  };

  const sendFeedback = async (helpful) => {
    setFeedback(helpful);
    try {
      await api(`/api/symptoms/${checkId}/feedback`, {
        method: "POST",
        body: JSON.stringify({ was_helpful: helpful }),
      });
    } catch (_) {}
  };

  const downloadSummary = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `zeevan-summary-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
  };

  const datasetMatches = result?.dataset_matches || [];
  const orderedDatasetMatches = [...datasetMatches].sort((a, b) => {
    const orderFor = match => CONDITION_DISPLAY_ORDER.get(match.label.trim().toLowerCase()) ?? 4 + (match.concern_order ?? 1);
    return orderFor(a) - orderFor(b)
      || b.shared_count - a.shared_count
      || b.overlap_pct - a.overlap_pct
      || a.label.localeCompare(b.label);
  });

  return (
    <div className="result-wrap">
      <div className="result-hero card">
        <div>
          <span className="result-badge"><Sparkles size={10} /> {result?.differential?.length ? "Symptom guide" : "Symptom pattern review"}</span>
          <h2>Here's what your symptoms may suggest.</h2>
          <p>{result?.differential?.length ? "Common possibilities based on this symptom pattern. This guide is not a diagnosis." : "Ranked pattern matches from an educational model, not a diagnosis or clinical probability."}</p>
        </div>
        <div className="result-mini-orb" />
      </div>

      {result?.urgent && (
        <div className="urgent-card">
          <ShieldCheck size={22} />
          <div>
            <strong>⚠ Seek urgent medical care</strong>
            <p>One or more of your symptoms may need immediate attention. Contact emergency services (112) or go to the nearest emergency room now.</p>
          </div>
        </div>
      )}

      <div className="result-grid" style={{ marginTop: 14 }}>

        {/* Conditions ranked by shared dataset symptoms */}
        <section className="result-card card">
          <h3><Activity size={15} style={{ display: "inline", marginRight: 7, color: "var(--primary)" }} />{datasetMatches.length ? "Possible condition patterns" : result?.differential?.length ? "Common possibilities" : "General symptom guidance"}</h3>
          <p>{datasetMatches.length ? "Listed from lower to higher general concern. These are symptom-pattern matches, not a diagnosis or a probability that you have a condition. The concern band is general; your personal urgency depends on your symptoms and warning signs." : result?.differential?.length ? "These possibilities can share symptoms; this list is not a diagnosis." : "Here are general next steps based on what you described. Add any other symptoms below if you want to continue."}</p>
          {datasetMatches.length ? (
            <div className="predictions-panel">
              {orderedDatasetMatches.map(match => (
                <div className="prediction-row" key={match.label} style={{ alignItems: "flex-start", padding: "12px 0" }}>
                  <div style={{ flex: 1 }}>
                    <span className="prediction-label">{match.label}</span>
                    <span className={`condition-concern concern-${match.concern_order}`}>{match.concern_label}</span>
                    <div className="features-panel" style={{ marginTop: 8 }}>
                      {match.shared_symptoms.map(symptom => <span key={symptom} className="feature-tag matched">{symptom}</span>)}
                    </div>
                  </div>
                  <span className="confidence-pct" title="Symptom overlap, not likelihood">{match.shared_count}/{match.reported_symptom_count} symptoms</span>
                </div>
              ))}
              {result?.differential?.length > 0 && (
                <div style={{ marginTop: 14 }}>
                  <strong>Other common possibilities to discuss</strong>
                  <ul className="bullet-list" style={{ marginTop: 8 }}>
                    {result.differential.map(item => <li key={item}><Activity size={13} />{item}</li>)}
                  </ul>
                </div>
              )}
              <p style={{ fontSize: ".72rem", color: "var(--text-faint)", marginTop: 8 }}>Matches reflect repeated symptom patterns in the source CSV; its rows are not unique, clinically validated patient cases. A clinician must assess the full context.</p>
            </div>
          ) : result?.differential?.length ? (
            <ul className="bullet-list">
              {result.differential.map(item => <li key={item}><Activity size={13} />{item}</li>)}
            </ul>
          ) : <div className="predictions-panel"><p style={{ color: "var(--text-muted)" }}>If symptoms are mild and improving, rest and monitor them. Contact a clinician if they worsen, persist, or concern you.</p></div>}
          {result?.medicine_note && <p className="medicine-note">{result.medicine_note}</p>}
        </section>

        {/* Matched symptoms & key features */}
        <section className="result-card card">
          <h3><Brain size={15} style={{ display: "inline", marginRight: 7, color: "var(--primary)" }} />What triggered the prediction</h3>
          <p>Symptoms detected in your message and the dataset features they could be matched to.</p>
          {result?.nlp_extracted_symptoms?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div className="input-label">Symptoms detected</div>
              <div className="features-panel">
                {result.nlp_extracted_symptoms.map(s => <span key={s} className="feature-tag matched">{s.replaceAll("_", " ")}</span>)}
              </div>
            </div>
          )}
          {result?.matched_symptoms?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div className="input-label">Symptoms matched to model</div>
              <div className="features-panel">
                {result.matched_symptoms.map(s => <span key={s} className="feature-tag matched">{s}</span>)}
              </div>
            </div>
          )}
          {result?.triggered_key_features?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div className="input-label">Key features activated</div>
              <div className="features-panel">
                {result.triggered_key_features.map(f => <span key={f} className="feature-tag">{f}</span>)}
              </div>
            </div>
          )}
        </section>

        {/* Disease-specific advice */}
        <section className="result-card card">
          <h3><Check size={15} style={{ display: "inline", marginRight: 7, color: "var(--primary)" }} />Health & lifestyle advice</h3>
          <ul className="bullet-list">
            {result?.advice?.map(x => <li key={x}><Check size={13} />{x}</li>)}
          </ul>
        </section>

        {/* Safety steps */}
        <section className="result-card card">
          <h3><ShieldCheck size={15} style={{ display: "inline", marginRight: 7, color: "var(--primary)" }} />Safety steps & precautions</h3>
          <ul className="bullet-list">
            {result?.safety?.map(x => <li key={x}><ShieldCheck size={13} />{x}</li>)}
          </ul>
        </section>

        {/* When to see a doctor */}
        <section className="result-card card" style={{ gridColumn: "1 / -1" }}>
          <h3><Info size={15} style={{ display: "inline", marginRight: 7, color: "var(--warn)" }} />What to do next</h3>
          <p><strong>Get emergency help now:</strong> {result?.care_guidance?.emergency || "Seek emergency help for severe or rapidly worsening symptoms."}</p>
          <p><strong>Home monitoring may be reasonable:</strong> {result?.care_guidance?.monitor || "If symptoms are mild and improving, monitor them and rest."}</p>
          <p><strong>Contact a clinician:</strong> {result?.care_guidance?.clinician || result?.doctor}</p>
        </section>
      </div>

      {/* Feedback */}
      <div className="feedback-row">
        <p>Was this AI analysis helpful to you?</p>
        <button className={`feedback-btn yes${feedback === true ? " active-yes" : ""}`} onClick={() => sendFeedback(true)}>
          <ThumbsUp size={13} style={{ marginRight: 5 }} />Yes
        </button>
        <button className={`feedback-btn no${feedback === false ? " active-no" : ""}`} onClick={() => sendFeedback(false)}>
          <ThumbsDown size={13} style={{ marginRight: 5 }} />No
        </button>
        {feedback !== null && <span style={{ fontSize: ".72rem", color: "var(--text-faint)" }}>Thank you! Your feedback improves the model.</span>}
      </div>

      <div className="result-actions">
        <button className="btn btn-primary" onClick={saveJourney} disabled={saved}>
          {saved ? <><Check size={14} /> Saved!</> : "Save to journey"}
        </button>
        <button className="btn btn-ghost" onClick={onNew}>New check</button>
        <button className="btn btn-ghost" onClick={downloadSummary}>Download JSON</button>
      </div>
      <p className="disclaimer">Zeevan provides general health awareness guidance only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.</p>
    </div>
  );
}

// ── Journey Page ───────────────────────────────────────────────────────────────
function JourneyPage({ go }) {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) { go("/login"); return; }
    api("/api/journeys").then(setItems).catch(() => {}).finally(() => setLoading(false));
  }, [user]);

  return (
    <main className="container journey-page">
      <div className="page-top journey-head">
        <div>
          <div className="eyebrow"><span className="eyebrow-dot" /> Your health journey</div>
          <h1>Understand your patterns over time.</h1>
          <p>Every symptom check you save appears here with AI predictions and timestamps.</p>
        </div>
        <Link href="/check" className="btn btn-primary">New check <ArrowRight size={14} /></Link>
      </div>

      {loading ? (
        <p style={{ color: "var(--text-muted)" }}>Loading your journey…</p>
      ) : items.length === 0 ? (
        <div className="card" style={{ padding: "32px", textAlign: "center", marginTop: 24, maxWidth: 600 }}>
          <HeartPulse size={36} color="var(--primary)" style={{ marginBottom: 14 }} />
          <h3 style={{ color: "var(--text)" }}>No checks saved yet</h3>
          <p style={{ color: "var(--text-muted)", fontSize: ".84rem", marginTop: 8 }}>Complete a symptom check and save it to start your health journey.</p>
          <button className="btn btn-primary" style={{ marginTop: 18 }} onClick={() => go("/check")}>Start first check <ArrowRight size={14} /></button>
        </div>
      ) : (
        <div className="timeline">
          {items.map(x => (
            <div className="timeline-item" key={x.id}>
              <span className="timeline-dot" />
              <div className="timeline-card card">
                <span className="date">{x.created_at ? new Date(x.created_at).toLocaleDateString("en-IN", { month: "long", day: "numeric", year: "numeric" }) : "Recent"}</span>
                <h3>{x.title || "Symptom check"}</h3>
                <p>{x.detail?.substring(0, 120)}</p>
                {x.prediction && (
                  <div style={{ marginTop: 10, display: "flex", gap: 8, alignItems: "center" }}>
                    <span className="feature-tag">AI: {x.prediction}</span>
                    {x.confidence && <span className="feature-tag matched">{(x.confidence * 100).toFixed(0)}% confidence</span>}
                  </div>
                )}
                <div className="timeline-meta">
                  <span className={`journey-status ${x.status}`}>{x.status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

// ── Profile Page ───────────────────────────────────────────────────────────────
function ProfilePage({ go }) {
  const { user, signIn, signOut } = useAuth();
  const [form, setForm] = useState({ full_name: user?.full_name || "", email: user?.email || "", date_of_birth: "", gender: "" });
  const set = field => e => setForm(f => ({ ...f, [field]: e.target.value }));

  if (!user) {
    return (
      <main className="container">
        <div className="page-top">
          <h1>Your profile</h1>
          <p>Sign in to access your profile and health journey.</p>
          <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
            <button className="btn btn-primary" onClick={() => go("/login")}><LogIn size={14} /> Sign in</button>
            <button className="btn btn-ghost" onClick={() => go("/register")}><UserPlus size={14} /> Create account</button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="container">
      <div className="page-top">
        <div className="eyebrow"><span className="eyebrow-dot" /> Your profile</div>
        <h1>Health profile.</h1>
        <p>Your preferences and account details are stored privately in your local database.</p>
      </div>
      <div className="profile-wrap card" style={{ padding: "28px" }}>
        <div className="profile-avatar"><CircleUserRound size={24} /></div>
        <h2 style={{ marginTop: 14, fontSize: "1.4rem", letterSpacing: "-.05em", color: "var(--text)" }}>{user.full_name}</h2>
        <p style={{ color: "var(--text-muted)", fontSize: ".82rem", marginBottom: 0 }}>{user.email}</p>
        <div className="profile-grid">
          <div className="field"><label>Full name</label><input value={form.full_name} onChange={set("full_name")} /></div>
          <div className="field"><label>Email</label><input value={form.email} disabled style={{ opacity: .6 }} /></div>
          <div className="field"><label>Date of birth</label><input type="date" value={form.date_of_birth} onChange={set("date_of_birth")} /></div>
          <div className="field"><label>Gender</label>
            <select value={form.gender} onChange={set("gender")}>
              <option value="">Prefer not to say</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
        <div className="db-info-card" style={{ marginTop: 20 }}>
          <strong>🗄️ Database location</strong>
          Your account data (email, hashed password, profile) is stored at:<br />
          <code style={{ color: "var(--primary)", fontSize: ".7rem" }}>backend/zeevan.db → users table</code><br />
          <code style={{ color: "var(--text-faint)", fontSize: ".67rem" }}>User ID: {user.id}</code>
        </div>
        <div className="profile-actions">
          <button className="btn btn-danger btn-sm" onClick={() => { signOut(); go("/"); }}>
            <LogOut size={13} /> Sign out
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => go("/journey")}>
            <HeartPulse size={13} /> View journey
          </button>
        </div>
      </div>
    </main>
  );
}

// ── About Page ────────────────────────────────────────────────────────────────
function AboutPage() {
  const features = [
    [HeartPulse, "A place to describe how you feel", "Share symptoms in your own words and add more details as the conversation continues."],
    [ShieldCheck, "Practical next steps", "See when home monitoring may be reasonable and when to seek medical care."],
    [Zap, "Language that feels natural", "Describe symptoms in English, Hindi, or Hinglish."],
    [Database, "Your private health journey", "Save symptom checks and notes to review over time."],
  ];
  return (
    <main className="container" style={{ paddingBottom: 100 }}>
      <div className="page-top">
        <div className="eyebrow"><span className="eyebrow-dot" /> About Zeevan</div>
        <h1>Healthcare information should feel understandable.</h1>
        <p>Zeevan helps you describe what is bothering you, explore possible explanations, and consider a sensible next step. It offers general health information, not a medical diagnosis.</p>
      </div>
      <div className="about-features">
        {features.map(([Icon, title, desc]) => (
          <div className="about-feature" key={title}>
            <Icon size={20} />
            <div><strong>{title}</strong><span style={{ display: "block", color: "var(--text-muted)", fontSize: ".77rem", marginTop: 3 }}>{desc}</span></div>
          </div>
        ))}
      </div>
    </main>
  );
}

// ── App Root ──────────────────────────────────────────────────────────────────
function App() {
  const [path, go] = useRouter();
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem("zeevan_theme");
    return saved === "light" || saved === "dark" ? saved : "dark";
  });
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    localStorage.setItem("zeevan_theme", theme);
  }, [theme]);
  const toggleTheme = () => setTheme(current => current === "dark" ? "light" : "dark");
  const routes = {
    "/":             <HomePage go={go} />,
    "/check":        <CheckPage go={go} />,
    "/journey":      <JourneyPage go={go} />,
    "/login":        <LoginPage go={go} />,
    "/register":     <RegisterPage go={go} />,
    "/profile":      <ProfilePage go={go} />,
    "/about":        <AboutPage />,
  };
  const page = routes[path] || routes["/"];
  return (
    <AuthProvider>
      <Layout path={path} go={go} theme={theme} toggleTheme={toggleTheme}>{page}</Layout>
    </AuthProvider>
  );
}

createRoot(document.getElementById("root")).render(<App />);
