"use client";

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { CircleDollarSign, Eye, GitCompare, History } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import { LoadingPage, TableSkeleton } from "@/components/ui/loading";
import { PriceDetailModal } from "@/components/prices";
import { usePrices } from "@/hooks/usePrices";
import { useCompanies } from "@/hooks/useCompanies";
import { PricePlan } from "@/types";

function PricesContent() {
  const searchParams = useSearchParams();
  const initialCompanyId = searchParams.get("company_id");

  const [page, setPage] = useState(1);
  const [companyFilter, setCompanyFilter] = useState<string>(initialCompanyId || "");
  const [planTypeFilter, setPlanTypeFilter] = useState<string>("");
  const [currentOnlyFilter, setCurrentOnlyFilter] = useState<boolean>(true);
  const [selectedPlan, setSelectedPlan] = useState<PricePlan | null>(null);

  const { data: companiesData } = useCompanies({ page_size: 100 });
  const { data, isLoading, error } = usePrices({
    page,
    page_size: 20,
    company_id: companyFilter ? parseInt(companyFilter) : undefined,
    plan_type: planTypeFilter || undefined,
    is_current: currentOnlyFilter ? true : undefined,
  });

  const companyOptions = [
    { value: "", label: "All Companies" },
    ...(companiesData?.items.map((c) => ({ value: c.id.toString(), label: c.name_en })) || []),
  ];

  const planTypeOptions = [
    { value: "", label: "All Types" },
    { value: "従量電灯A", label: "従量電灯A" },
    { value: "従量電灯B", label: "従量電灯B" },
    { value: "従量電灯C", label: "従量電灯C" },
    { value: "低圧電力", label: "低圧電力" },
    { value: "スタンダードS", label: "スタンダードS" },
    { value: "スタンダードL", label: "スタンダードL" },
  ];

  const formatPrice = (price: number | null) => {
    if (price === null) return "-";
    return `¥${price.toLocaleString()}`;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString("ja-JP");
  };

  if (error) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-destructive">
            Failed to load prices. Please try again.
          </div>
        </CardContent>
      </Card>
    );
  }

  const plans = data?.items || [];
  const totalPages = data ? Math.ceil(data.total / data.page_size) : 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <CircleDollarSign className="h-6 w-6" />
          <h1 className="text-2xl font-bold">Price Plans</h1>
          <span className="text-muted-foreground">({data?.total || 0})</span>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/prices/compare">
            <Button variant="outline">
              <GitCompare className="h-4 w-4 mr-2" />
              Compare
            </Button>
          </Link>
          <Link href="/prices/history">
            <Button variant="outline">
              <History className="h-4 w-4 mr-2" />
              History
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="py-4">
          <div className="flex flex-wrap gap-4">
            <Select
              options={companyOptions}
              value={companyFilter}
              onChange={(value) => {
                setCompanyFilter(value);
                setPage(1);
              }}
              label="Company"
              className="w-48"
            />

            <Select
              options={planTypeOptions}
              value={planTypeFilter}
              onChange={(value) => {
                setPlanTypeFilter(value);
                setPage(1);
              }}
              label="Plan Type"
              className="w-48"
            />

            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={currentOnlyFilter}
                  onChange={(e) => {
                    setCurrentOnlyFilter(e.target.checked);
                    setPage(1);
                  }}
                  className="h-4 w-4"
                />
                <span className="text-sm">Current plans only</span>
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      {isLoading ? (
        <Card>
          <CardContent className="py-4">
            <TableSkeleton rows={10} columns={6} />
          </CardContent>
        </Card>
      ) : plans.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <CircleDollarSign className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No price plans found</h3>
              <p className="mt-2 text-muted-foreground">
                Try adjusting your filters or run a crawl to fetch price data.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Company</TableHead>
                  <TableHead>Plan Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Base Charge</TableHead>
                  <TableHead className="text-right">Unit Price</TableHead>
                  <TableHead>Effective Date</TableHead>
                  <TableHead className="text-center">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {plans.map((plan) => (
                  <TableRow key={plan.id}>
                    <TableCell>
                      <span className="font-medium">{plan.company_name || "-"}</span>
                    </TableCell>
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
                      {plan.unit_price !== null ? `¥${plan.unit_price}/kWh` : "-"}
                    </TableCell>
                    <TableCell>{formatDate(plan.effective_date)}</TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedPlan(plan)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      )}

      {/* Detail Modal */}
      <PriceDetailModal
        isOpen={!!selectedPlan}
        onClose={() => setSelectedPlan(null)}
        plan={selectedPlan}
      />
    </div>
  );
}

export default function PricesPage() {
  return (
    <Suspense fallback={<LoadingPage />}>
      <PricesContent />
    </Suspense>
  );
}
