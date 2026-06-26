import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  BadgeCheck,
  Braces,
  ClipboardCopy,
  FileJson,
  Loader2,
  MessageSquareText,
  Plus,
  RefreshCcw,
  Route,
  ShieldCheck,
  Sparkles,
  Trash2,
  WalletCards
} from 'lucide-react';
import { API_BASE_URL, analyzeTicket, checkHealth, normalizeBaseUrl } from './api/client';
import { blankTransaction, languageOptions, sampleCases, transactionStatuses, transactionTypes, userTypes } from './data/examples';
import Footer from './components/Footer';

const defaultPayload = sampleCases[0].payload;
const API_STORAGE_KEY = 'queuestorm_api_base_url';

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function labelize(value) {
  if (value === null || value === undefined || value === '') return 'Not available';
  return String(value).replaceAll('_', ' ');
}

function Pill({ children, tone = 'neutral' }) {
  return <span className={`pill pill-${tone}`}>{children}</span>;
}

function SectionTitle({ icon: Icon, title, subtitle }) {
  return (
    <div className="section-title">
      <span className="section-icon"><Icon size={18} /></span>
      <div>
        <h2>{title}</h2>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
    </div>
  );
}

function StatCard({ title, value, tone = 'neutral', icon: Icon }) {
  return (
    <div className={`stat stat-${tone}`}>
      <div className="stat-top">
        <span>{title}</span>
        {Icon ? <Icon size={18} /> : null}
      </div>
      <strong>{value}</strong>
    </div>
  );
}

