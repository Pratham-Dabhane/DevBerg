import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "../api/client";

// Phase 1-5
export const useMetrics = () =>
  useQuery({ queryKey: ["metrics"], queryFn: api.metricsLatest, staleTime: 60_000 });

export const usePredictions = () =>
  useQuery({ queryKey: ["predictions"], queryFn: api.predictions, staleTime: 60_000 });

export const useHealthReports = () =>
  useQuery({ queryKey: ["healthReports"], queryFn: api.health, staleTime: 60_000 });

export const useEmergingInsights = (top = 10) =>
  useQuery({ queryKey: ["emergingInsights", top], queryFn: () => api.emerging(top), staleTime: 60_000 });

export const useTrends = (tech?: string, category?: string) =>
  useQuery({ queryKey: ["trends", tech, category], queryFn: () => api.trends(tech, category), staleTime: 60_000 });

export const useRisks = () =>
  useQuery({ queryKey: ["risks"], queryFn: api.risks, staleTime: 60_000 });

// Phase 6 — Analytics
export const useMomentum = () =>
  useQuery({ queryKey: ["momentum"], queryFn: api.momentum, staleTime: 60_000 });

export const useLifecycle = () =>
  useQuery({ queryKey: ["lifecycle"], queryFn: api.lifecycle, staleTime: 60_000 });

export const useEmergingAnalytics = () =>
  useQuery({ queryKey: ["emergingAnalytics"], queryFn: api.emergingAnalytics, staleTime: 60_000 });

// Phase 7 — Repo Health
export const useRepoHealth = () =>
  useQuery({ queryKey: ["repoHealth"], queryFn: api.repoHealth, staleTime: 60_000 });

// Phase 8 — Graph
export const useGraphNetwork = () =>
  useQuery({ queryKey: ["graphNetwork"], queryFn: api.graphNetwork, staleTime: 120_000 });

export const useGraphInfluence = () =>
  useQuery({ queryKey: ["graphInfluence"], queryFn: api.graphInfluence, staleTime: 120_000 });

export const useGraphClusters = () =>
  useQuery({ queryKey: ["graphClusters"], queryFn: api.graphClusters, staleTime: 120_000 });

// Phase 9 — AI
export const useRecommend = () =>
  useMutation({ mutationFn: (skills: string[]) => api.recommend(skills) });

export const useForecast = (technology?: string) =>
  useQuery({ queryKey: ["forecast", technology], queryFn: () => api.forecast(technology), staleTime: 60_000 });

export const useNLInsights = (category?: string) =>
  useQuery({ queryKey: ["nlInsights", category], queryFn: () => api.insights(category), staleTime: 60_000 });
