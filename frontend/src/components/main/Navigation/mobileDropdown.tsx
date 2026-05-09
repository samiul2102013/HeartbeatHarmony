"use client";

import { buttonVariants } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuGroup,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSub,
    DropdownMenuSubTrigger,
    DropdownMenuSubContent,
    DropdownMenuPortal,
} from "@/components/ui/dropdown-menu";
import { Menu } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils"; // if you have it, otherwise remove cn

export default function MobileDropdown() {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger 
                className={cn(
                    buttonVariants({ size: "icon", variant: "ghost" }),
                    "lg:hidden"
                )}
            >
                <Menu className="size-5" />
            </DropdownMenuTrigger>
            
            <DropdownMenuContent 
                align="start" 
                className="w-72 bg-white rounded-2xl shadow-lg border border-gray-100 p-1"
            >
                <DropdownMenuGroup>
                    <DropdownMenuLabel className="px-2 py-1.5 text-sm font-semibold">
                        Navigation
                    </DropdownMenuLabel>
                </DropdownMenuGroup>
                <DropdownMenuSeparator className="my-1" />

                {/* Home - direct link */}
                <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                    <Link href="/" className="w-full">Home</Link>
                </DropdownMenuItem>

                {/* Catalog submenu */}
                <DropdownMenuSub>
                    <DropdownMenuSubTrigger className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                        Catalog
                    </DropdownMenuSubTrigger>
                    <DropdownMenuPortal>
                        <DropdownMenuSubContent className="w-72 bg-white rounded-2xl shadow-lg border border-gray-100 p-1 ml-2">
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/catalog/catalog-drop-down" className="w-full">Day to Night Translight Rental Drops</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/catalog/all" className="w-full">All Catalogs</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/catalog/01" className="w-full">Architecture Large City</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/catalog/02" className="w-full">Architecture International</Link>
                            </DropdownMenuItem>
                        </DropdownMenuSubContent>
                    </DropdownMenuPortal>
                </DropdownMenuSub>

                {/* Photography submenu */}
                <DropdownMenuSub>
                    <DropdownMenuSubTrigger className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                        Photography
                    </DropdownMenuSubTrigger>
                    <DropdownMenuPortal>
                        <DropdownMenuSubContent className="w-72 bg-white rounded-2xl shadow-lg border border-gray-100 p-1 ml-2">
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/photography" className="w-full">Custom Build Day to Night Translight</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/photography" className="w-full">Custom Photography</Link>
                            </DropdownMenuItem>
                        </DropdownMenuSubContent>
                    </DropdownMenuPortal>
                </DropdownMenuSub>

                {/* Media submenu */}
                <DropdownMenuSub>
                    <DropdownMenuSubTrigger className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                        Media
                    </DropdownMenuSubTrigger>
                    <DropdownMenuPortal>
                        <DropdownMenuSubContent className="w-72 bg-white rounded-2xl shadow-lg border border-gray-100 p-1 ml-2">
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/media/drop-shop-photo-shoots" className="w-full">Drop Shop Photo Shoots</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/media/photo-gallery" className="w-full">Photo Gallery</Link>
                            </DropdownMenuItem>
                        </DropdownMenuSubContent>
                    </DropdownMenuPortal>
                </DropdownMenuSub>

                {/* About submenu */}
                <DropdownMenuSub>
                    <DropdownMenuSubTrigger className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                        About
                    </DropdownMenuSubTrigger>
                    <DropdownMenuPortal>
                        <DropdownMenuSubContent className="w-72 bg-white rounded-2xl shadow-lg border border-gray-100 p-1 ml-2">
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/general-information" className="w-full">General Information</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/image-license-and-agreement" className="w-full">Image License Agreement</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/privacy-policy" className="w-full">Privacy Policy</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                                <Link href="/terms-and-conditions" className="w-full">Terms and Conditions</Link>
                            </DropdownMenuItem>
                        </DropdownMenuSubContent>
                    </DropdownMenuPortal>
                </DropdownMenuSub>

                <DropdownMenuSeparator className="my-1" />

                {/* Contact - direct link */}
                <DropdownMenuItem className="rounded-xl hover:bg-gray-50 cursor-pointer px-2 py-2 text-sm">
                    <Link href="/contact" className="w-full">Contact</Link>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}