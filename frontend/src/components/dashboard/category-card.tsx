import Image from "next/image";

type CategoryCardProps = {
    title: string;
    subtitle: string;
    imageUrl: string;
};

export function CategoryCard({ title, subtitle, imageUrl }: CategoryCardProps) {
    return (
        <article className="relative w-full h-52 overflow-hidden rounded-2xl shadow-2xl">
            <Image src={imageUrl} alt={title} fill unoptimized className="object-cover" />

            <div className="absolute inset-x-0 bottom-0 flex flex-col items-center justify-center gap-1 py-2.5 bg-[rgba(51,51,51,0.84)] text-white text-center">
                <h3 className="text-xl font-semibold">{title}</h3>
                <p className="text-sm">{subtitle}</p>
            </div>
        </article>
    );
}
