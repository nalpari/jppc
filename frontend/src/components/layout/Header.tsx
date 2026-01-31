'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Zap, RefreshCw, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface HeaderProps {
  onMenuToggle?: () => void;
  isMenuOpen?: boolean;
}

export function Header({ onMenuToggle, isMenuOpen }: HeaderProps) {
  const [isCrawling, setIsCrawling] = useState(false);

  const handleManualCrawl = async () => {
    setIsCrawling(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/crawling/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) throw new Error('Crawl failed');
    } catch (error) {
      console.error('Crawl error:', error);
    } finally {
      setTimeout(() => setIsCrawling(false), 2000);
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-4 md:px-6">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          className="mr-2 md:hidden"
          onClick={onMenuToggle}
        >
          {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <Zap className="h-6 w-6 text-yellow-500" />
          <span className="hidden font-bold sm:inline-block">
            Japan Power Price Crawler
          </span>
          <span className="font-bold sm:hidden">JPPC</span>
        </Link>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Status badges */}
        <div className="hidden items-center gap-2 md:flex">
          <Badge variant="success" className="gap-1">
            <span className="h-2 w-2 rounded-full bg-green-500" />
            System OK
          </Badge>
        </div>

        {/* Manual crawl button */}
        <Button
          variant="outline"
          size="sm"
          className="ml-4 gap-2"
          onClick={handleManualCrawl}
          disabled={isCrawling}
        >
          <RefreshCw className={cn('h-4 w-4', isCrawling && 'animate-spin')} />
          <span className="hidden sm:inline">
            {isCrawling ? 'Crawling...' : 'Crawl Now'}
          </span>
        </Button>
      </div>
    </header>
  );
}
