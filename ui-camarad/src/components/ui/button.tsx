import * as React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", ...props }, ref) => (
    <button
      ref={ref}
      className={`inline-flex items-center justify-center rounded-lg border border-cyan-500 bg-cyan-400/90 px-4 py-2 text-sm font-semibold uppercase text-black transition hover:bg-cyan-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 ${className}`}
      {...props}
    />
  ),
);

Button.displayName = "Button";
