"use client";

import { useState, useMemo } from "react";
import { History, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
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
import { Spinner, Skeleton } from "@/components/ui/loading";
import { usePrices, usePriceHistory } from "@/hooks/usePrices";
import { useCompanies } from "@/hooks/useCompanies";

export default function PriceHistoryPage() {
  const [selectedCompany, setSelectedCompany] = useState<string>("");
  const [selectedPlan, setSelectedPlan] = useState<string>("");

  const { data: companiesData } = useCompanies({ page_size: 100 });
  const { data: pricesData, isLoading: pricesLoading } = usePrices({
    company_id: selectedCompany ? parseInt(selectedCompany) : undefined,
    page_size: 100,
  });

  const planId = selectedPlan ? parseInt(selectedPlan) : 0;
  const { data: historyData, isLoading: historyLoading } = usePriceHistory(planId, 50);

  const companyOptions = [
    { value: "", label: "Select Company" },
    ...(companiesData?.items.map((c) => ({ value: c.id.toString(), label: c.name_en })) || []),
  ];

  const planOptions = useMemo(() => {
    if (!pricesData?.items || !selectedCompany) return [{ value: "", label: "Select Plan" }];
    return [
      { value: "", label: "Select Plan" },
      ...pricesData.items.map((plan) => ({
        value: plan.id.toString(),
        label: plan.plan_name_ja,
      })),
    ];
  }, [pricesData, selectedCompany]);

  const formatPrice = (price: number | null) => {
    if (price === null) return "-";
    return `¥${price.toLocaleString()}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getChangeIcon = (changeType: string) => {
    switch (changeType) {
      case "increase":
        return <TrendingUp className="h-4 w-4 text-destructive" />;
      case "decrease":
        return <TrendingDown className="h-4 w-4 text-green-500" />;
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getChangeBadge = (changeType: string) => {
    switch (changeType) {
      case "increase":
        return <Badge variant="destructive">Increase</Badge>;
      case "decrease":
        return <Badge className="bg-green-500">Decrease</Badge>;
      case "initial":
        return <Badge variant="secondary">Initial</Badge>;
      default:
        return <Badge variant="outline">{changeType}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <History className="h-6 w-6" />
        <h1 className="text-2xl font-bold">Price History</h1>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Select Plan</CardTitle>
          <CardDescription>
            Choose a company and plan to view price history.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <Select
              options={companyOptions}
              value={selectedCompany}
              onChange={(value) => {
                setSelectedCompany(value);
                setSelectedPlan("");
              }}
              label="Company"
            />

            <Select
              options={planOptions}
              value={selectedPlan}
              onChange={setSelectedPlan}
              label="Plan"
              disabled={!selectedCompany || pricesLoading}
            />
          </div>
        </CardContent>
      </Card>

      {/* History Display */}
      {!selectedPlan ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <History className="mx-auto h-12 w-12 mb-4" />
              <p>Select a company and plan to view price history.</p>
            </div>
          </CardContent>
        </Card>
      ) : historyLoading ? (
        <Card>
          <CardContent className="py-8">
            <div className="flex items-center justify-center gap-2">
              <Spinner />
              <span>Loading history...</span>
            </div>
          </CardContent>
        </Card>
      ) : !historyData || historyData.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <History className="mx-auto h-12 w-12 mb-4" />
              <p>No price history available for this plan.</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Summary */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Records</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{historyData.length}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Price Increases</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-destructive">
                  {historyData.filter((h) => h.change_type === "increase").length}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Price Decreases</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-500">
                  {historyData.filter((h) => h.change_type === "decrease").length}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Latest Change</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-lg font-medium">
                  {historyData.length > 0 ? formatDate(historyData[0].recorded_at) : "-"}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* History Table */}
          <Card>
            <CardHeader>
              <CardTitle>Price Change History</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Change Type</TableHead>
                    <TableHead className="text-right">Base Charge</TableHead>
                    <TableHead className="text-right">Unit Price</TableHead>
                    <TableHead className="text-right">Fuel Adj.</TableHead>
                    <TableHead className="text-right">Renewable</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {historyData.map((record) => (
                    <TableRow key={record.id}>
                      <TableCell>{formatDate(record.recorded_at)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getChangeIcon(record.change_type)}
                          {getChangeBadge(record.change_type)}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        {formatPrice(record.base_charge)}
                      </TableCell>
                      <TableCell className="text-right">
                        {record.unit_price !== null ? `¥${record.unit_price}/kWh` : "-"}
                      </TableCell>
                      <TableCell className="text-right">
                        {record.fuel_adjustment !== null
                          ? `¥${record.fuel_adjustment}/kWh`
                          : "-"}
                      </TableCell>
                      <TableCell className="text-right">
                        {record.renewable_surcharge !== null
                          ? `¥${record.renewable_surcharge}/kWh`
                          : "-"}
                      </TableCell>
                      <TableCell>
                        {record.change_details ? (
                          <span className="text-sm text-muted-foreground">
                            {JSON.stringify(record.change_details).slice(0, 50)}...
                          </span>
                        ) : (
                          "-"
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
