import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { StatsCard } from '@/components/StatsCard';
import { Target, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';
import { api, type ModelMetrics } from '@/lib/api';

export function Reports() {
    const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        api.getMetrics()
            .then(setMetrics)
            .catch((e) => setError(e?.message || 'Failed to load metrics'))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return <div className="flex items-center justify-center h-64 text-muted-foreground">Loading metrics...</div>;
    }

    if (error) {
        return <div className="flex items-center justify-center h-64 text-destructive">Error: {error}</div>;
    }

    if (!metrics) {
        return <div className="flex items-center justify-center h-64 text-muted-foreground">No metrics data available.</div>;
    }

    const trainingData = metrics?.epochs.map((epoch, i) => ({
        epoch,
        train: metrics.training_loss[i],
        val: metrics.validation_loss[i],
    })) || [];

    const cm = metrics?.confusion_matrix || [[0, 0], [0, 0]];
    const confusionData = [
        { name: 'Predicted Negative', actualNegative: cm[0][0], actualPositive: cm[1][0] },
        { name: 'Predicted Positive', actualNegative: cm[0][1], actualPositive: cm[1][1] },
    ];

    const radarData = [
        { metric: 'Accuracy', value: metrics?.final_metrics.accuracy || 0 },
        { metric: 'Precision', value: metrics?.final_metrics.precision || 0 },
        { metric: 'Recall', value: metrics?.final_metrics.recall || 0 },
        { metric: 'F1 Score', value: metrics?.final_metrics.f1_score || 0 },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold mb-2">Model Metrics</h1>
                <p className="text-muted-foreground">
                    Performance evaluation (Reconstruction Error vs GNSS ROTI)
                </p>
            </div>

            {/* Quick Stats */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <StatsCard
                    label="Accuracy"
                    value={`${metrics?.final_metrics.accuracy || 0}%`}
                    icon={CheckCircle}
                    iconColor="bg-green-500/10"
                />
                <StatsCard
                    label="Precision"
                    value={`${metrics?.final_metrics.precision || 0}%`}
                    icon={Target}
                    iconColor="bg-primary/10"
                />
                <StatsCard
                    label="Recall"
                    value={`${metrics?.final_metrics.recall || 0}%`}
                    icon={Activity}
                    iconColor="bg-blue-500/10"
                />
                <StatsCard
                    label="F1 Score"
                    value={`${metrics?.final_metrics.f1_score || 0}%`}
                    icon={Target}
                    iconColor="bg-yellow-500/10"
                />
                <StatsCard
                    label="Validation MSE"
                    value={metrics?.final_metrics.mse?.toFixed(5) || "N/A"}
                    icon={AlertTriangle}
                    iconColor="bg-destructive/10"
                />
                <StatsCard
                    label="Threshold"
                    value="0.028"
                    icon={AlertTriangle}
                    iconColor="bg-destructive/10"
                />
            </div>

            {/* Tabbed Charts */}
            <Card className="glass-panel border-white/5">
                <Tabs defaultValue="training" className="p-6">
                    <TabsList className="grid w-full grid-cols-2 bg-black/20">
                        <TabsTrigger value="training">Training History</TabsTrigger>
                        <TabsTrigger value="evaluation">Evaluation Matrix</TabsTrigger>
                    </TabsList>

                    <TabsContent value="training" className="mt-6">
                        <h3 className="text-lg font-bold uppercase mb-4">Training Progress (Regression)</h3>
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={trainingData}>
                                <XAxis
                                    dataKey="epoch"
                                    stroke="hsl(var(--muted-foreground))"
                                    label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }}
                                />
                                <YAxis
                                    stroke="hsl(var(--muted-foreground))"
                                    label={{ value: 'MSE Loss', angle: -90, position: 'insideLeft' }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'hsl(var(--background))',
                                        border: '1px solid hsl(var(--border))',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="train"
                                    stroke="hsl(var(--primary))"
                                    strokeWidth={2}
                                    name="Training Loss"
                                    dot={false}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="val"
                                    stroke="hsl(var(--destructive))"
                                    strokeWidth={2}
                                    name="Validation Loss"
                                    dot={false}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </TabsContent>

                    <TabsContent value="evaluation" className="mt-6">
                        <div className="grid gap-6 md:grid-cols-2">
                            {/* Confusion Matrix */}
                            <div>
                                <h3 className="text-lg font-bold uppercase mb-4">Confusion Matrix</h3>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={confusionData}>
                                        <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
                                        <YAxis stroke="hsl(var(--muted-foreground))" />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: 'hsl(var(--background))',
                                                border: '1px solid hsl(var(--border))',
                                                borderRadius: '8px',
                                            }}
                                        />
                                        <Legend />
                                        <Bar dataKey="actualNegative" fill="hsl(var(--destructive))" name="Actual Negative" />
                                        <Bar dataKey="actualPositive" fill="hsl(var(--primary))" name="Actual Positive" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Radar Chart */}
                            <div>
                                <h3 className="text-lg font-bold uppercase mb-4">Model Capabilities</h3>
                                <ResponsiveContainer width="100%" height={300}>
                                    <RadarChart data={radarData}>
                                        <PolarGrid stroke="hsl(var(--border))" />
                                        <PolarAngleAxis
                                            dataKey="metric"
                                            stroke="hsl(var(--muted-foreground))"
                                            tick={{ fill: 'hsl(var(--muted-foreground))' }}
                                        />
                                        <PolarRadiusAxis
                                            angle={90}
                                            domain={[0, 100]}
                                            stroke="hsl(var(--muted-foreground))"
                                        />
                                        <Radar
                                            name="Performance"
                                            dataKey="value"
                                            stroke="hsl(var(--primary))"
                                            fill="hsl(var(--primary))"
                                            fillOpacity={0.3}
                                        />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </TabsContent>
                </Tabs>
            </Card>
        </div>
    );
}
