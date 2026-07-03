import { Elysia } from 'elysia'

export const dashboardRoutes = new Elysia({ prefix: '/dashboard' })
  .get('/', () => ({
    totalJobs: 0,
    completedJobs: 0,
    runningJobs: 0,
    failedJobs: 0,
    totalWhatsappLinks: 0
  }))
