import React from 'react'

const Button = ({ children, className = '', variant = 'default', size = 'default', onClick, ...props }) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none'
  
  const variants = {
    default: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    ghost: 'hover:bg-gray-700 hover:text-white focus:ring-gray-500',
  }
  
  const sizes = {
    sm: 'h-8 px-3 text-sm',
    default: 'h-10 px-4',
  }
  
  const classes = `${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`
  
  return (
    <button className={classes} onClick={onClick} {...props}>
      {children}
    </button>
  )
}

export { Button }
