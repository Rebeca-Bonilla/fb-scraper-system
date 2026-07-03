import { NavLink, useNavigate } from 'react-router-dom'

function Sidebar() {
  const navigate = useNavigate()

  return (
    <aside className="sidebar">
      <div className="logo" onClick={() => navigate('/dashboard')}>
        RECOLECTOR
      </div>

      <div className="user-info">
        <span className="username">Usuario demo</span>
        <span className="user-role">Operador</span>
      </div>

      <div className="timer">
        <span>Tiempo: 00:00</span>
        <span>Límite: 30:00</span>
      </div>

      <nav className="nav-menu">
        <NavLink to="/dashboard" className="nav-btn">Home</NavLink>
        <NavLink to="/new-job" className="nav-btn">Nueva búsqueda</NavLink>
        <NavLink to="/jobs" className="nav-btn">Historial</NavLink>
        <NavLink to="/accounts" className="nav-btn">Cuentas</NavLink>
      </nav>

      <div className="sidebar-buttons">
        <button className="sidebar-btn" onClick={() => navigate('/dashboard')}>Home</button>
        <button className="sidebar-btn" onClick={() => navigate(-1)}>Atrás</button>
        <button className="sidebar-btn logout" onClick={() => navigate('/login')}>
          Cerrar sesión
        </button>
      </div>
    </aside>
  )
}

export default Sidebar