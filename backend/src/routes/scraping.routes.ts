import { Elysia, t } from 'elysia'
import { runRealScraper } from '../services/realScraper.service'

// Servicio simple en memoria para pruebas
const jobs = new Map()

export const scrapingRoutes = new Elysia({ prefix: '/scraping' })

  .post('/start', async ({ body }) => {
    console.log('📥 Recibida solicitud de scraping:', body)

    const jobId = `job-${Date.now()}`

    const job = {
      id: jobId,
      keywords: body.keywords,
      locations: body.locations,
      maxResults: body.maxResults || 20,
      maxSeconds: body.maxSeconds || 60,
      workers: body.workers || 1,
      accountAliases: body.accountAliases || [],
      status: 'running',
      currentStep: 'Encolando tarea...',
      createdAt: new Date().toISOString(),
      totalWhatsappLinks: 0,
      results: [],
      error: null as string | null,
    }

    jobs.set(jobId, job)

    console.log(`📋 Job creado: ${jobId}`)

    // Ejecutar en segundo plano
    setTimeout(async () => {
      try {
        job.currentStep = 'Ejecutando scraper...'

        const results = await runRealScraper(job)

        job.status = 'completed'
        job.results = results
        job.totalWhatsappLinks = results.length
        job.currentStep = 'Proceso completado exitosamente'

        console.log(
          `✅ Job ${jobId} completado con ${results.length} resultados`
        )
      } catch (error: any) {
        console.error('❌ Error en scraper:', error)

        job.status = 'failed'
        job.error = error?.message ?? 'Error desconocido'
        job.currentStep = 'Ejecución interrumpida por error'
      }
    }, 0)

    // Respuesta inmediata al frontend
    return {
      success: true,
      message: 'Job iniciado',
      jobId: job.id,
      job,
    }
  }, {
    
    body: t.Object({
      keywords: t.Array(t.String()),
      locations: t.Array(t.String()),
      maxResults: t.Number({ default: 20 }),
      maxSeconds: t.Number({ default: 60 }),
      workers: t.Number({ default: 1 }),
      accountAliases: t.Optional(t.Array(t.String())),
    }),
  })

  .get('/task/:id', async ({ params }) => {
    const job = jobs.get(params.id)

    if (!job) {
      return {
        success: false,
        message: 'Job no encontrado',
      }
    }

    return {
      success: true,
      job,
    }
  })


  .get('/download/:id', async ({ params, set }) => {
    const job = jobs.get(params.id)

    if (!job) {
      set.status = 404
      return 'Job no encontrado'
    }

    const headers = [
      'accountAlias',
      'keyword',
      'location',
      'groupName',
      'groupUrl',
      'whatsappLink',
      'sourceSearch',
      'scrapedAt',
    ]

    const escapeCsv = (value: any) => {
      const text = String(value ?? '')
      return `"${text.replaceAll('"', '""')}"`
    }

    const rows = [
      headers.join(','),
      ...job.results.map((item: any) =>
        headers.map((header) => escapeCsv(item[header])).join(',')
      ),
    ]

    set.headers['Content-Type'] = 'text/csv; charset=utf-8'
    set.headers['Content-Disposition'] = `attachment; filename="${job.id}.csv"`

    return '\uFEFF' + rows.join('\n')
  })
  .get('/tasks', async () => {
    return {
      success: true,
      jobs: Array.from(jobs.values()),
    }
  })