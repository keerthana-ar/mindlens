'use client';

import { useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';

interface JournalInputProps {
    onAnalyze: (text: string) => Promise<void>;
    isAnalyzing: boolean;
}

export function JournalInput({ onAnalyze, isAnalyzing }: JournalInputProps) {
    const [content, setContent] = useState('');

    const handleSubmit = async () => {
        if (!content.trim() || isAnalyzing) return;
        await onAnalyze(content);
        setContent(''); // Clear after success
    };

    return (
        <div className="w-full max-w-2xl mx-auto space-y-8 mt-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="space-y-4 text-center">
                <h1 className="text-4xl md:text-5xl font-serif font-medium tracking-tight text-white/90">
                    How are you feeling right now?
                </h1>
                <p className="text-zinc-400 text-lg font-light max-w-lg mx-auto">
                    Take a moment to reflect. Write your thoughts, and let AI help you find clarity.
                </p>
            </div>

            <div className="glass-panel p-1 transition-all focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500/30">
                <div className="relative">
                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="I'm feeling..."
                        className="w-full h-48 bg-transparent text-lg text-zinc-100 placeholder:text-zinc-600 p-6 resize-none focus:outline-none font-sans leading-relaxed"
                        disabled={isAnalyzing}
                    />
                    <div className="absolute bottom-4 right-4 flex items-center gap-3">
                        <span className="text-xs text-zinc-600 font-medium">
                            {content.length}/2000
                        </span>
                        <button
                            onClick={handleSubmit}
                            disabled={isAnalyzing || !content.trim()}
                            className="bg-zinc-100 text-zinc-950 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed px-6 py-2.5 rounded-xl font-medium transition-all shadow-lg shadow-white/5 flex items-center gap-2 group"
                        >
                            {isAnalyzing ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-4 h-4 group-hover:scale-110 transition-transform" />
                                    Reflect
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
