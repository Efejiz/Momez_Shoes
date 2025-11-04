import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { Package } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function MyOrders() {
  const { t } = useTranslation();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`, { withCredentials: true });
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" data-testid="loading-spinner">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-32 px-4" data-testid="my-orders-page" style={{ paddingTop: '120px' }}>
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold text-foreground mb-8" data-testid="orders-title">
          {t('nav.myOrders')}
        </h1>

        {orders.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl" data-testid="no-orders">
            <Package className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <p className="text-xl text-gray-500">No orders yet</p>
          </div>
        ) : (
          <div className="space-y-6" data-testid="orders-list">
            {orders.map((order) => (
              <div key={order.id} className="bg-white rounded-2xl p-6 shadow-sm" data-testid={`order-${order.id}`}>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <p className="text-sm text-gray-500">Order ID</p>
                    <p className="font-mono font-semibold" data-testid="order-id">{order.id}</p>
                  </div>
                  <span
                    className={`px-4 py-1 rounded-full text-sm font-semibold ${getStatusColor(order.status)}`}
                    data-testid="order-status"
                  >
                    {order.status}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  {order.items.map((item, index) => (
                    <div key={index} className="flex justify-between text-sm" data-testid={`order-item-${index}`}>
                      <span className="text-gray-600">
                        {item.product_name} ({item.size}) x {item.quantity}
                      </span>
                      <span className="font-semibold">${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                  ))}
                </div>

                <div className="border-t pt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Subtotal</span>
                    <span data-testid="order-subtotal">${order.total_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Shipping</span>
                    <span data-testid="order-shipping">${order.shipping_cost.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between font-bold text-lg text-primary pt-2 border-t">
                    <span>Total</span>
                    <span data-testid="order-total">${(order.total_amount + order.shipping_cost).toFixed(2)}</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t text-sm text-gray-500">
                  <p>Ordered on {new Date(order.created_at).toLocaleDateString()}</p>
                  <p>Shipping to: {order.shipping_address}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
