import React from 'react';
import { Button } from './ui/button';

export default function EmptyState({ icon: Icon, title, description, actionText, onAction }) {
  return (
    <div className="text-center py-16" data-testid="empty-state">
      {Icon && (
        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-50 rounded-full mb-4">
          <Icon className="w-8 h-8 text-red-600" />
        </div>
      )}
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      {description && <p className="text-gray-600 mb-6">{description}</p>}
      {actionText && onAction && (
        <Button onClick={onAction} data-testid="empty-state-action">
          {actionText}
        </Button>
      )}
    </div>
  );
}
