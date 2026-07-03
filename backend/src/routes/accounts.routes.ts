import { Elysia, t } from 'elysia'
import type { FbAccount } from '../types'

const accounts: FbAccount[] = []

export const accountsRoutes = new Elysia({ prefix: '/accounts' })
  .get('/', () => ({ accounts }))

  .post('/', ({ body }) => {
    const account: FbAccount = {
      id: `acc-${Date.now()}`,
      alias: body.alias,
      email: body.email,
      status: 'active',
      createdAt: new Date().toISOString()
    }

    accounts.push(account)

    return {
      success: true,
      message: 'Cuenta registrada',
      account
    }
  }, {
    body: t.Object({
      alias: t.String({ minLength: 2 }),
      email: t.String({ format: 'email' }),
      password: t.String({ minLength: 1 })
    })
  })

  .delete('/:id', ({ params }) => {
    const index = accounts.findIndex(account => account.id === params.id)

    if (index === -1) {
      return {
        success: false,
        message: 'Cuenta no encontrada'
      }
    }

    accounts.splice(index, 1)

    return {
      success: true,
      message: 'Cuenta eliminada'
    }
  })
