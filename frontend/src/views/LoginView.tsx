import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../services/api'

function LoginView() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('admin@demo.com')
  const [password, setPassword] = useState('admin123')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isDevMode = import.meta.env.DEV

  async function handleLogin(event: FormEvent) {
    event.preventDefault()

    setError('')
    setLoading(true)

    try {
      if (!email.trim() || !password.trim()) {
        throw new Error('Por favor completa todos los campos')
      }

      const response = await login(email.trim(), password.trim())

      if (!response.token) {
        throw new Error('No se recibió token del servidor')
      }

      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))

      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  function autoFill(type: 'admin' | 'usuario') {
    if (type === 'admin') {
      setEmail('admin@demo.com')
      setPassword('admin123')
    } else {
      setEmail('usuario@demo.com')
      setPassword('usuario123')
    }
  }

  return (
    <section className="login-page">
      <div className="login-container">
        <div className="login-logo">RECOLECTOR</div>

        {isDevMode && (
          <div className="dev-tools">
            <button type="button" onClick={() => autoFill('admin')} className="btn-dev">
              Admin
            </button>
            <button type="button" onClick={() => autoFill('usuario')} className="btn-dev">
              Usuario
            </button>
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label>Usuario:</label>
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              required
              placeholder="admin@demo.com"
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <label>Contraseña:</label>

            <div className="password-wrapper">
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                type={showPassword ? 'text' : 'password'}
                required
                placeholder="admin123"
                disabled={loading}
              />

              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="toggle-password"
                disabled={loading}
              >
                {showPassword ? 'Ocultar' : 'Ver'}
              </button>
            </div>
          </div>

          <a href="#" className="forgot-password">
            ¿Olvidaste tu contraseña?
          </a>

          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Verificando...' : 'Iniciar sesión'}
          </button>

          {error && <div className="error-message">{error}</div>}
        </form>
      </div>
    </section>
  )
}

export default LoginView
