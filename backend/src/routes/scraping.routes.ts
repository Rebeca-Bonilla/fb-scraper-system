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
      status: 'running',
      createdAt: new Date().toISOString(),
      totalWhatsappLinks: 0,
      results: []
    }
    
    jobs.set(jobId, job)
    console.log(`📋 Job creado: ${jobId}`)
    
    try {
      const results = await runRealScraper(job)
      console.log(`✅ Scraper completado con ${results.length} resultados`)
      
      job.status = 'completed'
      job.results = results
      job.totalWhatsappLinks = results.length
      
      return {
        success: true,
        message: 'Ejecución completada',
        jobId: job.id,
        job: job
      }
    } catch (error) {
      console.error('❌ Error en scraper:', error)
      job.status = 'failed'
      job.error = error.message
      
      return {
        success: false,
        message: 'Error en la ejecución',
        jobId: job.id,
        error: error.message
      }
    }
  }, {
    body: t.Object({
      keywords: t.Array(t.String()),
      locations: t.Array(t.String()),
      maxResults: t.Number({ default: 20 }),
      maxSeconds: t.Number({ default: 60 }),
      workers: t.Number({ default: 1 })
    })
  })
  
  .get('/task/:id', async ({ params }) => {
    const job = jobs.get(params.id)
    if (!job) {
      return { success: false, message: 'Job no encontrado' }
    }
    return { success: true, job }
  })
  
  .get('/tasks', async () => {
    return { success: true, jobs: Array.from(jobs.values()) }
  })