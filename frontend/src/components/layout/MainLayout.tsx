'use client';

import { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { cn } from '@/lib/utils';

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <Header
        onMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        isMenuOpen={isMobileMenuOpen}
      />

      {/* Mobile sidebar overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/50 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar - hidden on mobile unless menu is open */}
      <div
        className={cn(
          'fixed left-0 top-16 z-30 h-[calc(100vh-4rem)] w-64 transform border-r bg-background transition-transform md:translate-x-0',
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <Sidebar />
      </div>

      {/* Main content */}
      <main className="min-h-[calc(100vh-4rem)] md:ml-64">
        <div className="container mx-auto p-4 md:p-6">{children}</div>
      </main>
    </div>
  );
}
