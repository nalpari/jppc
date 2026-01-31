"use client";

import { Building2, ExternalLink, Edit, Trash2, Power } from "lucide-react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Company } from "@/types";

interface CompanyCardProps {
  company: Company;
  onEdit: (company: Company) => void;
  onDelete: (company: Company) => void;
  onToggleActive: (company: Company) => void;
}

export function CompanyCard({
  company,
  onEdit,
  onDelete,
  onToggleActive,
}: CompanyCardProps) {
  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-lg">{company.name_en}</CardTitle>
          </div>
          <Badge variant={company.is_active ? "default" : "secondary"}>
            {company.is_active ? "Active" : "Inactive"}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">{company.name_ja}</p>
      </CardHeader>

      <CardContent className="flex-1 space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Code:</span>
          <span className="font-mono">{company.code}</span>
        </div>

        {company.region && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Region:</span>
            <span>{company.region}</span>
          </div>
        )}

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Plans:</span>
          <span>{company.plans_count}</span>
        </div>

        {company.description && (
          <p className="text-sm text-muted-foreground line-clamp-2">
            {company.description}
          </p>
        )}
      </CardContent>

      <CardFooter className="flex flex-wrap gap-2 pt-3 border-t">
        <Link href={`/companies/${company.id}`} className="flex-1">
          <Button variant="outline" size="sm" className="w-full">
            View Details
          </Button>
        </Link>

        <a
          href={company.website_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0"
        >
          <Button variant="outline" size="sm">
            <ExternalLink className="h-4 w-4" />
          </Button>
        </a>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onEdit(company)}
          className="flex-shrink-0"
        >
          <Edit className="h-4 w-4" />
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onToggleActive(company)}
          className="flex-shrink-0"
        >
          <Power className="h-4 w-4" />
        </Button>

        <Button
          variant="destructive"
          size="sm"
          onClick={() => onDelete(company)}
          className="flex-shrink-0"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
