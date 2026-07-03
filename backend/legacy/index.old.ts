import { Elysia, t } from 'elysia'
import { cors } from '@elysiajs/cors'
import { swagger } from '@elysiajs/swagger'

console.log('FB Scraper API iniciando...')

const app = new Elysia()
  .use(cors())
  .use(
    swagger({
      path: '/docs',
      documentation: {
        info: {
          title: 'FB Scraper API',
          version: '1.0.0',
          description: 'API para gestión de scraping de grupos de Facebook'
        }
      }
    })
  )

  .get('/', () => ({
    status: 'ok',
    message: 'API activa',
    docs: '/docs'
  }))

  .post('/auth/register', async ({ body }) => {
    const { email, username } = body as any

    console.log(`Registro: ${username}`)

    return {
      success: true,
      message: 'Usuario registrado',
      user: {
        email,
        username
      }
    }
  }, {
    body: t.Object({
      email: t.String({ format: 'email' }),
      username: t.String({ minLength: 3 }),
      password: t.String({ minLength: 6 })
    })
  })

  .post('/auth/login', async ({ body }) => {
    const { email } = body as any

    console.log(`Login: ${email}`)

    return {
      success: true,
      token: `token-${Date.now()}`,
      user: {
        email
      }
    }
  }, {
    body: t.Object({
      email: t.String({ format: 'email' }),
      password: t.String()
    })
  })

  .post('/scraping/start', async ({ body }) => {
    const { keywords, locations } = body as any

    const taskId = `task-${Date.now()}`

    console.log('Nueva tarea creada')
    console.log('Keywords:', keywords)
    console.log('Locations:', locations)

    return {
      taskId,
      status: 'queued',
      keywords,
      locations
    }
  }, {
    body: t.Object({
      keywords: t.Array(t.String()),
      locations: t.Array(t.String()),
      maxResults: t.Optional(t.Number())
    })
  })

  .get('/scraping/tasks', async () => ({
    tasks: [
      {
        id: 'task-001',
        status: 'completed',
        keywords: ['ventas', 'empleo'],
        locations: ['Cancun'],
        total_whatsapp_links: 15,
        created_at: new Date().toISOString()
      }
    ]
  }))

  .get('/scraping/task/:id', async ({ params }) => ({
    id: params.id,
    status: 'completed',
    keywords: ['ventas', 'empleo'],
    locations: ['Cancun'],
    results: [
      {
        group_name: 'Grupo de Ventas Cancun',
        group_url: 'https://facebook.com/groups/123',
        whatsapp_links: [
          'https://chat.whatsapp.com/abc123'
        ]
      }
    ],
    total_whatsapp_links: 15,
    created_at: new Date().toISOString()
  }))

  .listen(3000)

console.log('FB Scraper API ejecutándose')
console.log('Documentación: http://localhost:3000/docs')