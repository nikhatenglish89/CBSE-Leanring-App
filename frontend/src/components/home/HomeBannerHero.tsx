import { bannerImageUrl } from "../../hooks/useBanners";
import type { Banner } from "../../types/banners";

/** Admin-published banners take over the hero spot entirely when at
 * least one is active — the primary (lowest display_order) banner large,
 * roughly half the page, with any additional banners in a row beneath
 * it. HomePage renders its own default hero instead when there are none. */
export function HomeBannerHero({ banners }: { banners: Banner[] }) {
  const [primary, ...rest] = banners;

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-violet-700">
      <div
        className="bg-hero-grid absolute inset-0 opacity-40 [background-size:22px_22px]"
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full bg-accent-400/30 blur-3xl"
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute -left-24 bottom-0 h-80 w-80 rounded-full bg-violet-500/30 blur-3xl"
        aria-hidden="true"
      />

      <div className="page-shell relative flex flex-col gap-5 py-14 sm:py-20">
        <BannerFrame banner={primary} />

        {rest.length > 0 && (
          <div className="flex gap-4 overflow-x-auto pb-1">
            {rest.map((banner) => (
              <div key={banner.id} className="w-56 shrink-0 sm:w-64">
                <BannerFrame banner={banner} compact />
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

function BannerFrame({ banner, compact }: { banner: Banner; compact?: boolean }) {
  const frame = (
    <div
      className={`flex w-full items-center justify-center overflow-hidden rounded-2xl bg-white/95 shadow-soft ${
        compact ? "h-32 sm:h-36" : "min-h-[320px] sm:min-h-[420px] lg:min-h-[50vh]"
      }`}
    >
      <img src={bannerImageUrl(banner.id)} alt={banner.title} className="h-full w-full object-contain" />
    </div>
  );

  return banner.link_url ? (
    <a href={banner.link_url} target="_blank" rel="noopener noreferrer" className="hover-lift block">
      {frame}
    </a>
  ) : (
    frame
  );
}
