import React, { Component, ErrorInfo, ReactNode, useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Html, Line, MeshDistortMaterial, OrbitControls, Sparkles, Stars } from "@react-three/drei";
import * as THREE from "three";
import { Layers, Orbit, Pause, Play } from "lucide-react";
import { AspectBreakdownRow, MentionItem } from "../types";
import { BrandLogo } from "./BrandLogo";
import { resolveBrandVisualMeta } from "../utils/brandMeta";

interface SentimentOrb3DProps {
  brand: string;
  brandDomain?: string;
  industry?: string;
  netSentimentScore: number;
  crisisLevel: string;
  mentions: MentionItem[];
  aspectBreakdown?: AspectBreakdownRow[];
  selectedMentionId: string | null;
  onSelectMention: (mention: MentionItem) => void;
}

function getCorePalette(crisisLevel: string, nss: number, brandAccent: string) {
  if (crisisLevel === "CRITICAL_CRISIS") {
    return { main: "#ef4444", emissive: "#991b1b", ring: "#fb7185", wire: "#fca5a5", distort: 0.52, speed: 4.2 };
  }
  if (crisisLevel === "ELEVATED") {
    return { main: "#f97316", emissive: "#9a3412", ring: "#fdba74", wire: "#fb923c", distort: 0.38, speed: 2.9 };
  }
  if (crisisLevel === "WATCH" || nss < 5) {
    return { main: "#eab308", emissive: "#854d0e", ring: "#fde047", wire: "#facc15", distort: 0.32, speed: 2.1 };
  }
  return { main: "#06b6d4", emissive: "#0e7490", ring: "#34d399", wire: brandAccent || "#38bdf8", distort: 0.28, speed: 1.7 };
}

const HolographicCore: React.FC<{
  brand: string;
  brandDomain?: string;
  crisisLevel: string;
  nss: number;
}> = ({ brand, brandDomain, crisisLevel, nss }) => {
  const brandMeta = resolveBrandVisualMeta(brand, brandDomain);
  const palette = getCorePalette(crisisLevel, nss, brandMeta.accent);
  const cageRef = useRef<THREE.Mesh>(null);
  const ring1Ref = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);
  const ring3Ref = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    const mult = crisisLevel === "CRITICAL_CRISIS" ? 2.2 : 1.0;
    if (cageRef.current) {
      cageRef.current.rotation.y -= delta * 0.28 * mult;
      cageRef.current.rotation.x += delta * 0.14 * mult;
      const pulse = 1 + Math.sin(state.clock.elapsedTime * 2.2 * mult) * 0.035;
      cageRef.current.scale.setScalar(pulse);
    }
    if (ring1Ref.current) {
      ring1Ref.current.rotation.z += delta * 0.42 * mult;
      ring1Ref.current.rotation.x += delta * 0.12;
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.y -= delta * 0.35 * mult;
      ring2Ref.current.rotation.z -= delta * 0.18;
    }
    if (ring3Ref.current) {
      ring3Ref.current.rotation.x -= delta * 0.25 * mult;
      ring3Ref.current.rotation.y += delta * 0.22;
    }
  });

  return (
    <group>
      {/* Inner Liquid-Metal Distorted Core */}
      <Float speed={palette.speed} rotationIntensity={0.35} floatIntensity={0.4}>
        <mesh>
          <sphereGeometry args={[1.28, 64, 64]} />
          <MeshDistortMaterial
            color={palette.main}
            emissive={palette.emissive}
            emissiveIntensity={0.75}
            roughness={0.12}
            metalness={0.82}
            distort={palette.distort}
            speed={palette.speed}
          />
        </mesh>
      </Float>

      {/* Outer Holographic Geodesic Wireframe Shield */}
      <mesh ref={cageRef}>
        <icosahedronGeometry args={[1.68, 1]} />
        <meshStandardMaterial
          color={palette.wire}
          emissive={palette.wire}
          emissiveIntensity={0.65}
          wireframe
          transparent
          opacity={0.38}
        />
      </mesh>

      {/* 3 Gyroscope Orbital Rings */}
      <mesh ref={ring1Ref} rotation={[Math.PI / 2.6, 0.3, 0]}>
        <torusGeometry args={[2.18, 0.02, 16, 120]} />
        <meshStandardMaterial color={palette.ring} emissive={palette.ring} emissiveIntensity={1.1} transparent opacity={0.8} />
      </mesh>
      <mesh ref={ring2Ref} rotation={[Math.PI / 1.75, -0.55, 0.45]}>
        <torusGeometry args={[2.68, 0.015, 16, 120]} />
        <meshStandardMaterial color="#818cf8" emissive="#6366f1" emissiveIntensity={0.95} transparent opacity={0.55} />
      </mesh>
      <mesh ref={ring3Ref} rotation={[0.45, 0.9, Math.PI / 3]}>
        <torusGeometry args={[3.15, 0.01, 16, 120]} />
        <meshStandardMaterial color={palette.main} emissive={palette.main} emissiveIntensity={0.8} transparent opacity={0.35} />
      </mesh>

      {/* Center Floating Holographic Brand Logo Emblem */}
      <Html center distanceFactor={8.5} zIndexRange={[20, 0]}>
        <div className="pointer-events-none flex flex-col items-center">
          <div className="relative rounded-2xl border border-white/25 bg-obsidian-950/75 p-2 shadow-2xl backdrop-blur-md">
            <BrandLogo brand={brand} domain={brandDomain} size="lg" glow />
            <span
              className={`absolute -right-1.5 -top-1.5 h-3.5 w-3.5 rounded-full border-2 border-obsidian-950 ${
                crisisLevel === "CRITICAL_CRISIS"
                  ? "animate-ping bg-rose-500"
                  : crisisLevel === "ELEVATED"
                  ? "bg-orange-400"
                  : "bg-emerald-400"
              }`}
            />
          </div>
          <div className="mt-1.5 rounded-full border border-white/15 bg-obsidian-950/85 px-2.5 py-0.5 font-mono text-[10px] font-bold tracking-wide text-white shadow-lg backdrop-blur">
            {brand.toUpperCase()} • {nss >= 0 ? "+" : ""}
            {nss.toFixed(1)}
          </div>
        </div>
      </Html>
    </group>
  );
};

