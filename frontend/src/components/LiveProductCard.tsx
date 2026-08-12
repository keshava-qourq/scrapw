import type { LiveProduct } from "../types";

const MARKETPLACE_STYLES: Record<string, string> = {
  AMAZON: "bg-orange-50 text-orange-700 ring-orange-200",
  FLIPKART: "bg-blue-50 text-blue-700 ring-blue-200",
  AJIO: "bg-rose-50 text-rose-700 ring-rose-200",
  MYNTRA: "bg-pink-50 text-pink-700 ring-pink-200",
  OTHER: "bg-slate-50 text-slate-700 ring-slate-200",
};

function money(v: number | null) {
  if (v == null) return null;
  return v.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

export default function LiveProductCard({ product }: { product: LiveProduct }) {
  const price = money(product.price);
  const originalPrice = money(product.original_price);
  const discount = product.discount_percentage != null ? Math.round(product.discount_percentage) : null;
  const rating = product.rating != null ? product.rating.toFixed(1) : null;
  const badgeStyle = MARKETPLACE_STYLES[product.marketplace] ?? MARKETPLACE_STYLES.OTHER;
  const outOfStock = product.availability === "OUT_OF_STOCK";

  return (
    <a
      href={product.product_url}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="relative aspect-square w-full overflow-hidden bg-slate-100">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.title}
            loading="lazy"
            className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-sm text-slate-400">No image</div>
        )}
        <span
          className={`absolute left-2.5 top-2.5 rounded-full px-2 py-0.5 text-xs font-medium capitalize ring-1 ring-inset ${badgeStyle}`}
        >
          {product.marketplace}
        </span>
        {outOfStock && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/70 backdrop-blur-[1px]">
            <span className="rounded-full bg-slate-900/80 px-3 py-1 text-xs font-medium text-white">Out of stock</span>
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-1.5 p-4">
        {product.seller && <span className="text-xs font-medium uppercase tracking-wide text-slate-400">{product.seller}</span>}
        <h3 className="line-clamp-2 text-sm font-medium leading-snug text-slate-900">{product.title}</h3>

        {rating && (
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <span className="flex items-center gap-0.5 font-medium text-emerald-700">
              {rating}
              <svg className="h-3.5 w-3.5 fill-emerald-600" viewBox="0 0 20 20">
                <path d="M10 1l2.6 5.9 6.4.6-4.8 4.3 1.4 6.2L10 14.9 4.4 18l1.4-6.2L1 7.5l6.4-.6z" />
              </svg>
            </span>
            {product.review_count != null && <span>({product.review_count.toLocaleString()})</span>}
          </div>
        )}

        <div className="mt-auto pt-2">
          <div className="flex items-baseline gap-2">
            {price ? (
              <span className={`text-lg font-semibold ${product.effective_price != null ? "text-slate-400 line-through" : "text-slate-900"}`}>
                ₹{price}
              </span>
            ) : (
              <span className="text-sm text-slate-400">Price unavailable</span>
            )}
            {product.effective_price == null && originalPrice && originalPrice !== price && (
              <span className="text-sm text-slate-400 line-through">₹{originalPrice}</span>
            )}
            {product.effective_price == null && discount != null && discount > 0 && (
              <span className="text-sm font-medium text-emerald-600">{discount}% off</span>
            )}
          </div>
          {product.effective_price != null && (
            <div className="mt-0.5 flex items-center gap-1.5">
              <span className="text-lg font-semibold text-emerald-700">₹{money(product.effective_price)}</span>
              <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200">
                with card offer
              </span>
            </div>
          )}
          {product.applied_offer && (
            <p className="mt-0.5 line-clamp-1 text-xs text-slate-400">{product.applied_offer}</p>
          )}
        </div>
      </div>
    </a>
  );
}
