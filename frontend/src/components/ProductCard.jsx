import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from './ui/button';
import { ShoppingCart } from 'lucide-react';

export default function ProductCard({ product }) {
  const { i18n } = useTranslation();
  const navigate = useNavigate();
  const currentLang = i18n.language;

  const name = product.name[currentLang] || product.name.en;
  const firstImage = product.images[0] || 'https://via.placeholder.com/400x500';
  const hasStock = product.sizes_stock.some(s => s.stock > 0);

  return (
    <div className="group relative bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-500 cursor-pointer border border-gray-100" data-testid={`product-card-${product.id}`}>
      <div className="relative aspect-square overflow-hidden bg-gray-50" onClick={() => navigate(`/product/${product.id}`)}>
        <img src={firstImage} alt={name} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" data-testid="product-image" />
        
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        <div className="absolute top-4 left-4 flex flex-col space-y-2">
          {product.featured && (
            <span className="badge badge-primary text-xs shadow-lg" data-testid="featured-badge">✨ Featured</span>
          )}
          {!hasStock && (
            <span className="badge bg-gray-900 text-white text-xs shadow-lg" data-testid="out-of-stock-badge">Out of Stock</span>
          )}
        </div>

        {hasStock && (
          <div className="absolute bottom-4 left-4 right-4 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-4 group-hover:translate-y-0">
            <Button className="w-full bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white rounded-full shadow-xl" onClick={(e) => { e.stopPropagation(); navigate(`/product/${product.id}`); }} data-testid="quick-add-button">
              <ShoppingCart className="w-4 h-4 mr-2" />
              Quick View
            </Button>
          </div>
        )}
      </div>

      <div className="p-5 space-y-3" onClick={() => navigate(`/product/${product.id}`)}>
        <p className="text-xs font-semibold text-red-600 uppercase tracking-wider">{product.category.replace('_', ' ')}</p>
        <h3 className="text-lg font-bold text-gray-900 line-clamp-2 group-hover:text-red-600 transition-colors" data-testid="product-name">{name}</h3>
        
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500">Sizes:</span>
          <div className="flex space-x-1">
            {product.sizes_stock.slice(0, 4).map((size, index) => (
              <span key={index} className={`text-xs px-2 py-1 rounded ${size.stock > 0 ? 'bg-gray-100 text-gray-700' : 'bg-gray-50 text-gray-400 line-through'}`}>{size.size}</span>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <span className="text-2xl font-bold text-gray-900" data-testid="product-price">${product.price.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}
