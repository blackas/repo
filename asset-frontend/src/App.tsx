import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Toaster } from 'react-hot-toast';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import AssetListPage from './pages/AssetListPage';
import AssetDetailPage from './pages/AssetDetailPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UserProfilePage from './pages/UserProfilePage';
import WatchlistPage from './pages/WatchlistPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { useAuthStore } from './store/useAuthStore';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const { loadUser } = useAuthStore();

  // 앱 시작 시 사용자 정보 로드
  useEffect(() => {
    loadUser();
  }, [loadUser]);

  return (
    <ThemeProvider theme={theme}>
      <Toaster position="top-right" />
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route
              path="assets/stocks/kr"
              element={<AssetListPage assetType="kr-stock" title="Korean Stocks" market="KRX" />}
            />
            <Route
              path="assets/stocks/us"
              element={<AssetListPage assetType="us-stock" title="US Stocks" market="NASDAQ" />}
            />
            <Route
              path="assets/crypto"
              element={<AssetListPage assetType="crypto" title="Cryptocurrencies" />}
            />
            <Route path="assets/:assetType/:assetId" element={<AssetDetailPage />} />
            <Route path="profile" element={<UserProfilePage />} />
            <Route path="watchlists" element={<WatchlistPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
