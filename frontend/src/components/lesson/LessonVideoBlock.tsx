import { useState } from "react";

import { Button, Card, Input, Skeleton, useToast } from "../ui";
import { useDeleteVideo, useLessonVideo, useSetVideo } from "../../hooks/useMaterials";

function extractYoutubeId(url: string): string | null {
  const match = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{6,})/
  );
  return match ? match[1] : null;
}

function extractVimeoId(url: string): string | null {
  const match = url.match(/vimeo\.com\/(?:video\/)?(\d+)/);
  return match ? match[1] : null;
}

export function LessonVideoBlock({ lessonId, canEdit }: { lessonId: string; canEdit: boolean }) {
  const { data: video, isLoading } = useLessonVideo(lessonId);
  const setVideo = useSetVideo(lessonId);
  const deleteVideo = useDeleteVideo(lessonId);
  const { showToast } = useToast();

  const [editing, setEditing] = useState(false);
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");

  if (isLoading) {
    return (
      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Video</h2>
        <Skeleton className="mt-4 aspect-video w-full rounded-xl" />
      </Card>
    );
  }
  if (!video && !canEdit) return null;

  const onSave = async () => {
    if (!url.trim()) return;
    try {
      await setVideo.mutateAsync({ url: url.trim(), title: title.trim() });
      setEditing(false);
      setUrl("");
      setTitle("");
      showToast("Video saved.", "success");
    } catch {
      showToast("Could not save the video link.", "error");
    }
  };

  const onRemove = async () => {
    try {
      await deleteVideo.mutateAsync();
      showToast("Video removed.", "success");
    } catch {
      showToast("Could not remove the video.", "error");
    }
  };

  const youtubeId = video ? extractYoutubeId(video.provider_ref) : null;
  const vimeoId = video ? extractVimeoId(video.provider_ref) : null;

  return (
    <Card>
      <h2 className="text-lg font-semibold text-slate-900">Video</h2>

      {video && !editing && (
        <div className="mt-4 flex flex-col gap-3">
          {video.provider === "YOUTUBE" && youtubeId ? (
            <div className="aspect-video w-full overflow-hidden rounded-xl bg-black">
              <iframe
                className="h-full w-full"
                src={`https://www.youtube.com/embed/${youtubeId}`}
                title={video.title || "Lesson video"}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          ) : video.provider === "VIMEO" && vimeoId ? (
            <div className="aspect-video w-full overflow-hidden rounded-xl bg-black">
              <iframe
                className="h-full w-full"
                src={`https://player.vimeo.com/video/${vimeoId}`}
                title={video.title || "Lesson video"}
                allow="autoplay; fullscreen; picture-in-picture"
                allowFullScreen
              />
            </div>
          ) : (
            // eslint-disable-next-line jsx-a11y/media-has-caption
            <video className="w-full rounded-xl bg-black" controls src={video.provider_ref} />
          )}
          {video.title && <p className="text-sm font-medium text-slate-700">{video.title}</p>}
          <a
            href={video.provider_ref}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-brand-600 hover:underline"
          >
            Open original link &rarr;
          </a>
          {canEdit && (
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() => {
                  setUrl(video.provider_ref);
                  setTitle(video.title);
                  setEditing(true);
                }}
              >
                Replace video
              </Button>
              <Button variant="danger" onClick={onRemove} isLoading={deleteVideo.isPending}>
                Remove
              </Button>
            </div>
          )}
        </div>
      )}

      {!video && !editing && canEdit && (
        <div className="mt-4">
          <Button variant="secondary" onClick={() => setEditing(true)}>
            Add a video
          </Button>
        </div>
      )}

      {editing && (
        <div className="mt-4 flex flex-col gap-3">
          <Input
            label="Video URL"
            placeholder="YouTube, Vimeo, or a direct .mp4 link"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
          />
          <Input
            label="Title (optional)"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
          <div className="flex gap-2">
            <Button onClick={onSave} isLoading={setVideo.isPending}>
              Save
            </Button>
            <Button variant="secondary" onClick={() => setEditing(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
}
