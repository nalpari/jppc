'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Building2, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { companiesApi } from '@/lib/api';
import { Company } from '@/types';

export function CompaniesWidget() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const data = await companiesApi.list({ page_size: 10 });
        setCompanies(data.items || []);
      } catch (error) {
        console.error('Failed to fetch companies:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchCompanies();
  }, []);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5" />
          Power Companies
        </CardTitle>
        <Link href="/companies">
          <Button variant="ghost" size="sm">
            View All
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : companies.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">No companies registered</p>
            <Link href="/companies">
              <Button size="sm">Add Company</Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {companies.map((company) => (
              <div
                key={company.id}
                className="flex items-center justify-between p-3 rounded-lg border"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <Building2 className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">{company.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {company.region} • {company.plans_count || 0} plans
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {company.is_active ? (
                    <Badge variant="success" className="gap-1">
                      <CheckCircle className="h-3 w-3" />
                      Active
                    </Badge>
                  ) : (
                    <Badge variant="warning" className="gap-1">
                      <AlertCircle className="h-3 w-3" />
                      Inactive
                    </Badge>
                  )}
                  {company.website_url && (
                    <a
                      href={company.website_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground hover:text-foreground"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