export default function App() {
  const [baseUrl, setBaseUrl] = useState(() => localStorage.getItem(API_STORAGE_KEY) || API_BASE_URL);
  const [apiDraft, setApiDraft] = useState(() => localStorage.getItem(API_STORAGE_KEY) || API_BASE_URL);
  const [payload, setPayload] = useState(() => clone(defaultPayload));
  const [jsonText, setJsonText] = useState(() => pretty(defaultPayload));
  const [mode, setMode] = useState('form');
  const [loading, setLoading] = useState(false);
  const [healthLoading, setHealthLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setJsonText(pretty(payload));
  }, [payload]);

  useEffect(() => {
    setApiDraft(baseUrl);
  }, [baseUrl]);

  const parsedJson = useMemo(() => {
    try {
      return { ok: true, value: JSON.parse(jsonText) };
    } catch (err) {
      return { ok: false, error: err.message };
    }
  }, [jsonText]);


  function applyApiBaseUrl() {
    const nextUrl = normalizeBaseUrl(apiDraft);
    if (!nextUrl) {
      setHealth({ ok: false, message: 'Please enter a valid API base URL.' });
      return;
    }
    setBaseUrl(nextUrl);
    localStorage.setItem(API_STORAGE_KEY, nextUrl);
    setHealth(null);
    setError(null);
    setResult(null);
  }

  function resetApiBaseUrl() {
    setBaseUrl(API_BASE_URL);
    setApiDraft(API_BASE_URL);
    localStorage.removeItem(API_STORAGE_KEY);
    setHealth(null);
    setError(null);
    setResult(null);
  }

  async function runHealthCheck() {
    setHealthLoading(true);
    setHealth(null);
    try {
      const data = await checkHealth(baseUrl);
      setHealth({ ok: true, data });
    } catch (err) {
      setHealth({ ok: false, status: err.status, message: err.message, payload: err.payload });
    } finally {
      setHealthLoading(false);
    }
  }

  async function submitAnalysis(event) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const requestPayload = mode === 'json' ? parsedJson.value : payload;
      if (mode === 'json' && !parsedJson.ok) {
        throw new Error(`Invalid JSON: ${parsedJson.error}`);
      }
      const data = await analyzeTicket(requestPayload, baseUrl);
      setResult(data);
    } catch (err) {
      setError({ status: err.status, message: err.message, payload: err.payload });
    } finally {
      setLoading(false);
    }
  }

  function updateField(field, value) {
    setPayload(prev => ({ ...prev, [field]: value }));
  }

  function updateTransaction(index, field, value) {
    setPayload(prev => {
      const txs = [...(prev.transaction_history || [])];
      txs[index] = { ...txs[index], [field]: field === 'amount' ? Number(value) : value };
      return { ...prev, transaction_history: txs };
    });
  }

  function addTransaction() {
    setPayload(prev => ({
      ...prev,
      transaction_history: [...(prev.transaction_history || []), { ...blankTransaction }]
    }));
  }

  function removeTransaction(index) {
    setPayload(prev => ({
      ...prev,
      transaction_history: (prev.transaction_history || []).filter((_, i) => i !== index)
    }));
  }

  function loadSample(sample) {
    setPayload(clone(sample.payload));
    setResult(null);
    setError(null);
  }

  async function copyResult() {
    if (!result) return;
    await navigator.clipboard.writeText(pretty(result));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
  }

  const verdictTone = result?.evidence_verdict === 'consistent' ? 'success' : result?.evidence_verdict === 'inconsistent' ? 'danger' : 'warning';
  const severityTone = result?.severity === 'critical' || result?.severity === 'high' ? 'danger' : result?.severity === 'medium' ? 'warning' : 'success';

  return (
    <>
      <main className="app-shell">
      <section className="hero">
        <div className="hero-content">
          <Pill tone="brand"><Sparkles size={14} /> SUST QueueStorm Investigator</Pill>
          <h1>SupportOps Copilot Frontend</h1>
          <p>
            A Vite + React dashboard for testing the QueueStorm Investigator API. Set your backend URL once, submit customer complaints, inspect evidence reasoning, and copy the structured response.
          </p>
          <div className="hero-actions">
            <a href="#analyze" className="primary-link">Analyze Ticket</a>
            <button type="button" className="ghost-button" onClick={runHealthCheck} disabled={healthLoading}>
              {healthLoading ? <Loader2 className="spin" size={16} /> : <Activity size={16} />} Check API Health
            </button>
          </div>
        </div>
        <div className="hero-panel api-panel">
          <span>Current API Base URL</span>
          <code>{baseUrl}</code>

          <label className="field api-field">
            <span>Temporary API URL for testing</span>
            <input
              value={apiDraft}
              onChange={(e) => setApiDraft(e.target.value)}
              placeholder="https://your-test-api.example.com"
            />
            <small>
              Default comes from <code>VITE_API_BASE_URL</code>. A changed URL is saved only in this browser using localStorage.
            </small>
          </label>

          <div className="api-actions">
            <button type="button" className="ghost-button" onClick={applyApiBaseUrl}>Use This API</button>
            <button type="button" className="ghost-button" onClick={resetApiBaseUrl}>Reset Default</button>
          </div>

          <div className="health-line">
            {health ? (
              health.ok ? <Pill tone="success">API online: {health.data?.status || 'ok'}</Pill> : <Pill tone="danger">API error {health.status || ''}</Pill>
            ) : <Pill>Health not checked</Pill>}
          </div>
        </div>
      </section>

      <section className="grid-layout" id="analyze">
        <form className="card input-card" onSubmit={submitAnalysis}>
          <SectionTitle icon={WalletCards} title="Ticket Input" subtitle="Use the visual form or raw JSON request body." />

          <div className="api-note full">
            <strong>Using API:</strong> <code>{baseUrl}</code>
            <span>Change it from the API panel above when testing another backend.</span>
          </div>

          <div className="mode-switch">
            <button type="button" className={mode === 'form' ? 'active' : ''} onClick={() => setMode('form')}><MessageSquareText size={16} /> Form</button>
            <button type="button" className={mode === 'json' ? 'active' : ''} onClick={() => setMode('json')}><FileJson size={16} /> JSON</button>
          </div>

          <div className="sample-row">
            {sampleCases.map(sample => (
              <button type="button" key={sample.label} onClick={() => loadSample(sample)}>{sample.label}</button>
            ))}
          </div>

          {mode === 'form' ? (
            <div className="form-grid">
              <label className="field"><span>Ticket ID</span><input value={payload.ticket_id || ''} onChange={(e) => updateField('ticket_id', e.target.value)} required /></label>
              <label className="field"><span>Language</span><select value={payload.language || ''} onChange={(e) => updateField('language', e.target.value)}><option value="">Auto / empty</option>{languageOptions.map(x => <option key={x} value={x}>{x}</option>)}</select></label>
              <label className="field"><span>Channel</span><input value={payload.channel || ''} onChange={(e) => updateField('channel', e.target.value)} placeholder="in_app_chat" /></label>
              <label className="field"><span>User Type</span><select value={payload.user_type || ''} onChange={(e) => updateField('user_type', e.target.value)}><option value="">Empty</option>{userTypes.map(x => <option key={x} value={x}>{x}</option>)}</select></label>
              <label className="field full"><span>Campaign Context</span><input value={payload.campaign_context || ''} onChange={(e) => updateField('campaign_context', e.target.value)} placeholder="Optional campaign identifier" /></label>
              <label className="field full"><span>Complaint</span><textarea value={payload.complaint || ''} onChange={(e) => updateField('complaint', e.target.value)} rows="7" required /></label>

              <div className="transactions full">
                <div className="tx-header">
                  <h3>Transaction History</h3>
                  <button type="button" onClick={addTransaction}><Plus size={15} /> Add Transaction</button>
                </div>
                {(payload.transaction_history || []).map((tx, index) => (
                  <div className="tx-card" key={`${tx.transaction_id}-${index}`}>
                    <div className="tx-title">
                      <strong>Transaction #{index + 1}</strong>
                      <button type="button" className="icon-danger" onClick={() => removeTransaction(index)}><Trash2 size={15} /></button>
                    </div>
                    <label className="field"><span>Transaction ID</span><input value={tx.transaction_id} onChange={(e) => updateTransaction(index, 'transaction_id', e.target.value)} /></label>
                    <label className="field"><span>Timestamp</span><input value={tx.timestamp} onChange={(e) => updateTransaction(index, 'timestamp', e.target.value)} /></label>
                    <label className="field"><span>Type</span><select value={tx.type} onChange={(e) => updateTransaction(index, 'type', e.target.value)}>{transactionTypes.map(x => <option key={x} value={x}>{x}</option>)}</select></label>
                    <label className="field"><span>Status</span><select value={tx.status} onChange={(e) => updateTransaction(index, 'status', e.target.value)}>{transactionStatuses.map(x => <option key={x} value={x}>{x}</option>)}</select></label>
                    <label className="field"><span>Amount</span><input type="number" min="0" value={tx.amount} onChange={(e) => updateTransaction(index, 'amount', e.target.value)} /></label>
                    <label className="field"><span>Counterparty</span><input value={tx.counterparty} onChange={(e) => updateTransaction(index, 'counterparty', e.target.value)} /></label>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="json-editor">
              <textarea value={jsonText} onChange={(e) => setJsonText(e.target.value)} rows="28" spellCheck="false" />
              {!parsedJson.ok ? <p className="json-error">Invalid JSON: {parsedJson.error}</p> : <p className="json-ok">JSON is valid.</p>}
            </div>
          )}

          <button className="submit-button" type="submit" disabled={loading || (mode === 'json' && !parsedJson.ok)}>
            {loading ? <Loader2 className="spin" size={18} /> : <ShieldCheck size={18} />} Analyze Ticket
          </button>
        </form>

        <aside className="card result-card">
          <SectionTitle icon={Braces} title="API Response" subtitle="Structured investigation result from /analyze-ticket." />

          {!result && !error ? (
            <div className="empty-state">
              <Route size={44} />
              <h3>No analysis yet</h3>
              <p>Submit a ticket to see evidence verdict, case type, severity, routing department, and safe customer reply.</p>
            </div>
          ) : null}

          {error ? (
            <div className="error-box">
              <AlertTriangle size={24} />
              <div>
                <h3>{error.status ? `API Error ${error.status}` : 'Request Error'}</h3>
                <p>{error.message}</p>
                {error.payload ? <pre>{pretty(error.payload)}</pre> : null}
              </div>
            </div>
          ) : null}

          {result ? (
            <div className="result-wrap">
              <div className="result-actions">
                <Pill tone="success"><BadgeCheck size={14} /> Ticket {result.ticket_id}</Pill>
                <button type="button" onClick={copyResult}><ClipboardCopy size={15} /> {copied ? 'Copied' : 'Copy JSON'}</button>
              </div>

              <div className="stats-grid">
                <StatCard title="Evidence" value={labelize(result.evidence_verdict)} tone={verdictTone} icon={ShieldCheck} />
                <StatCard title="Severity" value={labelize(result.severity)} tone={severityTone} icon={AlertTriangle} />
                <StatCard title="Department" value={labelize(result.department)} tone="brand" icon={Route} />
                <StatCard title="Confidence" value={result.confidence ?? 'N/A'} tone="neutral" icon={Activity} />
              </div>

              <div className="detail-list">
                <div><span>Case Type</span><strong>{labelize(result.case_type)}</strong></div>
                <div><span>Relevant Transaction</span><strong>{result.relevant_transaction_id || 'None'}</strong></div>
                <div><span>Human Review</span><strong>{result.human_review_required ? 'Required' : 'Not required'}</strong></div>
              </div>

              <article className="text-panel"><h3>Agent Summary</h3><p>{result.agent_summary}</p></article>
              <article className="text-panel"><h3>Recommended Next Action</h3><p>{result.recommended_next_action}</p></article>
              <article className="text-panel customer"><h3>Customer Reply</h3><p>{result.customer_reply}</p></article>

              {result.reason_codes?.length ? (
                <div className="reason-codes">
                  <h3>Reason Codes</h3>
                  <div>{result.reason_codes.map(code => <Pill key={code}>{code}</Pill>)}</div>
                </div>
              ) : null}

              <details className="raw-json">
                <summary><RefreshCcw size={15} /> Raw JSON</summary>
                <pre>{pretty(result)}</pre>
              </details>
            </div>
          ) : null}
        </aside>
      </section>
      </main>
      <Footer />
    </>
  );
}
