import { bannerImageUrl } from "../../hooks/useBanners";
import type { Banner } from "../../types/banners";

function BannerFrame({ banner, className }: { banner: Banner; className: string }) {
  const frame = (
    <div
      className={`flex items-center justify-center overflow-hidden rounded-2xl bg-white/95 shadow-soft ${className}`}
    >
      <img src={bannerImageUrl(banner.id)} alt={banner.title} className="h-full w-full object-contain" />
    </div>
  );

  return banner.link_url ? (
    <a href={banner.link_url} target="_blank" rel="noopener noreferrer" className="hover-lift block w-full">
      {frame}
    </a>
  ) : (
    frame
  );
}

/** Sits in the hero's illustration slot (right column, next to the
 * "Learn Smarter..." copy) — the single highest-priority banner, sized
 * to roughly match the footprint of the illustration it replaces. */
export function HeroBannerImage({ banner }: { banner: Banner }) {
  return <BannerFrame banner={banner} className="h-[320px] w-full max-w-md sm:h-[380px]" />;
}

/** Any banners beyond the first render here, in a row directly below the
 * hero section — still prominent, but secondary to the hero banner. */
export function SecondaryBannerStrip({ banners }: { banners: Banner[] }) {
  if (banners.length === 0) return null;

  return (
    <section className="border-b border-slate-200 bg-white py-8">
      <div className="page-shell">
        <div className="flex gap-5 overflow-x-auto pb-2">
          {banners.map((banner) => (
            <div key={banner.id} className="w-64 shrink-0 sm:w-80">
              <BannerFrame banner={banner} className="h-36 w-full sm:h-40" />
              <p className="mt-2 truncate text-sm font-medium text-slate-700">{banner.title}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
