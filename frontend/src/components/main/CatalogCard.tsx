import { Badge } from "@/components/ui/badge";
import Image from "next/image";

interface CatalogCardProps {
    id: string;
    image: string;
    category: string;
    location: string;
    title: string;
    dimensions: string;
}

export function CatalogCard({ id, image, category, location, title, dimensions }: CatalogCardProps) {
    return (
        <div className="group w-full cursor-pointer">
            <div className="relative mb-4 h-75 w-full overflow-hidden rounded-[30px]">
                <Image src={image} alt={title} width={500} height={300} className="h-full w-full object-cover" />
                <Badge className="absolute left-6 bottom-6 rounded-[16px] bg-background px-3 py-2 text-[20px] font-medium text-foreground hover:bg-background">
                    {id}
                </Badge>
            </div>

            <div className="space-y-0">
                <p className="px-3 py-2 text-sm sm:text-base md:text-lg font-medium leading-normal text-foreground">
                    {category} . {location}
                </p>
                <h3 className="px-3 py-2 text-base sm:text-lg md:text-xl font-semibold leading-normal text-foreground">{title}</h3>
                <p className="px-3 py-2 text-sm sm:text-base md:text-lg font-medium leading-normal text-foreground">{dimensions}</p>
            </div>
        </div>
    );
}
