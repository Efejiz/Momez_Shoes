import React from 'react';

export default function LoadingSpinner({ size = 'md', text }) {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
    xl: 'w-16 h-16 border-4'
  };

  return (
    <div className="flex flex-col items-center justify-center" data-testid="loading-spinner">
      <div className={`${sizes[size]} border-red-200 border-t-red-600 rounded-full animate-spin`}></div>
      {text && <p className="mt-4 text-gray-600">{text}</p>}
    </div>
  );
}
