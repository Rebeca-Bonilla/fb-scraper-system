import { mkdirSync, writeFileSync } from 'fs'
import { join } from 'path'

export function createCsv(
  results: any[],
  jobId: string
): string {
  mkdirSync('data', { recursive: true })

  const filename = `resultados_${jobId}.csv`
  const path = join('data', filename)

  const headers = [
    'jobId',
    'accountAlias',
    'keyword',
    'location',
    'groupName',
    'groupUrl',
    'whatsappLink',
    'scrapedAt'
  ]

  const rows = results.map(result =>
    headers
      .map(header => JSON.stringify(result[header] ?? ''))
      .join(',')
  )

  writeFileSync(
    path,
    [headers.join(','), ...rows].join('\n'),
    'utf8'
  )

  return path
}
