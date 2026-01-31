"use client";

import { useState } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { cn } from "@/lib/utils";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop Sidebar */}
      <Sidebar className="hidden md:flex" />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header
          onMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          isMenuOpen={isMobileMenuOpen}
        />

        {/* Mobile sidebar overlay */}
        {isMobileMenuOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/50 md:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}

        {/* Mobile Sidebar (Drawer) */}
        <div
          className={cn(
            "fixed inset-y-0 left-0 z-50 w-64 transform border-r bg-background transition-transform md:hidden",
            isMobileMenuOpen ? "translate-x-0" : "-translate-x-full",
          )}
        >
          {/* Mobile Sidebar needs its own Logo since Desktop sidebar is hidden */}
          {/* Use same Sidebar content but we need to duplicate logic or make Sidebar accept props?
               Actually the Sidebar component we edited above is 'hidden md:flex'.
               So we need to make Sidebar component flexible or import it differently. 
               Let's just re-use the Sidebar component but override className?
               Sidebar component has 'hidden ... md:flex' baked in.
               
               Correction: I should modify Sidebar.tsx to accept className prop or NOT have 'hidden md:flex' by default if I want to reuse it.
               
               Let's update Sidebar.tsx AGAIN to make it reusable first.
               Actually, I can wrap it in MainLayout.
           */}
          {/* For now let's just make the Desktop Sidebar visible on md and up. 
               For mobile, I will render the Sidebar component but I need to force it to show.
               
               Wait, let's step back. Sidebar.tsx has 'hidden md:flex'.
               If I render <Sidebar /> here for mobile, it will be double hidden if I don't override the class.
           */}
          <Sidebar className="flex w-full" />
        </div>

        {/* Scrollable Page Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="container mx-auto max-w-7xl">{children}</div>
        </main>
      </div>
    </div>
  );
}
