import { Elysia, t } from 'elysia'

export const authRoutes = new Elysia({ prefix: '/auth' })
  .post('/register', ({ body }) => {
    const { email, username } = body

    return {
      success: true,
      message: 'Usuario registrado',
      user: { email, username }
    }
  }, {
    body: t.Object({
      email: t.String({ format: 'email' }),
      username: t.String({ minLength: 3 }),
      password: t.String({ minLength: 6 })
    })
  })

  .post('/login', ({ body }) => {
    const { email } = body

    return {
      success: true,
      token: `token-${Date.now()}`,
      user: { email }
    }
  }, {
    body: t.Object({
      email: t.String({ format: 'email' }),
      password: t.String()
    })
  })
