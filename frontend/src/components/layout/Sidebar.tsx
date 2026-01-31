"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  CircleDollarSign,
  GitCompare,
  History,
  RefreshCw,
  Bell,
  Settings,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Companies", href: "/companies", icon: Building2 },
  { name: "Prices", href: "/prices", icon: CircleDollarSign },
  { name: "Compare", href: "/prices/compare", icon: GitCompare },
  { name: "History", href: "/prices/history", icon: History },
  { name: "Crawling", href: "/crawling", icon: RefreshCw },
  { name: "Settings", href: "/settings", icon: Settings },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();

  // Find the best matching navigation item
  // 1. Exact match
  // 2. Longest prefix match (for detail pages)
  // 3. Fallback to Dashboard
  const activeItem =
    navigation.find((item) => item.href === pathname) ||
    navigation
      .filter((item) => item.href !== "/" && pathname.startsWith(item.href))
      .sort((a, b) => b.href.length - a.href.length)[0] ||
    navigation.find((item) => item.href === "/");

  return (
    <aside
      className={cn(
        "flex h-full w-64 flex-col border-r bg-background",
        className,
      )}
    >
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/" className="flex items-center gap-2">
          <Zap className="h-6 w-6 text-primary" />
          <span className="font-bold">JPPC</span>
        </Link>
      </div>
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-4">
        {navigation.map((item) => {
          const isActive = activeItem?.href === item.href;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
