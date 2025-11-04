import React, { useEffect, useState, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AuthContext } from '../App';
import { Button } from '../components/ui/button';
import LoadingSpinner from '../components/LoadingSpinner';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, Package, TrendingUp, MapPin } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminPanel() {
  const { t } = useTranslation();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [bestSelling, setBestSelling] = useState([]);
  const [activeRegions, setActiveRegions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showProductDialog, setShowProductDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  const [productForm, setProductForm] = useState({
    sku: '',
    name_en: '',
    name_ar: '',
    name_tr: '',
    description_en: '',
    description_ar: '',
    description_tr: '',
    price: '',
    category: 'men',
    featured: false,
    sizes_stock: [{ size: 'S', stock: 0 }]
  });

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/');
      return;
    }
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('session_token');
      const authHeaders = token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
      
      const [productsRes, ordersRes, bestSellingRes, regionsRes] = await Promise.all([
        axios.get(`${API}/products`),
        axios.get(`${API}/admin/orders`, authHeaders),
        axios.get(`${API}/admin/reports/best-selling`, authHeaders),
        axios.get(`${API}/admin/reports/regions`, authHeaders)
      ]);
      
      setProducts(productsRes.data);
      setOrders(ordersRes.data);
      setBestSelling(bestSellingRes.data);
      setActiveRegions(regionsRes.data);
    } catch (error) {
      console.error('Error fetching admin data:', error);
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('session_token');
      const authHeaders = token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
      
      if (editingProduct) {
        await axios.put(`${API}/admin/products/${editingProduct.id}`, productForm, authHeaders);
        toast.success('Product updated');
      } else {
        await axios.post(`${API}/admin/products`, productForm, authHeaders);
        toast.success('Product created');
      }
      setShowProductDialog(false);
      resetProductForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save product');
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      const token = localStorage.getItem('session_token');
      const authHeaders = token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
      
      await axios.delete(`${API}/admin/products/${productId}`, authHeaders);
      toast.success('Product deleted');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete product');
    }
  };

  const handleUpdateOrderStatus = async (orderId, status) => {
    try {
      const token = localStorage.getItem('session_token');
      const authHeaders = token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
      
      await axios.patch(`${API}/admin/orders/${orderId}/status`, { status }, authHeaders);
      toast.success('Order status updated');
      fetchData();
    } catch (error) {
      toast.error('Failed to update order status');
    }
  };

  const resetProductForm = () => {
    setProductForm({
      sku: '',
      name_en: '',
      name_ar: '',
      name_tr: '',
      description_en: '',
      description_ar: '',
      description_tr: '',
      price: '',
      category: 'men',
      featured: false,
      sizes_stock: [{ size: 'S', stock: 0 }]
    });
    setEditingProduct(null);
  };

  const openEditDialog = (product) => {
    setEditingProduct(product);
    setProductForm({
      sku: product.sku,
      name_en: product.name.en,
      name_ar: product.name.ar,
      name_tr: product.name.tr,
      description_en: product.description.en,
      description_ar: product.description.ar,
      description_tr: product.description.tr,
      price: product.price,
      category: product.category,
      featured: product.featured,
      sizes_stock: product.sizes_stock
    });
    setShowProductDialog(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="xl" text="Loading admin panel..." />
      </div>
    );
  }

  if (!user || user.role !== 'admin') {
    return null;
  }

  return (
    <div className="min-h-screen py-32 px-4" data-testid="admin-panel" style={{ paddingTop: '120px' }}>
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-foreground mb-8" data-testid="admin-title">
          {t('admin.title')}
        </h1>

        <Tabs defaultValue="products" className="w-full">
          <TabsList className="mb-8">
            <TabsTrigger value="products" data-testid="tab-products">
              <Package className="mr-2 h-4 w-4" />
              {t('admin.products')}
            </TabsTrigger>
            <TabsTrigger value="orders" data-testid="tab-orders">
              {t('admin.orders')}
            </TabsTrigger>
            <TabsTrigger value="reports" data-testid="tab-reports">
              <TrendingUp className="mr-2 h-4 w-4" />
              {t('admin.reports')}
            </TabsTrigger>
          </TabsList>

          {/* Products Tab */}
          <TabsContent value="products">
            <div className="mb-6">
              <Dialog open={showProductDialog} onOpenChange={setShowProductDialog}>
                <DialogTrigger asChild>
                  <Button onClick={resetProductForm} className="bg-foreground text-background hover:bg-foreground/90" data-testid="add-product-button">
                    <Plus className="mr-2 h-4 w-4" />
                    {t('admin.addProduct')}
                  </Button>
                </DialogTrigger>
                <DialogContent className="w-full sm:max-w-2xl max-h-[90vh] overflow-y-auto text-foreground">
                  <DialogHeader>
                    <DialogTitle>{editingProduct ? t('admin.editProduct') : t('admin.addProduct')}</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleProductSubmit} className="space-y-4" data-testid="product-form">
                    <div>
                      <Label className="text-foreground">SKU</Label>
                      <Input
                        value={productForm.sku}
                        onChange={(e) => setProductForm({ ...productForm, sku: e.target.value })}
                        required
                        data-testid="input-sku"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <Label className="text-foreground">Name (EN)</Label>
                        <Input
                          value={productForm.name_en}
                          onChange={(e) => setProductForm({ ...productForm, name_en: e.target.value })}
                          required
                          data-testid="input-name-en"
                        />
                      </div>
                      <div>
                        <Label className="text-foreground">Name (AR)</Label>
                        <Input
                          value={productForm.name_ar}
                          onChange={(e) => setProductForm({ ...productForm, name_ar: e.target.value })}
                          required
                          data-testid="input-name-ar"
                        />
                      </div>
                      <div>
                        <Label className="text-foreground">Name (TR)</Label>
                        <Input
                          value={productForm.name_tr}
                          onChange={(e) => setProductForm({ ...productForm, name_tr: e.target.value })}
                          required
                          data-testid="input-name-tr"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <Label className="text-foreground">Description (EN)</Label>
                        <Textarea
                          value={productForm.description_en}
                          onChange={(e) => setProductForm({ ...productForm, description_en: e.target.value })}
                          required
                          data-testid="input-desc-en"
                        />
                      </div>
                      <div>
                        <Label className="text-foreground">Description (AR)</Label>
                        <Textarea
                          value={productForm.description_ar}
                          onChange={(e) => setProductForm({ ...productForm, description_ar: e.target.value })}
                          required
                          data-testid="input-desc-ar"
                        />
                      </div>
                      <div>
                        <Label className="text-foreground">Description (TR)</Label>
                        <Textarea
                          value={productForm.description_tr}
                          onChange={(e) => setProductForm({ ...productForm, description_tr: e.target.value })}
                          required
                          data-testid="input-desc-tr"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label className="text-foreground">Price</Label>
                        <Input
                          type="number"
                          step="0.01"
                          value={productForm.price}
                          onChange={(e) => setProductForm({ ...productForm, price: parseFloat(e.target.value) })}
                          required
                          data-testid="input-price"
                        />
                      </div>
                      <div>
                        <Label className="text-foreground">Category</Label>
                        <Select
                          value={productForm.category}
                          onValueChange={(value) => setProductForm({ ...productForm, category: value })}
                        >
                          <SelectTrigger data-testid="select-category">
                            <SelectValue placeholder="Select category" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="men">Men</SelectItem>
                            <SelectItem value="women">Women</SelectItem>
                            <SelectItem value="sports">Sports</SelectItem>
                            <SelectItem value="new_arrivals">New Arrivals</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div>
                      <Label className="text-foreground">Sizes & Stock</Label>
                      <div className="space-y-2">
                        {productForm.sizes_stock.map((sizeStock, index) => (
                          <div key={index} className="flex flex-col sm:flex-row gap-2" data-testid={`size-stock-${index}`}>
                            <Input
                              placeholder="Size"
                              value={sizeStock.size}
                              onChange={(e) => {
                                const newSizes = [...productForm.sizes_stock];
                                newSizes[index].size = e.target.value;
                                setProductForm({ ...productForm, sizes_stock: newSizes });
                              }}
                            />
                            <Input
                              type="number"
                              placeholder="Stock"
                              value={sizeStock.stock}
                              onChange={(e) => {
                                const newSizes = [...productForm.sizes_stock];
                                newSizes[index].stock = parseInt(e.target.value) || 0;
                                setProductForm({ ...productForm, sizes_stock: newSizes });
                              }}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              onClick={() => {
                                const newSizes = productForm.sizes_stock.filter((_, i) => i !== index);
                                setProductForm({ ...productForm, sizes_stock: newSizes });
                              }}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => {
                            setProductForm({
                              ...productForm,
                              sizes_stock: [...productForm.sizes_stock, { size: '', stock: 0 }]
                            });
                          }}
                          data-testid="add-size-button"
                        >
                          Add Size
                        </Button>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="featured"
                        checked={productForm.featured}
                        onChange={(e) => setProductForm({ ...productForm, featured: e.target.checked })}
                        data-testid="checkbox-featured"
                      />
                      <Label htmlFor="featured" className="text-foreground">Featured Product</Label>
                    </div>

                    <Button type="submit" className="w-full" data-testid="submit-product-button">
                      {editingProduct ? 'Update Product' : 'Create Product'}
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="products-list">
              {products.map((product) => (
                <div key={product.id} className="bg-white rounded-xl p-6 shadow-sm" data-testid={`product-${product.id}`}>
                  <h3 className="font-semibold text-lg mb-2">{product.name.en}</h3>
                  <p className="text-sm text-gray-500 mb-2">SKU: {product.sku}</p>
                  <p className="text-primary font-bold text-xl mb-4">${product.price.toFixed(2)}</p>
                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openEditDialog(product)}
                      data-testid={`edit-product-${product.id}`}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeleteProduct(product.id)}
                      data-testid={`delete-product-${product.id}`}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Orders Tab */}
          <TabsContent value="orders">
            <div className="space-y-4" data-testid="orders-list">
              {orders.map((order) => (
                <div key={order.id} className="bg-white rounded-xl p-6 shadow-sm" data-testid={`order-${order.id}`}>
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <p className="font-semibold">Order #{order.id.slice(0, 8)}</p>
                      <p className="text-sm text-gray-500">{order.customer_name}</p>
                    </div>
                    <Select
                      value={order.status}
                      onValueChange={(value) => handleUpdateOrderStatus(order.id, value)}
                    >
                      <SelectTrigger className="w-40" data-testid={`order-status-${order.id}`}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="processing">Processing</SelectItem>
                        <SelectItem value="shipped">Shipped</SelectItem>
                        <SelectItem value="delivered">Delivered</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {order.items.length} items - Total: ${(order.total_amount + order.shipping_cost).toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">
                    Ordered: {new Date(order.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Best Selling Products */}
              <div className="bg-white rounded-xl p-6 shadow-sm" data-testid="best-selling-report">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <TrendingUp className="mr-2 h-5 w-5 text-primary" />
                  {t('admin.bestSelling')}
                </h3>
                <div className="space-y-3">
                  {bestSelling.map((item, index) => (
                    <div key={item._id} className="flex justify-between items-center" data-testid={`best-selling-${index}`}>
                      <div>
                        <p className="font-semibold">{item.product_name}</p>
                        <p className="text-sm text-gray-500">{item.total_quantity} units sold</p>
                      </div>
                      <p className="text-primary font-bold">${item.total_revenue?.toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Regions */}
              <div className="bg-white rounded-xl p-6 shadow-sm" data-testid="active-regions-report">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <MapPin className="mr-2 h-5 w-5 text-primary" />
                  {t('admin.activeRegions')}
                </h3>
                <div className="space-y-3">
                  {activeRegions.map((region, index) => (
                    <div key={region._id} className="flex justify-between items-center" data-testid={`region-${index}`}>
                      <div>
                        <p className="font-semibold">{region._id}</p>
                        <p className="text-sm text-gray-500">{region.total_orders} orders</p>
                      </div>
                      <p className="text-primary font-bold">${region.total_revenue?.toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
