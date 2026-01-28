import { cn } from "@/lib/utils";

interface EmotionCardProps {
    emotion: string;
    score: number;
    reflection: string;
}

const emotionColors: Record<string, string> = {
    joy: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
    sadness: "text-blue-400 bg-blue-400/10 border-blue-400/20",
    anger: "text-red-400 bg-red-400/10 border-red-400/20",
    fear: "text-purple-400 bg-purple-400/10 border-purple-400/20",
    love: "text-pink-400 bg-pink-400/10 border-pink-400/20",
    surprise: "text-orange-400 bg-orange-400/10 border-orange-400/20",
    neutral: "text-zinc-400 bg-zinc-400/10 border-zinc-400/20",
};

const emotionEmojis: Record<string, string> = {
    joy: "☀️",
    sadness: "🌧️",
    anger: "🔥",
    fear: "😨",
    love: "❤️",
    surprise: "😲",
    neutral: "😐",
};

export function EmotionCard({ emotion, score, reflection }: EmotionCardProps) {
    const colorClass = emotionColors[emotion.toLowerCase()] || emotionColors.neutral;
    const emoji = emotionEmojis[emotion.toLowerCase()] || emotionEmojis.neutral;

    return (
        <div className="w-full max-w-2xl mx-auto mt-12 animate-in fade-in slide-in-from-bottom-6 duration-700">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Emotion Display */}
                <div className="glass-panel p-8 flex flex-col items-center justify-center text-center space-y-4">
                    <div className="text-6xl animate-bounce">{emoji}</div>
                    <div className={cn("px-4 py-1.5 rounded-full border font-medium text-sm tracking-wide uppercase", colorClass)}>
                        {emotion}
                    </div>
                    <div className="text-zinc-500 text-xs uppercase tracking-widest font-medium">
                        Confidence: {score.toFixed(0)}%
                    </div>
                </div>

                {/* Reflection */}
                <div className="col-span-1 md:col-span-2 glass-panel p-8 relative overflow-hidden flex flex-col justify-center">
                    <div className="absolute top-4 right-6 text-zinc-800 text-9xl font-serif opacity-20 pointer-events-none select-none">
                        ”
                    </div>
                    <h3 className="text-zinc-400 text-xs font-bold tracking-widest uppercase mb-4">
                        AI Reflection
                    </h3>
                    <p className="text-zinc-200 text-lg leading-relaxed font-serif relative z-10">
                        "{reflection}"
                    </p>
                </div>
            </div>
        </div>
    );
}
