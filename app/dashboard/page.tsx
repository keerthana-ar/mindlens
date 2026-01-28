'use client';

import { useEffect, useState } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Loader2, TrendingUp, Calendar, Zap } from 'lucide-react';

interface AnalyticsData {
    emotionCounts: { name: string; value: number; color: string }[];
    totalEntries: number;
    streak: number;
    weeklyCount: number;
}

const COLORS = {
    joy: '#FBBF24',      // yellow-400
    sadness: '#60A5FA',  // blue-400
    anger: '#F87171',    // red-400
    fear: '#A78BFA',     // purple-400
    love: '#EC4899',     // pink-500
    surprise: '#FB923C', // orange-400
    neutral: '#9CA3AF',  // gray-400
};

export default function DashboardPage() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/entries')
            .then(res => res.json())
            .then((entries: any[]) => {
                if (!Array.isArray(entries)) {
                    // If the API returns an error object (e.g. { error: 'Unauthorized' }), treat it as empty data
                    // or handle specific errors if needed.
                    console.warn('API returned non-array:', entries);
                    return; // Stop processing to avoid the "Invalid data format" error
                }

                // 1. Emotion Config
                const counts: Record<string, number> = {};
                entries.forEach(e => {
                    const em = e.emotion.toLowerCase();
                    counts[em] = (counts[em] || 0) + 1;
                });

                const emotionCounts = Object.keys(counts).map(key => ({
                    name: key.charAt(0).toUpperCase() + key.slice(1),
                    value: counts[key],
                    color: COLORS[key as keyof typeof COLORS] || '#CBD5E1'
                }));

                // 2. Weekly Count
                const oneWeekAgo = new Date();
                oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
                const weeklyCount = entries.filter(e => new Date(e.createdAt) > oneWeekAgo).length;

                // 3. Streak (Simplified)
                const streak = entries.length > 0 ? 1 : 0;

                setData({
                    emotionCounts,
                    totalEntries: entries.length,
                    streak: streak,
                    weeklyCount
                });
            })
            .catch(err => {
                console.error(err);
                // Set empty data instead of null to allow rendering
                setData({
                    emotionCounts: [],
                    totalEntries: 0,
                    streak: 0,
                    weeklyCount: 0
                });
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center py-20 min-h-[50vh]">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="space-y-8 py-8">
            <div className="space-y-2">
                <h1 className="text-3xl font-serif text-white">Emotional Analytics</h1>
                <p className="text-zinc-400 font-light">Insights from your reflections.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-panel p-6 flex items-center gap-5">
                    <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">
                        <TrendingUp className="w-6 h-6" />
                    </div>
                    <div>
                        <div className="text-3xl font-serif text-zinc-100">{data.totalEntries}</div>
                        <div className="text-sm text-zinc-500 uppercase tracking-wider font-medium">Total Entries</div>
                    </div>
                </div>
                <div className="glass-panel p-6 flex items-center gap-5">
                    <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                        <Calendar className="w-6 h-6" />
                    </div>
                    <div>
                        <div className="text-3xl font-serif text-zinc-100">{data.weeklyCount}</div>
                        <div className="text-sm text-zinc-500 uppercase tracking-wider font-medium">This Week</div>
                    </div>
                </div>
                <div className="glass-panel p-6 flex items-center gap-5">
                    <div className="p-3 bg-orange-500/10 text-orange-400 rounded-xl">
                        <Zap className="w-6 h-6" />
                    </div>
                    <div>
                        <div className="text-3xl font-serif text-zinc-100">{data.streak}</div>
                        <div className="text-sm text-zinc-500 uppercase tracking-wider font-medium">Day Streak</div>
                    </div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="glass-panel p-8">
                    <h3 className="text-lg font-serif text-zinc-200 mb-8 text-center">Emotion Distribution</h3>
                    <div className="h-[300px] w-full">
                        {data.emotionCounts.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={data.emotionCounts}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                        stroke="none"
                                    >
                                        {data.emotionCounts.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', color: '#f4f4f5' }}
                                        itemStyle={{ color: '#f4f4f5' }}
                                    />
                                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex items-center justify-center text-zinc-500">
                                No data available yet
                            </div>
                        )}
                    </div>
                </div>

                {/* Placeholder for future mood trend chart */}
                <div className="glass-panel p-8 flex flex-col justify-center items-center text-center">
                    <div className="w-16 h-16 rounded-full bg-zinc-800/50 flex items-center justify-center mb-4">
                        <TrendingUp className="w-8 h-8 text-zinc-600" />
                    </div>
                    <h3 className="text-lg font-serif text-zinc-200 mb-2">Mood Trends</h3>
                    <p className="text-zinc-500 max-w-xs">
                        Trend visualization is coming in the next update. Keep consistency to unlock more insights!
                    </p>
                </div>
            </div>
        </div>
    );
}
