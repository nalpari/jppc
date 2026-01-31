import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { MainLayout } from '@/components/layout';
import { QueryProvider } from '@/components/providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'JPPC - Japan Power Price Crawler',
  description: '일본 주요 전력회사 요금 정보 자동 수집 시스템',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={inter.className}>
        <QueryProvider>
          <MainLayout>{children}</MainLayout>
        </QueryProvider>
      </body>
    </html>
  );
}
