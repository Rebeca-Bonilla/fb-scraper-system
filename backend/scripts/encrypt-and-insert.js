import mysql from 'mysql2/promise'
import { encrypt } from '../src/utils/crypto.ts'
import { randomUUID } from 'crypto'

// ⚠️ Después de correr este script una vez, borra los passwords en texto plano de aquí abajo
const accounts = []
const conn = await mysql.createConnection({
  host: 'localhost',
  port: 3308,
  user: 'root',
  password: 'rootpass',
  database: 'fb_scraper',
})

for (const acc of accounts) {
  const encrypted = encrypt(acc.password)
  await conn.execute(
    'INSERT INTO fb_accounts (id, alias, email, password_encrypted) VALUES (?, ?, ?, ?)',
    [randomUUID(), acc.alias, acc.email, encrypted]
  )
  console.log(`✅ Insertada cuenta: ${acc.alias}`)
}

await conn.end()
console.log('Listo. Ahora borra los passwords en texto plano de este archivo.')