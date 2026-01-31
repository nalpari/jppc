'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Building2, CircleDollarSign, RefreshCw, TrendingUp } from 'lucide-react';
import { statsApi } from '@/lib/api';
import { DashboardStats } from '@/types';
import { formatDate } from '@/lib/utils';
import { StatsCard, RecentCrawlsWidget, CompaniesWidget } from '@/components/dashboard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await statsApi.getDashboard();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load stats');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent className="pt-6">
          <p className="text-center text-destructive">Error: {error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <Link href="/crawling">
          <Button>
            <RefreshCw className="mr-2 h-4 w-4" />
            Start Crawling
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Active Companies"
          value={stats.companies.active}
          description={`${stats.companies.total} total registered`}
          icon={Building2}
        />
        <StatsCard
          title="Current Plans"
          value={stats.price_plans.current}
          description={`${stats.price_plans.total} total plans tracked`}
          icon={CircleDollarSign}
        />
        <StatsCard
          title="Success Rate"
          value={`${stats.crawling.success_rate}%`}
          description={`${stats.crawling.successful}/${stats.crawling.total} crawls`}
          icon={TrendingUp}
        />
        <StatsCard
          title="Recent Crawls"
          value={stats.crawling.recent_7days}
          description={`Last: ${formatDate(stats.crawling.last_crawl_at) || 'Never'}`}
          icon={RefreshCw}
        />
      </div>

      {/* Widgets Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        <RecentCrawlsWidget />
        <CompaniesWidget />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Link href="/crawling">
            <Button variant="default">
              <RefreshCw className="mr-2 h-4 w-4" />
              Start Crawling
            </Button>
          </Link>
          <Link href="/companies">
            <Button variant="outline">
              <Building2 className="mr-2 h-4 w-4" />
              Manage Companies
            </Button>
          </Link>
          <Link href="/prices/compare">
            <Button variant="outline">
              <CircleDollarSign className="mr-2 h-4 w-4" />
              Compare Prices
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
