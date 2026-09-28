import { motion, useMotionTemplate, useMotionValue, useSpring } from "motion/react";
import { useState, type PointerEvent } from "react";
import type { LiveProduct } from "../types";
import { ArrowUpRight, StarIcon } from "./ui/icons";
import { EASE } from "./ui/motion";

const MARKETPLACE_DOT: Record<string, string> = {
  AMAZON: "bg-[#ff9900]",
  FLIPKART: "bg-[#2874f0]",
  MYNTRA: "bg-[#ff3f6c]",
  AJIO: "bg-[#2c4152]",
  OTHER: "bg-ash",
};

function money(v: number | null) {
  if (v == null) return null;
  return v.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

function marketplaceName(code: string) {
  return code === "AJIO" ? "AJIO" : code.charAt(0) + code.slice(1).toLowerCase();
}

interface Props {
  product: LiveProduct;
  index: number;
}

export default function LiveProductCard({ product, index }: Props) {
  const [imageFailed, setImageFailed] = useState(false);
  const price = money(product.price);
  const originalPrice = money(product.original_price);
  const effectivePrice = money(product.effective_price);
  const discount = product.discount_percentage != null ? Math.round(product.discount_percentage) : null;
  const rating = product.rating != null ? product.rating.toFixed(1) : null;
  const outOfStock = product.availability === "OUT_OF_STOCK";
  // Results outside the four big marketplaces come back as OTHER — name the actual seller instead.
  const store =
    product.marketplace === "OTHER" ? (product.seller ?? "store") : marketplaceName(product.marketplace);

  // Pointer-driven 3D tilt with a soft glare that follows the cursor (mouse only).
  const tiltX = useSpring(0, { stiffness: 220, damping: 20 });
  const tiltY = useSpring(0, { stiffness: 220, damping: 20 });
  const glareX = useMotionValue(50);
  const glareY = useMotionValue(50);
  const glare = useMotionTemplate`radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255,255,255,0.55), transparent 55%)`;

  function handleTilt(e: PointerEvent<HTMLDivElement>) {
    if (e.pointerType !== "mouse") return;
    const rect = e.currentTarget.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width;
    const py = (e.clientY - rect.top) / rect.height;
    tiltY.set((px - 0.5) * 9);
    tiltX.set((0.5 - py) * 9);
    glareX.set(px * 100);
    glareY.set(py * 100);
  }

  function resetTilt() {
    tiltX.set(0);
    tiltY.set(0);
  }

  return (
    <motion.a
      href={product.product_url}
      target="_blank"
      rel="noopener noreferrer"
      data-cursor="View ↗"
      layout
      initial={{ opacity: 0, y: 48 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "0px 0px -8% 0px" }}
      transition={{ duration: 0.9, ease: EASE, delay: (index % 4) * 0.07 }}
      className="group block outline-none"
    >
      <motion.div
        onPointerMove={handleTilt}
        onPointerLeave={resetTilt}
        style={{ rotateX: tiltX, rotateY: tiltY, transformPerspective: 900 }}
        className="relative aspect-[4/5] overflow-hidden rounded-[6px] bg-bone ring-ink/0 transition-[box-shadow] duration-500 group-focus-visible:ring-2 group-focus-visible:ring-ink"
      >
        {product.image_url && !imageFailed ? (
          <img
            src={product.image_url}
            alt={product.title}
            loading="lazy"
            onError={() => setImageFailed(true)}
            className="h-full w-full object-contain p-7 mix-blend-multiply transition-transform duration-[1.4s] ease-expo group-hover:scale-[1.08]"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center p-6 text-center font-serif text-2xl italic text-ash/70">
            {product.brand ?? store}
          </div>
        )}

        <span className="absolute left-3 top-3 flex max-w-[calc(100%-5.5rem)] items-center gap-1.5 rounded-full bg-paper/90 px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.12em] backdrop-blur">
          <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${MARKETPLACE_DOT[product.marketplace] ?? MARKETPLACE_DOT.OTHER}`} />
          <span className="truncate">{store}</span>
        </span>

        {discount != null && discount > 0 && (
          <span className="absolute right-3 top-3 rounded-full bg-acid px-2.5 py-1 font-mono text-[11px] font-medium tabular-nums">
            −{discount}%
          </span>
        )}

        <div className="absolute inset-x-3 bottom-3 flex translate-y-[calc(100%+1rem)] items-center justify-between rounded-full bg-ink py-2.5 pl-4 pr-2.5 text-[13px] font-medium text-paper transition-transform duration-700 ease-expo group-hover:translate-y-0">
          <span className="truncate">View on {store}</span>
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-acid text-ink">
            <ArrowUpRight className="h-3.5 w-3.5" />
          </span>
        </div>

        {outOfStock && (
          <div className="absolute inset-0 flex items-center justify-center bg-paper/60 backdrop-blur-[2px]">
            <span className="rounded-full border border-ink px-3 py-1 font-mono text-[10px] uppercase tracking-[0.16em]">
              Out of stock
            </span>
          </div>
        )}

        <motion.div
          aria-hidden
          style={{ backgroundImage: glare }}
          className="pointer-events-none absolute inset-0 opacity-0 mix-blend-soft-light transition-opacity duration-500 group-hover:opacity-100"
        />
      </motion.div>

      <div className="mt-4 flex flex-col gap-1">
        {(product.brand || (product.seller && product.marketplace !== "OTHER")) && (
          <span className="truncate font-mono text-[10px] uppercase tracking-[0.16em] text-ash">
            {product.brand ?? (product.marketplace === "OTHER" ? null : product.seller)}
          </span>
        )}
        <h3 className="line-clamp-2 text-[14px] leading-snug text-ink/90 transition-colors group-hover:text-ink">
          {product.title}
        </h3>

        <div className="mt-2 flex flex-wrap items-baseline gap-x-2.5 gap-y-1">
          {effectivePrice ? (
            <>
              <span className="text-[19px] font-medium tracking-[-0.02em] tabular-nums">₹{effectivePrice}</span>
              <span className="text-[13px] text-ash line-through tabular-nums">₹{price}</span>
            </>
          ) : price ? (
            <>
              <span className="text-[19px] font-medium tracking-[-0.02em] tabular-nums">₹{price}</span>
              {originalPrice && originalPrice !== price && (
                <span className="text-[13px] text-ash line-through tabular-nums">₹{originalPrice}</span>
              )}
            </>
          ) : (
            <span className="text-sm text-ash">Price unavailable</span>
          )}

          {rating && (
            <span className="ml-auto flex items-center gap-1 font-mono text-[11px] text-ash tabular-nums">
              <StarIcon className="h-3 w-3 text-ink" />
              {rating}
              {product.review_count != null && <span>({product.review_count.toLocaleString("en-IN")})</span>}
            </span>
          )}
        </div>

        {effectivePrice && (
          <span className="mt-1 w-fit rounded-full bg-acid px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.12em]">
            With your card
          </span>
        )}
        {product.applied_offer && <p className="line-clamp-1 text-xs text-ash">{product.applied_offer}</p>}
      </div>
    </motion.a>
  );
}
