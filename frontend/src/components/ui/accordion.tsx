"use client"

import { Accordion as AccordionPrimitive } from "@base-ui/react/accordion"
import { ChevronDown, ChevronRight } from "lucide-react"

import { cn } from "@/lib/utils"

function Accordion({ className, ...props }: AccordionPrimitive.Root.Props) {
  return (
    <AccordionPrimitive.Root
      data-slot="accordion"
      className={cn("flex w-full flex-col gap-7.5", className)}
      {...props}
    />
  )
}

function AccordionItem({ className, ...props }: AccordionPrimitive.Item.Props) {
  return (
    <AccordionPrimitive.Item
      data-slot="accordion-item"
      className={cn("rounded-[10px] border border-border px-3 py-3", className)}
      {...props}
    />
  )
}

function AccordionTrigger({
  className,
  children,
  ...props
}: AccordionPrimitive.Trigger.Props) {
  return (
    <AccordionPrimitive.Header className="flex">
      <AccordionPrimitive.Trigger
        data-slot="accordion-trigger"
        className={cn(
          "group/accordion-trigger flex w-full items-center justify-between gap-4 text-left text-[20px] leading-normal font-normal text-foreground outline-none",
          className
        )}
        {...props}
      >
        <span>{children}</span>
        <ChevronRight
          data-slot="accordion-trigger-icon"
          className="pointer-events-none size-6 shrink-0 group-aria-expanded/accordion-trigger:hidden"
          strokeWidth={2}
        />
        <ChevronDown
          data-slot="accordion-trigger-icon"
          className="pointer-events-none hidden size-6 shrink-0 group-aria-expanded/accordion-trigger:inline"
          strokeWidth={2}
        />
      </AccordionPrimitive.Trigger>
    </AccordionPrimitive.Header>
  )
}

function AccordionContent({
  className,
  children,
  ...props
}: AccordionPrimitive.Panel.Props) {
  return (
    <AccordionPrimitive.Panel
      data-slot="accordion-content"
      className="overflow-hidden text-[16px] leading-normal font-normal text-muted-foreground data-open:animate-accordion-down data-closed:animate-accordion-up"
      {...props}
    >
      <div
        className={cn(
          "h-(--accordion-panel-height) pt-2 pb-0 data-ending-style:h-0 data-starting-style:h-0",
          className
        )}
      >
        {children}
      </div>
    </AccordionPrimitive.Panel>
  )
}

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent }
