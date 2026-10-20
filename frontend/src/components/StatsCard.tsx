import type { LucideIcon } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { ArrowUpRight } from 'lucide-react';

interface StatsCardProps {
    label: string;
    value: string | number;
    change?: string;
    icon: LucideIcon;
    iconColor?: string;
}

export function StatsCard({ label, value, change, icon: Icon, iconColor }: StatsCardProps) {
    return (
        <Card className="glass-panel border-white/5 hover:border-primary/50 transition-all duration-300">
            <div className="p-6">
                <div className="flex items-start justify-between">
                    <div className="space-y-2">
                        <p className="text-xs uppercase tracking-wider text-muted-foreground">
                            {label}
                        </p>
                        <p className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                            {value}
                        </p>
                        {change && (
                            <div className="flex items-center gap-1 text-xs text-success">
                                <ArrowUpRight className="h-3 w-3" />
                                <span>{change} from last cycle</span>
                            </div>
                        )}
                    </div>
                    <div className={`rounded-lg p-2 ${iconColor || 'bg-primary/10'}`}>
                        <Icon className={`h-5 w-5 ${iconColor ? '' : 'text-primary'}`} />
                    </div>
                </div>
            </div>
        </Card>
    );
}
