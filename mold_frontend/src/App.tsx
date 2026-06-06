import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { VendorPage } from './pages/VendorPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/vendor" element={<VendorPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;