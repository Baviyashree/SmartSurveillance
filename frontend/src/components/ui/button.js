import * as React from "react";

export function Button({ className, children, ...props }) {
  return (
    <button
      className={`rounded-xl bg-purple-500 px-4 py-2 text-white hover:bg-purple-600 transition ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
