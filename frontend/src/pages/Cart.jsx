import React, { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { AuthContext } from '../App';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { Trash2, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Cart() {
  const { t, i18n } = useTranslation();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [cart, setCart] = useState({ items: [] });
  const [products, setProducts] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchCart();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchCart = async () => {
    try {
      const response = await axios.get(`${API}/cart`, { withCredentials: true });
      setCart(response.data);
      
      // Fetch product details
      const productIds = [...new Set(response.data.items.map(item => item.product_id))];
      const productPromises = productIds.map(id => axios.get(`${API}/products/${id}`));
      const productResponses = await Promise.all(productPromises);
      
      const productsMap = {};
      productResponses.forEach(res => {
        productsMap[res.data.id] = res.data;
      });
      setProducts(productsMap);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (productId, size) => {
    try {
      await axios.delete(`${API}/cart/remove/${productId}/${size}`, { withCredentials: true });
      toast.success('Removed from cart');
      fetchCart();
    } catch (error) {
      toast.error('Failed to remove item');
    }
  };

  const calculateSubtotal = () => {
    return cart.items.reduce((sum, item) => {
      const product = products[item.product_id];
      if (product) {
        return sum + product.price * item.quantity;
      }
      return sum;
    }, 0);
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center" data-testid="login-required">
        <EmptyState
          icon={ShoppingBag}
          title="Login Required"
          description="Please login to view your shopping cart and start shopping"
          actionText="Go to Login"
          onAction={() => navigate('/login')}
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="xl" text="Loading your cart..." />
      </div>
    );
  }

  const subtotal = calculateSubtotal();

  return (
    <div className="min-h-screen py-32 px-4" data-testid="cart-page" style={{ paddingTop: '120px' }}>
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold text-foreground mb-8" data-testid="cart-title">
          {t('cart.title')}
        </h1>

        {cart.items.length === 0 ? (
          <div className="bg-white rounded-2xl p-8" data-testid="empty-cart">
            <EmptyState
              icon={ShoppingBag}
              title={t('cart.empty')}
              description="Add some amazing shoes to your cart and start shopping!"
              actionText={t('cart.continueShopping')}
              onAction={() => navigate('/')}
            />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Cart Items */}
            <div className="space-y-4" data-testid="cart-items">
              {cart.items.map((item) => {
                const product = products[item.product_id];
                if (!product) return null;

                const name = product.name[i18n.language] || product.name.en;
                const image = product.images[0] || 'https://via.placeholder.com/200';

                return (
                  <div
                    key={`${item.product_id}-${item.size}`}
                    className="bg-white rounded-xl p-6 flex items-center space-x-6 shadow-sm"
                    data-testid={`cart-item-${item.product_id}`}
                  >
                    <img
                      src={image}
                      alt={name}
                      className="w-24 h-24 object-cover rounded-lg"
                      data-testid="cart-item-image"
                    />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold" data-testid="cart-item-name">
                        {name}
                      </h3>
                      <p className="text-gray-500" data-testid="cart-item-size">
                        Size: {item.size}
                      </p>
                      <p className="text-primary font-semibold" data-testid="cart-item-price">
                        ${product.price.toFixed(2)} x {item.quantity}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold text-primary mb-2" data-testid="cart-item-total">
                        ${(product.price * item.quantity).toFixed(2)}
                      </p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemove(item.product_id, item.size)}
                        data-testid="remove-item-button"
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Cart Summary */}
            <div className="bg-white rounded-xl p-6 shadow-sm" data-testid="cart-summary">
              <div className="flex justify-between items-center mb-6">
                <span className="text-xl font-semibold">{t('cart.subtotal')}</span>
                <span className="text-2xl font-bold text-primary" data-testid="cart-subtotal">
                  ${subtotal.toFixed(2)}
                </span>
              </div>
              <Button
                size="lg"
                className="w-full rounded-full"
                onClick={() => navigate('/checkout')}
                data-testid="checkout-button"
              >
                {t('cart.checkout')}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
