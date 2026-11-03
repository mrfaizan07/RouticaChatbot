import React from "react";
import { LoadingSpinner } from "./LoadingSpinner";

export function IconButton({
  icon: Icon,
  onClick,
  ariaLabel,
  title,
  type = "button",
  variant = "ghost",
  size = "md",
  disabled = false,
  loading = false,
  className = "",
}) {
  const baseClasses =
    "inline-flex items-center justify-center transition-all duration-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed";

  const variantClasses = {
    ghost: "text-slate-500 hover:text-slate-800 hover:bg-slate-100 focus:ring-slate-300",
    primary: "bg-routica-600 hover:bg-routica-700 text-white focus:ring-routica-500 shadow-sm",
    secondary: "bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 focus:ring-slate-300",
    header: "text-slate-300 hover:text-white hover:bg-white/10 focus:ring-white/20",
  };

  const sizeClasses = {
    sm: "w-7 h-7 p-1 text-xs",
    md: "w-8 h-8 p-1.5 text-sm",
    lg: "w-10 h-10 p-2 text-base",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      aria-label={ariaLabel || title}
      title={title}
      className={`${baseClasses} ${variantClasses[variant] || variantClasses.ghost} ${
        sizeClasses[size] || sizeClasses.md
      } ${className}`}
    >
      {loading ? <LoadingSpinner size="sm" /> : Icon ? <Icon className="w-full h-full" /> : null}
    </button>
  );
}

