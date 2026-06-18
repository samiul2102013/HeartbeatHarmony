"use client";

import { cn } from "@/lib/utils";
import { clearAdminSession, getAdminAccessToken, getAdminProfile } from "@/lib/index";
import { 
  LayoutDashboard, 
  Settings, 
  Shapes, 
  Smile,
  SlidersHorizontal, 
  Users, 
  CheckCircle, 
  GraduationCap, 
  BookOpen, 
  FileText,
  ClipboardList,
  CircleDollarSign,
  LogOut,
  Menu,
  ChevronDown,
  FileText as FileTextIcon,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Header } from "@/components/dashboard/header";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [headerUser, setHeaderUser] = useState<{ name?: string; image?: string }>({});
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    let mounted = true;
    const token = getAdminAccessToken();
    if (!token) {
      router.push("/signin");
      if (mounted) setIsLoading(false);
      return;
    }
    setIsAuthenticated(true);

    getAdminProfile()
      .then((data) => {
        if (!mounted) return;
        const name = [data?.first_name, data?.last_name].filter(Boolean).join(" ") || data?.institute_name || data?.username || "";
        setHeaderUser({ name, image: data?.avatar || undefined });
      })
      .catch(() => {
        // Silent fail — header will show fallback initials
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => { mounted = false; };
  }, [router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-white">
      <Header user={headerUser} onToggleMobileNav={() => setMobileNavOpen(true)} />
      <div className="flex pt-24">
        <aside className="hidden md:block fixed top-24 left-0 h-[calc(100vh-96px)] w-64 border-r border-gray-100 bg-white">
          <SidebarNav />
        </aside>
        <main className="flex-1 md:ml-64 bg-white min-h-[calc(100vh-96px)]">{children}</main>
      </div>

      <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
        <SheetContent side="left" className="w-72 p-0">
          <SidebarNav onNavigate={() => setMobileNavOpen(false)} />
        </SheetContent>
      </Sheet>
    </div>
  );
}

function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
    const pathname = usePathname();
    const router = useRouter();
    const [contentOpen, setContentOpen] = useState(true);

    const contentItems = [
    { label: "Terms & Conditions", href: "/terms-and-conditions", icon: FileTextIcon },
    { label: "Privacy Policy", href: "/privacy", icon: FileTextIcon },
    { label: "Account Deletion Policy", href: "/account-deletion-policy", icon: FileTextIcon },
];

    const navItems = [
    { label: "Dashboard", href: "/", icon: LayoutDashboard },
    { label: "User management", href: "/users", icon: Users },
    { label: "Check-ins", href: "/check-ins", icon: CheckCircle },
    { label: "Categories", href: "/categories", icon: Shapes },
    { label: "Habits", href: "/habits", icon: CheckCircle },
    { label: "Mood Categories", href: "/mood-categories", icon: Shapes },
    { label: "Mood Scoring", href: "/mood-scoring", icon: Smile },
    { label: "Study Materials", href: "/study-materials", icon: BookOpen },
    { label: "Subject Uploads", href: "/subject-uploads", icon: FileText },
    { label: "Material Under Habit", href: "/habit-materials", icon: BookOpen },
    { label: "Quiz Test", href: "/quiz-test", icon: ClipboardList },
    { label: "Pricing", href: "/pricing", icon: CircleDollarSign },
    { label: "Settings", href: "/settings", icon: Settings },
];

    return (
      <nav className="flex h-full flex-col justify-between p-4">
        <div className="space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            onClick={onNavigate}
                            className={cn(
                                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors text-sm font-medium",
                                isActive 
                                    ? "bg-[#D13D3D] text-white" 
                                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                            )}
                        >
                            <Icon className="h-5 w-5" />
                            {item.label}
                        </Link>
                    );
                })}

                {/* Content dropdown */}
                <div>
                  <button
                    onClick={() => setContentOpen(!contentOpen)}
                    className={cn(
                      "flex items-center justify-between w-full px-3 py-2.5 rounded-xl transition-colors text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                  >
                    <span className="flex items-center gap-3">
                      <FileTextIcon className="h-5 w-5" />
                      Content
                    </span>
                    <ChevronDown className={cn("h-4 w-4 transition-transform", contentOpen && "rotate-180")} />
                  </button>
                  {contentOpen && (
                    <div className="ml-2 mt-0.5 space-y-0.5 border-l-2 border-muted pl-3">
                      {contentItems.map((item) => {
                        const isActive = pathname === item.href;
                        const Icon = item.icon;
                        return (
                          <Link
                            key={item.href}
                            href={item.href}
                            onClick={onNavigate}
                            className={cn(
                              "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm",
                              isActive
                                ? "bg-[#D13D3D] text-white"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                            )}
                          >
                            <Icon className="h-4 w-4" />
                            {item.label}
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
            </div>

            <button
              onClick={() => {
                onNavigate?.();
                clearAdminSession();
                router.push("/signin");
              }}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-[#D13D3D] hover:bg-red-50 transition-colors"
            >
                <LogOut className="h-5 w-5" />
                Logout
            </button>
        </nav>
    );
}
