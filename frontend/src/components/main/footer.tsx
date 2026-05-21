import Image from "next/image";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="dark bg-background text-foreground w-full">
      {/* Inner container */}
      <div className="mx-auto w-full max-w-screen-2xl px-4 py-10 sm:px-6 lg:px-12 flex flex-col gap-10">
        {/* Top */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="flex flex-col gap-5">
            <Image src="/hartwellness.png" alt="Hart Wellness Logo" width={202} height={32} />
            <p className="text-muted-foreground">
              The definitive platform for cinematic asset discovery and
              production design.
            </p>
          </div>

          {/* Platform */}
          <div className="flex flex-col">
            <h3 className="p-3 text-xl font-medium">Platform</h3>
            <div className="flex flex-col gap-4 px-3 py-2">
              <Link href="/catalog/catalog-drop-down">All Catalog</Link>
              <Link href="/catalog/all">View Catalog</Link>
              <Link href="/photography">Photography</Link>
              <Link href="/media/drop-shop-photo-shoots">Drop Shop Photo Shoots</Link>
            </div>
          </div>

          {/* Company */}
          <div className="flex flex-col">
            <h3 className="p-3 text-xl font-medium">Company</h3>
            <div className="flex flex-col gap-4 px-3 py-2">
              <Link href="/about">About Us</Link>
              <Link href="//general-information">General Information</Link>
              <Link href="/image-license-and-agreement">Image License and Agreement</Link>
              <Link href="/contact">Contact Us</Link>
            </div>
          </div>

          {/* Support */}
          <div className="flex flex-col">
            <h3 className="p-3 text-xl font-medium">Support</h3>
            <div className="flex flex-col gap-4 px-3 py-2">
              <Link href="/shipping">Shipping</Link>
              <Link href="/privacy-policy">Privacy Policy</Link>
              <Link href="/faq">FAQ</Link>
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="flex flex-col gap-4 border-t border-border pt-6 md:flex-row md:items-center md:justify-between">
          <p>© 2026 OmniSearch. All rights reserved.</p>
          <div className="flex flex-wrap items-center gap-4 md:gap-6">
            <Link href="/terms-and-conditions">Terms & Conditions</Link>
            <Link href="/privacy-policy">Privacy</Link>
            <Link href="/cookies">Cookies</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
