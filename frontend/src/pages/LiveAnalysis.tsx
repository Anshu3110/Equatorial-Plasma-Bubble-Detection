import { useState } from 'react';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Upload,
    Play,
    RefreshCw,
    AlertTriangle,
    CheckCircle2
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api, type PredictionResult } from '@/lib/api';

// Mock TEC data
const tecData = Array.from({ length: 20 }, (_, i) => ({
    time: i,
    tec: 40 + Math.sin(i / 3) * 10 - (i > 10 ? (i - 10) * 2 : 0),
}));

export function LiveAnalysis() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string>('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<PredictionResult | null>(null);
    const [error, setError] = useState<string>('');
    const [analysisLog, setAnalysisLog] = useState<Array<{
        id: string;
        status: 'DETECTED' | 'CLEAR';
        time: string;
    }>>([
        { id: 'GOLD-2024-1234', status: 'CLEAR', time: '14:23:45' },
        { id: 'GOLD-2024-1233', status: 'DETECTED', time: '14:18:12' },
        { id: 'GOLD-2024-1232', status: 'CLEAR', time: '14:12:08' },
    ]);

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));
            setResult(null);
            setError('');
        }
    };

    const handleAnalysis = async () => {
        if (!selectedFile) return;

        setIsAnalyzing(true);
        setResult(null);
        setError('');

        try {
            const prediction = await api.predict(selectedFile);

            setResult(prediction);
            setIsAnalyzing(false);

            // Add to log
            setAnalysisLog(prev => [
                {
                    id: prediction.scan_id,
                    status: prediction.status,
                    time: new Date().toLocaleTimeString(),
                },
                ...prev.slice(0, 4),
            ]);
        } catch (err: any) {
            console.error('Analysis failed:', err);
            setError(err?.message || 'Analysis failed. Check backend connection.');
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold mb-2">Live Analysis</h1>
                <p className="text-muted-foreground">
                    Real-time EPB detection using Convolutional Autoencoder (Unsupervised)
                </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Main Visualization - 2/3 width */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Image Display */}
                    <Card className="glass-panel border-white/5 p-1">
                        <div className="relative aspect-square bg-black rounded-lg overflow-hidden">
                            {/* Live Feed Badge */}
                            {previewUrl && (
                                <div className="absolute top-4 left-4 z-10 backdrop-blur-sm bg-black/50 px-3 py-1.5 rounded border border-primary/30">
                                    <p className="text-xs font-mono text-primary">
                                        LIVE FEED: {result?.scan_id || 'GOLD-2024-XXXX'}
                                    </p>
                                </div>
                            )}

                            {/* Image */}
                            {previewUrl ? (
                                <img
                                    src={previewUrl}
                                    alt="Scan preview"
                                    className="h-full w-full object-contain opacity-80"
                                />
                            ) : (
                                <div className="h-full flex items-center justify-center text-muted-foreground">
                                    <p>Upload an image to begin analysis</p>
                                </div>
                            )}

                            {/* Scanning Overlay */}
                            {isAnalyzing && (
                                <div className="absolute inset-0 bg-primary/5">
                                    <div className="scan-line" />
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <p className="text-primary font-mono text-sm tracking-widest animate-bounce">
                                            PROCESSING...
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* Detection Result Overlay */}
                            {result?.epb_detected && (
                                <>
                                    <div className="absolute inset-0 border-4 border-destructive/50 animate-pulse" />
                                    <div className="absolute bottom-0 left-0 right-0 bg-destructive/20 backdrop-blur-sm p-4 border-t border-destructive/50">
                                        <div className="flex items-center gap-3">
                                            <AlertTriangle className="h-5 w-5 text-destructive" />
                                            <div className="flex-1">
                                                <p className="text-sm font-bold uppercase text-destructive">
                                                    Plasma Bubble Detected
                                                </p>
                                                <p className="text-xs text-muted-foreground">
                                                    MSE: {result.mse_score.toFixed(4)} • Threshold: {result.threshold}
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Bounding Box */}
                                    <div className="absolute top-1/4 left-1/4 w-1/2 h-1/2 border-2 border-dashed border-destructive">
                                        <div className="absolute -top-6 left-0 bg-black/80 px-2 py-1 text-xs text-destructive">
                                            EPB-01
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    </Card>

                    {/* TEC Correlation Chart */}
                    <Card className="glass-panel border-white/5 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold uppercase">GNSS TEC Correlation</h3>
                            <Badge variant="outline" className="bg-success/20 border-success text-success">
                                <CheckCircle2 className="h-3 w-3 mr-1" />
                                Synced
                            </Badge>
                        </div>

                        <ResponsiveContainer width="100%" height={250}>
                            <AreaChart data={tecData}>
                                <defs>
                                    <linearGradient id="tecGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                                        <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis
                                    dataKey="time"
                                    stroke="hsl(var(--muted-foreground))"
                                    label={{ value: 'Time (minutes)', position: 'insideBottom', offset: -5 }}
                                />
                                <YAxis
                                    stroke="hsl(var(--muted-foreground))"
                                    label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft' }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'hsl(var(--background))',
                                        border: '1px solid hsl(var(--border))',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="tec"
                                    stroke="hsl(var(--primary))"
                                    fill="url(#tecGradient)"
                                    strokeWidth={2}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </Card>
                </div>

                {/* Control Panel - 1/3 width */}
                <div className="space-y-6">
                    {/* Upload Section */}
                    <Card className="glass-panel border-white/5 p-6">
                        <h3 className="text-lg font-bold uppercase mb-4">Control Station</h3>

                        <label className="group">
                            <div className="border-2 border-dashed border-white/20 hover:border-primary/50 rounded-lg p-8 text-center cursor-pointer transition-all">
                                <Upload className="h-8 w-8 mx-auto mb-3 text-muted-foreground group-hover:text-primary transition-colors" />
                                <p className="text-sm font-medium mb-1">
                                    {selectedFile ? selectedFile.name : 'Click to upload'}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                    PNG, JPG up to 10MB
                                </p>
                            </div>
                            <input
                                type="file"
                                accept="image/png,image/jpeg"
                                className="hidden"
                                onChange={handleFileSelect}
                            />
                        </label>
                    </Card>

                    {/* Model Info */}
                    <Card className="glass-panel border-white/5 p-6">
                        <h4 className="text-sm font-bold uppercase mb-4 text-muted-foreground">
                            Model Information
                        </h4>
                        <div className="space-y-3 text-sm">
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Model:</span>
                                <span className="font-mono">Conv Autoencoder</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Method:</span>
                                <Badge variant="outline" className="bg-blue-500/20 border-blue-500 text-blue-500">
                                    Anomaly Detection
                                </Badge>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">TEC Validation:</span>
                                <Badge variant="outline" className="bg-success/20 border-success text-success">
                                    Enabled
                                </Badge>
                            </div>
                        </div>
                    </Card>

                    {/* Run Detection Button */}
                    <Button
                        onClick={handleAnalysis}
                        disabled={!selectedFile || isAnalyzing}
                        className="w-full h-12 text-lg font-bold uppercase gap-2"
                    >
                        {isAnalyzing ? (
                            <>
                                <RefreshCw className="h-5 w-5 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Play className="h-5 w-5 fill-current" />
                                Run Detection
                            </>
                        )}
                    </Button>

                    {/* Error Display */}
                    {error && (
                        <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm">
                            <div className="flex items-center gap-2">
                                <AlertTriangle className="h-4 w-4 flex-shrink-0" />
                                <span>{error}</span>
                            </div>
                        </div>
                    )}

                    {/* Result Summary */}
                    {result && (
                        <Card className="glass-panel border-white/5 p-4">
                            <h4 className="text-sm font-bold uppercase mb-3 text-muted-foreground">
                                Detection Result
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Status:</span>
                                    <Badge variant={result.epb_detected ? "destructive" : "default"} className={!result.epb_detected ? "bg-success/20 border-success text-success" : ""}>
                                        {result.status}
                                    </Badge>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">MSE Score:</span>
                                    <span className="font-mono">{result.mse_score?.toFixed(5) || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Confidence:</span>
                                    <span className="font-mono">{result.confidence}%</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Scan ID:</span>
                                    <span className="font-mono text-xs">{result.scan_id}</span>
                                </div>
                            </div>
                        </Card>
                    )}
                    {/* Analysis Log */}
                    <Card className="glass-panel border-white/5 p-6">
                        <h4 className="text-sm font-bold uppercase mb-4 text-muted-foreground">
                            Recent Analysis
                        </h4>
                        <div className="space-y-3">
                            {analysisLog.map((log, i) => (
                                <div key={i} className="flex items-center gap-3 text-sm">
                                    <div className={`h-2 w-2 rounded-full ${log.status === 'DETECTED' ? 'bg-destructive' : 'bg-success'
                                        }`} />
                                    <span className="font-mono flex-1">{log.id}</span>
                                    <span className="text-xs text-muted-foreground">{log.time}</span>
                                </div>
                            ))}
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
