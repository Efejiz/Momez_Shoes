import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import ProductCard from '../components/ProductCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { ChevronRight, Sparkles, TrendingUp, Shield, Truck, Award } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFeaturedProducts();
  }, []);

  const fetchFeaturedProducts = async () => {
    try {
      const response = await axios.get(`${API}/products?featured=true`);
      setFeaturedProducts(response.data.slice(0, 8));
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen" data-testid="home-page">
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden" data-testid="hero-section">
        <div className="absolute inset-0 bg-gradient-to-br from-red-50 via-white to-rose-50"></div>
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-10 w-96 h-96 bg-red-200/30 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '4s' }}></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-rose-200/30 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '6s', animationDelay: '2s' }}></div>
        </div>
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left space-y-8 fade-in">
              <div className="inline-block">
                <span className="badge badge-primary animate-pulse">
                  <Sparkles className="inline w-4 h-4 mr-2" />
                  New Collection 2025
                </span>
              </div>
              
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-tight" data-testid="hero-title">
                <span className="text-gray-900">Step Into</span><br />
                <span className="gradient-text">Premium Style</span>
              </h1>
              
              <p className="text-lg sm:text-xl text-gray-600 leading-relaxed max-w-xl" data-testid="hero-subtitle">
                Discover the perfect blend of comfort, quality, and timeless design.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button size="lg" className="btn-primary text-lg" onClick={() => navigate('/products/new_arrivals')} data-testid="hero-shop-now-button">
                  Shop New Arrivals
                  <ChevronRight className="ml-2 h-5 w-5" />
                </Button>
              </div>
              
              <div className="grid grid-cols-3 gap-6 pt-8">
                <div className="text-center lg:text-left">
                  <p className="text-3xl font-bold text-gray-900">1000+</p>
                  <p className="text-sm text-gray-600">Premium Shoes</p>
                </div>
                <div className="text-center lg:text-left">
                  <p className="text-3xl font-bold text-gray-900">50K+</p>
                  <p className="text-sm text-gray-600">Happy Customers</p>
                </div>
                <div className="text-center lg:text-left">
                  <p className="text-3xl font-bold text-gray-900">100%</p>
                  <p className="text-sm text-gray-600">Authentic</p>
                </div>
              </div>
            </div>
            
            <div className="relative float">
              <img src="https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800" alt="Premium Shoes" className="w-full h-auto rounded-3xl shadow-2xl" />
            </div>
          </div>
        </div>
      </section>

      <section className="section bg-white" data-testid="features-section">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center group">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-red-100 transition-colors">
                <Truck className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Free Shipping</h3>
              <p className="text-gray-600 text-sm">On orders over $100</p>
            </div>
            <div className="text-center group">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-red-100 transition-colors">
                <Shield className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Secure Payment</h3>
              <p className="text-gray-600 text-sm">100% secure transactions</p>
            </div>
            <div className="text-center group">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-red-100 transition-colors">
                <Award className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Premium Quality</h3>
              <p className="text-gray-600 text-sm">Authentic products only</p>
            </div>
            <div className="text-center group">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-red-100 transition-colors">
                <TrendingUp className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Latest Trends</h3>
              <p className="text-gray-600 text-sm">New styles every week</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section bg-gradient-to-b from-white to-gray-50" data-testid="categories-section">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">Shop by Category</h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">Find your perfect pair</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: "Men's Shoes", category: 'men', image: 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=600' },
              { name: "Women's Shoes", category: 'women', image: 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600' },
              { name: 'Sports Shoes', category: 'sports', image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600' }
            ].map((cat) => (
              <div key={cat.category} className="relative h-96 rounded-3xl overflow-hidden cursor-pointer group card-hover shadow-xl" onClick={() => navigate(`/products/${cat.category}`)} data-testid={`category-card-${cat.category}`}>
                <img src={cat.image} alt={cat.name} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                <div className="absolute inset-0 bg-gradient-to-br from-red-600 to-red-700 opacity-60 group-hover:opacity-70 transition-opacity"></div>
                <div className="absolute inset-0 flex flex-col items-center justify-center text-white p-6">
                  <h3 className="text-3xl font-bold mb-4">{cat.name}</h3>
                  <Button variant="outline" className="border-white text-white hover:bg-white hover:text-gray-900 rounded-full">Shop Now</Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section bg-white" data-testid="featured-products-section">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4" data-testid="featured-title">Premium Collection</h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">Handpicked selection of our finest footwear</p>
          </div>

          {loading ? (
            <div className="flex justify-center py-20">
              <LoadingSpinner size="lg" text="Loading featured products..." />
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {featuredProducts.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
