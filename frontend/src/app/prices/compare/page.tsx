"use client";

import { useState, useMemo } from "react";
import { GitCompare, Calculator, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { MultiSelect } from "@/components/ui/select";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import { Spinner } from "@/components/ui/loading";
import { usePrices, usePriceComparison } from "@/hooks/usePrices";
import { PriceCompareItem } from "@/types";

export default function PriceComparePage() {
  const [selectedPlanIds, setSelectedPlanIds] = useState<string[]>([]);
  const [usageKwh, setUsageKwh] = useState<number>(300);

  const { data: pricesData, isLoading: pricesLoading } = usePrices({
    is_current: true,
    page_size: 100,
  });

  const planIds = useMemo(() => selectedPlanIds.map((id) => parseInt(id)), [selectedPlanIds]);

  const {
    data: compareData,
    isLoading: compareLoading,
    error: compareError,
  } = usePriceComparison(planIds, usageKwh, planIds.length >= 2);

  const planOptions = useMemo(() => {
    if (!pricesData?.items) return [];
    return pricesData.items.map((plan) => ({
      value: plan.id.toString(),
      label: `${plan.company_name} - ${plan.plan_name_ja}`,
    }));
  }, [pricesData]);

  const formatPrice = (price: number | null) => {
    if (price === null) return "-";
    return `¥${price.toLocaleString()}`;
  };

  const getCheapestBadge = (item: PriceCompareItem) => {
    if (!compareData) return null;
    if (item.plan_id === compareData.cheapest_plan_id) {
      return (
        <Badge className="ml-2 bg-green-500">
          <TrendingDown className="h-3 w-3 mr-1" />
          Cheapest
        </Badge>
      );
    }
    return null;
  };

  const getSavings = (item: PriceCompareItem) => {
    if (!compareData || !item.total_estimated) return null;
    const cheapest = compareData.comparisons.find(
      (c) => c.plan_id === compareData.cheapest_plan_id
    );
    if (!cheapest?.total_estimated || item.plan_id === compareData.cheapest_plan_id) {
      return null;
    }
    const diff = item.total_estimated - cheapest.total_estimated;
    return diff > 0 ? (
      <span className="text-destructive text-sm">
        +¥{diff.toLocaleString()}
      </span>
    ) : null;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <GitCompare className="h-6 w-6" />
        <h1 className="text-2xl font-bold">Price Comparison</h1>
      </div>

      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Compare Settings</CardTitle>
          <CardDescription>
            Select at least 2 plans and enter your monthly usage to compare prices.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <MultiSelect
              options={planOptions}
              value={selectedPlanIds}
              onChange={setSelectedPlanIds}
              label="Select Plans to Compare"
              placeholder="Select plans..."
              disabled={pricesLoading}
            />

            <Input
              type="number"
              label="Monthly Usage (kWh)"
              value={usageKwh}
              onChange={(e) => setUsageKwh(parseInt(e.target.value) || 0)}
              min={0}
              max={10000}
            />
          </div>

          {selectedPlanIds.length < 2 && (
            <p className="text-sm text-muted-foreground">
              Select at least 2 plans to compare.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Comparison Results */}
      {selectedPlanIds.length >= 2 && (
        <>
          {compareLoading ? (
            <Card>
              <CardContent className="py-12">
                <div className="flex items-center justify-center gap-2">
                  <Spinner />
                  <span>Calculating comparison...</span>
                </div>
              </CardContent>
            </Card>
          ) : compareError ? (
            <Card>
              <CardContent className="py-8">
                <div className="text-center text-destructive">
                  Failed to compare prices. Please try again.
                </div>
              </CardContent>
            </Card>
          ) : compareData ? (
            <>
              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-3">
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription className="flex items-center gap-2">
                      <Calculator className="h-4 w-4" />
                      Monthly Usage
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {compareData.usage_kwh.toLocaleString()} kWh
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription className="flex items-center gap-2">
                      <TrendingDown className="h-4 w-4" />
                      Cheapest Option
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const cheapest = compareData.comparisons.find(
                        (c) => c.plan_id === compareData.cheapest_plan_id
                      );
                      return cheapest ? (
                        <>
                          <div className="text-2xl font-bold text-green-600">
                            {formatPrice(cheapest.total_estimated)}
                          </div>
                          <div className="text-sm text-muted-foreground truncate">
                            {cheapest.company_name} - {cheapest.plan_name}
                          </div>
                        </>
                      ) : (
                        <div className="text-muted-foreground">-</div>
                      );
                    })()}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Potential Savings
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const prices = compareData.comparisons
                        .map((c) => c.total_estimated)
                        .filter((p): p is number => p !== null);
                      if (prices.length < 2) return <div>-</div>;
                      const max = Math.max(...prices);
                      const min = Math.min(...prices);
                      return (
                        <div className="text-2xl font-bold text-green-600">
                          Up to ¥{(max - min).toLocaleString()}
                        </div>
                      );
                    })()}
                  </CardContent>
                </Card>
              </div>

              {/* Comparison Table */}
              <Card>
                <CardHeader>
                  <CardTitle>Detailed Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Plan</TableHead>
                        <TableHead className="text-right">Base Charge</TableHead>
                        <TableHead className="text-right">Usage Cost</TableHead>
                        <TableHead className="text-right">Fuel Adj.</TableHead>
                        <TableHead className="text-right">Renewable</TableHead>
                        <TableHead className="text-right">Total</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {compareData.comparisons.map((item) => (
                        <TableRow
                          key={item.plan_id}
                          className={
                            item.plan_id === compareData.cheapest_plan_id
                              ? "bg-green-50 dark:bg-green-950"
                              : ""
                          }
                        >
                          <TableCell>
                            <div className="flex items-center">
                              <div>
                                <div className="font-medium">
                                  {item.company_name}
                                  {getCheapestBadge(item)}
                                </div>
                                <div className="text-sm text-muted-foreground">
                                  {item.plan_name}
                                </div>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="text-right">
                            {formatPrice(item.base_charge)}
                          </TableCell>
                          <TableCell className="text-right">
                            {formatPrice(item.estimated_monthly_cost)}
                          </TableCell>
                          <TableCell className="text-right">
                            {item.fuel_adjustment !== null
                              ? `¥${(item.fuel_adjustment * usageKwh).toLocaleString()}`
                              : "-"}
                          </TableCell>
                          <TableCell className="text-right">
                            {item.renewable_surcharge !== null
                              ? `¥${(item.renewable_surcharge * usageKwh).toLocaleString()}`
                              : "-"}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="font-bold">{formatPrice(item.total_estimated)}</div>
                            {getSavings(item)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

              {/* Usage Scenarios */}
              <Card>
                <CardHeader>
                  <CardTitle>Usage Scenarios</CardTitle>
                  <CardDescription>
                    Compare costs at different usage levels
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {[100, 200, 300, 400, 500, 750, 1000].map((kwh) => (
                      <Button
                        key={kwh}
                        variant={usageKwh === kwh ? "default" : "outline"}
                        size="sm"
                        onClick={() => setUsageKwh(kwh)}
                      >
                        {kwh} kWh
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : null}
        </>
      )}
    </div>
  );
}
