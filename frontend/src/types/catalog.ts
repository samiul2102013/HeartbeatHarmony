export interface CatalogItem {
    id: string;
    image: string;
    category: string;
    location: string;
    title: string;
    dimensions: string;
}


export interface CatalogGridProps {
    title?: string;
    items?: CatalogItem[];
    showPagination?: boolean;
}
