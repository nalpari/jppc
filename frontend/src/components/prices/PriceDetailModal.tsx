"use client";

import { CircleDollarSign, Calendar, ExternalLink, Info } from "lucide-react";
import { Modal, ModalFooter } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { PricePlan } from "@/types";

interface PriceDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan: PricePlan | null;
}

export function PriceDetailModal({ isOpen, onClose, plan }: PriceDetailModalProps) {
  if (!plan) return null;

  const formatPrice = (price: number | null) => {
    if (price === null) return "-";
    return `¥${price.toLocaleString()}`;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={plan.plan_name_ja}
      description={plan.plan_name_en || undefined}
      size="lg"
    >
      <div className="space-y-6">
        {/* Header Info */}
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline">{plan.plan_type}</Badge>
          {plan.contract_type && <Badge variant="outline">{plan.contract_type}</Badge>}
          <Badge variant={plan.is_current ? "default" : "secondary"}>
            {plan.is_current ? "Current" : "Historical"}
          </Badge>
        </div>

        {/* Company */}
        {plan.company_name && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Info className="h-4 w-4" />
            <span>{plan.company_name}</span>
          </div>
        )}

        {/* Price Information */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-2">
                <CircleDollarSign className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Base Charge</span>
              </div>
              <div className="text-2xl font-bold">{formatPrice(plan.base_charge)}</div>
              <div className="text-sm text-muted-foreground">per month</div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-2">
                <CircleDollarSign className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Unit Price</span>
              </div>
              <div className="text-2xl font-bold">
                {plan.unit_price !== null ? `¥${plan.unit_price}` : "-"}
              </div>
              <div className="text-sm text-muted-foreground">per kWh</div>
            </CardContent>
          </Card>
        </div>

        {/* Price Tiers */}
        {plan.price_tiers && Object.keys(plan.price_tiers).length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Price Tiers (従量電灯)</h4>
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-2 text-left">Tier</th>
                    <th className="px-4 py-2 text-left">Usage Range</th>
                    <th className="px-4 py-2 text-right">Price</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(plan.price_tiers as Record<string, { min?: number; max?: number; price: number }>).map(
                    ([tier, data]) => (
                      <tr key={tier} className="border-t">
                        <td className="px-4 py-2">{tier}</td>
                        <td className="px-4 py-2">
                          {data.min !== undefined ? `${data.min}kWh` : "0kWh"} ~{" "}
                          {data.max !== undefined ? `${data.max}kWh` : ""}
                        </td>
                        <td className="px-4 py-2 text-right">¥{data.price}/kWh</td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Time of Use */}
        {plan.time_of_use && Object.keys(plan.time_of_use).length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Time of Use Rates</h4>
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-2 text-left">Period</th>
                    <th className="px-4 py-2 text-left">Hours</th>
                    <th className="px-4 py-2 text-right">Price</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(plan.time_of_use as Record<string, { hours: string; price: number }>).map(
                    ([period, data]) => (
                      <tr key={period} className="border-t">
                        <td className="px-4 py-2">{period}</td>
                        <td className="px-4 py-2">{data.hours}</td>
                        <td className="px-4 py-2 text-right">¥{data.price}/kWh</td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Additional Charges */}
        <div className="grid gap-4 md:grid-cols-2">
          {plan.fuel_adjustment !== null && (
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="text-sm text-muted-foreground">Fuel Adjustment</span>
              <span className="font-medium">¥{plan.fuel_adjustment}/kWh</span>
            </div>
          )}
          {plan.renewable_surcharge !== null && (
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="text-sm text-muted-foreground">Renewable Surcharge</span>
              <span className="font-medium">¥{plan.renewable_surcharge}/kWh</span>
            </div>
          )}
        </div>

        {/* Metadata */}
        <div className="pt-4 border-t space-y-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Effective Date: {formatDate(plan.effective_date)}</span>
          </div>
          {plan.source_url && (
            <div className="flex items-center gap-2">
              <ExternalLink className="h-4 w-4" />
              <a
                href={plan.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline truncate"
              >
                Source
              </a>
            </div>
          )}
          {plan.notes && (
            <div className="pt-2">
              <span className="font-medium">Notes:</span>
              <p className="mt-1">{plan.notes}</p>
            </div>
          )}
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Close
        </Button>
      </ModalFooter>
    </Modal>
  );
}
