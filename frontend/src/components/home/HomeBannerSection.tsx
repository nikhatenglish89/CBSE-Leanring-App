import { bannerImageUrl, usePublicBanners } from "../../hooks/useBanners";

/** Admin-published banners for result showcases, advertising, and
 * announcements — publicly visible, no login required. Renders nothing
 * when there are no active banners, so it never leaves an empty gap on
 * the home page. */
export function HomeBannerSection() {
  const { data: banners } = usePublicBanners();

  if (!banners || banners.length === 0) return null;

  return (
    <section className="border-b border-slate-200 bg-white py-10">
      <div className="page-shell">
        <div className="flex gap-5 overflow-x-auto pb-2">
          {banners.map((banner) => {
            const image = (
              <div className="flex h-48 w-full items-center justify-center overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 shadow-card sm:h-56">
                {/* object-contain (not cover) — a banner's whole image
                 * must stay visible regardless of its aspect ratio,
                 * rather than being cropped to fill a fixed box. */}
                <img
                  src={bannerImageUrl(banner.id)}
                  alt={banner.title}
                  className="h-full w-full object-contain"
                />
              </div>
            );
            return (
              <div key={banner.id} className="w-72 shrink-0 sm:w-96">
                {banner.link_url ? (
                  <a
                    href={banner.link_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover-lift block"
                  >
                    {image}
                  </a>
                ) : (
                  image
                )}
                <p className="mt-2 truncate text-sm font-medium text-slate-700">{banner.title}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
