import { Elysia } from 'elysia'
import { cors } from '@elysiajs/cors'
import { swagger } from '@elysiajs/swagger'

import { authRoutes } from './routes/auth.routes'
import { accountsRoutes } from './routes/accounts.routes'
import { scrapingRoutes } from './routes/scraping.routes'

const app = new Elysia()
  .use(cors())
  .use(swagger())
  .use(authRoutes)
  .use(accountsRoutes)
  .use(scrapingRoutes)
  .get('/', () => ({
    status: 'ok',
    message: 'FB Scraper API activo',
  }))
  .listen(3000)

console.log(`FB Scraper API ejecutándose en http://localhost:${app.server?.port}`)
console.log(`Documentación disponible en http://localhost:${app.server?.port}/docs`)

