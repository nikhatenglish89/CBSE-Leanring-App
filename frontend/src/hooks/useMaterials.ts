import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { LessonMaterialOut, VideoOut } from "../types/curriculum";

export function useLessonMaterials(lessonId: string | undefined) {
  return useQuery({
    queryKey: ["lesson-materials", lessonId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<LessonMaterialOut[]>>(`/lessons/${lessonId}/materials`);
      return data.data;
    },
    enabled: Boolean(lessonId),
  });
}

export function useUploadMaterial(lessonId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      const { data } = await api.post<ApiSuccess<LessonMaterialOut>>(
        `/lessons/${lessonId}/materials`,
        form
      );
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["lesson-materials", lessonId] }),
  });
}

export function useReplaceMaterial(lessonId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ materialId, file }: { materialId: string; file: File }) => {
      const form = new FormData();
      form.append("file", file);
      const { data } = await api.put<ApiSuccess<LessonMaterialOut>>(`/materials/${materialId}`, form);
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["lesson-materials", lessonId] }),
  });
}

export function useDeleteMaterial(lessonId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (materialId: string) => {
      await api.delete(`/materials/${materialId}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["lesson-materials", lessonId] }),
  });
}

export async function downloadMaterial(materialId: string, fileName: string) {
  const response = await api.get(`/materials/${materialId}/download`, { responseType: "blob" });
  const url = URL.createObjectURL(response.data as Blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

/** Fetches a material's bytes for inline viewing (as opposed to
 * downloadMaterial, which saves the file to disk). Text files are
 * returned as a string so callers can render them directly; everything
 * else is returned as an object URL for use in an <iframe>/<img>. */
export async function viewMaterial(
  materialId: string,
  materialType: string
): Promise<{ kind: "text"; text: string } | { kind: "url"; url: string }> {
  const response = await api.get(`/materials/${materialId}/download`, { responseType: "blob" });
  const blob = response.data as Blob;
  if (materialType === "TEXT") {
    return { kind: "text", text: await blob.text() };
  }
  return { kind: "url", url: URL.createObjectURL(blob) };
}

export function useLessonVideo(lessonId: string | undefined) {
  return useQuery({
    queryKey: ["lesson-video", lessonId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<VideoOut | null>>(`/lessons/${lessonId}/video`);
      return data.data;
    },
    enabled: Boolean(lessonId),
  });
}

export function useSetVideo(lessonId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ url, title }: { url: string; title?: string }) => {
      const { data } = await api.put<ApiSuccess<VideoOut>>(`/lessons/${lessonId}/video`, {
        url,
        title: title ?? "",
      });
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["lesson-video", lessonId] }),
  });
}

export function useDeleteVideo(lessonId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await api.delete(`/lessons/${lessonId}/video`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["lesson-video", lessonId] }),
  });
}
