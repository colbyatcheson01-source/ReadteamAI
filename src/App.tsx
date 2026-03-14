import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import WarDrive from './pages/WarDrive';
import VulnScanner from './pages/VulnScanner';
import ExploitChooser from './pages/ExploitChooser';
import PayloadDelivery from './pages/PayloadDelivery';
import Reports from './pages/Reports';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="wardrive" element={<WarDrive />} />
          <Route path="scanner" element={<VulnScanner />} />
          <Route path="exploits" element={<ExploitChooser />} />
          <Route path="payload" element={<PayloadDelivery />} />
          <Route path="reports" element={<Reports />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
