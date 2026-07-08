import { useEffect, useState } from 'react'
import { getDownloadUrl, getTasks } from '../services/api'

type Job = {
  id: string
  keywords: string[]
  locations: string[]
  maxSeconds: number
  workers: number
  accountAliases?: string[]
  status: string
  currentStep?: string
  createdAt: string
  totalWhatsappLinks: number
  results: any[]
  error?: string | null
}

function JobsView() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null)

  useEffect(() => {
    cargarJobs()
  }, [])

  async function cargarJobs() {
    setLoading(true)
    const response = await getTasks()
    setJobs(response.jobs || [])
    setLoading(false)
  }

  function descargarCsv(job: Job) {
    if (job.status !== 'completed') return
    window.open(getDownloadUrl(job.id), '_blank')
  }

  const orderedJobs = [...jobs].reverse()

  return (
    <section className="wireframe-page">
      <div className="search-form-wireframe" style={{ width: '760px', maxWidth: '95%' }}>
        <h2 style={{ marginBottom: '20px' }}>Historial</h2>

        <button onClick={cargarJobs} style={{ marginBottom: '16px' }}>
          Actualizar
        </button>

        {loading && <div className="notice">Cargando historial...</div>}

        {!loading && orderedJobs.length === 0 && (
          <div className="notice">Todavía no hay trabajos registrados.</div>
        )}

        {!loading && orderedJobs.length > 0 && (
          <div style={{ display: 'grid', gap: '10px' }}>
            {orderedJobs.map((job) => {
              const isOpen = selectedJobId === job.id

              return (
                <div
                  key={job.id}
                  style={{
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    background: '#fff',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    onClick={() => setSelectedJobId(isOpen ? null : job.id)}
                    style={{
                      cursor: 'pointer',
                      padding: '12px',
                      background: '#f4f4f6',
                      display: 'grid',
                      gridTemplateColumns: '1.2fr 1fr 1fr 0.7fr',
                      gap: '10px',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <strong>{job.id}</strong>
                      <div style={{ fontSize: '13px', color: '#666' }}>
                        {formatDate(job.createdAt)}
                      </div>
                    </div>

                    <div>
                      <strong>{job.keywords?.join(', ') || '-'}</strong>
                      <div style={{ fontSize: '13px', color: '#666' }}>
                        {job.locations?.join(', ') || 'Sin región'}
                      </div>
                    </div>

                    <StatusBadge status={job.status} />

                    <div>
                      <strong>{job.totalWhatsappLinks || 0}</strong> enlaces
                    </div>
                  </div>

                  {isOpen && (
                    <div style={{ padding: '12px' }}>
                      <div>ID: <strong>{job.id}</strong></div>
                      <div>Estado: <strong>{job.status.toUpperCase()}</strong></div>
                      <div>Concepto: <strong>{job.keywords?.join(', ') || '-'}</strong></div>
                      <div>Región: <strong>{job.locations?.join(', ') || 'Sin región'}</strong></div>
                      <div>Tiempo configurado: <strong>{job.maxSeconds || 0} segundos</strong></div>
                      <div>Cuentas usadas: <strong>{job.accountAliases?.join(', ') || job.workers}</strong></div>
                      <div>Etapa final: <strong>{job.currentStep || '-'}</strong></div>
                      <div>Resultados: <strong>{job.totalWhatsappLinks || 0}</strong></div>

                      {job.error && (
                        <div style={{ color: '#cc3333', marginTop: '8px' }}>
                          Error: {job.error}
                        </div>
                      )}

                      <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
                        <button
                          onClick={() => descargarCsv(job)}
                          disabled={job.status !== 'completed'}
                          className={job.status === 'completed' ? 'csv-ready' : 'csv-disabled'}
                        >
                          Descargar CSV
                        </button>
                      </div>

                      {job.results?.length > 0 && (
                        <div style={{ marginTop: '14px' }}>
                          <h4>Resultados</h4>

                          <div style={{ display: 'grid', gap: '8px' }}>
                            {job.results.map((item, index) => (
                              <div
                                key={`${item.whatsappLink}-${index}`}
                                style={{
                                  border: '1px solid #ddd',
                                  borderRadius: '6px',
                                  padding: '8px',
                                  background: '#fafafa',
                                }}
                              >
                                <div>
                                  <strong>{item.whatsappLink}</strong>
                                </div>
                                <div style={{ fontSize: '13px', color: '#555' }}>
                                  Grupo: {item.groupName}
                                </div>
                                <div style={{ fontSize: '13px', color: '#555' }}>
                                  Cuenta: {item.accountAlias}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </section>
  )
}

function StatusBadge({ status }: { status: string }) {
  const color =
    status === 'completed'
      ? '#2e8b57'
      : status === 'failed'
        ? '#cc3333'
        : status === 'running'
          ? '#0066cc'
          : '#777'

  return (
    <div style={{ fontWeight: 'bold', color }}>
      {status.toUpperCase()}
    </div>
  )
}

function formatDate(value: string) {
  if (!value) return '-'

  try {
    return new Date(value).toLocaleString()
  } catch {
    return value
  }
}

export default JobsView