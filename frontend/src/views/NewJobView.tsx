import { useState } from 'react'
import { getDownloadUrl, getTask, startScraping } from '../services/api'

const ciudadesPorEstado: Record<string, string[]> = {
  'Quintana Roo': ['Cancun', 'Playa del Carmen', 'Tulum', 'Chetumal'],
  'Yucatán': ['Mérida', 'Valladolid', 'Progreso'],
  'Campeche': ['Campeche', 'Ciudad del Carmen'],
  'CDMX': ['CDMX'],
}

function NewJobView() {
  const [concepto, setConcepto] = useState('')
  const [estado, setEstado] = useState('Quintana Roo')
  const [ciudad, setCiudad] = useState('Cancun')
  const [usarEstado, setUsarEstado] = useState(true)
  const [usarCiudad, setUsarCiudad] = useState(true)
  const [cuentas, setCuentas] = useState(1)
  const [tiempo, setTiempo] = useState(20)

  const [jobId, setJobId] = useState('')
  const [jobStatus, setJobStatus] = useState('')
  const [currentStep, setCurrentStep] = useState('') // 🌟 NUEVO: Estado para el flujo exacto
  const [csvReady, setCsvReady] = useState(false)
  const [message, setMessage] = useState('')

  const ciudades = ciudadesPorEstado[estado] || []

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

  async function esperarResultado(id: string) {
    setMessage('Búsqueda en proceso...')

    const interval = setInterval(async () => {
      const response = await getTask(id)
      const job = response.job

      if (!job) return

      setJobStatus(job.status)
      if (job.currentStep) {
        setCurrentStep(job.currentStep) // 🌟 Actualizamos el paso real del flujo
      }

      if (job.status === 'completed') {
        clearInterval(interval)
        setCsvReady(true)
        setCurrentStep('🏁 ¡Proceso completado exitosamente!')
        setMessage(`Búsqueda completada. ${job.totalWhatsappLinks} enlaces encontrados.`)
      }

      if (job.status === 'failed') {
        clearInterval(interval)
        setCsvReady(false)
        setCurrentStep('❌ Ejecución interrumpida por error')
        setMessage('La búsqueda falló. Revisa los logs del backend.')
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

    const location = construirLocation()

    setCsvReady(false)
    setJobStatus('queued')
    setCurrentStep('Encolando la tarea en el sistema...')
    setMessage('Creando búsqueda...')

    const response = await startScraping({
      keywords,
      locations: location ? [location] : [],
      maxResults: 10,
      maxSeconds: tiempo,
      workers: cuentas,
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
          <label>Cantidad de cuentas</label>
          <select value={cuentas} onChange={(e) => setCuentas(Number(e.target.value))}>
            <option value={1}>1 cuenta</option>
            <option value={2}>2 cuentas</option>
            <option value={3}>3 cuentas</option>
            <option value={4}>4 cuentas</option>
            <option value={5}>5 cuentas</option>
          </select>
        </div>

        <div className="form-row">
          <label>Tiempo de scroll</label>
          <select value={tiempo} onChange={(e) => setTiempo(Number(e.target.value))}>
            <option value={20}>20 segundos</option>
            <option value={60}>1 minuto</option>
            <option value={180}>3 minutos</option>
            <option value={300}>5 minutos</option>
            <option value={600}>10 minutos</option>
          </select>
        </div>

        <div className="search-preview">
          Región usada: <strong>{construirLocation() || 'Sin región'}</strong>
        </div>

        {/* 🌟 SECCIÓN EN VIVO DEL FLUJO DE TRABAJO DEL SISTEMA */}
        {jobId && (
          <div className="job-status-container" style={{
            background: '#f4f4f6', 
            padding: '12px', 
            borderRadius: '6px', 
            margin: '15px 0', 
            borderLeft: '4px solid #0066cc'
          }}>
            <div className="job-status">
              ID Tarea: <strong style={{ fontFamily: 'monospace' }}>{jobId}</strong><br />
              Estado Global: <span className={`badge-${jobStatus}`} style={{ fontWeight: 'bold' }}>{jobStatus.toUpperCase()}</span>
            </div>
            
            {/* Indicador de Flujo Interno */}
            <div className="flow-tracker" style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #ddd' }}>
              Etapa del proceso: <br />
              <strong style={{ color: '#0066cc', display: 'block', marginTop: '3px' }}>
                {currentStep || 'Esperando asignación...'}
              </strong>
            </div>
          </div>
        )}

        {message && <div className="notice">{message}</div>}

        <div className="action-row">
          <button onClick={iniciarBusqueda} disabled={jobStatus === 'running' || jobStatus === 'queued'}>
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