import * as React from "react";

import { cn } from "@/lib/utils";

function Input({ className, type = "text", ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      className={cn(
        "flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-right text-sm tabular-nums text-foreground shadow-inner shadow-black/10 outline-none transition focus:border-primary/60 focus:bg-white/8 focus:ring-4 focus:ring-primary/10 disabled:cursor-not-allowed disabled:opacity-60",
        className
      )}
      {...props}
    />
  );
}

export { Input };
