import React, { useEffect, useState, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { AuthContext } from '../App';
import LoadingSpinner from '../components/LoadingSpinner';
import { ShoppingCart, Check, X, Heart } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ProductDetail() {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [selectedSize, setSelectedSize] = useState('');
  const [loading, setLoading] = useState(true);
  const [addingToCart, setAddingToCart] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`${API}/products/${id}`);
      setProduct(response.data);
    } catch (error) {
      console.error('Error fetching product:', error);
      toast.error('Product not found');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!user) {
      toast.error('Please login to add items to cart');
      navigate('/login');
      return;
    }

    if (!selectedSize) {
      toast.error(t('product.selectSize'));
      return;
    }

    setAddingToCart(true);
    try {
      await axios.post(
        `${API}/cart/add`,
        {
          product_id: product.id,
          size: selectedSize,
          quantity: 1
        },
        { withCredentials: true }
      );
      toast.success('Added to cart!');
      setSelectedSize('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add to cart');
    } finally {
      setAddingToCart(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="xl" text="Loading product..." />
      </div>
    );
  }

  if (!product) return null;

  const currentLang = i18n.language;
  const name = product.name[currentLang] || product.name.en;
  const description = product.description[currentLang] || product.description.en;
  const images = product.images.length > 0 ? product.images : ['https://via.placeholder.com/800x1000'];

  return (
    <div className="min-h-screen py-32 px-4" data-testid="product-detail-page" style={{ paddingTop: '120px' }}>
      <div className="container mx-auto max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="space-y-4">
            <div className="aspect-square rounded-3xl overflow-hidden bg-gray-50 shadow-xl" data-testid="main-product-image">
              <img src={images[currentImageIndex]} alt={name} className="w-full h-full object-cover" />
            </div>
            {images.length > 1 && (
              <div className="grid grid-cols-4 gap-4" data-testid="product-thumbnails">
                {images.map((img, index) => (
                  <div key={index} className={`aspect-square rounded-xl overflow-hidden cursor-pointer border-2 transition-all ${index === currentImageIndex ? 'border-red-600 scale-105' : 'border-gray-200 hover:border-red-300'}`} onClick={() => setCurrentImageIndex(index)} data-testid={`thumbnail-${index}`}>
                    <img src={img} alt={`${name} ${index + 1}`} className="w-full h-full object-cover" />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-8">
            <div>
              <div className="inline-block px-4 py-1 bg-red-100 text-red-600 rounded-full text-sm font-semibold mb-4">{product.category.replace('_', ' ').toUpperCase()}</div>
              <h1 className="text-5xl font-bold text-gray-900 mb-4" data-testid="product-name">{name}</h1>
              <p className="text-sm text-gray-500" data-testid="product-sku">{t('product.sku')}: {product.sku}</p>
            </div>

            <div className="text-4xl font-bold text-red-600" data-testid="product-price">${product.price.toFixed(2)}</div>

            <div>
              <h3 className="text-xl font-semibold mb-3 text-gray-900">{t('product.description')}</h3>
              <p className="text-gray-600 leading-relaxed text-lg" data-testid="product-description">{description}</p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-4 text-gray-900">{t('product.selectSize')}</h3>
              <div className="flex flex-wrap gap-3" data-testid="size-selector">
                {product.sizes_stock.map((sizeStock) => {
                  const isAvailable = sizeStock.stock > 0;
                  const isSelected = selectedSize === sizeStock.size;
                  return (
                    <button key={sizeStock.size} onClick={() => isAvailable && setSelectedSize(sizeStock.size)} disabled={!isAvailable} className={`relative w-16 h-16 rounded-xl border-2 font-bold text-lg transition-all ${isSelected ? 'border-red-600 bg-red-600 text-white scale-110' : isAvailable ? 'border-gray-300 hover:border-red-600 hover:scale-105' : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'}`} data-testid={`size-${sizeStock.size}`}>
                      {sizeStock.size}
                      {!isAvailable && <X className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-10 h-10 text-red-500" />}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex gap-4">
              <Button size="lg" className="flex-1 h-14 text-lg bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 rounded-full" onClick={handleAddToCart} disabled={addingToCart || !selectedSize} data-testid="add-to-cart-button">
                {addingToCart ? <LoadingSpinner size="sm" /> : <><ShoppingCart className="mr-2 h-5 w-5" />{t('product.addToCart')}</>}
              </Button>
              <Button size="lg" variant="outline" className="h-14 w-14 rounded-full border-2 border-gray-300 hover:border-red-600 hover:bg-red-50">
                <Heart className="h-5 w-5" />
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-4 pt-6 border-t">
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <Check className="w-6 h-6 text-red-600 mx-auto mb-2" />
                <p className="text-sm font-semibold text-gray-900">Free Shipping</p>
                <p className="text-xs text-gray-500">On orders $100+</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <Check className="w-6 h-6 text-red-600 mx-auto mb-2" />
                <p className="text-sm font-semibold text-gray-900">Authentic</p>
                <p className="text-xs text-gray-500">100% Original</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <Check className="w-6 h-6 text-red-600 mx-auto mb-2" />
                <p className="text-sm font-semibold text-gray-900">Warranty</p>
                <p className="text-xs text-gray-500">1 Year</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
