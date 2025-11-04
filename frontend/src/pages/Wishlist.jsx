import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import axios from 'axios';
import ProductCard from '../components/ProductCard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { Heart } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Wishlist() {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchWishlist();
  }, [user, navigate]);

  const fetchWishlist = async () => {
    try {
      const token = localStorage.getItem('session_token');
      const response = await axios.get(`${API}/wishlist`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      toast.error('Favoriler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen py-32 px-4" style={{ paddingTop: '120px' }}>
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold mb-8 flex items-center gap-3">
          <Heart className="w-10 h-10 text-red-600" />
          Favorilerim
        </h1>

        {products.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} onWishlistUpdate={fetchWishlist} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Heart}
            title="Favori ürününüz yok"
            description="Beğendiğiniz ürünleri favorilere ekleyin"
          />
        )}
      </div>
    </div>
  );
}