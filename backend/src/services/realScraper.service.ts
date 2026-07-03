import type { ScrapingJob, ScrapingResult } from '../types'

const SCRAPER_URL = process.env.SCRAPER_URL ?? 'http://scraper:8000'

export async function runRealScraper(job: ScrapingJob): Promise<ScrapingResult[]> {
  console.log(`🚀 Enviando Job ${job.id} al scraper en ${SCRAPER_URL}/scrape`)
  console.log(`   Keywords: ${job.keywords.join(', ')}`)
  console.log(`   Locations: ${job.locations.join(', ')}`)

  const payload = {
    jobId: job.id,
    keywords: job.keywords,
    locations: job.locations,
    maxResults: job.maxResults,
    maxSeconds: job.maxSeconds,
    workers: job.workers
  }

  console.log('📦 Payload:', JSON.stringify(payload, null, 2))

  const response = await fetch(`${SCRAPER_URL}/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    const errorText = await response.text()
    console.error(`❌ Scraper error ${response.status}:`, errorText)
    throw new Error(`Scraper engine error (${response.status}): ${errorText}`)
  }

  const data = await response.json()
  console.log('📦 Respuesta del scraper:', JSON.stringify(data, null, 2))

  const results = data.results ?? data.data ?? []

  console.log(`✅ Scraper devolvió ${results.length} resultados`)

  return results
}