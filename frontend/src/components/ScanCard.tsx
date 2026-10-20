import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye } from 'lucide-react';
import { type DatasetItem } from '@/lib/api';

interface ScanCardProps {
    scan: DatasetItem;
    onAnalyze?: (scan: DatasetItem) => void;
}

export function ScanCard({ scan, onAnalyze }: ScanCardProps) {
    return (
        <Card className="glass-panel group border-white/5 hover:border-primary/50 transition-all duration-300 overflow-hidden">
            {/* Image */}
            <div className="relative aspect-square overflow-hidden bg-black/50">
                <img
                    src={scan.image_url}
                    alt={scan.id}
                    className="h-full w-full object-cover transition-all duration-300 group-hover:scale-110 group-hover:opacity-100 opacity-80"
                />

                {/* Detection Badge */}
                {scan.epb_detected && (
                    <Badge
                        variant="destructive"
                        className="absolute top-2 right-2 animate-pulse"
                    >
                        BUBBLE DETECTED
                    </Badge>
                )}

                {/* Hover Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <div className="absolute bottom-4 left-0 right-0 px-4">
                        <Button
                            onClick={() => onAnalyze?.(scan)}
                            className="w-full gap-2"
                            variant="outline"
                        >
                            <Eye className="h-4 w-4" />
                            Analyze
                        </Button>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="p-4 space-y-3">
                <div>
                    <p className="font-mono text-sm font-medium">{scan.id}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                        <span>{scan.date}</span>
                        <span>•</span>
                        <span>{scan.region}</span>
                    </div>
                </div>

                <div>
                    <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">
                        Anomaly Score (MSE)
                    </p>
                    <p className={`text-lg font-bold ${scan.epb_detected ? 'text-destructive' : 'text-muted-foreground'}`}>
                        {scan.confidence ? (scan.confidence / 1000).toFixed(4) : "0.0000"}
                    </p>
                </div>
            </div>
        </Card>
    );
}
