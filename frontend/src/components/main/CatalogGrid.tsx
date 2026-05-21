import { CatalogCard } from "./CatalogCard";
import { Button } from "@/components/ui/button";

export interface CatalogItem {
    id: string;
    image: string;
    category: string;
    location: string;
    title: string;
    dimensions: string;
}

const defaultCatalogItems: CatalogItem[] = [
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
    {
        id: "#34567",
        image: "/dummy1.jpg",
        category: "Landscape",
        location: "Stamford",
        title: "Alpine Mountain Range",
        dimensions: "80'x 40'",
    },
];

interface CatalogGridProps {
    title?: string;
    items?: CatalogItem[];
    showPagination?: boolean;
}

export function CatalogGrid({ title = "The Catalog", items = defaultCatalogItems, showPagination = false }: CatalogGridProps) {
    return (
        <div className="w-full max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 xl:px-12 py-0">
            <h1 className="mb-8 sm:mb-12 lg:mb-17 px-3 py-2 text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold leading-normal text-foreground">{title}</h1>

            <div className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 lg:gap-8 xl:grid-cols-3">
                {items.map((item, index) => (
                    <CatalogCard key={index} {...item} />
                ))}
            </div>

            {showPagination ? (
                <div className="mt-17.5 flex items-center justify-center text-[24px] leading-normal text-foreground">
                    <Button type="button" className="bg-transparent px-3 py-2 text-foreground hover:bg-transparent">
                        Previous
                    </Button>
                    <Button type="button" className="bg-primary px-3 py-2 text-[#F5F5F5] hover:bg-primary">
                        1
                    </Button>
                    <Button type="button" className="bg-transparent px-3 py-2 text-foreground hover:bg-transparent">
                        2
                    </Button>
                    <Button type="button" className="bg-transparent px-3 py-2 text-foreground hover:bg-transparent">
                        3
                    </Button>
                    <Button type="button" className="bg-transparent px-3 py-2 text-foreground hover:bg-transparent">
                        4
                    </Button>
                    <Button type="button" className="bg-transparent px-3 py-2 text-foreground hover:bg-transparent">
                        5
                    </Button>
                    <Button type="button" className="bg-transparent px-3 py-2 text-foreground hover:bg-transparent">
                        6
                    </Button>
                    <Button type="button" className="bg-transparent px-3 py-2 text-foreground hover:bg-transparent">
                        7
                    </Button>
                    <Button type="button" className="bg-transparent px-3 py-2 text-foreground hover:bg-transparent">
                        Next
                    </Button>
                </div>
            ) : null}
        </div>
    );
}
