import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Home, Search } from 'lucide-react';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 px-4">
      <div className="text-center max-w-2xl">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-gray-300">404</h1>
          <div className="relative -mt-16">
            <div className="text-6xl">👟</div>
          </div>
        </div>
        
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Sayfa Bulunamadı
        </h2>
        <p className="text-xl text-gray-600 mb-8">
          Aradığınız sayfa mevcut değil veya taşınmış olabilir.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            onClick={() => navigate('/')}
            className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 text-lg"
          >
            <Home className="w-5 h-5 mr-2" />
            Ana Sayfaya Dön
          </Button>
          <Button
            onClick={() => navigate('/products/new_arrivals')}
            variant="outline"
            className="px-8 py-3 text-lg"
          >
            <Search className="w-5 h-5 mr-2" />
            Ürünlere Göz At
          </Button>
        </div>
      </div>
    </div>
  );
}