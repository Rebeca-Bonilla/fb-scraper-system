import { useEffect, useState } from 'react'
import { getAccounts, getTasks } from '../services/api'

type Job = {
  id: string
  keywords: string[]
  locations: string[]
  status: string
  totalWhatsappLinks: number
  createdAt: string
  error?: string | null
}

function DashboardView() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [accountsCount, setAccountsCount] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    cargarDashboard()
  }, [])

  async function cargarDashboard() {
    setLoading(true)

    const [tasksResponse, accountsResponse] = await Promise.all([
      getTasks(),
      getAccounts(),
    ])

    setJobs(tasksResponse.jobs || [])
    setAccountsCount((accountsResponse.accounts || []).length)

    setLoading(false)
  }

  const completed = jobs.filter((job) => job.status === 'completed').length
  const failed = jobs.filter((job) => job.status === 'failed').length
  const running = jobs.filter((job) => job.status === 'running').length
  const totalLinks = jobs.reduce((sum, job) => sum + (job.totalWhatsappLinks || 0), 0)

  const lastJob = jobs[jobs.length - 1]
  const recentJobs = [...jobs].reverse().slice(0, 5)

  return (
    <section className="wireframe-page">
      <div className="search-form-wireframe">
        <h2 style={{ marginBottom: '20px' }}>Dashboard</h2>

        <button onClick={cargarDashboard} style={{ marginBottom: '16px' }}>
          Actualizar
        </button>

        {loading && <div className="notice">Cargando dashboard...</div>}

        {!loading && (
          <>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
                gap: '12px',
                marginBottom: '20px',
              }}
            >
              <StatCard title="Cuentas activas" value={accountsCount} />
              <StatCard title="Trabajos ejecutados" value={jobs.length} />
              <StatCard title="Completados" value={completed} />
              <StatCard title="Fallidos" value={failed} />
              <StatCard title="En ejecución" value={running} />
              <StatCard title="WA encontrados" value={totalLinks} />
            </div>

            {lastJob && (
              <div
                style={{
                  background: '#f4f4f6',
                  borderLeft: '4px solid #0066cc',
                  borderRadius: '6px',
                  padding: '12px',
                  marginBottom: '20px',
                }}
              >
                <h3 style={{ marginTop: 0 }}>Último trabajo</h3>

                <div>ID: <strong>{lastJob.id}</strong></div>
                <div>Estado: <strong>{lastJob.status.toUpperCase()}</strong></div>
                <div>Concepto: <strong>{lastJob.keywords?.join(', ') || '-'}</strong></div>
                <div>Región: <strong>{lastJob.locations?.join(', ') || 'Sin región'}</strong></div>
                <div>Resultados: <strong>{lastJob.totalWhatsappLinks || 0}</strong></div>

                {lastJob.error && (
                  <div style={{ marginTop: '8px', color: '#cc3333' }}>
                    Error: {lastJob.error}
                  </div>
                )}
              </div>
            )}

            <h3>Últimos trabajos</h3>

            <div style={{ display: 'grid', gap: '8px' }}>
              {recentJobs.length === 0 && (
                <div className="notice">Todavía no hay trabajos registrados.</div>
              )}

              {recentJobs.map((job) => (
                <div
                  key={job.id}
                  style={{
                    background: '#fff',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    padding: '10px',
                  }}
                >
                  <strong>{job.id}</strong>
                  <div>Estado: {job.status.toUpperCase()}</div>
                  <div>Concepto: {job.keywords?.join(', ') || '-'}</div>
                  <div>Resultados: {job.totalWhatsappLinks || 0}</div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  )
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <div
      style={{
        background: '#f4f4f6',
        borderLeft: '4px solid #0066cc',
        borderRadius: '6px',
        padding: '12px',
      }}
    >
      <div style={{ color: '#555', fontSize: '14px' }}>{title}</div>
      <div style={{ fontSize: '28px', fontWeight: 'bold' }}>{value}</div>
    </div>
  )
}

export default DashboardView