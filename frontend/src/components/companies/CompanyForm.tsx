"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input, Textarea } from "@/components/ui/input";
import { Modal, ModalFooter } from "@/components/ui/modal";
import { Company, CompanyCreate, CompanyUpdate } from "@/types";
import { useCreateCompany, useUpdateCompany } from "@/hooks/useCompanies";

interface CompanyFormProps {
  isOpen: boolean;
  onClose: () => void;
  company?: Company | null;
}

export function CompanyForm({ isOpen, onClose, company }: CompanyFormProps) {
  const isEditing = !!company;
  const createMutation = useCreateCompany();
  const updateMutation = useUpdateCompany();

  const [formData, setFormData] = useState<CompanyCreate>({
    code: "",
    name_ja: "",
    name_en: "",
    name_ko: "",
    website_url: "",
    price_page_url: "",
    region: "",
    description: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (company) {
      setFormData({
        code: company.code,
        name_ja: company.name_ja,
        name_en: company.name_en,
        name_ko: company.name_ko || "",
        website_url: company.website_url,
        price_page_url: company.price_page_url,
        region: company.region || "",
        description: company.description || "",
      });
    } else {
      setFormData({
        code: "",
        name_ja: "",
        name_en: "",
        name_ko: "",
        website_url: "",
        price_page_url: "",
        region: "",
        description: "",
      });
    }
    setErrors({});
  }, [company, isOpen]);

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.code.trim()) {
      newErrors.code = "Company code is required";
    }
    if (!formData.name_ja.trim()) {
      newErrors.name_ja = "Japanese name is required";
    }
    if (!formData.name_en.trim()) {
      newErrors.name_en = "English name is required";
    }
    if (!formData.website_url.trim()) {
      newErrors.website_url = "Website URL is required";
    } else if (!isValidUrl(formData.website_url)) {
      newErrors.website_url = "Invalid URL format";
    }
    if (!formData.price_page_url.trim()) {
      newErrors.price_page_url = "Price page URL is required";
    } else if (!isValidUrl(formData.price_page_url)) {
      newErrors.price_page_url = "Invalid URL format";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    try {
      if (isEditing && company) {
        const updateData: CompanyUpdate = {
          name_ja: formData.name_ja,
          name_en: formData.name_en,
          name_ko: formData.name_ko || undefined,
          website_url: formData.website_url,
          price_page_url: formData.price_page_url,
          region: formData.region || undefined,
          description: formData.description || undefined,
        };
        await updateMutation.mutateAsync({ id: company.id, data: updateData });
      } else {
        await createMutation.mutateAsync(formData);
      }
      onClose();
    } catch (error) {
      console.error("Failed to save company:", error);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? "Edit Company" : "Add Company"}
      description={
        isEditing
          ? "Update the company information below."
          : "Fill in the company information below."
      }
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <Input
            label="Company Code"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            error={errors.code}
            disabled={isEditing}
            placeholder="e.g., tepco"
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Japanese Name"
              value={formData.name_ja}
              onChange={(e) => setFormData({ ...formData, name_ja: e.target.value })}
              error={errors.name_ja}
              placeholder="e.g., 東京電力"
            />
            <Input
              label="English Name"
              value={formData.name_en}
              onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
              error={errors.name_en}
              placeholder="e.g., TEPCO"
            />
            <Input
              label="Korean Name"
              value={formData.name_ko || ""}
              onChange={(e) => setFormData({ ...formData, name_ko: e.target.value })}
              placeholder="e.g., 도쿄전력"
            />
          </div>

          <Input
            label="Website URL"
            type="url"
            value={formData.website_url}
            onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
            error={errors.website_url}
            placeholder="https://www.tepco.co.jp"
          />

          <Input
            label="Price Page URL"
            type="url"
            value={formData.price_page_url}
            onChange={(e) =>
              setFormData({ ...formData, price_page_url: e.target.value })
            }
            error={errors.price_page_url}
            placeholder="https://www.tepco.co.jp/ep/private/plan/..."
          />

          <Input
            label="Region"
            value={formData.region || ""}
            onChange={(e) => setFormData({ ...formData, region: e.target.value })}
            placeholder="e.g., Kanto"
          />

          <Textarea
            label="Description"
            value={formData.description || ""}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Additional information about the company..."
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Saving..." : isEditing ? "Update" : "Create"}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
