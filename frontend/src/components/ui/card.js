import * as React from "react";

export function Card({ className, ...props }) {
  return (
    <div
      className={`rounded-2xl border bg-white p-6 shadow-sm ${className}`}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }) {
  return <div className={`mb-2 font-semibold ${className}`} {...props} />;
}

export function CardContent({ className, ...props }) {
  return <div className={`text-gray-600 ${className}`} {...props} />;
}
