"use client";

import { useRouter } from "next/navigation";
import Image from "next/image";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { clearAdminSession } from "@/lib/index";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type HeaderUser = {
  name?: string;
  image?: string;
};

type HeaderProps = {
  user?: HeaderUser;
};

export function Header({ user }: HeaderProps) {
  const router = useRouter();

  const handleLogout = () => {
    clearAdminSession();
    router.push("/signin");
  };

  const displayName = user?.name ?? "Rumi Aktar";

  return (
    <header className="fixed top-0 left-0 right-0 z-40 bg-white border-b border-gray-100 shadow-sm">
      <div className="flex items-center justify-between h-24 px-6">

        {/* Logo */}
        <div className="flex items-center w-64">
          <Image
            src="/hartwellness.png"
            alt="Hart Wellness Logo"
            width={280}
            height={80}
            priority
            style={{ width: "auto", height: "80px" }}
            className="object-contain"
          />
        </div>

        {/* Profile */}
        <DropdownMenu>
          <DropdownMenuTrigger className="flex items-center gap-4 cursor-pointer focus:outline-none pr-4">
            <div className="text-right hidden sm:block">
              <span className="text-xl font-bold text-gray-900 block leading-tight">
                {displayName}
              </span>
            </div>
            <Avatar className="h-14 w-14 border-2 border-white shadow-md">
              <AvatarImage
                src={user?.image ?? "/profile.png"}
                alt={displayName}
              />
              <AvatarFallback className="bg-gray-100 text-sm font-medium text-gray-600">
                {displayName.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end" className="w-44 rounded-lg">
            <DropdownMenuItem
              className="text-sm cursor-pointer"
              onClick={() => router.push("/settings")}
            >
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-sm cursor-pointer"
              onClick={() => router.push("/settings")}
            >
              Settings
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-sm cursor-pointer text-destructive focus:text-destructive"
              onClick={handleLogout}
            >
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

      </div>
    </header>
  );
}