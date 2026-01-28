'use client';

import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { EmotionCard } from '@/components/EmotionCard'; // We can reuse aspects or just style similarly

interface Entry {
    id: string;
    content: string;
    emotion: string;
    score: number;
    reflection: string;
    createdAt: string;
}

const emotionColors: Record<string, string> = {
    joy: "text-yellow-400 border-yellow-400/20 bg-yellow-400/5",
    sadness: "text-blue-400 border-blue-400/20 bg-blue-400/5",
    anger: "text-red-400 border-red-400/20 bg-red-400/5",
    fear: "text-purple-400 border-purple-400/20 bg-purple-400/5",
    love: "text-pink-400 border-pink-400/20 bg-pink-400/5",
    surprise: "text-orange-400 border-orange-400/20 bg-orange-400/5",
    neutral: "text-zinc-400 border-zinc-400/20 bg-zinc-400/5",
};

export default function HistoryPage() {
    const [entries, setEntries] = useState<Entry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/entries')
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    setEntries(data);
                }
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center py-20 min-h-[50vh]">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
            </div>
        );
    }

    return (
        <div className="space-y-8 py-8">
            <div className="space-y-2">
                <h1 className="text-3xl font-serif text-white">Journal History</h1>
                <p className="text-zinc-400 font-light">Your journey of reflection.</p>
            </div>

            <div className="grid gap-6">
                {entries.map((entry) => (
                    <div key={entry.id} className="glass-panel p-6 md:p-8 transition-all hover:bg-zinc-900/60">
                        <div className="flex flex-col md:flex-row gap-6 justify-between items-start mb-6">
                            <div className="flex items-center gap-4">
                                <div className={cn("px-4 py-1.5 rounded-full border text-xs font-bold uppercase tracking-wider",
                                    emotionColors[entry.emotion.toLowerCase()] || emotionColors.neutral
                                )}>
                                    {entry.emotion}
                                </div>
                                <span className="text-zinc-500 text-sm font-medium uppercase tracking-widest">
                                    {new Date(entry.createdAt).toLocaleDateString(undefined, {
                                        month: 'short', day: 'numeric', year: 'numeric'
                                    })}
                                </span>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <p className="text-zinc-300 font-serif text-lg leading-relaxed whitespace-pre-wrap">
                                {entry.content}
                            </p>

                            <div className="relative pl-6 border-l-2 border-indigo-500/30">
                                <h4 className="text-indigo-400 text-xs font-bold uppercase tracking-widest mb-2">AI Reflection</h4>
                                <p className="text-zinc-400 italic leading-relaxed">
                                    "{entry.reflection}"
                                </p>
                            </div>
                        </div>
                    </div>
                ))}

                {entries.length === 0 && (
                    <div className="text-center py-20 bg-zinc-900/20 rounded-3xl border border-white/5 border-dashed">
                        <p className="text-zinc-500 mb-4">No entries yet.</p>
                        <a href="/" className="text-indigo-400 hover:text-indigo-300 underline underline-offset-4">
                            Write your first entry
                        </a>
                    </div>
                )}
            </div>
        </div>
    );
}
