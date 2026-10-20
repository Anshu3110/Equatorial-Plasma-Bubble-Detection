import { Link, useRoute } from 'wouter';
import {
    LayoutDashboard,
    Database,
    Satellite,
    Activity,
    FileText,
    Menu,
} from 'lucide-react';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Data Explorer', href: '/dataset', icon: Database },
    { name: 'Live Analysis', href: '/analysis', icon: Satellite },
    { name: 'Model Metrics', href: '/reports', icon: Activity },
    { name: 'Documentation', href: '/docs', icon: FileText },
];

export function Sidebar() {
    return (
        <>
            {/* Desktop Sidebar */}
            <div className="hidden md:fixed md:inset-y-0 md:flex md:w-72 md:flex-col">
                <div className="flex flex-col flex-grow border-r border-white/5 bg-background/95 backdrop-blur">
                    <SidebarContent />
                </div>
            </div>

            {/* Mobile Sidebar */}
            <div className="md:hidden">
                <MobileSidebar />
            </div>
        </>
    );
}

function SidebarContent() {
    return (
        <>
            {/* Logo */}
            <div className="flex h-20 items-center gap-3 border-b border-white/5 px-6">
                <div className="flex h-8 w-8 items-center justify-center rounded border border-primary/30 bg-primary/10">
                    <Satellite className="h-5 w-5 text-primary" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold">EPB-NET</h1>
                    <p className="text-xs uppercase tracking-widest text-muted-foreground">
                        Deep Space Monitor
                    </p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 px-4 py-6">
                {navigation.map((item) => (
                    <NavItem key={item.name} item={item} />
                ))}
            </nav>

            {/* System Status */}
            <div className="p-4">
                <div className="glass-panel rounded-lg p-4">
                    <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-3">
                        System Status
                    </p>
                    <div className="space-y-2">
                        <StatusIndicator label="NASA GOLD" status="Online" />
                        <StatusIndicator label="GNSS Grid" status="Synced" />
                    </div>
                </div>
            </div>
        </>
    );
}

function NavItem({ item }: { item: typeof navigation[0] }) {
    const [isActive] = useRoute(item.href);
    const Icon = item.icon;

    return (
        <Link href={item.href}>
            <a
                className={`
          group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium
          transition-all duration-200
          ${isActive
                        ? 'bg-primary/10 text-primary border border-primary/20 shadow-[0_0_15px_rgba(0,240,255,0.1)]'
                        : 'text-muted-foreground hover:bg-white/5 hover:text-white border border-transparent'
                    }
        `}
            >
                <Icon className={`h-5 w-5 ${isActive ? 'animate-pulse' : ''}`} />
                <span>{item.name}</span>
                {isActive && (
                    <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(0,240,255,0.8)]" />
                )}
            </a>
        </Link>
    );
}

function StatusIndicator({ label, status }: { label: string; status: string }) {
    return (
        <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">{label}</span>
            <div className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.8)]" />
                <span className="text-success">{status}</span>
            </div>
        </div>
    );
}

function MobileSidebar() {
    const [open, setOpen] = useState(false);

    return (
        <div className="fixed top-0 left-0 right-0 z-50 flex h-16 items-center gap-4 border-b border-white/5 bg-background/95 backdrop-blur px-4">
            <Sheet open={open} onOpenChange={setOpen}>
                <SheetTrigger asChild>
                    <Button variant="ghost" size="icon">
                        <Menu className="h-6 w-6" />
                    </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-72 p-0">
                    <SidebarContent />
                </SheetContent>
            </Sheet>
            <h1 className="text-xl font-bold">EPB-NET</h1>
        </div>
    );
}
