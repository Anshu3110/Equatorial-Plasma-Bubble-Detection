import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ScanCard } from '@/components/ScanCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Search, Download, Upload } from 'lucide-react';
import { api, type DatasetItem } from '@/lib/api';

export function DataExplorer() {
    const [dataset, setDataset] = useState<DatasetItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [sortBy, setSortBy] = useState('newest');

    const [analyzingIds, setAnalyzingIds] = useState<Set<string>>(new Set());

    const handleAnalyze = async (scan: DatasetItem) => {
        setAnalyzingIds(prev => new Set(prev).add(scan.id));
        try {
            const result = await api.analyzeNasaFile(scan.filename);

            // Update dataset with result
            setDataset(prev => prev.map(item => {
                if (item.id === scan.id) {
                    return {
                        ...item,
                        epb_detected: result.epb_detected,
                        confidence: result.confidence,
                        // @ts-ignore
                        mse: result.mse_score,
                        image_url: result.image_url,
                        analyzed: true
                    };
                }
                return item;
            }));
        } catch (error) {
            console.error("Analysis failed", error);
            alert("Failed to analyze file. It might not be available on NASA servers yet.");
        } finally {
            setAnalyzingIds(prev => {
                const next = new Set(prev);
                next.delete(scan.id);
                return next;
            });
        }
    };

    const loadLocalDataset = () => {
        setLoading(true);
        api.getDataset()
            .then(setDataset)
            .finally(() => setLoading(false));
    };

    const loadNasaArchive = () => {
        setLoading(true);
        api.getArchive().then(data => {
            const mapped = data.map((item: any) => ({
                id: item.id,
                filename: item.filename,
                epb_detected: false,
                confidence: 0,
                date: item.date,
                region: "NASA Archive",
                image_url: "/placeholder.png"
            }));
            setDataset(mapped);
        }).finally(() => setLoading(false));
    };

    useEffect(() => {
        loadLocalDataset();
    }, []);

    // Filter and sort dataset
    const filteredDataset = dataset
        .filter(item => {
            if (statusFilter === 'detected') return item.epb_detected;
            if (statusFilter === 'clear') return !item.epb_detected;
            return true;
        })
        .filter(item =>
            item.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.region.toLowerCase().includes(searchTerm.toLowerCase())
        )
        .sort((a, b) => {
            if (sortBy === 'newest') return b.id.localeCompare(a.id);
            if (sortBy === 'oldest') return a.id.localeCompare(b.id);
            if (sortBy === 'confidence') return b.confidence - a.confidence;
            return 0;
        });

    if (loading) {
        return <div className="flex items-center justify-center h-screen">Loading dataset...</div>;
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold mb-2">Data Explorer</h1>
                <p className="text-muted-foreground">
                    Browse and label ionospheric imagery from NASA GOLD mission
                </p>
            </div>

            {/* Action Bar */}
            <div className="flex flex-col sm:flex-row gap-4">
                <Button variant="outline" className="gap-2">
                    <Download className="h-4 w-4" />
                    Export CSV
                </Button>
                <Button className="gap-2">
                    <Upload className="h-4 w-4" />
                    Upload New Batch
                </Button>
            </div>

            {/* Filter Bar */}
            <div className="glass-panel border-white/5 p-4 rounded-lg">
                <div className="grid gap-4 md:grid-cols-3">
                    {/* Search */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search by ID or Region..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-10 bg-black/20 border-white/10"
                        />
                    </div>

                    {/* Status Filter */}
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                        <SelectTrigger className="bg-black/20 border-white/10">
                            <SelectValue placeholder="Filter by status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Scans</SelectItem>
                            <SelectItem value="detected">EPB Detected</SelectItem>
                            <SelectItem value="clear">Clear</SelectItem>
                        </SelectContent>
                    </Select>

                    {/* Sort */}
                    <Select value={sortBy} onValueChange={setSortBy}>
                        <SelectTrigger className="bg-black/20 border-white/10">
                            <SelectValue placeholder="Sort by" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="newest">Newest First</SelectItem>
                            <SelectItem value="oldest">Oldest First</SelectItem>
                            <SelectItem value="confidence">Highest Confidence</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Tabs for Local vs Remote */}
            <div className="flex gap-4 border-b border-white/10 pb-4">
                <Button
                    variant={statusFilter !== 'nasa' ? "default" : "outline"}
                    onClick={() => {
                        setStatusFilter('all');
                        loadLocalDataset();
                    }}
                >
                    Processed Dataset
                </Button>
                <Button
                    variant={statusFilter === 'nasa' ? "default" : "outline"}
                    onClick={() => {
                        setStatusFilter('nasa');
                        loadNasaArchive();
                    }}
                >
                    NASA Archive (Live)
                </Button>
            </div>

            {/* Results Count */}
            <p className="text-sm text-muted-foreground">
                Showing {dataset.length} scans
            </p>

            {/* Data Grid */}
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {filteredDataset.map((scan, i) => (
                    <motion.div
                        key={scan.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: i * 0.05 }}
                    >
                        {statusFilter === 'nasa' && !scan.analyzed ? (
                            <div className="glass-panel border-white/5 p-4 rounded-lg space-y-2">
                                <p className="font-mono text-sm font-bold truncate" title={scan.filename}>{scan.filename}</p>
                                <p className="text-xs text-muted-foreground">{scan.date}</p>
                                <Button
                                    size="sm"
                                    className="w-full mt-2"
                                    variant="secondary"
                                    onClick={() => handleAnalyze(scan)}
                                    disabled={analyzingIds.has(scan.id)}
                                >
                                    {analyzingIds.has(scan.id) ? (
                                        "Analyzing..."
                                    ) : (
                                        <>
                                            <Search className="h-3 w-3 mr-2" />
                                            Analyze
                                        </>
                                    )}
                                </Button>
                            </div>
                        ) : (
                            <ScanCard scan={scan} />
                        )}
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
