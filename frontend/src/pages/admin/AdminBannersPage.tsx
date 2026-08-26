import { type FormEvent, useState } from "react";

import { PageHeader } from "../../components/layout/PageHeader";
import { Badge, Button, Card, CardSkeleton, EmptyState, Input, useToast } from "../../components/ui";
import {
  bannerImageUrl,
  useAdminBanners,
  useCreateBanner,
  useDeleteBanner,
  useUpdateBanner,
} from "../../hooks/useBanners";

export function AdminBannersPage() {
  const { data: banners, isLoading } = useAdminBanners();
  const createBanner = useCreateBanner();
  const updateBanner = useUpdateBanner();
  const deleteBanner = useDeleteBanner();
  const { showToast } = useToast();

  const [title, setTitle] = useState("");
  const [linkUrl, setLinkUrl] = useState("");
  const [displayOrder, setDisplayOrder] = useState(0);
  const [file, setFile] = useState<File | null>(null);

  const resetForm = () => {
    setTitle("");
    setLinkUrl("");
    setDisplayOrder(0);
    setFile(null);
    const input = document.getElementById("banner-file-input") as HTMLInputElement | null;
    if (input) input.value = "";
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!title.trim() || !file) {
      showToast("Add a title and choose an image first.", "error");
      return;
    }
    try {
      await createBanner.mutateAsync({ file, title, linkUrl, displayOrder });
      resetForm();
      showToast("Banner published to the home page.", "success");
    } catch {
      showToast("Could not upload — check the file is a PNG/JPEG/WEBP under 5 MB.", "error");
    }
  };

  const onToggleActive = async (bannerId: string, isActive: boolean) => {
    try {
      await updateBanner.mutateAsync({ bannerId, payload: { is_active: !isActive } });
      showToast(
        !isActive ? "Banner is now live on the home page." : "Banner hidden from the home page.",
        "success"
      );
    } catch {
      showToast("Could not update the banner.", "error");
    }
  };

  const onDelete = async (bannerId: string) => {
    try {
      await deleteBanner.mutateAsync(bannerId);
      showToast("Banner deleted.", "success");
    } catch {
      showToast("Could not delete the banner.", "error");
    }
  };

  return (
    <div className="page-shell flex flex-col gap-6 py-10">
      <PageHeader
        eyebrow="Admin"
        title="Home Page Banners"
        subtitle="Upload images to showcase on the public home page — results, advertising, announcements. Only banners marked Live are shown to visitors, in display-order."
      />

      <Card className="flex flex-col gap-4">
        <h2 className="text-lg font-semibold text-slate-900">Publish a new banner</h2>
        <form className="grid gap-4 sm:grid-cols-2" onSubmit={onSubmit} noValidate>
          <Input
            label="Title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="e.g. Class X Board Results 2026"
          />
          <Input
            label="Link URL (optional)"
            value={linkUrl}
            onChange={(event) => setLinkUrl(event.target.value)}
            placeholder="https://..."
          />
          <Input
            label="Display order"
            type="number"
            value={displayOrder}
            onChange={(event) => setDisplayOrder(Number(event.target.value))}
          />
          <div>
            <label htmlFor="banner-file-input" className="mb-1.5 block text-sm font-medium text-slate-700">
              Image
            </label>
            <input
              id="banner-file-input"
              type="file"
              accept="image/png,image/jpeg,image/webp"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-brand-700 hover:file:bg-brand-100"
            />
          </div>
          <div className="sm:col-span-2">
            <Button type="submit" isLoading={createBanner.isPending}>
              Publish banner
            </Button>
            <p className="mt-2 text-xs text-slate-500">
              PNG, JPEG, or WEBP, up to 5 MB. Lower display order shows first.
            </p>
          </div>
        </form>
      </Card>

      {isLoading && <CardSkeleton />}

      {!isLoading && banners && banners.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {banners.map((banner) => (
            <Card key={banner.id} className="flex flex-col gap-3">
              <img
                src={bannerImageUrl(banner.id)}
                alt={banner.title}
                className="h-36 w-full rounded-lg border border-slate-200 object-cover"
              />
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="truncate font-medium text-slate-800">{banner.title}</p>
                  {banner.link_url && <p className="truncate text-xs text-slate-500">{banner.link_url}</p>}
                </div>
                <Badge tone={banner.is_active ? "success" : "neutral"}>
                  {banner.is_active ? "Live" : "Hidden"}
                </Badge>
              </div>
              <p className="text-xs text-slate-500">Display order: {banner.display_order}</p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={() => onToggleActive(banner.id, banner.is_active)}
                  isLoading={updateBanner.isPending}
                >
                  {banner.is_active ? "Hide" : "Show"}
                </Button>
                <Button
                  variant="ghost"
                  className="!text-red-600"
                  onClick={() => onDelete(banner.id)}
                  isLoading={deleteBanner.isPending}
                >
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && banners?.length === 0 && (
        <EmptyState
          icon="🖼️"
          title="No banners yet"
          description="Publish one above to feature it on the home page."
        />
      )}
    </div>
  );
}
