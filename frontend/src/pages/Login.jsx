import React, { useContext, useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../App';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import axios from 'axios';
import { toast } from 'sonner';
import { ShoppingBag, Check } from 'lucide-react';

const AUTH_URL = 'https://auth.emergentagent.com';
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Login() {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  const handleGoogleLogin = () => {
    const redirectUrl = encodeURIComponent(window.location.origin + '/');
    window.location.href = `${AUTH_URL}/?redirect=${redirectUrl}`;
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password,
        remember_me: rememberMe,
      });

      const token = response.data.session_token;
      localStorage.setItem('session_token', token);

      const me = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      localStorage.setItem('user', JSON.stringify(me.data));
      setUser(me.data);
      toast.success('Giriş başarılı');

      if (me.data.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Giriş başarısız');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 via-white to-rose-50 relative overflow-hidden" data-testid="login-page">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-96 h-96 bg-red-200/30 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '4s' }}></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-rose-200/30 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '6s', animationDelay: '2s' }}></div>
      </div>

      <div className="max-w-6xl w-full mx-4 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <div className="hidden lg:block space-y-8">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 bg-gradient-to-br from-red-600 to-red-500 rounded-full flex items-center justify-center shadow-2xl">
                <span className="text-white font-bold text-3xl">M</span>
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900">Momez <span className="gradient-text">Shoes</span></h1>
                <p className="text-gray-600">Premium Footwear Collection</p>
              </div>
            </div>

            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-gray-900">Step Into a World of Premium Style</h2>
              <p className="text-lg text-gray-600 leading-relaxed">Join thousands of satisfied customers who trust Momez Shoes for authentic, high-quality footwear.</p>

              <div className="space-y-4">
                {[
                  'Authentic Premium Products',
                  'Secure & Fast Checkout',
                  'Free Shipping on Orders $100+',
                  '24/7 Customer Support'
                ].map((feature, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-red-600" />
                    </div>
                    <span className="text-gray-700 font-medium">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="w-full">
            <div className="glass rounded-3xl shadow-2xl p-8 md:p-12 border border-white/20">
              <div className="lg:hidden text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-red-600 to-red-500 rounded-full mb-4 shadow-lg">
                  <ShoppingBag className="w-8 h-8 text-white" />
                </div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">Momez Shoes</h1>
                <p className="text-gray-600">Premium Footwear</p>
              </div>

              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">Hoş Geldiniz</h2>
                  <p className="text-gray-600">Google hesabınızla giriş yapın</p>
                </div>

                <Button 
                  onClick={handleGoogleLogin} 
                  className="w-full h-14 text-lg bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white rounded-full shadow-xl hover:shadow-2xl transition-all duration-300" 
                  data-testid="google-login-button"
                >
                  <svg className="w-6 h-6 mr-3" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Google ile Devam Et
                </Button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-white text-gray-500">veya</span>
                  </div>
                </div>

                <form onSubmit={handleEmailLogin} className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="email">E-posta</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="ornek@mail.com"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Şifre</Label>
                    <Input
                      id="password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                    />
                  </div>

                  <div className="flex items-center gap-3">
                    <Checkbox id="remember" checked={rememberMe} onCheckedChange={(v) => setRememberMe(!!v)} />
                    <Label htmlFor="remember" className="text-sm text-gray-700">Beni Hatırla</Label>
                  </div>

                  <Button
                    type="submit"
                    disabled={submitting}
                    className="w-full h-12 bg-foreground text-background hover:bg-foreground/90 rounded-full"
                  >
                    {submitting ? 'Giriş yapılıyor...' : 'Giriş Yap'}
                  </Button>
                </form>

                <p className="text-center text-sm text-gray-600 mt-4">
                  Hesabınız yok mu?{' '}
                  <Link to="/register" className="text-red-600 hover:underline font-semibold">
                    Kayıt Ol
                  </Link>
                </p>

                <div className="text-center text-sm text-gray-500">
                  <p>Devam ederek Hizmet Şartları ve Gizlilik Politikamızı kabul etmiş olursunuz</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
