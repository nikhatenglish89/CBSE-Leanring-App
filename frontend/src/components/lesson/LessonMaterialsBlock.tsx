import { useEffect, useState } from "react";

import {
  downloadMaterial,
  useDeleteMaterial,
  useLessonMaterials,
  useReplaceMaterial,
  useUploadMaterial,
  viewMaterial,
} from "../../hooks/useMaterials";
import { formatFileSize } from "../../lib/format";
import type { LessonMaterialOut, MaterialType } from "../../types/curriculum";
import { Button, Card, Skeleton, useToast } from "../ui";

const MATERIAL_ICON: Record<MaterialType, string> = {
  PDF: "📕",
  DOCUMENT: "📄",
  PRESENTATION: "📊",
  IMAGE: "🖼️",
  TEXT: "📝",
  OTHER: "📎",
};

// Word/PowerPoint files have no reliable in-browser renderer without a
// conversion service we don't have — those stay download-only.
const VIEWABLE_TYPES = new Set<MaterialType>(["PDF", "TEXT", "IMAGE"]);

const ACCEPTED_TYPES =
  ".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg,.webp,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,image/png,image/jpeg,image/webp,text/plain";

type ViewState = { kind: "text"; text: string } | { kind: "url"; url: string };

export function LessonMaterialsBlock({ lessonId, canEdit }: { lessonId: string; canEdit: boolean }) {
  const { data: materials, isLoading } = useLessonMaterials(lessonId);
  const uploadMaterial = useUploadMaterial(lessonId);
  const replaceMaterial = useReplaceMaterial(lessonId);
  const deleteMaterial = useDeleteMaterial(lessonId);
  const { showToast } = useToast();

  const [viewingId, setViewingId] = useState<string | null>(null);
  const [viewState, setViewState] = useState<ViewState | null>(null);
  const [viewLoading, setViewLoading] = useState(false);

  useEffect(() => {
    // Release the blob URL whenever we close the viewer or the component unmounts.
    return () => {
      if (viewState?.kind === "url") URL.revokeObjectURL(viewState.url);
    };
  }, [viewState]);

  if (isLoading) {
    return (
      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Study materials</h2>
        <div className="mt-4 flex flex-col gap-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </Card>
    );
  }
  if ((materials?.length ?? 0) === 0 && !canEdit) return null;

  const onUploadChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    try {
      await uploadMaterial.mutateAsync(file);
      showToast("Material uploaded.", "success");
    } catch {
      showToast("Could not upload — check the file type and size (max 8 MB).", "error");
    }
  };

  const onReplaceChange = async (materialId: string, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    try {
      await replaceMaterial.mutateAsync({ materialId, file });
      showToast("Material replaced.", "success");
      if (viewingId === materialId) closeViewer();
    } catch {
      showToast("Could not replace — check the file type and size (max 8 MB).", "error");
    }
  };

  const onDelete = async (materialId: string) => {
    try {
      await deleteMaterial.mutateAsync(materialId);
      showToast("Material removed.", "success");
      if (viewingId === materialId) closeViewer();
    } catch {
      showToast("Could not remove the material.", "error");
    }
  };

  const onDownload = async (materialId: string, fileName: string) => {
    try {
      await downloadMaterial(materialId, fileName);
    } catch {
      showToast("Could not download the file.", "error");
    }
  };

  const closeViewer = () => {
    setViewingId(null);
    setViewState(null);
  };

  const onToggleView = async (material: LessonMaterialOut) => {
    if (viewingId === material.id) {
      closeViewer();
      return;
    }
    setViewingId(material.id);
    setViewState(null);
    setViewLoading(true);
    try {
      const result = await viewMaterial(material.id, material.material_type);
      setViewState(result);
    } catch {
      showToast("Could not open the file for viewing.", "error");
      setViewingId(null);
    } finally {
      setViewLoading(false);
    }
  };

  return (
    <Card>
      <h2 className="text-lg font-semibold text-slate-900">Study materials</h2>

      {materials && materials.length > 0 ? (
        <ul className="mt-4 flex flex-col divide-y divide-slate-100 border-t border-slate-100">
          {materials.map((material) => (
            <li key={material.id} className="flex flex-col py-3">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xl">{MATERIAL_ICON[material.material_type]}</span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-800">{material.file_name}</p>
                  <p className="text-xs text-slate-500">{formatFileSize(material.file_size)}</p>
                </div>
                {VIEWABLE_TYPES.has(material.material_type) ? (
                  <Button
                    variant="secondary"
                    onClick={() => onToggleView(material)}
                    isLoading={viewLoading && viewingId === material.id}
                  >
                    {viewingId === material.id ? "Hide" : "View"}
                  </Button>
                ) : (
                  <span className="text-xs italic text-slate-400">No preview available</span>
                )}
                <Button
                  variant="secondary"
                  onClick={() => onDownload(material.id, material.file_name)}
                >
                  Download
                </Button>
                {canEdit && (
                  <>
                    <input
                      type="file"
                      id={`replace-material-${material.id}`}
                      accept={ACCEPTED_TYPES}
                      className="hidden"
                      onChange={(event) => onReplaceChange(material.id, event)}
                    />
                    <Button
                      variant="ghost"
                      onClick={() =>
                        document.getElementById(`replace-material-${material.id}`)?.click()
                      }
                    >
                      Replace
                    </Button>
                    <Button
                      variant="ghost"
                      className="!text-red-600"
                      onClick={() => onDelete(material.id)}
                      isLoading={deleteMaterial.isPending}
                    >
                      Delete
                    </Button>
                  </>
                )}
              </div>

              {viewingId === material.id && (
                <div className="mt-3">
                  {viewLoading && <Skeleton className="h-64 w-full" />}
                  {!viewLoading && viewState?.kind === "text" && (
                    <pre className="max-h-[70vh] overflow-auto whitespace-pre-wrap rounded-lg border border-slate-200 bg-slate-50 p-4 font-serif text-sm leading-7 text-slate-800">
                      {viewState.text}
                    </pre>
                  )}
                  {!viewLoading && viewState?.kind === "url" && material.material_type === "PDF" && (
                    <iframe
                      src={viewState.url}
                      title={material.file_name}
                      className="h-[70vh] w-full rounded-lg border border-slate-200"
                    />
                  )}
                  {!viewLoading && viewState?.kind === "url" && material.material_type === "IMAGE" && (
                    <img
                      src={viewState.url}
                      alt={material.file_name}
                      className="max-h-[70vh] w-full rounded-lg border border-slate-200 object-contain"
                    />
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 text-sm italic text-slate-500">No study materials attached yet.</p>
      )}

      {canEdit && (
        <div className="mt-4 border-t border-slate-100 pt-4">
          <input
            type="file"
            id={`upload-material-${lessonId}`}
            accept={ACCEPTED_TYPES}
            className="hidden"
            onChange={onUploadChange}
          />
          <Button
            variant="secondary"
            onClick={() => document.getElementById(`upload-material-${lessonId}`)?.click()}
            isLoading={uploadMaterial.isPending}
          >
            Upload PDF / document / image
          </Button>
          <p className="mt-2 text-xs text-slate-500">
            PDF, Word, PowerPoint, text, or image files up to 8 MB. PDF, text, and image files can be
            viewed right here on the page — Word and PowerPoint files download only.
          </p>
        </div>
      )}
    </Card>
  );
}
