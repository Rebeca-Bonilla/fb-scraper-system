import { Route, Routes } from 'react-router-dom'

import Sidebar from './components/layout/Sidebar'
import LoginView from './views/LoginView'
import DashboardView from './views/DashboardView'
import AccountsView from './views/AccountsView'
import NewJobView from './views/NewJobView'
import JobsView from './views/JobsView'
import JobDetailView from './views/JobDetailView'

function App() {
  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<DashboardView />} />
          <Route path="/login" element={<LoginView />} />
          <Route path="/dashboard" element={<DashboardView />} />
          <Route path="/accounts" element={<AccountsView />} />
          <Route path="/new-job" element={<NewJobView />} />
          <Route path="/jobs" element={<JobsView />} />
          <Route path="/jobs/:id" element={<JobDetailView />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
