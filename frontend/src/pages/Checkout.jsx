import React, { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import { AuthContext } from '../App';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Checkout() {
  const { t, i18n } = useTranslation();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [cart, setCart] = useState({ items: [] });
  const [products, setProducts] = useState({});
  const [regions, setRegions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  const [formData, setFormData] = useState({
    customer_name: user?.name || '',
    customer_email: user?.email || '',
    customer_phone: '',
    shipping_address: '',
    shipping_region_id: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [cartRes, regionsRes] = await Promise.all([
        axios.get(`${API}/cart`, { withCredentials: true }),
        axios.get(`${API}/shipping-regions`)
      ]);
      
      setCart(cartRes.data);
      setRegions(regionsRes.data);
      
      // Fetch products
      const productIds = [...new Set(cartRes.data.items.map(item => item.product_id))];
      const productPromises = productIds.map(id => axios.get(`${API}/products/${id}`));
      const productResponses = await Promise.all(productPromises);
      
      const productsMap = {};
      productResponses.forEach(res => {
        productsMap[res.data.id] = res.data;
      });
      setProducts(productsMap);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load checkout data');
    } finally {
      setLoading(false);
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

  const selectedRegion = regions.find(r => r.id === formData.shipping_region_id);
  const shippingCost = selectedRegion ? selectedRegion.cost : 0;
  const total = calculateSubtotal() + shippingCost;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.shipping_region_id) {
      toast.error(t('checkout.selectRegion'));
      return;
    }

    setSubmitting(true);
    try {
      const response = await axios.post(`${API}/orders`, formData, { withCredentials: true });
      toast.success('Order placed successfully!');
      navigate('/my-orders');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to place order');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" data-testid="loading-spinner">
        <div className="spinner"></div>
      </div>
    );
  }

  if (cart.items.length === 0) {
    navigate('/cart');
    return null;
  }

  return (
    <div className="min-h-screen py-32 px-4" data-testid="checkout-page" style={{ paddingTop: '120px' }}>
      <div className="container mx-auto max-w-6xl">
        <h1 className="text-4xl font-bold text-foreground mb-8" data-testid="checkout-title">
          {t('checkout.title')}
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Checkout Form */}
          <div className="bg-white rounded-2xl p-8 shadow-sm" data-testid="checkout-form">
            <h2 className="text-2xl font-semibold mb-6">{t('checkout.customerInfo')}</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="name">{t('checkout.name')}</Label>
                <Input
                  id="name"
                  value={formData.customer_name}
                  onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                  required
                  data-testid="input-name"
                />
              </div>

              <div>
                <Label htmlFor="email">{t('checkout.email')}</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.customer_email}
                  onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
                  required
                  data-testid="input-email"
                />
              </div>

              <div>
                <Label htmlFor="phone">{t('checkout.phone')}</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.customer_phone}
                  onChange={(e) => setFormData({ ...formData, customer_phone: e.target.value })}
                  required
                  data-testid="input-phone"
                />
              </div>

              <div>
                <Label htmlFor="address">{t('checkout.shippingAddress')}</Label>
                <Textarea
                  id="address"
                  value={formData.shipping_address}
                  onChange={(e) => setFormData({ ...formData, shipping_address: e.target.value })}
                  rows={4}
                  required
                  data-testid="input-address"
                />
              </div>

              <div>
                <Label>{t('checkout.selectRegion')}</Label>
                <Select
                  value={formData.shipping_region_id}
                  onValueChange={(value) => setFormData({ ...formData, shipping_region_id: value })}
                >
                  <SelectTrigger data-testid="select-region">
                    <SelectValue placeholder="Select region" />
                  </SelectTrigger>
                  <SelectContent>
                    {regions.map((region) => (
                      <SelectItem key={region.id} value={region.id} data-testid={`region-${region.id}`}>
                        {region.name[i18n.language] || region.name.en} - ${region.cost.toFixed(2)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="pt-4">
                <p className="text-sm text-gray-500 mb-4">{t('checkout.paymentMethod')}</p>
                <Button
                  type="submit"
                  size="lg"
                  className="w-full rounded-full"
                  disabled={submitting}
                  data-testid="place-order-button"
                >
                  {submitting ? (
                    <div className="spinner border-white"></div>
                  ) : (
                    t('checkout.placeOrder')
                  )}
                </Button>
              </div>
            </form>
          </div>

          {/* Order Summary */}
          <div className="bg-white rounded-2xl p-8 shadow-sm h-fit" data-testid="order-summary">
            <h2 className="text-2xl font-semibold mb-6">Order Summary</h2>
            <div className="space-y-4 mb-6">
              {cart.items.map((item) => {
                const product = products[item.product_id];
                if (!product) return null;

                const name = product.name[i18n.language] || product.name.en;

                return (
                  <div key={`${item.product_id}-${item.size}`} className="flex justify-between" data-testid={`summary-item-${item.product_id}`}>
                    <span className="text-gray-600">
                      {name} ({item.size}) x {item.quantity}
                    </span>
                    <span className="font-semibold">${(product.price * item.quantity).toFixed(2)}</span>
                  </div>
                );
              })}
            </div>

            <div className="border-t pt-4 space-y-3">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span data-testid="summary-subtotal">${calculateSubtotal().toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>{t('checkout.shippingCost')}</span>
                <span data-testid="summary-shipping">${shippingCost.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-xl font-bold text-primary pt-3 border-t">
                <span>{t('checkout.total')}</span>
                <span data-testid="summary-total">${total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
