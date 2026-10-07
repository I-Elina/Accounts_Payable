import React from 'react';

export function Button({
  children,
  variant = 'primary', // 'primary' | 'secondary' | 'danger' | 'pass'
  size = 'md', // 'sm' | 'md' | 'lg'
  onClick,
  disabled = false,
  type = 'button',
  icon: Icon,
  className = '',
  ...props
}) {
  const variantClass = `btn-${variant}`;
  const sizeClass = size !== 'md' ? `btn-${size}` : '';

  return (
    <button
      type={type}
      className={`btn ${variantClass} ${sizeClass} ${className}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {Icon && <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />}
      {children}
    </button>
  );
}
