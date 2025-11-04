import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { AuthContext } from '../App';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import LoadingSpinner from '../components/LoadingSpinner';
import { User, MapPin, Lock, Plus, Edit, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Profile() {
  const { t } = useTranslation();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [addresses, setAddresses] = useState([]);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  
  const [addressForm, setAddressForm] = useState({
    full_name: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'TR',
    is_default: false
  });

  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchAddresses();
  }, [user, navigate]);

  const fetchAddresses = async () => {
    try {
      const token = localStorage.getItem('session_token');
      const response = await axios.get(`${API}/profile/addresses`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setAddresses(response.data);
    } catch (error) {
      console.error('Error fetching addresses:', error);
      toast.error('Adresler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleAddressSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('session_token');
      if (editingAddress) {
        await axios.put(`${API}/profile/addresses/${editingAddress.id}`, addressForm, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        toast.success('Adres güncellendi');
      } else {
        await axios.post(`${API}/profile/addresses`, addressForm, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        toast.success('Adres eklendi');
      }
      setShowAddressForm(false);
      setEditingAddress(null);
      resetAddressForm();
      fetchAddresses();
    } catch (error) {
      console.error('Error saving address:', error);
      toast.error('Adres kaydedilemedi');
    }
  };

  const handleDeleteAddress = async (addressId) => {
    if (!window.confirm('Bu adresi silmek istediğinizden emin misiniz?')) return;
    
    try {
      const token = localStorage.getItem('session_token');
      await axios.delete(`${API}/profile/addresses/${addressId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      toast.success('Adres silindi');
      fetchAddresses();
    } catch (error) {
      console.error('Error deleting address:', error);
      toast.error('Adres silinemedi');
    }
  };

  const handleEditAddress = (address) => {
    setEditingAddress(address);
    setAddressForm({
      full_name: address.full_name,
      phone: address.phone,
      address_line1: address.address_line1,
      address_line2: address.address_line2 || '',
      city: address.city,
      state: address.state,
      postal_code: address.postal_code,
      country: address.country,
      is_default: address.is_default
    });
    setShowAddressForm(true);
  };

  const resetAddressForm = () => {
    setAddressForm({
      full_name: '',
      phone: '',
      address_line1: '',
      address_line2: '',
      city: '',
      state: '',
      postal_code: '',
      country: 'TR',
      is_default: false
    });
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Yeni şifreler eşleşmiyor');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      toast.error('Şifre en az 8 karakter olmalıdır');
      return;
    }

    try {
      const token = localStorage.getItem('session_token');
      await axios.post(`${API}/auth/change-password`, {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      toast.success('Şifre başarıyla değiştirildi');
      setShowPasswordForm(false);
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      console.error('Error changing password:', error);
      toast.error(error.response?.data?.detail || 'Şifre değiştirilemedi');
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Profilim</h1>

        {/* User Info Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-red-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">{user?.name}</h2>
              <p className="text-gray-600">{user?.email}</p>
              {user?.role === 'admin' && (
                <span className="inline-block px-3 py-1 bg-red-100 text-red-600 text-sm rounded-full mt-2">
                  Admin
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Password Change Section */}
        {user?.role === 'admin' && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Lock className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-semibold">Şifre Değiştir</h3>
              </div>
              <Button
                onClick={() => setShowPasswordForm(!showPasswordForm)}
                variant="outline"
                size="sm"
              >
                {showPasswordForm ? 'İptal' : 'Değiştir'}
              </Button>
            </div>

            {showPasswordForm && (
              <form onSubmit={handlePasswordSubmit} className="space-y-4 mt-4">
                <div>
                  <Label htmlFor="old_password">Mevcut Şifre</Label>
                  <Input
                    id="old_password"
                    type="password"
                    value={passwordForm.old_password}
                    onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="new_password">Yeni Şifre</Label>
                  <Input
                    id="new_password"
                    type="password"
                    value={passwordForm.new_password}
                    onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="confirm_password">Yeni Şifre (Tekrar)</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    value={passwordForm.confirm_password}
                    onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                    required
                  />
                </div>
                <Button type="submit" className="w-full">Şifreyi Değiştir</Button>
              </form>
            )}
          </div>
        )}

        {/* Addresses Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <MapPin className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-semibold">Adreslerim</h3>
            </div>
            <Button
              onClick={() => {
                setEditingAddress(null);
                resetAddressForm();
                setShowAddressForm(true);
              }}
              className="bg-red-600 hover:bg-red-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Yeni Adres
            </Button>
          </div>

          {/* Address Form */}
          {showAddressForm && (
            <form onSubmit={handleAddressSubmit} className="mb-6 p-4 border rounded-lg space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="full_name">Ad Soyad *</Label>
                  <Input
                    id="full_name"
                    value={addressForm.full_name}
                    onChange={(e) => setAddressForm({ ...addressForm, full_name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Telefon *</Label>
                  <Input
                    id="phone"
                    value={addressForm.phone}
                    onChange={(e) => setAddressForm({ ...addressForm, phone: e.target.value })}
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="address_line1">Adres Satırı 1 *</Label>
                  <Input
                    id="address_line1"
                    value={addressForm.address_line1}
                    onChange={(e) => setAddressForm({ ...addressForm, address_line1: e.target.value })}
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="address_line2">Adres Satırı 2</Label>
                  <Input
                    id="address_line2"
                    value={addressForm.address_line2}
                    onChange={(e) => setAddressForm({ ...addressForm, address_line2: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="city">Şehir *</Label>
                  <Input
                    id="city"
                    value={addressForm.city}
                    onChange={(e) => setAddressForm({ ...addressForm, city: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="state">İlçe/Bölge *</Label>
                  <Input
                    id="state"
                    value={addressForm.state}
                    onChange={(e) => setAddressForm({ ...addressForm, state: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="postal_code">Posta Kodu *</Label>
                  <Input
                    id="postal_code"
                    value={addressForm.postal_code}
                    onChange={(e) => setAddressForm({ ...addressForm, postal_code: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="country">Ülke *</Label>
                  <Input
                    id="country"
                    value={addressForm.country}
                    onChange={(e) => setAddressForm({ ...addressForm, country: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_default"
                  checked={addressForm.is_default}
                  onChange={(e) => setAddressForm({ ...addressForm, is_default: e.target.checked })}
                  className="w-4 h-4"
                />
                <Label htmlFor="is_default" className="cursor-pointer">
                  Varsayılan adres olarak ayarla
                </Label>
              </div>
              <div className="flex gap-2">
                <Button type="submit" className="bg-red-600 hover:bg-red-700">
                  {editingAddress ? 'Güncelle' : 'Kaydet'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowAddressForm(false);
                    setEditingAddress(null);
                    resetAddressForm();
                  }}
                >
                  İptal
                </Button>
              </div>
            </form>
          )}

          {/* Address List */}
          {addresses.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Henüz kayıtlı adres yok</p>
          ) : (
            <div className="space-y-4">
              {addresses.map((address) => (
                <div
                  key={address.id}
                  className={`p-4 border rounded-lg ${address.is_default ? 'border-red-500 bg-red-50' : 'border-gray-200'}`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      {address.is_default && (
                        <span className="inline-block px-2 py-1 bg-red-600 text-white text-xs rounded mb-2">
                          Varsayılan
                        </span>
                      )}
                      <h4 className="font-semibold">{address.full_name}</h4>
                      <p className="text-sm text-gray-600">{address.phone}</p>
                      <p className="text-sm text-gray-600 mt-2">
                        {address.address_line1}
                        {address.address_line2 && `, ${address.address_line2}`}
                      </p>
                      <p className="text-sm text-gray-600">
                        {address.city}, {address.state} {address.postal_code}
                      </p>
                      <p className="text-sm text-gray-600">{address.country}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEditAddress(address)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDeleteAddress(address.id)}
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
