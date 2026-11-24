import React, { useEffect, useState } from "react";
import { resolveBrandVisualMeta } from "../utils/brandMeta";

interface BrandLogoProps {
  brand: string;
  domain?: string;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  className?: string;
  glow?: boolean;
}

const SIZE_MAP = {
  xs: { box: "h-5 w-5 rounded-md", img: "h-3.5 w-3.5", text: "text-[10px]" },
  sm: { box: "h-7 w-7 rounded-lg", img: "h-4 w-4", text: "text-xs" },
  md: { box: "h-10 w-10 rounded-xl", img: "h-6 w-6", text: "text-sm" },
  lg: { box: "h-14 w-14 rounded-2xl", img: "h-8 w-8", text: "text-lg" },
  xl: { box: "h-16 w-16 rounded-2xl", img: "h-10 w-10", text: "text-xl" },
};

export const BrandLogo: React.FC<BrandLogoProps> = ({
  brand,
  domain,
  size = "md",
  className = "",
  glow = false,
}) => {
  const meta = resolveBrandVisualMeta(brand, domain);
  // Tier 0: SimpleIcons crisp vector SVG -> Tier 1: Google High-Res Favicon -> Tier 2: Glowing Monogram
  const [tier, setTier] = useState<0 | 1 | 2>(0);

  useEffect(() => {
    setTier(0);
  }, [brand, domain]);

  const sz = SIZE_MAP[size];
  const initials = brand
    .trim()
    .split(/\s+/)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const src =
    tier === 0
      ? `https://cdn.simpleicons.org/${meta.slug}/ffffff?viewbox=auto`
      : tier === 1
      ? `https://www.google.com/s2/favicons?domain=${encodeURIComponent(meta.domain)}&sz=128`
      : "";

  return (
    <div
      className={`relative flex shrink-0 items-center justify-center overflow-hidden border border-white/15 bg-obsidian-900/90 ${sz.box} ${className}`}
      style={{
        boxShadow: glow ? `0 0 26px ${meta.accent}55, inset 0 0 12px ${meta.accent}33` : undefined,
        background:
          tier === 2
            ? `linear-gradient(135deg, ${meta.accent}, ${meta.secondary})`
            : `radial-gradient(circle at 30% 25%, ${meta.accent}28, rgba(10, 16, 32, 0.94))`,
      }}
      title={brand}
    >
      {tier < 2 ? (
        <img
          src={src}
          alt={`${brand} logo`}
          className={`${sz.img} object-contain ${tier === 1 ? "rounded-sm" : ""}`}
          loading="lazy"
          onError={() => setTier((prev) => (prev === 0 ? 1 : 2))}
        />
      ) : (
        <span className={`font-display font-extrabold tracking-tight text-white ${sz.text}`}>
          {initials || "B"}
        </span>
      )}
    </div>
  );
};
