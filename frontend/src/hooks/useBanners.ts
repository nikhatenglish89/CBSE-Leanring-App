import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, API_BASE_URL } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { Banner, BannerUpdatePayload } from "../types/banners";

export function bannerImageUrl(bannerId: string): string {
  return `${API_BASE_URL}/banners/${bannerId}/image`;
}

/** Public — no login required; this is what the home page uses. */
export function usePublicBanners() {
  return useQuery({
    queryKey: ["public-banners"],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<Banner[]>>("/banners/public");
      return data.data;
    },
  });
}

/** Admin-only — includes inactive banners so they can be reviewed/restored. */
export function useAdminBanners() {
  return useQuery({
    queryKey: ["admin-banners"],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<Banner[]>>("/banners");
      return data.data;
    },
  });
}

export function useCreateBanner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      file,
      title,
      linkUrl,
      displayOrder,
    }: {
      file: File;
      title: string;
      linkUrl: string;
      displayOrder: number;
    }) => {
      const form = new FormData();
      form.append("file", file);
      form.append("title", title);
      form.append("link_url", linkUrl);
      form.append("display_order", String(displayOrder));
      const { data } = await api.post<ApiSuccess<Banner>>("/banners", form);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-banners"] });
      queryClient.invalidateQueries({ queryKey: ["public-banners"] });
    },
  });
}

export function useUpdateBanner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ bannerId, payload }: { bannerId: string; payload: BannerUpdatePayload }) => {
      const { data } = await api.patch<ApiSuccess<Banner>>(`/banners/${bannerId}`, payload);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-banners"] });
      queryClient.invalidateQueries({ queryKey: ["public-banners"] });
    },
  });
}

export function useDeleteBanner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (bannerId: string) => {
      await api.delete(`/banners/${bannerId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-banners"] });
      queryClient.invalidateQueries({ queryKey: ["public-banners"] });
    },
  });
}
