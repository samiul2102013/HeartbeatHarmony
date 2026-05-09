"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Search, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { NativeSelect } from "@/components/ui/native-select";

export interface CatalogItem {
    id: string;
    title: string;
    dimensions: string;
    imageUrl: string;
}

export interface CategoryFilterOption {
    key: string;
    label: string;
    href: string;
}

interface CategoryPageProps {
    title: string;
    items: CatalogItem[];
    currentPage?: number;
    totalPages?: number;
    pageBasePath?: string;
    currentCategoryKey: string;
    categoryOptions: CategoryFilterOption[];
    itemHrefBasePath?: string;
    itemsPerPage?: number;
}

export default function CatelogPage({
    title,
    items,
    currentPage = 1,
    totalPages,
    pageBasePath,
    currentCategoryKey,
    categoryOptions,
    itemHrefBasePath = "/single-details",
    itemsPerPage = 6,
}: CategoryPageProps) {
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();

    const pageParam = Number(searchParams.get("page"));
    const safeCurrentPage = Number.isFinite(pageParam) && pageParam > 0 ? pageParam : currentPage;
    const computedTotalPages = Math.max(1, Math.ceil(items.length / itemsPerPage));
    const effectiveTotalPages = totalPages ? Math.max(1, totalPages) : computedTotalPages;
    const clampedCurrentPage = Math.min(Math.max(1, safeCurrentPage), effectiveTotalPages);

    const startIndex = (clampedCurrentPage - 1) * itemsPerPage;
    const visibleItems = items.slice(startIndex, startIndex + itemsPerPage);
    const paginationItems = Array.from({ length: effectiveTotalPages }, (_, i) => i + 1);

    const basePath = pageBasePath ?? pathname;
    const buildPageHref = (page: number) => (page === 1 ? basePath : `${basePath}?page=${page}`);

    return (
        <main className="bg-muted pb-20">
            {/* Search & Filter Section */}
            <section className="mx-auto mt-6 sm:mt-8 lg:mt-9 w-full max-w-screen-2xl px-4 sm:px-6 lg:px-8 xl:px-12">
                <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                    <div className="flex flex-wrap gap-5">
                        <div className="flex h-auto md:h-12 lg:h-auto min-w-0 flex-1 items-center justify-between rounded-[20px] border border-border bg-background px-4 sm:px-5 py-3 sm:py-4 text-base sm:text-lg md:text-lg text-muted-foreground lg:max-w-xs">
                            <span className="truncate">Enter keywords</span>
                            <Search className="size-5 sm:size-6 lg:size-7 shrink-0 text-muted-foreground" />
                        </div>
                        <Button
                            type="button"
                            className="flex h-auto md:h-12 lg:h-auto items-center justify-center rounded-[20px] border border-border bg-background px-3 sm:px-6 lg:px-9 py-3 sm:py-4 text-sm sm:text-base md:text-lg font-normal leading-normal text-muted-foreground transition-colors hover:bg-muted"
                        >
                            #ID
                        </Button>
                    </div>

                    <div className="flex flex-wrap gap-5">
                        <Button
                            type="button"
                            className="inline-flex h-auto md:h-12 lg:h-auto items-center justify-center rounded-[20px] border border-border bg-background px-3 sm:px-6 lg:px-9 py-3 sm:py-4 text-sm sm:text-base md:text-lg font-normal leading-normal text-muted-foreground transition-colors hover:bg-muted"
                        >
                            Advance Search
                        </Button>
                        <Button
                            type="button"
                            className="inline-flex h-auto md:h-12 lg:h-auto items-center gap-2 rounded-[20px] border border-border bg-background px-3 sm:px-6 lg:px-9 py-3 sm:py-4 text-sm sm:text-base md:text-lg font-normal leading-normal text-muted-foreground transition-colors hover:bg-muted"
                        >
                            Filters
                            <Filter className="size-5 sm:size-6 lg:size-7" />
                        </Button>
                    </div>
                </div>
            </section>

            {/* Title & Select Category */}
            <section className="mx-auto mt-6 sm:mt-8 lg:mt-10 flex w-full max-w-screen-2xl items-center justify-between px-4 sm:px-6 lg:px-8 xl:px-12 flex-col sm:flex-row gap-4 sm:gap-6">
                <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold leading-normal text-foreground">{title}</h1>
                <NativeSelect
                    value={currentCategoryKey}
                    onChange={(event) => {
                        const selectedHref = categoryOptions.find((option) => option.key === event.target.value)?.href;
                        if (selectedHref && selectedHref !== pathname) {
                            router.push(selectedHref);
                        }
                    }}
                    containerClassName="w-full sm:w-auto"
                    className="h-auto min-w-44 rounded-[5px] border border-border bg-background px-3 py-2 sm:py-3 text-sm sm:text-base md:text-lg font-medium leading-normal text-foreground"
                    iconClassName="size-4 sm:size-5"
                    aria-label="Select catalog category"
                >
                    {categoryOptions.map((option) => (
                        <option key={option.key} value={option.key}>
                            {option.label}
                        </option>
                    ))}
                </NativeSelect>
            </section>

            {/* Grid of Catalog Items */}
            <section className="mx-auto mt-8 sm:mt-10 lg:mt-10 w-full max-w-screen-2xl px-4 sm:px-6 lg:px-8 xl:px-12">
                <div className="grid gap-4 sm:gap-6 md:grid-cols-2 lg:gap-8 lg:grid-cols-3">
                    {visibleItems.map((item) => (
                        <Link
                            key={item.id}
                            href={itemHrefBasePath}
                            className="group flex flex-col gap-4 transition-opacity hover:opacity-80"
                        >
                            {/* Image Container */}
                            <div className="relative aspect-91.5/81 w-full overflow-hidden rounded-[30px] bg-gray-200">
                                <Image src={item.imageUrl} alt={item.title} fill unoptimized className="absolute inset-0 object-cover" />
                                {/* ID Badge */}
                                <div className="absolute bottom-5 sm:bottom-6 left-5 sm:left-6 flex h-6 sm:h-7 lg:h-8 items-center justify-center rounded-[16px] bg-background px-2 sm:px-3 py-1.5 sm:py-2">
                                    <span className="font-medium text-foreground text-sm sm:text-base md:text-lg whitespace-nowrap">
                                        {item.id}
                                    </span>
                                </div>
                            </div>

                            {/* Item Info */}
                            <div className="space-y-1 sm:space-y-2 px-2 sm:px-3 py-1 sm:py-2">
                                <h3 className="text-base sm:text-lg md:text-xl font-semibold leading-normal text-foreground">
                                    {item.title}
                                </h3>
                                <p className="text-sm sm:text-base md:text-lg font-medium leading-normal text-foreground">
                                    {item.dimensions}
                                </p>
                            </div>
                        </Link>
                    ))}
                </div>
            </section>

            {/* Pagination */}
            <section className="mx-auto mt-10 sm:mt-12 lg:mt-15 w-full max-w-screen-2xl px-4 sm:px-6 lg:px-8 xl:px-12">
                <div className="flex items-center justify-center gap-1">
                    {clampedCurrentPage > 1 ? (
                        <Link
                            href={buildPageHref(clampedCurrentPage - 1)}
                            className="rounded-md bg-transparent px-3 py-2 text-sm sm:text-base md:text-lg font-normal leading-normal text-foreground transition-colors hover:bg-muted"
                        >
                            Previous
                        </Link>
                    ) : (
                        <Button
                            type="button"
                            disabled
                            className="rounded-md bg-transparent px-3 py-2 text-sm sm:text-base md:text-lg font-normal leading-normal text-muted-foreground"
                        >
                            Previous
                        </Button>
                    )}

                    {paginationItems.map((page) => (
                        <Link
                            key={page}
                            href={buildPageHref(page)}
                            className={`min-w-9 sm:min-w-10 rounded-md px-3 py-2 text-sm sm:text-base md:text-lg font-normal leading-normal transition-colors ${
                                page === clampedCurrentPage ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
                            }`}
                        >
                            {page}
                        </Link>
                    ))}

                    {clampedCurrentPage < effectiveTotalPages ? (
                        <Link
                            href={buildPageHref(clampedCurrentPage + 1)}
                            className="rounded-md bg-transparent px-3 py-2 text-sm sm:text-base md:text-lg font-normal leading-normal text-foreground transition-colors hover:bg-muted"
                        >
                            Next
                        </Link>
                    ) : (
                        <Button
                            type="button"
                            disabled
                            className="rounded-md bg-transparent px-3 py-2 text-sm sm:text-base md:text-lg font-normal leading-normal text-muted-foreground"
                        >
                            Next
                        </Button>
                    )}
                </div>
            </section>
        </main>
    );
}
