import { useEffect, useState } from 'react'
import { getAccounts, getDownloadUrl, getTask, startScraping } from '../services/api'

const ciudadesPorEstado: Record<string, string[]> = {
  'Quintana Roo': ['Cancun', 'Playa del Carmen', 'Tulum', 'Chetumal'],
  'Yucatán': ['Mérida', 'Valladolid', 'Progreso'],
  'Campeche': ['Campeche', 'Ciudad del Carmen'],
  'CDMX': ['CDMX'],
}

type Account = {
  id?: string
  alias: string
  email: string
  status?: string
}

function NewJobView() {
  const [concepto, setConcepto] = useState('')
  const [estado, setEstado] = useState('Quintana Roo')
  const [ciudad, setCiudad] = useState('Cancun')
  const [usarEstado, setUsarEstado] = useState(true)
  const [usarCiudad, setUsarCiudad] = useState(true)
  const [tiempo, setTiempo] = useState(180)

  const [accounts, setAccounts] = useState<Account[]>([])
  const [selectedAliases, setSelectedAliases] = useState<string[]>([])

  const [jobId, setJobId] = useState('')
  const [jobStatus, setJobStatus] = useState('')
  const [currentStep, setCurrentStep] = useState('')
  const [csvReady, setCsvReady] = useState(false)
  const [message, setMessage] = useState('')
  const [totalLinks, setTotalLinks] = useState(0)

  const ciudades = ciudadesPorEstado[estado] || []

  useEffect(() => {
    cargarCuentas()
  }, [])

  async function cargarCuentas() {
    const response = await getAccounts()
    const loadedAccounts = response.accounts || []

    setAccounts(loadedAccounts)

    if (loadedAccounts.length > 0) {
      setSelectedAliases(loadedAccounts.map((account: Account) => account.alias))
    }
  }

  function cambiarEstado(nuevoEstado: string) {
    setEstado(nuevoEstado)
    setCiudad(ciudadesPorEstado[nuevoEstado][0])
  }

  function construirLocation() {
    if (usarEstado && usarCiudad) return `${ciudad}, ${estado}`
    if (usarCiudad) return ciudad
    if (usarEstado) return estado
    return ''
  }

  function toggleAccount(alias: string) {
    setSelectedAliases((current) => {
      if (current.includes(alias)) {
        return current.filter((item) => item !== alias)
      }

      return [...current, alias]
    })
  }

  function seleccionarTodas() {
    setSelectedAliases(accounts.map((account) => account.alias))
  }

  function deseleccionarTodas() {
    setSelectedAliases([])
  }

  async function esperarResultado(id: string) {
    setMessage('Búsqueda en proceso...')

    const interval = setInterval(async () => {
      const response = await getTask(id)
      const job = response.job

      if (!job) return

      setJobStatus(job.status)
      setTotalLinks(job.totalWhatsappLinks || 0)

      if (job.currentStep) {
        setCurrentStep(job.currentStep)
      }

      if (job.status === 'completed') {
        clearInterval(interval)
        setCsvReady(true)
        setCurrentStep('Proceso completado exitosamente')
        setMessage(`Búsqueda completada. ${job.totalWhatsappLinks} enlaces encontrados.`)
      }

      if (job.status === 'failed') {
        clearInterval(interval)
        setCsvReady(false)
        setCurrentStep('Ejecución interrumpida por error')
        setMessage(`La búsqueda falló: ${job.error || 'revisa los logs del backend.'}`)
      }
    }, 1000)
  }

  async function iniciarBusqueda() {
    const keywords = concepto
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)

    if (keywords.length === 0) {
      setMessage('Ingresa al menos un concepto de búsqueda.')
      return
    }

    if (selectedAliases.length === 0) {
      setMessage('Selecciona al menos una cuenta para ejecutar la búsqueda.')
      return
    }

    const location = construirLocation()

    setCsvReady(false)
    setTotalLinks(0)
    setJobStatus('queued')
    setCurrentStep('Encolando la tarea en el sistema...')
    setMessage('Creando búsqueda...')

    const response = await startScraping({
      keywords,
      locations: location ? [location] : [],
      maxResults: 10,
      maxSeconds: tiempo,
      workers: selectedAliases.length,
      accountAliases: selectedAliases,
    })

    setJobId(response.jobId)
    setJobStatus(response.job?.status || 'queued')
    esperarResultado(response.jobId)
  }

  function descargarCsv() {
    if (!jobId || !csvReady) {
      setMessage('El CSV todavía no está listo. Espera a que termine la búsqueda.')
      return
    }

    window.open(getDownloadUrl(jobId), '_blank')
  }

  const isRunning = jobStatus === 'running' || jobStatus === 'queued'
  const progressPercent =
    jobStatus === 'completed'
      ? 100
      : jobStatus === 'failed'
        ? 100
        : isRunning
          ? 45
          : 0

  return (
    <section className="wireframe-page">
      <div className="search-form-wireframe">
        <div className="form-row">
          <label>Concepto</label>
          <input
            value={concepto}
            onChange={(e) => setConcepto(e.target.value)}
            placeholder="ventas, empleo"
          />
        </div>

        <div className="form-row with-check">
          <label>Estado</label>
          <div className="input-with-check">
            <select value={estado} onChange={(e) => cambiarEstado(e.target.value)}>
              {Object.keys(ciudadesPorEstado).map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>

            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={usarEstado}
                onChange={(e) => setUsarEstado(e.target.checked)}
              />
              Considerar
            </label>
          </div>
        </div>

        <div className="form-row with-check">
          <label>Ciudad</label>
          <div className="input-with-check">
            <select value={ciudad} onChange={(e) => setCiudad(e.target.value)}>
              {ciudades.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>

            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={usarCiudad}
                onChange={(e) => setUsarCiudad(e.target.checked)}
              />
              Considerar
            </label>
          </div>
        </div>

        <div className="form-row">
          <label>Cuentas disponibles</label>

          <div
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '12px',
              background: '#fafafa',
            }}
          >
            <div style={{ marginBottom: '8px', fontWeight: 'bold' }}>
              Seleccionadas: {selectedAliases.length} / {accounts.length}
            </div>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
              <button type="button" onClick={seleccionarTodas}>
                Seleccionar todas
              </button>

              <button type="button" onClick={deseleccionarTodas}>
                Deseleccionar todas
              </button>
            </div>

            {accounts.length === 0 && (
              <div style={{ color: '#777' }}>
                No hay cuentas disponibles.
              </div>
            )}

            {accounts.map((account) => (
              <label
                key={account.alias}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 0',
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedAliases.includes(account.alias)}
                  onChange={() => toggleAccount(account.alias)}
                />

                <span>
                  <strong>{account.alias}</strong>
                  <span style={{ color: '#666' }}> — {account.email}</span>
                </span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-row">
          <label>Tiempo de ejecución</label>
          <select value={tiempo} onChange={(e) => setTiempo(Number(e.target.value))}>
            <option value={180}>3 minutos</option>
            <option value={300}>5 minutos</option>
          </select>
        </div>

        <div className="search-preview">
          Región usada: <strong>{construirLocation() || 'Sin región'}</strong>
          <br />
          Cuentas usadas: <strong>{selectedAliases.join(', ') || 'Ninguna'}</strong>
        </div>

        {jobId && (
          <div
            className="job-status-container"
            style={{
              background: '#f4f4f6',
              padding: '12px',
              borderRadius: '6px',
              margin: '15px 0',
              borderLeft: '4px solid #0066cc',
            }}
          >
            <div className="job-status">
              ID Tarea:{' '}
              <strong style={{ fontFamily: 'monospace' }}>{jobId}</strong>
              <br />
              Estado Global:{' '}
              <span className={`badge-${jobStatus}`} style={{ fontWeight: 'bold' }}>
                {jobStatus.toUpperCase()}
              </span>
            </div>

            <div style={{ marginTop: '12px' }}>
              <div
                style={{
                  height: '10px',
                  background: '#ddd',
                  borderRadius: '999px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    height: '100%',
                    width: `${progressPercent}%`,
                    background:
                      jobStatus === 'failed'
                        ? '#cc3333'
                        : jobStatus === 'completed'
                          ? '#2e8b57'
                          : '#0066cc',
                    transition: 'width 0.3s ease',
                  }}
                />
              </div>

              <div style={{ marginTop: '6px', fontSize: '13px', color: '#555' }}>
                Progreso estimado: {progressPercent}%
              </div>
            </div>

            <div
              className="flow-tracker"
              style={{
                marginTop: '8px',
                paddingTop: '8px',
                borderTop: '1px solid #ddd',
              }}
            >
              Etapa del proceso:
              <br />
              <strong style={{ color: '#0066cc', display: 'block', marginTop: '3px' }}>
                {currentStep || 'Esperando asignación...'}
              </strong>
            </div>

            <div style={{ marginTop: '8px' }}>
              Enlaces encontrados:{' '}
              <strong>{totalLinks}</strong>
            </div>

            <div style={{ marginTop: '8px' }}>
              Cuentas activas:
              <div style={{ display: 'grid', gap: '6px', marginTop: '6px' }}>
                {selectedAliases.map((alias) => (
                  <div
                    key={alias}
                    style={{
                      background: '#fff',
                      border: '1px solid #ddd',
                      borderRadius: '6px',
                      padding: '8px',
                    }}
                  >
                    <strong>{alias}</strong>
                    <div style={{ fontSize: '13px', color: '#666' }}>
                      {isRunning
                        ? 'Trabajando en la búsqueda...'
                        : jobStatus === 'completed'
                          ? 'Finalizado'
                          : jobStatus === 'failed'
                            ? 'Interrumpido'
                            : 'En espera'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {message && <div className="notice">{message}</div>}

        <div className="action-row">
          <button onClick={iniciarBusqueda} disabled={isRunning}>
            Iniciar búsqueda
          </button>

          <button
            onClick={descargarCsv}
            className={csvReady ? 'csv-ready' : 'csv-disabled'}
          >
            Descargar CSV
          </button>
        </div>
      </div>
    </section>
  )
}

export default NewJobView