"use client";

import { Button, buttonVariants } from "@/components/ui/button";
import {
    NavigationMenu,
    NavigationMenuContent,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import { Login01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import Image from "next/image";
import Link from "next/link";
import MobileDropdown from "./Navigation/mobileDropdown";

export default function Navbar() {
    return (
        <nav className="absolute inset-x-0 top-0 z-50 dark">
            <div className="mx-auto flex w-full max-w-screen-2xl items-center justify-between gap-3 px-4 py-4 sm:px-6 lg:px-12">

                {/* Mobile menu button */}
                <div className="lg:hidden bg-white rounded-3xl p-0.5">
                    <MobileDropdown />
                </div>

                {/* Logo */}
                <Link href="/">
                    <Image
                        src="/hartwellness.png"
                        alt="Hart Wellness Logo"
                        width={200}
                        height={40}
                        style={{ width: "auto", height: "auto" }}
                    />
                </Link>

                <NavigationMenu className="hidden lg:flex">
                    <NavigationMenuList>
                        <NavigationMenuItem>
                            <NavigationMenuLink render={<Link href="/">Home</Link>} />
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuTrigger>Catalog</NavigationMenuTrigger>
                            <NavigationMenuContent className="divide-y">
                                <NavigationMenuLink render={<Link href="/catalog/catalog-drop-down">Day to Night Translight Rental Drops</Link>} />
                                <NavigationMenuLink render={<Link href="/catalog/all">All Catalogs</Link>} />
                                <NavigationMenuLink render={<Link href="/catalog/01">Architecture Large City</Link>} />
                                <NavigationMenuLink render={<Link href="/catalog/02">Architecture International</Link>} />
                            </NavigationMenuContent>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuTrigger>Photography</NavigationMenuTrigger>
                            <NavigationMenuContent className="divide-y">
                                <NavigationMenuLink render={<Link href="/photography">Custom Build Day to Night Translight</Link>} />
                                <NavigationMenuLink render={<Link href="/photography">Custom Photography</Link>} />
                            </NavigationMenuContent>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuTrigger>Media</NavigationMenuTrigger>
                            <NavigationMenuContent className="divide-y">
                                <NavigationMenuLink render={<Link href="/media/drop-shop-photo-shoots">Drop Shop Photo Shoots</Link>} />
                            </NavigationMenuContent>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuTrigger>About</NavigationMenuTrigger>
                            <NavigationMenuContent className="divide-y">
                                <NavigationMenuLink render={<Link href="/general-information">General Information</Link>} />
                                <NavigationMenuLink render={<Link href="/image-license-and-agreement">Image License Agreement</Link>} />
                                <NavigationMenuLink render={<Link href="/privacy-policy">Privacy Policy</Link>} />
                                <NavigationMenuLink render={<Link href="/terms-and-conditions">Terms and Conditions</Link>} />
                            </NavigationMenuContent>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuLink render={<Link href="/contact">Contact</Link>} />
                        </NavigationMenuItem>
                    </NavigationMenuList>
                </NavigationMenu>

                <div className="flex items-center gap-2 sm:gap-3">
                    <Link href="/search" className="hidden sm:block">
                        <Button>Advance Search</Button>
                    </Link>
                    <Link href="/signin" className={buttonVariants({ size: "icon" })}>
                        <HugeiconsIcon icon={Login01Icon} />
                    </Link>
                </div>
            </div>
        </nav>
    );
}