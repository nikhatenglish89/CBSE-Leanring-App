import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { Group, GroupDetail, TaskSubmission } from "../types/groups";

export function useMyGroups() {
  return useQuery({
    queryKey: ["my-groups"],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<Group[]>>("/groups/mine");
      return data.data;
    },
  });
}

export function useGroupDetail(groupId: string | undefined) {
  return useQuery({
    queryKey: ["group", groupId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<GroupDetail>>(`/groups/${groupId}`);
      return data.data;
    },
    enabled: Boolean(groupId),
  });
}

export function useCreateGroup() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { name: string; description?: string }) => {
      const { data } = await api.post<ApiSuccess<Group>>("/groups", payload);
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-groups"] }),
  });
}

export function useAddGroupMember(groupId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (studentId: string) => {
      await api.post(`/groups/${groupId}/members`, { student_id: studentId });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["group", groupId] });
      queryClient.invalidateQueries({ queryKey: ["my-groups"] });
    },
  });
}

export function useRemoveGroupMember(groupId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (studentId: string) => {
      await api.delete(`/groups/${groupId}/members/${studentId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["group", groupId] });
      queryClient.invalidateQueries({ queryKey: ["my-groups"] });
    },
  });
}

export function useCreateGroupTask(groupId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { title: string; description?: string; due_date?: string | null }) => {
      const { data } = await api.post(`/groups/${groupId}/tasks`, payload);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["group", groupId] });
      queryClient.invalidateQueries({ queryKey: ["my-groups"] });
    },
  });
}

export function useSubmitTask(groupId: string, taskId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ content, file }: { content: string; file?: File | null }) => {
      const form = new FormData();
      form.append("content", content);
      if (file) {
        form.append("file", file);
      }
      const { data } = await api.post<ApiSuccess<TaskSubmission>>(
        `/groups/${groupId}/tasks/${taskId}/submit`,
        form
      );
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["group", groupId] }),
  });
}

export async function downloadSubmissionFile(
  groupId: string,
  taskId: string,
  submissionId: string,
  fileName: string
) {
  const response = await api.get(`/groups/${groupId}/tasks/${taskId}/submissions/${submissionId}/file`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(response.data as Blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function useTaskSubmissions(groupId: string, taskId: string | null) {
  return useQuery({
    queryKey: ["task-submissions", groupId, taskId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<TaskSubmission[]>>(
        `/groups/${groupId}/tasks/${taskId}/submissions`
      );
      return data.data;
    },
    enabled: Boolean(taskId),
  });
}
