import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

import MetricCard from "../components/ui/MetricCard";
import TechnologyBadge from "../components/ui/TechnologyBadge";
import { SectionCard, PageSpinner, PageError } from "../components/ui/PageShell";
import ScoreBar from "../components/ui/ScoreBar";
import { useGraphNetwork, useGraphInfluence, useGraphClusters } from "../hooks/useApi";

const ECOSYSTEM_COLORS: Record<string, string> = {
  "AI Ecosystem": "#A78BFA",
  "Backend Ecosystem": "#6BE6C1",
  "Systems Ecosystem": "#F0B866",
  "Frontend Ecosystem": "#7C9BFF",
  "DevOps Ecosystem": "#34D399",
  "Database Ecosystem": "#F87171",
  "Data Ecosystem": "#F472B6",
  "Mobile Ecosystem": "#2DD4BF",
  "Runtime Ecosystem": "#FBBF24",
};

const FALLBACK_COLORS = ["#A78BFA", "#6BE6C1", "#F0B866", "#7C9BFF", "#34D399", "#F87171", "#F472B6", "#2DD4BF", "#FBBF24", "#818CF8"];

function ecosystemColor(label: string): string {
  if (ECOSYSTEM_COLORS[label]) return ECOSYSTEM_COLORS[label];
  let hash = 0;
  for (let i = 0; i < label.length; i++) hash = ((hash << 5) - hash + label.charCodeAt(i)) | 0;
  return FALLBACK_COLORS[Math.abs(hash) % FALLBACK_COLORS.length];
}

export default function EcosystemGraphPage() {
  const network = useGraphNetwork();
  const influence = useGraphInfluence();
  const clusters = useGraphClusters();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<any>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const isLoading = network.isLoading || influence.isLoading || clusters.isLoading;
  const error = network.error || influence.error || clusters.error;

  useEffect(() => {
    if (!network.data || !containerRef.current) return;

    let cy: any;

    import("cytoscape").then((cytoscapeModule) => {
      const cytoscape = cytoscapeModule.default;

      const elements = [
        ...network.data!.nodes.map((n) => ({
          data: { id: n.id, label: n.label, cluster_label: n.cluster_label },
        })),
        ...network.data!.edges.map((e, i) => ({
          data: { id: `e${i}`, source: e.source, target: e.target, relationship: e.relationship },
        })),
      ];

      cy = cytoscape({
        container: containerRef.current,
        elements,
        style: [
          {
            selector: "node",
            style: {
              label: "data(label)",
              "background-color": (ele: any) => ecosystemColor(ele.data("cluster_label")),
              "border-width": 2,
              "border-color": "#1E1F27",
              color: "#F5F5F7",
              "font-size": "10px",
              "text-valign": "bottom",
              "text-margin-y": 6,
              width: 28,
              height: 28,
            } as any,
          },
          {
            selector: "edge",
            style: {
              width: 1.5,
              "line-color": "#1E1F27",
              "curve-style": "bezier",
              "target-arrow-shape": "triangle",
              "target-arrow-color": "#1E1F27",
              "arrow-scale": 0.6,
            } as any,
          },
          {
            selector: "node:selected",
            style: {
              "border-color": "#6BE6C1",
              "border-width": 3,
            } as any,
          },
        ],
        layout: {
          name: "cose",
          animate: true,
          animationDuration: 800,
          nodeRepulsion: () => 8000,
          idealEdgeLength: () => 80,
          gravity: 0.3,
        } as any,
      });

      cy.on("tap", "node", (evt: any) => {
        setSelectedNode(evt.target.id());
      });

      cy.on("tap", (evt: any) => {
        if (evt.target === cy) setSelectedNode(null);
      });

      cyRef.current = cy;
    });

    return () => {
      if (cy) cy.destroy();
    };
  }, [network.data]);

  if (isLoading) return <PageSpinner />;
  if (error) return <PageError message={(error as Error).message} />;

  const influenceData = influence.data ?? [];
  const clusterData = clusters.data ?? [];
  const selectedInfluence = influenceData.find((i) => i.technology_name === selectedNode);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Technology Ecosystem Graph</h1>
        <p className="text-sm text-dp-text-3">Interactive dependency and influence network</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard label="Technologies" value={network.data?.nodes.length ?? 0} />
        <MetricCard label="Dependencies" value={network.data?.edges.length ?? 0} />
        <MetricCard label="Clusters" value={clusterData.length} />
        <MetricCard
          label="Most Influential"
          value={influenceData.length > 0 ? influenceData[0].technology_name : "N/A"}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Graph */}
        <SectionCard title="Network Graph" subtitle="Click nodes to inspect" className="lg:col-span-2">
          <div ref={containerRef} className="h-[500px] rounded-lg bg-dp-surface" />
        </SectionCard>

        {/* Side panel */}
        <div className="space-y-4">
          {selectedInfluence ? (
            <motion.div
              key={selectedNode}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <SectionCard title={selectedInfluence.technology_name} subtitle="Influence Metrics">
                <div className="space-y-3">
                  {[
                    { label: "Ecosystem Influence", value: selectedInfluence.ecosystem_influence },
                    { label: "Degree Centrality", value: selectedInfluence.degree_centrality },
                    { label: "PageRank", value: selectedInfluence.pagerank },
                    { label: "Betweenness", value: selectedInfluence.betweenness_centrality },
                    { label: "Closeness", value: selectedInfluence.closeness_centrality },
                  ].map((m) => (
                    <div key={m.label}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-dp-text-2">{m.label}</span>
                        <span className="text-dp-text">{m.value.toFixed(4)}</span>
                      </div>
                      <ScoreBar value={m.value * 100} />
                    </div>
                  ))}
                </div>
              </SectionCard>
            </motion.div>
          ) : (
            <SectionCard title="Node Details" subtitle="Click a node to view metrics">
              <p className="text-sm text-dp-text-3 py-4">Interact with the graph to explore technology influences.</p>
            </SectionCard>
          )}

          {/* Clusters */}
          <SectionCard title="Clusters" subtitle={`${clusterData.length} communities detected`}>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {clusterData.map((c) => (
                <div key={c.cluster_id} className="rounded-lg border border-dp-border bg-dp-surface-2 px-3 py-2">
                  <p className="text-xs font-semibold text-dp-text mb-1">{c.cluster_label}</p>
                  <div className="flex flex-wrap gap-1">
                    {c.technologies.map((t) => (
                      <TechnologyBadge key={t} name={t} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>

          {/* Influence rankings */}
          <SectionCard title="Influence Rankings">
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {influenceData.slice(0, 10).map((inf, i) => (
                <div
                  key={inf.technology_name}
                  className="flex items-center gap-2 text-sm cursor-pointer hover:bg-dp-surface-2 rounded px-2 py-1 transition-colors"
                  onClick={() => setSelectedNode(inf.technology_name)}
                >
                  <span className="text-xs font-bold text-dp-text-3 w-5">{i + 1}</span>
                  <span className="text-dp-text flex-1">{inf.technology_name}</span>
                  <span className="text-xs text-dp-accent">{inf.ecosystem_influence.toFixed(3)}</span>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>

      {/* Ecosystem legend */}
      <SectionCard title="Ecosystem Legend">
        <div className="flex flex-wrap gap-3">
          {clusterData.map((c) => (
            <div key={c.cluster_label} className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: ecosystemColor(c.cluster_label) }} />
              <span className="text-xs text-dp-text-2">{c.cluster_label}</span>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
