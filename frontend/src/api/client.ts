import {
  AnalyzeResponse,
  BrandSummary,
  EvaluationResponse,
  OntologyFrame,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE || "";

async function requestJson<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API Error (${res.status}): ${text || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function fetchKnownBrands(): Promise<BrandSummary[]> {
  return requestJson<BrandSummary[]>("/api/brands");
}

export function analyzeBrandApi(params: {
  brand: string;
  competitors?: string[];
  live?: boolean;
  simulateCrisis?: boolean;
  useTransformer?: boolean;
}): Promise<AnalyzeResponse> {
  const qs = new URLSearchParams();
  qs.set("brand", params.brand);
  if (params.competitors && params.competitors.length > 0) {
    qs.set("competitors", params.competitors.join(","));
  }
  qs.set("live", String(params.live ?? true));
  qs.set("simulate_crisis", String(params.simulateCrisis ?? false));
  qs.set("use_transformer", String(params.useTransformer ?? true));
  return requestJson<AnalyzeResponse>(`/api/analyze?${qs.toString()}`);
}

export function fetchEvaluationApi(refresh = false): Promise<EvaluationResponse> {
  return requestJson<EvaluationResponse>(`/api/evaluation?refresh=${refresh}`);
}

export function fetchOntologyApi(): Promise<{ frames: OntologyFrame[] }> {
  return requestJson<{ frames: OntologyFrame[] }>("/api/ontology");
}
