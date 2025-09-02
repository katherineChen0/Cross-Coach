import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

type User = { id: string; email: string; name?: string }

type Log = {
  id: string
  user_id: string
  log_date: string
  domain: string
  value?: number | null
  metrics?: Record<string, any> | null
  note?: string | null
}

type Insight = {
  id: string
  user_id: string
  week_start: string
  summary?: string | null
  correlations?: Record<string, number> | null
}

const domains = ['fitness', 'climbing', 'coding', 'mood', 'sleep', 'journaling'] as const

type Domain = typeof domains[number]

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const [active, setActive] = useState<Domain>('fitness')
  const [date, setDate] = useState<string>(new Date().toISOString().slice(0, 10))
  const [value, setValue] = useState<string>('')
  const [note, setNote] = useState<string>('')
  const [logs, setLogs] = useState<Log[]>([])
  const [insights, setInsights] = useState<Insight[]>([])

  useEffect(() => {
    // ensure demo user exists (created by seed ideally, but fallback here)
    const ensureDemo = async () => {
      const email = 'demo@crosscoach.app'
      try {
        const created = await axios.post(`${API_BASE}/api/users`, { email, name: 'Demo User' })
        setUser(created.data)
      } catch (e: any) {
        // try to fetch if already exists via seed by scanning logs later; for MVP just store null
      }
    }
    ensureDemo()
  }, [])

  useEffect(() => {
    const load = async () => {
      if (!user) return
      const res = await axios.get(`${API_BASE}/api/logs/${user.id}`)
      setLogs(res.data)
      const ins = await axios.get(`${API_BASE}/api/insights/${user.id}`)
      setInsights(ins.data)
    }
    load()
  }, [user])

  const createLog = async () => {
    if (!user) return
    const payload = { user_id: user.id, log_date: date, domain: active, value: value === '' ? null : Number(value), note: note || null }
    const res = await axios.post(`${API_BASE}/api/logs`, payload)
    setLogs([res.data, ...logs])
    setValue('')
    setNote('')
  }

  const correlationsList = useMemo(() => {
    const row = insights[0]
    const corr = row?.correlations || {}
    return Object.entries(corr).map(([k, v]) => `${k}: ${v.toFixed(2)}`)
  }, [insights])

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">CrossCoach</h1>
        <span className="text-sm text-gray-600">{user?.email || 'Loading user...'}</span>
      </header>

      <nav className="flex gap-2 flex-wrap">
        {domains.map(d => (
          <button key={d} onClick={() => setActive(d)} className={`px-3 py-1 rounded-full border ${active === d ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}>
            {d}
          </button>
        ))}
      </nav>

      <section className="bg-white rounded-xl p-4 shadow space-y-2">
        <div className="flex gap-2">
          <input type="date" value={date} onChange={e => setDate(e.target.value)} className="border rounded px-2 py-1" />
          {active !== 'journaling' && (
            <input type="number" value={value} onChange={e => setValue(e.target.value)} placeholder="Value" className="border rounded px-2 py-1 w-32" />
          )}
        </div>
        <textarea value={note} onChange={e => setNote(e.target.value)} placeholder="Optional note / journal" className="w-full border rounded px-2 py-1" rows={3} />
        <div>
          <button onClick={createLog} className="px-4 py-2 bg-blue-600 text-white rounded">Log</button>
        </div>
      </section>

      <section className="space-y-2">
        <h2 className="font-semibold">Recent Logs</h2>
        <div className="grid gap-2">
          {logs.slice(0, 10).map(l => (
            <div key={l.id} className="bg-white p-3 rounded shadow flex justify-between text-sm">
              <div className="font-medium">{l.domain}</div>
              <div>{l.log_date}</div>
              <div>{l.value ?? '-'}</div>
              <div className="text-gray-600 truncate max-w-[40%]">{l.note}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-2">
        <h2 className="font-semibold">Weekly Insights</h2>
        {insights.length === 0 ? (
          <p className="text-sm text-gray-600">No insights yet. Run analytics worker.</p>
        ) : (
          <div className="bg-white rounded p-4 shadow space-y-2">
            <div className="text-sm text-gray-600">Week starting {insights[0].week_start}</div>
            {insights[0].summary && <p className="whitespace-pre-wrap">{insights[0].summary}</p>}
            {correlationsList.length > 0 && (
              <div>
                <h3 className="font-medium">Correlations</h3>
                <ul className="list-disc pl-5 text-sm">
                  {correlationsList.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </section>

      <footer className="text-center text-xs text-gray-500 py-8">MVP · CrossCoach</footer>
    </div>
  )
} 