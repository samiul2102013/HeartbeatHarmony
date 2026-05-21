import Image from "next/image";
import { ArrowLeft, ArrowRight, Search } from "lucide-react";
import { Button } from "@/components/ui/button";

const heroImage = "https://www.figma.com/api/mcp/asset/e3c61a82-8ae4-4e51-909f-f67a50461826";
const thumbnailImages = [
    "https://www.figma.com/api/mcp/asset/e3c61a82-8ae4-4e51-909f-f67a50461826",
    "https://www.figma.com/api/mcp/asset/34bb3300-1b36-45de-aec0-b4bd63095afa",
    "https://www.figma.com/api/mcp/asset/174ae668-b435-4a75-954e-237ecb1f55ea",
    "https://www.figma.com/api/mcp/asset/cdb504ed-a6cc-4897-95fc-1c8d51c4f66a",
    "https://www.figma.com/api/mcp/asset/9c6c60f8-963a-400c-806e-4b1df4b25d6c",
    "https://www.figma.com/api/mcp/asset/888eee8a-9773-489c-abc7-edd444bf73c7",
];

function SearchField({ label, className = "" }: { label: string; className?: string }) {
    return (
        <Button
            type="button"
            className={`flex w-full items-center justify-between rounded-[20px] border border-border bg-background px-5 py-4 text-base leading-normal text-muted-foreground md:text-xl ${className}`}
        >
            <span className="whitespace-nowrap">{label}</span>
            <Search className="size-6 shrink-0 text-muted-foreground" />
        </Button>
    );
}

function MenuArrowButton({ direction }: { direction: "left" | "right" }) {
    const Icon = direction === "left" ? ArrowLeft : ArrowRight;

    return (
        <Button
            type="button"
            className="flex size-10 items-center justify-center rounded-[20px] bg-[rgba(194,194,194,0.64)] text-primary-foreground"
        >
            <Icon className="size-6" />
        </Button>
    );
}

export default function PhotoGalleryPage() {
    return (
        <main className="bg-muted pb-0">
            <section className="mx-auto w-full max-w-screen-2xl px-4 pt-10 sm:px-6 sm:pt-12 lg:px-8 xl:px-12">
                <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                    <div className="flex w-full flex-col gap-4 sm:flex-row lg:flex-1">
                        <SearchField label="Enter keywords" className="sm:flex-[3]" />
                        <Button
                            type="button"
                            className="flex w-full items-center justify-center rounded-[20px] border border-border bg-background px-9 py-4 text-base leading-normal text-muted-foreground md:text-lg sm:flex-1"
                        >
                            #ID
                        </Button>
                    </div>

                    <Button
                        type="button"
                        className="flex w-full items-center justify-center rounded-[20px] border border-border bg-background px-9 py-4 text-base leading-normal text-muted-foreground md:text-lg lg:w-auto"
                    >
                        Advance Search
                    </Button>
                </div>

                <div className="mt-10 flex flex-col gap-4 px-3 py-3 lg:flex-row lg:items-start lg:justify-between">
                    <h1 className="text-3xl font-bold leading-normal text-foreground sm:text-4xl lg:text-5xl">Photo Gallery</h1>
                    <p className="max-w-prose text-base font-normal leading-normal text-foreground">
                        Lynne Coakley shows off two backings painted by her grandfather, John Harold Coakley
                    </p>
                </div>

                <div className="mt-10 overflow-hidden rounded-[10px]">
                    <div className="relative aspect-[2.1/1] w-full overflow-hidden rounded-[10px]">
                        <Image src={heroImage} alt="Digital Print Area" fill className="object-cover" unoptimized />

                        <div className="absolute left-3 top-1/2 -translate-y-1/2 sm:left-6">
                            <MenuArrowButton direction="left" />
                        </div>
                        <div className="absolute right-3 top-1/2 -translate-y-1/2 sm:right-6">
                            <MenuArrowButton direction="right" />
                        </div>

                        <div className="absolute inset-x-0 bottom-0 bg-[rgba(0,0,0,0.4)] px-3 py-2.5 text-center text-base font-semibold leading-normal text-primary-foreground sm:text-lg">
                            Digital Print Area
                        </div>
                    </div>
                </div>

                <div className="mt-10 grid grid-flow-col auto-cols-[70%] items-center gap-4 overflow-x-auto pb-2 sm:auto-cols-[45%] lg:auto-cols-[22%]">
                    <Button
                        type="button"
                        className="flex w-fit items-center justify-center rounded-[20px] bg-[rgba(194,194,194,0.64)] p-2 text-primary-foreground"
                    >
                        <ArrowLeft className="size-4" />
                    </Button>

                    {thumbnailImages.map((image, index) => (
                        <div key={image} className="relative aspect-[5/4] w-full overflow-hidden rounded-[10px]">
                            <Image src={image} alt={`Gallery thumbnail ${index + 1}`} fill className="object-cover" unoptimized />
                        </div>
                    ))}

                    <Button
                        type="button"
                        className="flex w-fit items-center justify-center rounded-[20px] bg-[rgba(194,194,194,0.64)] p-2 text-primary-foreground"
                    >
                        <ArrowRight className="size-4" />
                    </Button>
                </div>
            </section>
        </main>
    );
}