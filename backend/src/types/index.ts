export interface ScrapingJob {
  id: string
  keywords: string[]
  locations: string[]
  maxResults: number
  maxSeconds: number
  workers: number
  accountAliases?: string[]
  status: 'pending' | 'running' | 'completed' | 'failed'
  currentStep?: string
  createdAt: string
  startedAt?: string
  completedAt?: string
  totalWhatsappLinks: number
  results: ScrapingResult[]
  error?: string | null
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