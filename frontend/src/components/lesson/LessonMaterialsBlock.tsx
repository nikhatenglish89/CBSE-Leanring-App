import {
  downloadMaterial,
  useDeleteMaterial,
  useLessonMaterials,
  useReplaceMaterial,
  useUploadMaterial,
} from "../../hooks/useMaterials";
import { formatFileSize } from "../../lib/format";
import type { MaterialType } from "../../types/curriculum";
import { Button, Card, useToast } from "../ui";

const MATERIAL_ICON: Record<MaterialType, string> = {
  PDF: "📕",
  DOCUMENT: "📄",
  PRESENTATION: "📊",
  IMAGE: "🖼️",
  OTHER: "📎",
};

const ACCEPTED_TYPES =
  ".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg,.webp,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,image/png,image/jpeg,image/webp";

export function LessonMaterialsBlock({ lessonId, canEdit }: { lessonId: string; canEdit: boolean }) {
  const { data: materials, isLoading } = useLessonMaterials(lessonId);
  const uploadMaterial = useUploadMaterial(lessonId);
  const replaceMaterial = useReplaceMaterial(lessonId);
  const deleteMaterial = useDeleteMaterial(lessonId);
  const { showToast } = useToast();

  if (isLoading) return null;
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
    } catch {
      showToast("Could not replace — check the file type and size (max 8 MB).", "error");
    }
  };

  const onDelete = async (materialId: string) => {
    try {
      await deleteMaterial.mutateAsync(materialId);
      showToast("Material removed.", "success");
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

  return (
    <Card>
      <h2 className="text-lg font-semibold text-slate-900">Study materials</h2>

      {materials && materials.length > 0 ? (
        <ul className="mt-4 flex flex-col divide-y divide-slate-100 border-t border-slate-100">
          {materials.map((material) => (
            <li key={material.id} className="flex flex-wrap items-center gap-3 py-3">
              <span className="text-xl">{MATERIAL_ICON[material.material_type]}</span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-800">{material.file_name}</p>
                <p className="text-xs text-slate-500">{formatFileSize(material.file_size)}</p>
              </div>
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
          <p className="mt-2 text-xs text-slate-500">PDF, Word, PowerPoint, or image files up to 8 MB.</p>
        </div>
      )}
    </Card>
  );
}
