import * as React from "react";
import * as ScrollAreaPrimitive from "@radix-ui/react-scroll-area";
import { cn } from "@/lib/utils";

const ScrollArea = React.forwardRef<
  React.ElementRef<typeof ScrollAreaPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.Root>
>(({ className, ...props }, ref) => (
  <ScrollAreaPrimitive.Root
    ref={ref}
    className={cn(
      "relative",
      className
    )}
    {...props}
  />
));
ScrollArea.displayName = ScrollAreaPrimitive.Root.displayName;

const Viewport = React.forwardRef<
  React.ElementRef<typeof ScrollAreaPrimitive.Viewport>,
  React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.Viewport>
>(({ className, ...props }, ref) => (
  <ScrollAreaPrimitive.Viewport
    ref={ref}
    className={cn(
      "relative w-full h-full overflow-auto rounded-md",
      className
    )}
    {...props}
  />
));
Viewport.displayName = ScrollAreaPrimitive.Viewport.displayName;

const Scrollbar = React.forwardRef<
  React.ElementRef<typeof ScrollAreaPrimitive.Scrollbar>,
  React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.Scrollbar>
>(({ className, ...props }, ref) => (
  <ScrollAreaPrimitive.Scrollbar
    ref={ref}
    className={cn(
      "relative z-10 w-[8px] flex-1",
      className
    )}
    {...props}
  />
));
Scrollbar.displayName = ScrollAreaPrimitive.Scrollbar.displayName;

const Thumb = React.forwardRef<
  React.ElementRef<typeof ScrollAreaPrimitive.Thumb>,
  React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.Thumb>
>(({ className, ...props }, ref) => (
  <ScrollAreaPrimitive.Thumb
    ref={ref}
    className={cn(
      "relative flex-1 bg-background/50 rounded-full",
      "data-[state=active]:bg-background/100",
      className
    )}
    {...props}
  />
));
Thumb.displayName = ScrollAreaPrimitive.Thumb.displayName;

export { ScrollArea, Viewport, Scrollbar, Thumb };