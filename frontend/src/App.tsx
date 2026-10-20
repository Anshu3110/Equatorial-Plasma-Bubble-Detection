import { Route, Router } from 'wouter';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { DataExplorer } from './pages/DataExplorer';
import { LiveAnalysis } from './pages/LiveAnalysis';
import { Reports } from './pages/Reports';

export default function App() {
  return (
    <div className="app-container">
      <Sidebar />

      {/* Main Content */}
      <div className="md:pl-72">
        <div className="min-h-screen p-8">
          <Router>
            <Route path="/" component={Dashboard} />
            <Route path="/dataset" component={DataExplorer} />
            <Route path="/analysis" component={LiveAnalysis} />
            <Route path="/reports" component={Reports} />
            <Route path="/docs">
              <div className="text-center py-20">
                <h1 className="text-4xl font-bold mb-4">Documentation</h1>
                <p className="text-muted-foreground">Coming soon...</p>
              </div>
            </Route>
          </Router>
        </div>
      </div>
    </div>
  );
}
