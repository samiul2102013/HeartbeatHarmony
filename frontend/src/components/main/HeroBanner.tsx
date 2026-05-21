"use client";

import Image from "next/image";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselDots,
} from "../ui/carousel";
import { Button } from "../ui/button";
import { ArrowRightLeft } from "lucide-react";

export default function HeroBanner() {
  const slides = [
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1494526585095-c41746248156?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?q=80&w=1200&auto=format&fit=crop",
  ];

  return (
    <section className="relative min-h-screen sm:min-h-[80vh] overflow-hidden">
      <Carousel className="h-full w-full">
        <CarouselContent>
          {slides.map((img, index) => (
            <CarouselItem key={index}>
              <div className="relative h-screen sm:h-[80vh] w-full">
                {/* Image (REAL image, full cover) */}
                <Image
                  src={img}
                  alt={`Slide ${index + 1}`}
                  fill
                  priority={index === 0} // first image loads fast
                  className="object-cover"
                />
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>

        {/* Dots */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20">
          <CarouselDots />
        </div>
      </Carousel>
      {/* Overlay */}
      <div className="absolute inset-0 bg-primary/40" />

      {/* Content */}
      <div className="absolute inset-0 z-10 h-full flex flex-col justify-center items-center px-6 dark text-foreground">
        <h1 className="text-7xl md:text-8xl text-center font-bold">
          <span className="font-serif italic font-semibold">Omni</span>{" "}
          <span>SEARCH.</span>
        </h1>

        <div className="text-center sm:text-left max-w-164 mx-auto flex flex-col sm:flex-row justify-between items-center gap-6 mt-6">
          <p>
            The world&apos;s most comprehensive library documenting backdrop and
            scenic production design.
          </p>
            <Button>
            Launch Library
            <ArrowRightLeft className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </section>
  );
}
