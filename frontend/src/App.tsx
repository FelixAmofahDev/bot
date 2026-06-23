import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Participants } from './pages/Participants';
import { Recordings } from './pages/Recordings';
import { Sentences } from './pages/Sentences';
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/participants" element={<Participants />} />
          <Route path="/recordings" element={<Recordings />} />
          <Route path="/sentences" element={<Sentences />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
