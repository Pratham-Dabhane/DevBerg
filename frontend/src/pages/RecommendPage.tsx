import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X, Plus } from "lucide-react";

import TechnologyBadge from "../components/ui/TechnologyBadge";
import ScoreBar from "../components/ui/ScoreBar";
import { SectionCard, PageError } from "../components/ui/PageShell";
import { useRecommend } from "../hooks/useApi";

const SKILL_SUGGESTIONS = [
  "Python", "FastAPI", "Docker", "React", "TypeScript", "Rust", "PostgreSQL",
  "LangChain", "TensorFlow", "PyTorch", "Node.js", "Go", "Kubernetes",
  "Redis", "MongoDB", "GraphQL", "Next.js", "Tailwind", "Vue.js", "Django",
];

export default function RecommendPage() {
  const [skills, setSkills] = useState<string[]>([]);
  const [inputValue, setInputValue] = useState("");
  const recommend = useRecommend();

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
        <p className="text-sm text-gray-500">Personalized technology recommendations based on your skill profile</p>
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
                  className="inline-flex items-center gap-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 px-3 py-1.5 text-sm text-blue-300"
                >
                  {skill}
                  <button onClick={() => removeSkill(skill)} className="hover:text-blue-100">
                    <X className="h-3 w-3" />
                  </button>
                </motion.span>
              ))}
            </AnimatePresence>
            {skills.length === 0 && (
              <p className="text-sm text-gray-600 py-1">No skills added yet. Add some below!</p>
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
              className="flex-1 rounded-lg border border-gray-800/60 bg-gray-900/50 px-3 py-2 text-sm text-gray-300 placeholder-gray-600 outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20"
            />
            <button
              onClick={() => addSkill(inputValue)}
              className="rounded-lg bg-gray-800 px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Suggestions */}
          <div>
            <p className="text-xs text-gray-500 mb-2">Quick add:</p>
            <div className="flex flex-wrap gap-1.5">
              {SKILL_SUGGESTIONS.filter((s) => !skills.includes(s)).slice(0, 12).map((s) => (
                <button
                  key={s}
                  onClick={() => addSkill(s)}
                  className="rounded-md bg-gray-800/50 px-2 py-1 text-xs text-gray-400 hover:bg-gray-700 hover:text-gray-300 transition-colors"
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
            className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
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
            <span className="rounded-full bg-blue-500/10 px-2 py-0.5 text-xs text-blue-400">
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
                className="rounded-xl border border-gray-800/60 bg-gray-900/30 p-5 hover:border-blue-500/20 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <TechnologyBadge name={rec.technology_name} />
                  <span className="text-lg font-bold text-blue-400">
                    {(rec.recommendation_score * 100).toFixed(0)}
                    <span className="text-xs font-normal text-gray-500">%</span>
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-500">Match Score</span>
                      <span className="text-gray-300">{(rec.recommendation_score * 100).toFixed(1)}%</span>
                    </div>
                    <ScoreBar value={rec.recommendation_score * 100} />
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="rounded bg-gray-800/30 px-2 py-1.5">
                      <p className="text-[10px] text-gray-500">Momentum</p>
                      <p className="text-sm font-semibold">{rec.momentum_score.toFixed(2)}</p>
                    </div>
                    <div className="rounded bg-gray-800/30 px-2 py-1.5">
                      <p className="text-[10px] text-gray-500">Similarity</p>
                      <p className="text-sm font-semibold">{rec.skill_similarity.toFixed(2)}</p>
                    </div>
                    <div className="rounded bg-gray-800/30 px-2 py-1.5">
                      <p className="text-[10px] text-gray-500">Proximity</p>
                      <p className="text-sm font-semibold">{rec.ecosystem_proximity.toFixed(2)}</p>
                    </div>
                  </div>

                  <p className="text-xs text-gray-400 leading-relaxed">{rec.reason}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
