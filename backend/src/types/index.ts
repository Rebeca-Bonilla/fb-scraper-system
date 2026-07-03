export interface ScrapingJob {
  id: string
  keywords: string[]
  locations: string[]
  maxResults: number
  maxSeconds: number
  workers: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  createdAt: string
  startedAt?: string
  completedAt?: string
  totalWhatsappLinks: number
  results: ScrapingResult[]
  error?: string
}

export interface ScrapingResult {
  accountAlias: string
  keyword: string
  location: string
  groupName: string
  groupUrl: string
  whatsappLink: string
  scrapedAt: string
}