"use client";

import { useState } from "react";
import { Plus, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { LoadingPage, CardSkeleton } from "@/components/ui/loading";
import { CompanyCard, CompanyForm } from "@/components/companies";
import { useCompanies, useUpdateCompany, useDeleteCompany } from "@/hooks/useCompanies";
import { Company } from "@/types";

export default function CompaniesPage() {
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState<string>("all");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState<Company | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Company | null>(null);

  const isActiveFilter = filter === "active" ? true : filter === "inactive" ? false : undefined;
  const { data, isLoading, error } = useCompanies({ page, page_size: 12, is_active: isActiveFilter });
  const updateMutation = useUpdateCompany();
  const deleteMutation = useDeleteCompany();

  const handleEdit = (company: Company) => {
    setEditingCompany(company);
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingCompany(null);
  };

  const handleToggleActive = async (company: Company) => {
    try {
      await updateMutation.mutateAsync({
        id: company.id,
        data: { is_active: !company.is_active },
      });
    } catch (error) {
      console.error("Failed to toggle company status:", error);
    }
  };

  const handleDelete = async (company: Company) => {
    setDeleteConfirm(company);
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;
    try {
      await deleteMutation.mutateAsync(deleteConfirm.id);
      setDeleteConfirm(null);
    } catch (error) {
      console.error("Failed to delete company:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Companies</h1>
        </div>
        <CardSkeleton count={8} />
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-destructive">
            Failed to load companies. Please try again.
          </div>
        </CardContent>
      </Card>
    );
  }

  const companies = data?.items || [];
  const totalPages = data ? Math.ceil(data.total / data.page_size) : 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Building2 className="h-6 w-6" />
          <h1 className="text-2xl font-bold">Companies</h1>
          <span className="text-muted-foreground">({data?.total || 0})</span>
        </div>

        <div className="flex items-center gap-2">
          <Select
            options={[
              { value: "all", label: "All" },
              { value: "active", label: "Active Only" },
              { value: "inactive", label: "Inactive Only" },
            ]}
            value={filter}
            onChange={setFilter}
            className="w-36"
          />
          <Button onClick={() => setIsFormOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Company
          </Button>
        </div>
      </div>

      {/* Companies Grid */}
      {companies.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <Building2 className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No companies found</h3>
              <p className="mt-2 text-muted-foreground">
                Get started by adding your first power company.
              </p>
              <Button className="mt-4" onClick={() => setIsFormOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Company
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {companies.map((company) => (
            <CompanyCard
              key={company.id}
              company={company}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onToggleActive={handleToggleActive}
            />
          ))}
        </div>
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

      {/* Company Form Modal */}
      <CompanyForm
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        company={editingCompany}
      />

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black/50" onClick={() => setDeleteConfirm(null)} />
          <Card className="relative z-50 w-full max-w-md">
            <CardHeader>
              <CardTitle>Delete Company</CardTitle>
            </CardHeader>
            <CardContent>
              <p>
                Are you sure you want to delete <strong>{deleteConfirm.name_en}</strong>?
                This action cannot be undone.
              </p>
              <div className="mt-4 flex justify-end gap-2">
                <Button variant="outline" onClick={() => setDeleteConfirm(null)}>
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={confirmDelete}
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? "Deleting..." : "Delete"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
