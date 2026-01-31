"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Building2,
  ArrowLeft,
  ExternalLink,
  Edit,
  Globe,
  MapPin,
  Calendar,
  FileText,
  TrendingUp,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import { LoadingPage, Skeleton } from "@/components/ui/loading";
import { CompanyForm } from "@/components/companies";
import { useCompany, useCompanyStats } from "@/hooks/useCompanies";
import { usePrices } from "@/hooks/usePrices";
import { useCrawlLogs } from "@/hooks/useCrawling";
import { Company } from "@/types";

interface PageProps {
  params: { id: string };
}

export default function CompanyDetailPage({ params }: PageProps) {
  const companyId = parseInt(params.id, 10);
  const [isFormOpen, setIsFormOpen] = useState(false);

  const { data: company, isLoading: companyLoading, error: companyError } = useCompany(companyId);
  const { data: stats, isLoading: statsLoading } = useCompanyStats(companyId);
  const { data: pricesData, isLoading: pricesLoading } = usePrices({
    company_id: companyId,
    is_current: true,
    page_size: 10,
  });
  const { data: logsData, isLoading: logsLoading } = useCrawlLogs({
    company_id: companyId,
    page_size: 5,
  });

  if (companyLoading) {
    return <LoadingPage />;
  }

  if (companyError || !company) {
    return (
      <div className="space-y-6">
        <Link href="/companies">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Companies
          </Button>
        </Link>
        <Card>
          <CardContent className="py-8">
            <div className="text-center text-destructive">
              Company not found or failed to load.
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatPrice = (price: number | null) => {
    if (price === null) return "-";
    return `¥${price.toLocaleString()}`;
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link href="/companies">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Companies
        </Button>
      </Link>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-primary/10">
            <Building2 className="h-8 w-8 text-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold">{company.name_en}</h1>
              <Badge variant={company.is_active ? "default" : "secondary"}>
                {company.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
            <p className="text-lg text-muted-foreground">{company.name_ja}</p>
            {company.name_ko && (
              <p className="text-sm text-muted-foreground">{company.name_ko}</p>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <a href={company.website_url} target="_blank" rel="noopener noreferrer">
            <Button variant="outline">
              <ExternalLink className="h-4 w-4 mr-2" />
              Website
            </Button>
          </a>
          <Button onClick={() => setIsFormOpen(true)}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Current Plans
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? <Skeleton className="h-8 w-12" /> : stats?.current_plans || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Total Crawls
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? <Skeleton className="h-8 w-12" /> : stats?.total_crawls || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Success Rate
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                `${stats?.success_rate?.toFixed(1) || 0}%`
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Last Crawl
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-medium">
              {statsLoading ? (
                <Skeleton className="h-6 w-24" />
              ) : stats?.last_crawl_at ? (
                formatDate(stats.last_crawl_at)
              ) : (
                "Never"
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Company Info */}
        <Card>
          <CardHeader>
            <CardTitle>Company Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Code:</span>
              <span className="font-mono">{company.code}</span>
            </div>

            {company.region && (
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Region:</span>
                <span>{company.region}</span>
              </div>
            )}

            <div className="flex items-start gap-2">
              <ExternalLink className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                <span className="text-sm text-muted-foreground">Price Page:</span>
                <a
                  href={company.price_page_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-sm text-primary hover:underline truncate max-w-md"
                >
                  {company.price_page_url}
                </a>
              </div>
            </div>

            {company.description && (
              <div>
                <span className="text-sm text-muted-foreground">Description:</span>
                <p className="mt-1 text-sm">{company.description}</p>
              </div>
            )}

            <div className="pt-2 border-t text-sm text-muted-foreground">
              <div>Created: {formatDate(company.created_at)}</div>
              <div>Updated: {formatDate(company.updated_at)}</div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Crawls */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Crawl Logs</CardTitle>
          </CardHeader>
          <CardContent>
            {logsLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : logsData?.items.length === 0 ? (
              <p className="text-sm text-muted-foreground">No crawl logs yet.</p>
            ) : (
              <div className="space-y-2">
                {logsData?.items.map((log) => (
                  <div
                    key={log.id}
                    className="flex items-center justify-between p-2 rounded border"
                  >
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={
                          log.status === "success"
                            ? "default"
                            : log.status === "failed"
                            ? "destructive"
                            : "secondary"
                        }
                      >
                        {log.status}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {formatDate(log.started_at)}
                      </span>
                    </div>
                    <span className="text-sm">
                      {log.plans_found} plans found
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Current Price Plans */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Current Price Plans</CardTitle>
            <Link href={`/prices?company_id=${company.id}`}>
              <Button variant="outline" size="sm">
                View All Plans
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {pricesLoading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : pricesData?.items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No price plans available.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Plan Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Base Charge</TableHead>
                  <TableHead className="text-right">Unit Price</TableHead>
                  <TableHead>Effective Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pricesData?.items.map((plan) => (
                  <TableRow key={plan.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{plan.plan_name_ja}</div>
                        {plan.plan_name_en && (
                          <div className="text-sm text-muted-foreground">
                            {plan.plan_name_en}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{plan.plan_type}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {formatPrice(plan.base_charge)}
                    </TableCell>
                    <TableCell className="text-right">
                      {plan.unit_price ? `¥${plan.unit_price}/kWh` : "-"}
                    </TableCell>
                    <TableCell>
                      {plan.effective_date ? formatDate(plan.effective_date) : "-"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Edit Form Modal */}
      <CompanyForm
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        company={company}
      />
    </div>
  );
}
