import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      nav: {
        home: 'Home',
        men: 'Men',
        women: 'Women',
        sports: 'Sports',
        newArrivals: 'New Arrivals',
        cart: 'Cart',
        login: 'Login',
        logout: 'Logout',
        admin: 'Admin Panel',
        myOrders: 'My Orders'
      },
      home: {
        hero: 'Discover Your Style',
        heroSubtitle: 'Shop the latest trends in fashion',
        featured: 'Featured Products',
        shopNow: 'Shop Now',
        viewAll: 'View All'
      },
      product: {
        addToCart: 'Add to Cart',
        selectSize: 'Select Size',
        outOfStock: 'Out of Stock',
        price: 'Price',
        description: 'Description',
        sku: 'SKU'
      },
      cart: {
        title: 'Shopping Cart',
        empty: 'Your cart is empty',
        continueShopping: 'Continue Shopping',
        checkout: 'Proceed to Checkout',
        subtotal: 'Subtotal',
        remove: 'Remove'
      },
      checkout: {
        title: 'Checkout',
        customerInfo: 'Customer Information',
        name: 'Full Name',
        email: 'Email',
        phone: 'Phone Number',
        shippingAddress: 'Shipping Address',
        selectRegion: 'Select Shipping Region',
        shippingCost: 'Shipping Cost',
        total: 'Total',
        placeOrder: 'Place Order',
        paymentMethod: 'Payment Method: Cash on Delivery'
      },
      admin: {
        title: 'Admin Panel',
        products: 'Products',
        orders: 'Orders',
        reports: 'Reports',
        addProduct: 'Add Product',
        editProduct: 'Edit Product',
        bestSelling: 'Best Selling Products',
        activeRegions: 'Most Active Regions'
      },
      common: {
        loading: 'Loading...',
        error: 'An error occurred',
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit'
      }
    }
  },
  ar: {
    translation: {
      nav: {
        home: 'الرئيسية',
        men: 'رجال',
        women: 'نساء',
        sports: 'رياضة',
        newArrivals: 'وصل حديثاً',
        cart: 'السلة',
        login: 'تسجيل الدخول',
        logout: 'تسجيل الخروج',
        admin: 'لوحة الإدارة',
        myOrders: 'طلباتي'
      },
      home: {
        hero: 'اكتشف أسلوبك',
        heroSubtitle: 'تسوق أحدث صيحات الموضة',
        featured: 'منتجات مميزة',
        shopNow: 'تسوق الآن',
        viewAll: 'عرض الكل'
      },
      product: {
        addToCart: 'أضف إلى السلة',
        selectSize: 'اختر المقاس',
        outOfStock: 'غير متوفر',
        price: 'السعر',
        description: 'الوصف',
        sku: 'رمز المنتج'
      },
      cart: {
        title: 'سلة التسوق',
        empty: 'سلتك فارغة',
        continueShopping: 'متابعة التسوق',
        checkout: 'إتمام الطلب',
        subtotal: 'المجموع الفرعي',
        remove: 'حذف'
      },
      checkout: {
        title: 'إتمام الطلب',
        customerInfo: 'معلومات العميل',
        name: 'الاسم الكامل',
        email: 'البريد الإلكتروني',
        phone: 'رقم الهاتف',
        shippingAddress: 'عنوان الشحن',
        selectRegion: 'اختر منطقة الشحن',
        shippingCost: 'تكلفة الشحن',
        total: 'المجموع',
        placeOrder: 'تأكيد الطلب',
        paymentMethod: 'طريقة الدفع: الدفع عند الاستلام'
      },
      admin: {
        title: 'لوحة الإدارة',
        products: 'المنتجات',
        orders: 'الطلبات',
        reports: 'التقارير',
        addProduct: 'إضافة منتج',
        editProduct: 'تعديل منتج',
        bestSelling: 'المنتجات الأكثر مبيعاً',
        activeRegions: 'المناطق الأكثر نشاطاً'
      },
      common: {
        loading: 'جاري التحميل...',
        error: 'حدث خطأ',
        save: 'حفظ',
        cancel: 'إلغاء',
        delete: 'حذف',
        edit: 'تعديل'
      }
    }
  },
  tr: {
    translation: {
      nav: {
        home: 'Ana Sayfa',
        men: 'Erkek',
        women: 'Kadın',
        sports: 'Spor',
        newArrivals: 'Yeni Gelenler',
        cart: 'Sepet',
        login: 'Giriş Yap',
        logout: 'Çıkış Yap',
        admin: 'Yönetim Paneli',
        myOrders: 'Siparişlerim'
      },
      home: {
        hero: 'Tarzını Keşfet',
        heroSubtitle: 'Modadaki en son trendleri alışveriş yapın',
        featured: 'Öne Çıkan Ürünler',
        shopNow: 'Hemen Alışveriş Yap',
        viewAll: 'Tümünü Gör'
      },
      product: {
        addToCart: 'Sepete Ekle',
        selectSize: 'Beden Seç',
        outOfStock: 'Stokta Yok',
        price: 'Fiyat',
        description: 'Açıklama',
        sku: 'Ürün Kodu'
      },
      cart: {
        title: 'Alışveriş Sepeti',
        empty: 'Sepetiniz boş',
        continueShopping: 'Alışverişe Devam Et',
        checkout: 'Ödemeye Geç',
        subtotal: 'Ara Toplam',
        remove: 'Kaldır'
      },
      checkout: {
        title: 'Ödeme',
        customerInfo: 'Müşteri Bilgileri',
        name: 'Ad Soyad',
        email: 'E-posta',
        phone: 'Telefon Numarası',
        shippingAddress: 'Teslimat Adresi',
        selectRegion: 'Teslimat Bölgesi Seç',
        shippingCost: 'Kargo Ücreti',
        total: 'Toplam',
        placeOrder: 'Sipariş Ver',
        paymentMethod: 'Ödeme Yöntemi: Kapıda Ödeme'
      },
      admin: {
        title: 'Yönetim Paneli',
        products: 'Ürünler',
        orders: 'Siparişler',
        reports: 'Raporlar',
        addProduct: 'Ürün Ekle',
        editProduct: 'Ürünü Düzenle',
        bestSelling: 'En Çok Satan Ürünler',
        activeRegions: 'En Aktif Bölgeler'
      },
      common: {
        loading: 'Yükleniyor...',
        error: 'Bir hata oluştu',
        save: 'Kaydet',
        cancel: 'İptal',
        delete: 'Sil',
        edit: 'Düzenle'
      }
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
