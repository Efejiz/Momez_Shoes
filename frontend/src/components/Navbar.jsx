import React, { useContext } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AuthContext } from '../App';
import { ShoppingCart, User, LogOut, Menu, X, Globe, Heart } from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { toast } from 'sonner';

export default function Navbar() {
  const { t, i18n } = useTranslation();
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  const changeLanguage = (lang) => {
    i18n.changeLanguage(lang);
  };

  const isActive = (path) => location.pathname === path;

  if (location.pathname === '/login') return null;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass shadow-lg py-3" data-testid="main-navbar">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 group" data-testid="nav-logo">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-red-500 rounded-full flex items-center justify-center transform group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <span className="text-white font-bold text-xl">M</span>
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full border-2 border-white"></div>
            </div>
            <div className="hidden md:block">
              <span className="text-2xl font-bold text-gray-900">Momez</span>
              <span className="text-2xl font-bold gradient-text ml-1">Shoes</span>
              <p className="text-xs text-gray-500 -mt-1">Premium Footwear</p>
            </div>
          </Link>

          <div className="hidden lg:flex items-center space-x-8">
            <Link to="/" className={`nav-link ${isActive('/') ? 'text-red-600 font-semibold' : 'text-gray-700'}`} data-testid="nav-home">{t('nav.home')}</Link>
            <Link to="/products/men" className={`nav-link ${isActive('/products/men') ? 'text-red-600 font-semibold' : 'text-gray-700'}`} data-testid="nav-men">{t('nav.men')}</Link>
            <Link to="/products/women" className={`nav-link ${isActive('/products/women') ? 'text-red-600 font-semibold' : 'text-gray-700'}`} data-testid="nav-women">{t('nav.women')}</Link>
            <Link to="/products/sports" className={`nav-link ${isActive('/products/sports') ? 'text-red-600 font-semibold' : 'text-gray-700'}`} data-testid="nav-sports">{t('nav.sports')}</Link>
            <Link to="/products/new_arrivals" className={`nav-link ${isActive('/products/new_arrivals') ? 'text-red-600 font-semibold' : 'text-gray-700'}`} data-testid="nav-new-arrivals">{t('nav.newArrivals')}</Link>
            <Link to="/contact" className={`nav-link ${isActive('/contact') ? 'text-red-600 font-semibold' : 'text-gray-700'}`}>İletişim</Link>
          </div>

          <div className="flex items-center space-x-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="hover:bg-red-50" data-testid="language-selector">
                  <Globe className="h-5 w-5 text-gray-700" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-40">
                <DropdownMenuItem onClick={() => changeLanguage('en')} data-testid="lang-en">🇬🇧 English</DropdownMenuItem>
                <DropdownMenuItem onClick={() => changeLanguage('ar')} data-testid="lang-ar">🇸🇦 العربية</DropdownMenuItem>
                <DropdownMenuItem onClick={() => changeLanguage('tr')} data-testid="lang-tr">🇹🇷 Türkçe</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {user && (
              <Link to="/wishlist" className="hidden sm:block">
                <Button variant="ghost" size="icon" className="hover:bg-red-50 group">
                  <Heart className="h-5 w-5 text-gray-700 group-hover:text-red-600 transition-colors" />
                </Button>
              </Link>
            )}

            <Link to="/cart" data-testid="nav-cart" className="hidden sm:block">
              <Button variant="ghost" size="icon" className="relative hover:bg-red-50 group">
                <ShoppingCart className="h-5 w-5 text-gray-700 group-hover:text-red-600 transition-colors" />
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-600 text-white text-xs rounded-full flex items-center justify-center font-semibold">0</span>
              </Button>
            </Link>

            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="hover:bg-red-50" data-testid="user-menu">
                    <User className="h-5 w-5 text-gray-700" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="px-3 py-2 border-b">
                    <p className="font-semibold text-gray-900">{user.name}</p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                  <DropdownMenuItem onClick={() => navigate('/profile')} data-testid="nav-profile">👤 Profilim</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/my-orders')} data-testid="nav-my-orders">📦 {t('nav.myOrders')}</DropdownMenuItem>
                  {user.role === 'admin' && (
                    <DropdownMenuItem onClick={() => navigate('/admin')} data-testid="nav-admin">⚙️ {t('nav.admin')}</DropdownMenuItem>
                  )}
                  <DropdownMenuItem onClick={handleLogout} data-testid="nav-logout" className="text-red-600">
                    <LogOut className="mr-2 h-4 w-4" />{t('nav.logout')}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button onClick={() => navigate('/login')} className="hidden sm:flex bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white rounded-full px-6 shadow-lg hover:shadow-xl transition-all" data-testid="nav-login">
                {t('nav.login')}
              </Button>
            )}
          </div>
        </div>
      </div>

      <style>{`
        .nav-link {
          position: relative;
          font-weight: 500;
          font-size: 0.95rem;
          transition: all 0.3s ease;
        }
        .nav-link::after {
          content: '';
          position: absolute;
          bottom: -4px;
          left: 0;
          width: 0;
          height: 2px;
          background: linear-gradient(to right, #E31837, #FF3D57);
          transition: width 0.3s ease;
        }
        .nav-link:hover {
          color: #E31837;
        }
        .nav-link:hover::after {
          width: 100%;
        }
      `}</style>
    </nav>
  );
}
