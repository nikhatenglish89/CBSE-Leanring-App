import { bannerImageUrl } from "../../hooks/useBanners";
import type { Banner } from "../../types/banners";

/** No fixed-height box, and no object-cover/object-contain — either one
 * forces a shape onto the image (cropping it, or letterboxing it with
 * blank space) unless it happens to match that exact aspect ratio. The
 * image instead just renders at its own natural aspect ratio, scaled to
 * fill the available width, so it always shows completely with zero
 * blank space regardless of what shape an admin uploads. */
function BannerImage({ banner, className }: { banner: Banner; className: string }) {
  const img = (
    <img
      src={bannerImageUrl(banner.id)}
      alt={banner.title}
      className={`w-full rounded-2xl shadow-soft ${className}`}
    />
  );

  return banner.link_url ? (
    <a href={banner.link_url} target="_blank" rel="noopener noreferrer" className="hover-lift block w-full">
      {img}
    </a>
  ) : (
    img
  );
}

/** Sits in the hero's illustration slot (right column, next to the
 * "Learn Smarter..." copy) — the single highest-priority banner. */
export function HeroBannerImage({ banner }: { banner: Banner }) {
  return <BannerImage banner={banner} className="" />;
}

/** Any banners beyond the first render here, in a row directly below the
 * hero section — still prominent, but secondary to the hero banner. Each
 * card sizes to its own image's aspect ratio (items-start keeps the row
 * from stretching shorter images to match a taller neighbor). */
export function SecondaryBannerStrip({ banners }: { banners: Banner[] }) {
  if (banners.length === 0) return null;

  return (
    <section className="border-b border-slate-200 bg-white py-8">
      <div className="page-shell">
        <div className="flex items-start gap-5 overflow-x-auto pb-2">
          {banners.map((banner) => (
            <div key={banner.id} className="w-64 shrink-0 sm:w-80">
              <BannerImage banner={banner} className="" />
              <p className="mt-2 truncate text-sm font-medium text-slate-700">{banner.title}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