const CyberGridFloor: React.FC<{ color: string }> = ({ color }) => (
  <group position={[0, -3.1, 0]}>
    <gridHelper args={[24, 24, color, "#1e293b"]} />
  </group>
);

const OrbitingMentionNode: React.FC<{
  mention: MentionItem;
  index: number;
  total: number;
  isSelected: boolean;
  onSelect: (m: MentionItem) => void;
}> = ({ mention, index, total, isSelected, onSelect }) => {
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState(false);
  const [beamEnd, setBeamEnd] = useState<[number, number, number]>([0, 0, 0]);

  const orbitParams = useMemo(() => {
    const phi = Math.acos(1 - (2 * (index + 0.5)) / Math.max(total, 1));
    const theta = Math.PI * (1 + Math.sqrt(5)) * index;
    const radius = 2.85 + (index % 3) * 0.48;
    const speed = 0.14 + (index % 5) * 0.035;
    return { phi, theta, radius, speed };
  }, [index, total]);

  useFrame((state) => {
    const angle = orbitParams.theta + state.clock.getElapsedTime() * orbitParams.speed;
    const x = orbitParams.radius * Math.sin(orbitParams.phi) * Math.cos(angle);
    const y = orbitParams.radius * Math.cos(orbitParams.phi) * 0.72;
    const z = orbitParams.radius * Math.sin(orbitParams.phi) * Math.sin(angle);
    if (groupRef.current) {
      groupRef.current.position.set(x, y, z);
    }
    if (hovered || isSelected) {
      setBeamEnd([x, y, z]);
    }
  });

  const color =
    mention.sentiment_label === "Positive"
      ? "#10b981"
      : mention.sentiment_label === "Negative"
      ? "#f43f5e"
      : "#f59e0b";

  return (
    <>
      {(hovered || isSelected) && (
        <Line points={[[0, 0, 0], beamEnd]} color={color} lineWidth={2.2} transparent opacity={0.85} />
      )}
      <group ref={groupRef}>
        <mesh
          scale={isSelected ? 1.75 : hovered ? 1.5 : 1.0}
          onClick={(e) => {
            e.stopPropagation();
            onSelect(mention);
          }}
          onPointerOver={(e) => {
            e.stopPropagation();
            setHovered(true);
            document.body.style.cursor = "pointer";
          }}
          onPointerOut={() => {
            setHovered(false);
            document.body.style.cursor = "default";
          }}
        >
          <octahedronGeometry args={[0.14, 2]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={isSelected || hovered ? 1.8 : 0.85}
            roughness={0.2}
            metalness={0.4}
          />
          {(hovered || isSelected) && (
            <Html distanceFactor={10} center>
              <div className="pointer-events-none w-56 rounded-xl border border-cyan-500/40 bg-obsidian-950/95 px-3 py-2.5 text-[11px] text-slate-100 shadow-2xl backdrop-blur-md">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-[10px] font-bold uppercase text-cyan-300">{mention.source}</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                      mention.sentiment_label === "Positive"
                        ? "bg-emerald-500/20 text-emerald-300"
                        : mention.sentiment_label === "Negative"
                        ? "bg-rose-500/20 text-rose-300"
                        : "bg-amber-500/20 text-amber-300"
                    }`}
                  >
                    {mention.sentiment_label} ({mention.ensemble_score >= 0 ? "+" : ""}
                    {mention.ensemble_score.toFixed(2)})
                  </span>
                </div>
                <p className="mt-1.5 line-clamp-2 font-semibold leading-snug text-white">{mention.title}</p>
                <p className="mt-1 font-mono text-[10px] text-cyan-300/90">
                  VADER {mention.vader_score.toFixed(2)} • BERT {mention.bert_score.toFixed(2)}
                </p>
              </div>
            </Html>
          )}
        </mesh>
      </group>
    </>
  );
};

const AspectConstellationNode: React.FC<{
  item: AspectBreakdownRow;
  index: number;
  total: number;
}> = ({ item, index, total }) => {
  const ref = useRef<THREE.Group>(null);
  const angle0 = (index / Math.max(total, 1)) * Math.PI * 2;
  const radius = 3.25;
  const yOffset = ((index % 3) - 1) * 0.85;

  const net = item.positive - item.negative;
  const color = net > 0 ? "#10b981" : net < 0 ? "#f43f5e" : "#f59e0b";
  const nodeSize = Math.min(0.46, 0.22 + item.total * 0.025);

  useFrame((state) => {
    if (!ref.current) return;
    const t = angle0 + state.clock.getElapsedTime() * 0.14;
    ref.current.position.set(Math.cos(t) * radius, yOffset + Math.sin(t * 1.5) * 0.2, Math.sin(t) * radius);
  });

  return (
    <group ref={ref}>
      <mesh>
        <dodecahedronGeometry args={[nodeSize, 1]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.0} roughness={0.2} metalness={0.6} />
      </mesh>
      <Html distanceFactor={10} center>
        <div className="pointer-events-none whitespace-nowrap rounded-lg border border-white/15 bg-obsidian-950/90 px-2.5 py-1 text-center shadow-xl backdrop-blur">
          <div className="text-[11px] font-bold text-white">{item.aspect}</div>
          <div className="font-mono text-[10px]">
            <span className="text-emerald-400">+{item.positive}</span>{" "}
            <span className="text-amber-300">~{item.neutral}</span>{" "}
            <span className="text-rose-400">-{item.negative}</span>
          </div>
        </div>
      </Html>
    </group>
  );
};

class WebGLErrorBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { hasError: boolean }> {
  constructor(props: { children: ReactNode; fallback: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }
  componentDidCatch(_err: Error, _info: ErrorInfo) {}
  render() {
    return this.state.hasError ? this.props.fallback : this.props.children;
  }
}

export const SentimentOrb3D: React.FC<SentimentOrb3DProps> = ({
  brand,
  brandDomain,
  industry,
  netSentimentScore,
  crisisLevel,
  mentions,
  aspectBreakdown = [],
  selectedMentionId,
  onSelectMention,
}) => {
  const [sceneMode, setSceneMode] = useState<"mentions" | "aspects">("mentions");
  const [autoRotate, setAutoRotate] = useState<boolean>(true);
  const visibleNodes = useMemo(() => mentions.slice(0, 28), [mentions]);
  const brandMeta = resolveBrandVisualMeta(brand, brandDomain);
  const palette = getCorePalette(crisisLevel, netSentimentScore, brandMeta.accent);

  const fallbackUI = (
    <div className="flex h-full w-full flex-col items-center justify-center p-6 text-center">
      <BrandLogo brand={brand} domain={brandDomain} size="xl" glow />
      <p className="mt-4 font-display text-base font-bold text-white">{brand} Reputation Core</p>
      <p className="text-xs text-slate-400">WebGL disabled — displaying 2D holographic fallback</p>
    </div>
  );

  return (
    <div className="glass-panel holo-border relative h-[475px] overflow-hidden rounded-2xl">
      {/* Subtle Holographic Scanline */}
      <div className="holo-scanline pointer-events-none absolute inset-x-0 top-0 z-10 h-16 bg-gradient-to-b from-cyan-400/10 to-transparent" />

      {/* Top HUD Overlay */}
      <div className="absolute left-4 right-4 top-4 z-20 flex flex-wrap items-start justify-between gap-2">
        <div className="flex items-center gap-3">
          <BrandLogo brand={brand} domain={brandDomain} size="md" glow />
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-cyan-400">
                3D Holographic Core
              </span>
              {industry && (
                <span className="rounded-full border border-indigo-400/35 bg-indigo-500/15 px-2 py-0.5 text-[10px] font-semibold text-indigo-200">
                  {industry}
                </span>
              )}
            </div>
            <h2 className="font-display text-lg font-bold text-white">{brand} Sentiment Telemetry</h2>
          </div>
        </div>

        {/* Scene Controls */}
        <div className="flex items-center gap-1.5 rounded-xl border border-slate-700/80 bg-obsidian-950/85 p-1 backdrop-blur">
          <button
            type="button"
            onClick={() => setSceneMode("mentions")}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${
              sceneMode === "mentions" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            <Orbit className="h-3.5 w-3.5" /> Mentions
          </button>
          <button
            type="button"
            onClick={() => setSceneMode("aspects")}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${
              sceneMode === "aspects" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            <Layers className="h-3.5 w-3.5" /> Aspects
          </button>
          <button
            type="button"
            onClick={() => setAutoRotate((r) => !r)}
            title={autoRotate ? "Pause 3D orbit" : "Resume 3D orbit"}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-cyan-300"
          >
            {autoRotate ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
          </button>
        </div>
      </div>

      {/* Interactive 3D WebGL Canvas */}
      <WebGLErrorBoundary fallback={fallbackUI}>
        <Canvas camera={{ position: [0, 1.5, 7.6], fov: 46 }} dpr={[1, 2]}>
          <ambientLight intensity={0.7} />
          <pointLight position={[8, 9, 8]} intensity={1.9} color="#ffffff" />
          <pointLight position={[-8, -5, -7]} intensity={1.1} color={palette.main} />
          <pointLight position={[0, 6, -6]} intensity={0.9} color="#818cf8" />

          <Stars radius={50} depth={35} count={1400} factor={3} fade speed={1.0} />
          <Sparkles count={70} scale={9} size={2.2} speed={0.5} opacity={0.55} color={palette.ring} />
          <CyberGridFloor color={palette.main} />

          <HolographicCore brand={brand} brandDomain={brandDomain} crisisLevel={crisisLevel} nss={netSentimentScore} />

          {sceneMode === "mentions"
            ? visibleNodes.map((m, idx) => (
                <OrbitingMentionNode
                  key={m.id}
                  mention={m}
                  index={idx}
                  total={visibleNodes.length}
                  isSelected={selectedMentionId === m.id}
                  onSelect={onSelectMention}
                />
              ))
            : aspectBreakdown.map((asp, idx) => (
                <AspectConstellationNode
                  key={asp.aspect}
                  item={asp}
                  index={idx}
                  total={aspectBreakdown.length}
                />
              ))}

          <OrbitControls
            enablePan={false}
            minDistance={4.8}
            maxDistance={12}
            autoRotate={autoRotate}
            autoRotateSpeed={0.6}
          />
        </Canvas>
      </WebGLErrorBoundary>

      {/* Bottom Legend HUD */}
      <div className="pointer-events-none absolute bottom-3 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-800/90 bg-obsidian-950/80 px-3.5 py-2 text-[11px] text-slate-300 backdrop-blur">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400" /> Positive</span>
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-amber-400 shadow-sm shadow-amber-400" /> Neutral</span>
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500" /> Negative</span>
        </div>
        <span className="text-slate-400">
          {sceneMode === "mentions"
            ? "Drag to orbit • Hover for laser beam • Click node to inspect"
            : "3D Aspect Constellation — Node size = mention volume"}
        </span>
      </div>
    </div>
  );
};
