'use client';

import { useState } from 'react';
import { JournalInput } from '@/components/JournalInput';
import { EmotionCard } from '@/components/EmotionCard';
import { motion, AnimatePresence } from 'framer-motion';

interface AnalysisResult {
  id: string;
  emotion: string;
  score: number;
  reflection: string;
}

export default function Home() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (text: string) => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed');
      }

      setResult(data);
    } catch (error: any) {
      console.error(error);
      alert(error.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 py-8">


      <JournalInput onAnalyze={handleAnalyze} isAnalyzing={loading} />

      <AnimatePresence mode="wait">
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            <EmotionCard
              emotion={result.emotion}
              score={result.score}
              reflection={result.reflection}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
