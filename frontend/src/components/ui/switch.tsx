import * as React from "react";
import * as SwitchPrimitive from "@radix-ui/react-switch";
import { cn } from "@/lib/utils";

const Switch = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitive.Root>
>(({ className, ...props }, ref) => (
  <SwitchPrimitive.Root
    ref={ref}
    className={cn(
      "inline-flex h-4 w-6 items-center shrink-0 cursor-pointer border-2 border-transparent rounded-full bg-background p-0.5 transition-all duration-200 ease-in-out data-[state=checked]:translate-x-2 data-[state=checked]:border-primary",
      className
    )}
    {...props}
  />
));

Switch.displayName = SwitchPrimitive.Root.displayName;

const Thumb = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitive.Thumb>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitive.Thumb>
>(({ className, ...props }, ref) => (
  <SwitchPrimitive.Thumb
    ref={ref}
    className={cn(
      "block h-3 w-3 rounded-full bg-primary ring-0 transition-transform duration-200",
      className
    )}
    {...props}
  />
));

Thumb.displayName = SwitchPrimitive.Thumb.displayName;

export { Switch, Thumb as SwitchThumb };