import { Elysia, t } from 'elysia'
import type { FbAccount } from '../types'

const ACCOUNTS_URL = process.env.SCRAPER_URL ?? 'http://scraper:8000'

const localAccounts: FbAccount[] = []

export const accountsRoutes = new Elysia({ prefix: '/accounts' })

  .get('/', async () => {
    try {
      const response = await fetch(`${ACCOUNTS_URL}/accounts`)
      const data = await response.json()

      const accounts: FbAccount[] = (data.accounts || []).map((account: any) => ({
        id: account.alias,
        alias: account.alias,
        email: account.email,
        status: 'active',
        createdAt: new Date().toISOString(),
      }))

      return { accounts }
    } catch (error) {
      return { accounts: localAccounts }
    }
  })

  .post('/', ({ body }) => {
    const account: FbAccount = {
      id: `acc-${Date.now()}`,
      alias: body.alias,
      email: body.email,
      status: 'active',
      createdAt: new Date().toISOString(),
    }

    localAccounts.push(account)

    return {
      success: true,
      message: 'Cuenta registrada localmente',
      account,
    }
  }, {
    body: t.Object({
      alias: t.String({ minLength: 2 }),
      email: t.String({ format: 'email' }),
      password: t.String({ minLength: 1 }),
    }),
  })

  .delete('/:id', ({ params }) => {
    const index = localAccounts.findIndex((account) => account.id === params.id)

    if (index === -1) {
      return {
        success: false,
        message: 'Cuenta no encontrada',
      }
    }

    localAccounts.splice(index, 1)

    return {
      success: true,
      message: 'Cuenta eliminada',
    }
  })