import { useEffect, useState } from 'react'
import { getAccounts } from '../services/api'

type Account = {
  id: string
  alias: string
  email: string
  status: string
  createdAt: string
}

function AccountsView() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    cargarCuentas()
  }, [])

  async function cargarCuentas() {
    setLoading(true)
    const response = await getAccounts()
    setAccounts(response.accounts || [])
    setLoading(false)
  }

  return (
    <section className="wireframe-page">
      <div className="search-form-wireframe">
        <h2 style={{ marginBottom: '20px' }}>Cuentas disponibles</h2>

        <button onClick={cargarCuentas} style={{ marginBottom: '16px' }}>
          Actualizar
        </button>

        {loading && <div className="notice">Cargando cuentas...</div>}

        {!loading && accounts.length === 0 && (
          <div className="notice">No hay cuentas registradas.</div>
        )}

        <div style={{ display: 'grid', gap: '12px' }}>
          {accounts.map((account) => (
            <div
              key={account.alias}
              style={{
                background: '#f4f4f6',
                borderLeft: '4px solid #0066cc',
                borderRadius: '6px',
                padding: '12px',
              }}
            >
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                {account.alias}
              </div>

              <div style={{ color: '#555', marginTop: '4px' }}>
                {account.email}
              </div>

              <div style={{ marginTop: '8px' }}>
                Estado:{' '}
                <strong style={{ color: '#2e8b57' }}>
                  {account.status || 'active'}
                </strong>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default AccountsView