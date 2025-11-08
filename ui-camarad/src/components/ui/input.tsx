import * as React from "react";

type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className = "", ...props }, ref) => (
    <input
      ref={ref}
      className={`flex h-10 w-full rounded-md border border-cyan-500 bg-black px-3 py-2 text-sm text-cyan-400 placeholder:text-cyan-600 focus:outline-none focus:ring-2 focus:ring-cyan-300 ${className}`}
      {...props}
    />
  ),
);

Input.displayName = "Input";