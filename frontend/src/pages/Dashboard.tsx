import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { StatsCard } from '@/components/StatsCard';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Database,
    AlertTriangle,
    Target,
    Activity,
    Globe,
    ArrowRight
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api, type SystemStats } from '@/lib/api';
import { Link } from 'wouter';

// Mock chart data
const activityData = Array.from({ length: 24 }, (_, i) => ({
    hour: i,
    activity: Math.random() * 100,
}));

export function Dashboard() {
    const [stats, setStats] = useState<SystemStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getStats()
            .then(setStats)
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return <div className="flex items-center justify-center h-screen">Loading...</div>;
    }

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <Card className="relative overflow-hidden border-white/5">
                    {/* Background Image */}
                    <div
                        className="absolute inset-0 z-0 opacity-20"
                        style={{
                            backgroundImage: 'url(/hero-bg.png)',
                            backgroundSize: 'cover',
                            backgroundPosition: 'center',
                        }}
                    />

                    {/* Content */}
                    <div className="relative z-10 p-12">
                        <h1 className="text-5xl font-bold mb-4">
                            Global Ionosphere{' '}
                            <span className="text-primary">Status</span>
                        </h1>
                        <p className="text-lg text-muted-foreground mb-8 max-w-2xl">
                            Real-time monitoring and detection of Equatorial Plasma Bubbles
                            using NASA GOLD satellite imagery and deep learning analysis
                        </p>
                        <div className="flex gap-4">
                            <Link href="/analysis">
                                <Button size="lg" className="gap-2 font-bold uppercase">
                                    <Activity className="h-5 w-5" />
                                    View Latest Scans
                                </Button>
                            </Link>
                            <Link href="/reports">
                                <Button size="lg" variant="outline" className="gap-2">
                                    <ArrowRight className="h-4 w-4" />
                                    System Report
                                </Button>
                            </Link>
                        </div>
                    </div>
                </Card>
            </motion.div>

            {/* Stats Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                >
                    <StatsCard
                        label="Total Scans"
                        value={stats?.total_scans.toLocaleString() || '0'}
                        change="+12.5%"
                        icon={Database}
                        iconColor="bg-primary/10"
                    />
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                >
                    <StatsCard
                        label="EPB Detections"
                        value={stats?.epb_detections.toLocaleString() || '0'}
                        change="+4.2%"
                        icon={AlertTriangle}
                        iconColor="bg-destructive/10"
                    />
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                >
                    <StatsCard
                        label="Accuracy"
                        value={`${stats?.accuracy || 0}%`}
                        change="+0.3%"
                        icon={Target}
                        iconColor="bg-success/10"
                    />
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.4 }}
                >
                    <StatsCard
                        label="Active Alerts"
                        value={stats?.active_alerts || 0}
                        icon={Activity}
                        iconColor="bg-yellow-500/10"
                    />
                </motion.div>
            </div>

            {/* Charts Row */}
            <div className="grid gap-6 lg:grid-cols-3">
                {/* Global Map */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.5 }}
                    className="lg:col-span-2"
                >
                    <Card className="glass-panel border-white/5">
                        <div className="p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <Globe className="h-5 w-5 text-primary" />
                                    <h3 className="text-lg font-bold uppercase">Global Disturbance Map</h3>
                                </div>
                                <Badge variant="outline" className="bg-primary/20 border-primary text-primary">
                                    LIVE FEED
                                </Badge>
                            </div>

                            <div className="relative h-[300px] bg-black/40 rounded-lg overflow-hidden">
                                {/* Grid overlay */}
                                <div
                                    className="absolute inset-0 opacity-20"
                                    style={{
                                        backgroundImage: `
                      linear-gradient(hsl(var(--primary) / 0.3) 1px, transparent 1px),
                      linear-gradient(90deg, hsl(var(--primary) / 0.3) 1px, transparent 1px)
                    `,
                                        backgroundSize: '40px 40px',
                                    }}
                                />

                                {/* Data points */}
                                <DataPoint x="20%" y="30%" />
                                <DataPoint x="60%" y="45%" alert />
                                <DataPoint x="75%" y="25%" />
                                <DataPoint x="40%" y="60%" />
                                <DataPoint x="85%" y="70%" alert />

                                <div className="absolute inset-0 flex items-center justify-center">
                                    <p className="text-muted-foreground text-sm">
                                        Interactive Globe Visualization
                                    </p>
                                </div>
                            </div>
                        </div>
                    </Card>
                </motion.div>

                {/* Activity Chart */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.6 }}
                >
                    <Card className="glass-panel border-white/5">
                        <div className="p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <Activity className="h-5 w-5 text-primary" />
                                <h3 className="text-lg font-bold uppercase">Ionospheric Activity</h3>
                            </div>

                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={activityData}>
                                    <defs>
                                        <linearGradient id="activityGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                                            <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <XAxis dataKey="hour" stroke="hsl(var(--muted-foreground))" />
                                    <YAxis stroke="hsl(var(--muted-foreground))" />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'hsl(var(--background))',
                                            border: '1px solid hsl(var(--border))',
                                            borderRadius: '8px',
                                        }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="activity"
                                        stroke="hsl(var(--primary))"
                                        fill="url(#activityGradient)"
                                        strokeWidth={2}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>
                </motion.div>
            </div>
        </div>
    );
}

function DataPoint({ x, y, alert = false }: { x: string; y: string; alert?: boolean }) {
    return (
        <div
            className="absolute"
            style={{ left: x, top: y }}
        >
            <div className={`
        h-3 w-3 rounded-full
        ${alert ? 'bg-destructive' : 'bg-primary'}
        animate-ping absolute
      `} />
            <div className={`
        h-3 w-3 rounded-full
        ${alert ? 'bg-destructive' : 'bg-primary'}
        relative
      `} />
        </div>
    );
}
