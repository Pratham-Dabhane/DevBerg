import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X, Plus } from "lucide-react";

import TechnologyBadge from "../components/ui/TechnologyBadge";
import ScoreBar from "../components/ui/ScoreBar";
import { SectionCard, PageError } from "../components/ui/PageShell";
import { useRecommend, useTechnologies } from "../hooks/useApi";

export default function RecommendPage() {
  const [skills, setSkills] = useState<string[]>([]);
  const [inputValue, setInputValue] = useState("");
  const recommend = useRecommend();
  const { data: techList } = useTechnologies();

  const skillSuggestions = (techList ?? []).map((t) => t.name);

  function addSkill(skill: string) {
    const trimmed = skill.trim();
    if (trimmed && !skills.includes(trimmed)) {
      setSkills([...skills, trimmed]);
    }
    setInputValue("");
  }

  function removeSkill(skill: string) {
    setSkills(skills.filter((s) => s !== skill));
  }

  function handleSubmit() {
    if (skills.length > 0) {
      recommend.mutate(skills);
    }
  }

  const recommendations = recommend.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">AI Recommendations</h1>
        <p className="text-sm text-dp-text-3">Personalized technology recommendations based on your skill profile</p>
      </div>

      {/* Skill input */}
      <SectionCard title="Your Skill Profile" subtitle="Add technologies you already know">
        <div className="space-y-4">
          {/* Current skills */}
          <div className="flex flex-wrap gap-2 min-h-[40px]">
            <AnimatePresence>
              {skills.map((skill) => (
                <motion.span
                  key={skill}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-dp-accent-dim border border-dp-accent/20 px-3 py-1.5 text-sm text-dp-accent"
                >
                  {skill}
                  <button onClick={() => removeSkill(skill)} className="hover:text-dp-text">
                    <X className="h-3 w-3" />
                  </button>
                </motion.span>
              ))}
            </AnimatePresence>
            {skills.length === 0 && (
              <p className="text-sm text-dp-text-4 py-1">No skills added yet. Add some below!</p>
            )}
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Add a skill..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addSkill(inputValue)}
              className="flex-1 rounded-lg border border-dp-border bg-dp-surface px-3 py-2 text-sm text-dp-text-2 placeholder-dp-text-4 outline-none focus:border-dp-accent/40 focus:ring-1 focus:ring-dp-accent/15"
            />
            <button
              onClick={() => addSkill(inputValue)}
              className="rounded-lg bg-dp-surface-2 px-3 py-2 text-sm text-dp-text-2 hover:bg-dp-border transition-colors"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Suggestions */}
          <div>
            <p className="text-xs text-dp-text-3 mb-2">Quick add:</p>
            <div className="flex flex-wrap gap-1.5">
              {skillSuggestions.filter((s) => !skills.includes(s)).slice(0, 12).map((s) => (
                <button
                  key={s}
                  onClick={() => addSkill(s)}
                  className="rounded-md bg-dp-surface px-2 py-1 text-xs text-dp-text-2 hover:bg-dp-surface-2 hover:text-dp-text transition-colors"
                >
                  + {s}
                </button>
              ))}
            </div>
          </div>

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={skills.length === 0 || recommend.isPending}
            className="w-full rounded-lg bg-dp-accent px-4 py-2.5 text-sm font-medium text-dp-bg hover:shadow-[0_0_20px_rgba(107,230,193,0.25)] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            <Sparkles className="h-4 w-4" />
            {recommend.isPending ? "Analyzing..." : "Get Recommendations"}
          </button>
        </div>
      </SectionCard>

      {/* Results */}
      {recommend.isError && (
        <PageError message={(recommend.error as Error).message} />
      )}

      {recommendations.length > 0 && (
        <>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">Recommended Technologies</h2>
            <span className="rounded-full bg-dp-accent-dim px-2 py-0.5 text-xs text-dp-accent">
              {recommendations.length} results
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {recommendations.map((rec, i) => (
              <motion.div
                key={rec.technology_name}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                className="dp-card p-5 hover:border-dp-accent/15 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <TechnologyBadge name={rec.technology_name} />
                  <span className="text-lg font-bold text-dp-accent">
                    {(rec.recommendation_score * 100).toFixed(0)}
                    <span className="text-xs font-normal text-dp-text-3">%</span>
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-dp-text-3">Match Score</span>
                      <span className="text-dp-text">{(rec.recommendation_score * 100).toFixed(1)}%</span>
                    </div>
                    <ScoreBar value={rec.recommendation_score * 100} />
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="rounded bg-dp-surface-2 px-2 py-1.5">
                      <p className="text-[10px] text-dp-text-3">Momentum</p>
                      <p className="text-sm font-semibold">{rec.momentum_score.toFixed(2)}</p>
                    </div>
                    <div className="rounded bg-dp-surface-2 px-2 py-1.5">
                      <p className="text-[10px] text-dp-text-3">Similarity</p>
                      <p className="text-sm font-semibold">{rec.skill_similarity.toFixed(2)}</p>
                    </div>
                    <div className="rounded bg-dp-surface-2 px-2 py-1.5">
                      <p className="text-[10px] text-dp-text-3">Proximity</p>
                      <p className="text-sm font-semibold">{rec.ecosystem_proximity.toFixed(2)}</p>
                    </div>
                  </div>

                  <p className="text-xs text-dp-text-2 leading-relaxed">{rec.reason}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
