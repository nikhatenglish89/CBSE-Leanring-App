export interface Banner {
  id: string;
  title: string;
  link_url: string;
  display_order: number;
  is_active: boolean;
  created_at: string;
}

export interface BannerUpdatePayload {
  title?: string;
  link_url?: string;
  display_order?: number;
  is_active?: boolean;
}
