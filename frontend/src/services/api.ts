const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

export async function login(email: string, password: string) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  return response.json()
}

export async function getAccounts() {
  const response = await fetch(`${API_URL}/accounts/`)
  return response.json()
}

export async function createAccount(data: {
  alias: string
  email: string
  password: string
}) {
  const response = await fetch(`${API_URL}/accounts/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  return response.json()
}

export async function deleteAccount(id: string) {
  const response = await fetch(`${API_URL}/accounts/${id}`, {
    method: 'DELETE',
  })

  return response.json()
}

export async function startScraping(data: {
  keywords: string[]
  locations: string[]
  maxResults: number
  maxSeconds: number
  workers: number
  accountAliases: string[]
}) {
  const response = await fetch(`${API_URL}/scraping/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  return response.json()
}

export async function getTasks() {
  const response = await fetch(`${API_URL}/scraping/tasks`)
  return response.json()
}

export async function getTask(id: string) {
  const response = await fetch(`${API_URL}/scraping/task/${id}`)
  return response.json()
}

export function getDownloadUrl(id: string) {
  return `${API_URL}/scraping/download/${id}`
}