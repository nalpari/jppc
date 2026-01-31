// Company types
export interface Company {
  id: number;
  code: string;
  name: string; // Display name (alias for name_en)
  name_ja: string;
  name_en: string;
  name_ko: string | null;
  website_url: string;
  price_page_url: string;
  region: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  plans_count: number;
}

export interface CompanyCreate {
  code: string;
  name_ja: string;
  name_en: string;
  name_ko?: string;
  website_url: string;
  price_page_url: string;
  region?: string;
  description?: string;
}

export interface CompanyUpdate {
  name_ja?: string;
  name_en?: string;
  name_ko?: string;
  website_url?: string;
  price_page_url?: string;
  region?: string;
  description?: string;
  is_active?: boolean;
}

// Price Plan types
export interface PricePlan {
  id: number;
  company_id: number;
  company_name: string | null;
  plan_code: string;
  plan_name_ja: string;
  plan_name_en: string | null;
  plan_type: string;
  contract_type: string | null;
  base_charge: number | null;
  unit_price: number | null;
  price_tiers: Record<string, unknown> | null;
  time_of_use: Record<string, unknown> | null;
  fuel_adjustment: number | null;
  renewable_surcharge: number | null;
  effective_date: string | null;
  source_url: string | null;
  notes: string | null;
  is_current: boolean;
  created_at: string;
  updated_at: string;
}

export interface PriceHistory {
  id: number;
  price_plan_id: number;
  base_charge: number | null;
  unit_price: number | null;
  price_tiers: Record<string, unknown> | null;
  fuel_adjustment: number | null;
  renewable_surcharge: number | null;
  change_type: string;
  change_details: Record<string, unknown> | null;
  recorded_at: string;
}

export interface PriceCompareItem {
  plan_id: number;
  company_name: string;
  plan_name: string;
  base_charge: number | null;
  unit_price: number | null;
  estimated_monthly_cost: number | null;
  fuel_adjustment: number | null;
  renewable_surcharge: number | null;
  total_estimated: number | null;
}

export interface PriceCompareResponse {
  usage_kwh: number;
  comparisons: PriceCompareItem[];
  cheapest_plan_id: number | null;
}

// Crawling types
export interface CrawlLog {
  id: number;
  company_id: number | null;
  company_name: string | null;
  status: 'pending' | 'running' | 'success' | 'failed' | 'partial';
  trigger_type: 'scheduled' | 'manual';
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  plans_found: number;
  plans_updated: number;
  plans_created: number;
  error_message: string | null;
  error_details: Record<string, unknown> | null;
}

export interface CrawlStatus {
  is_running: boolean;
  current_crawl_id: number | null;
  current_company: string | null;
  progress: number;
  last_crawl_at: string | null;
  next_scheduled_at: string | null;
}

export interface ScheduleConfig {
  enabled: boolean;
  day_of_week: number;
  hour: number;
  minute: number;
  timezone: string;
}

// Alert types
export interface AlertRecipient {
  id: number;
  email: string;
  name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AlertSetting {
  id: number;
  alert_type: 'crawl_failure' | 'price_change' | 'weekly_report';
  is_enabled: boolean;
  recipients: AlertRecipient[];
  created_at: string;
  updated_at: string;
}

// Dashboard types
export interface DashboardStats {
  companies: {
    total: number;
    active: number;
  };
  price_plans: {
    total: number;
    current: number;
  };
  crawling: {
    total: number;
    successful: number;
    failed: number;
    recent_7days: number;
    success_rate: number;
    last_crawl_at: string | null;
  };
}

// Pagination types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// API Response types
export type CompanyListResponse = PaginatedResponse<Company>;
export type PricePlanListResponse = PaginatedResponse<PricePlan>;
export type CrawlLogListResponse = PaginatedResponse<CrawlLog>;
