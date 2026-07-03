import type { ScrapingJob, ScrapingResult } from '../types'

const delay = (ms: number) =>
  new Promise(resolve => setTimeout(resolve, ms))

export async function runMockScraper(
  job: ScrapingJob
): Promise<ScrapingResult[]> {
  const results: ScrapingResult[] = []

  const fakeGroups = [
    {
      name: 'Ventas Cancun',
      url: 'https://facebook.com/groups/ventas-cancun'
    },
    {
      name: 'Empleos Quintana Roo',
      url: 'https://facebook.com/groups/empleos-qroo'
    },
    {
      name: 'Compras Playa del Carmen',
      url: 'https://facebook.com/groups/compras-playa'
    }
  ]

  for (const keyword of job.keywords) {
    const locations = job.locations.length > 0 ? job.locations : ['']

    for (const location of locations) {
        for (const group of fakeGroups) {
        if (results.length >= job.maxResults) {
          return results
        }

        await delay(500)

        results.push({
          jobId: job.id,
          accountAlias: 'demo-account',
          keyword,
          location,
          groupName: group.name,
          groupUrl: group.url,
          whatsappLink: `https://chat.whatsapp.com/mock-${results.length + 1}`,
          scrapedAt: new Date().toISOString()
        })
      }
    }
  }

  return results
}
