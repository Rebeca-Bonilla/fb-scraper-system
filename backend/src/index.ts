import { Elysia } from 'elysia'
import { cors } from '@elysiajs/cors'
import { swagger } from '@elysiajs/swagger'

import { authRoutes } from './routes/auth.routes'
import { accountsRoutes } from './routes/accounts.routes'
import { scrapingRoutes } from './routes/scraping.routes'
import { dashboardRoutes } from './routes/dashboard.routes'

const app = new Elysia()
  .use(cors())
  .use(swagger({
    path: '/docs',
    documentation: {
      info: {
        title: 'FB Scraper API',
        version: '1.0.0',
        description: 'API para gestión de ejecuciones de scraping'
      }
    }
  }))
  .get('/', () => ({
    status: 'ok',
    message: 'FB Scraper API activa',
    docs: '/docs'
  }))
  .use(authRoutes)
  .use(accountsRoutes)
  .use(scrapingRoutes)
  .use(dashboardRoutes)
  .listen(3000)

console.log('FB Scraper API ejecutándose en http://localhost:3000')
console.log('Documentación disponible en http://localhost:3000/docs')
