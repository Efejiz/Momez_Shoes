import React, { useEffect, useState, createContext } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './i18n';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import MyOrders from './pages/MyOrders';
import AdminPanel from './pages/AdminPanel';
import Login from './pages/Login';
import Register from './pages/Register';
// AdminLogin kaldırıldı: birleşik giriş akışı kullanılıyor
import Profile from './pages/Profile';
import Wishlist from './pages/Wishlist';
import Contact from './pages/Contact';
import NotFound from './pages/NotFound';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AuthContext = createContext(null);

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    // Support both hash (#session_id=...) and query (?session_id=...)
    const hash = window.location.hash;
    const search = window.location.search;

    let sessionId = null;
    if (hash && hash.includes('session_id=')) {
      sessionId = hash.split('session_id=')[1].split('&')[0];
    } else if (search && search.includes('session_id=')) {
      const params = new URLSearchParams(search);
      sessionId = params.get('session_id');
    }

    if (sessionId) {
      console.log('📱 OAuth callback detected, session_id:', sessionId);
      try {
        const response = await axios.get(`${API}/auth/session-data`, {
          headers: { 'X-Session-ID': sessionId }
        });

        const token = response.data.session_token;
        // Save to localStorage
        localStorage.setItem('session_token', token);

        // Fetch full user to know role
        const me = await axios.get(`${API}/auth/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        localStorage.setItem('user', JSON.stringify(me.data));
        setUser(me.data);

        // Clear hash/query
        window.history.replaceState(null, '', '/');
        // Redirect by role
        if (me.data.role === 'admin') {
          window.location.href = '/admin';
        } else {
          window.location.href = '/';
        }
      } catch (error) {
        console.error('❌ OAuth error:', error);
      }
    }
  };

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('session_token');
      const savedUser = localStorage.getItem('user');

      if (token && savedUser) {
        // Try to verify token with backend
        const response = await axios.get(`${API}/auth/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setUser(response.data);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.log('Auth check failed, clearing session');
      localStorage.removeItem('session_token');
      localStorage.removeItem('user');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('session_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  // Netlify/production ortamında backend URL'i yoksa beyaz ekran yerine açıklayıcı mesaj göster
  if (!BACKEND_URL || BACKEND_URL.trim() === '') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="max-w-xl text-center">
          <h1 className="text-2xl font-bold mb-3">Konfigürasyon Hatası</h1>
          <p className="text-gray-700 mb-4">
            REACT_APP_BACKEND_URL ayarlı değil. Netlify’da Site Settings → Build & deploy → Environment altında
            <code className="bg-gray-100 px-2 py-1 mx-1">REACT_APP_BACKEND_URL</code> değişkenini, Railway backend adresinizle
            (ör. <code className="bg-gray-100 px-2 py-1">https://&lt;proje&gt;.up.railway.app</code>) ekleyip yeniden deploy edin.
          </p>
          <p className="text-sm text-gray-500">CORS için backend tarafında <code className="bg-gray-100 px-2 py-1">CORS_ORIGINS</code> içine Netlify domaininizi eklemeyi unutmayın.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, setUser, checkAuth, logout }}>
      <div className="App min-h-screen bg-background">
        <BrowserRouter>
          <Navbar />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            {/* Ayrı admin giriş rotası kaldırıldı */}
            <Route path="/" element={<Home />} />
            <Route path="/products/:category" element={<Products />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={user ? <Checkout /> : <Navigate to="/login" />} />
            <Route path="/my-orders" element={user ? <MyOrders /> : <Navigate to="/login" />} />
            <Route path="/profile" element={user ? <Profile /> : <Navigate to="/login" />} />
            <Route path="/wishlist" element={user ? <Wishlist /> : <Navigate to="/login" />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/admin" element={user && user.role === 'admin' ? <AdminPanel /> : <Navigate to="/login" />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          <Footer />
          <Toaster />
        </BrowserRouter>
      </div>
    </AuthContext.Provider>
  );
}

export default App;
