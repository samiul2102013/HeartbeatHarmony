import Image from "next/image";

type MediaLibraryCardProps = {
    title: string;
    tags: string;
    imageUrl: string;
    prioritizeImage?: boolean;
};

export function MediaLibraryCard({ title, tags, imageUrl, prioritizeImage = false }: MediaLibraryCardProps) {
    return (
        <article className="w-full h-75 overflow-hidden rounded-2xl shadow-2xl flex flex-col">
            <div className="flex-1 relative w-full">
                <Image src={imageUrl} alt={title} fill unoptimized loading={prioritizeImage ? "eager" : "lazy"} className="object-cover" />
            </div>

            <div className="space-y-1 p-4 pt-2.5">
                <h3 className="text-xl font-medium text-foreground">{title}</h3>
                <p className="px-2 py-1 w-max rounded text-sm bg-muted text-foreground">{tags}</p>
            </div>
        </article>
    );
}
