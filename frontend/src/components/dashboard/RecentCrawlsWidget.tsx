'use client';

import { useEffect, useState } from 'react';
import { RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { crawlingApi } from '@/lib/api';
import { CrawlLog } from '@/types';
import { formatDate, formatDuration } from '@/lib/utils';

export function RecentCrawlsWidget() {
  const [logs, setLogs] = useState<CrawlLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await crawlingApi.getLogs({ page_size: 5 });
        setLogs(data.items || []);
      } catch (error) {
        console.error('Failed to fetch crawl logs:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="success">Success</Badge>;
      case 'failed':
        return <Badge variant="error">Failed</Badge>;
      case 'running':
        return <Badge variant="info">Running</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5" />
          Recent Crawls
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : logs.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">
            No crawl history yet
          </p>
        ) : (
          <div className="space-y-4">
            {logs.map((log) => (
              <div
                key={log.id}
                className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0"
              >
                <div className="flex items-center gap-3">
                  {getStatusIcon(log.status)}
                  <div>
                    <p className="font-medium">{log.company_name || 'All Companies'}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDate(log.started_at)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {log.duration_seconds && (
                    <span className="text-xs text-muted-foreground">
                      {formatDuration(log.duration_seconds)}
                    </span>
                  )}
                  {getStatusBadge(log.status)}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
