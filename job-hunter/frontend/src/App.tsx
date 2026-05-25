import { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Briefcase, Zap } from 'lucide-react';
import CVInput from './components/CVInput';
import SourceSelector from './components/SourceSelector';
import Summary from './components/Summary';
import SearchingAnimation from './components/SearchingAnimation';
import { startSession, approveSources } from './hooks/useApi';
import { AppState } from './types';
import './App.css';

const initialState: AppState = {
  phase: 'cv_input',
  threadId: uuidv4(),
  cvText: '',
  sources: [],
  approvedSources: [],
  summary: '',
  error: null,
};

export default function App() {
  const [state, setState] = useState<AppState>(initialState);
  const [loading, setLoading] = useState(false);

  const handleCvSubmit = async (cv: string) => {
    setLoading(true);
    setState(prev => ({ ...prev, cvText: cv, phase: 'searching', error: null }));

    try {
      const result = await startSession(cv, state.threadId);
      setState(prev => ({
        ...prev,
        sources: result.sources,
        phase: 'awaiting_approval',
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        phase: 'cv_input',
        error: `שגיאה: ${err instanceof Error ? err.message : 'משהו השתבש'}`,
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (indices: number[]) => {
    setLoading(true);
    setState(prev => ({ ...prev, phase: 'summarizing' }));

    try {
      const result = await approveSources(state.threadId, indices);
      setState(prev => ({
        ...prev,
        approvedSources: result.approved_sources,
        summary: result.summary,
        phase: 'done',
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        phase: 'awaiting_approval',
        error: `שגיאה: ${err instanceof Error ? err.message : 'משהו השתבש'}`,
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = () => {
    setState({ ...initialState, threadId: uuidv4() });
  };

  return (
    <div className="app" dir="rtl">
      {/* Header */}
      <header className="app-header">
        <div className="header-logo">
          <Briefcase size={22} />
          <span>Job Hunter</span>
          <span className="header-ai-badge">
            <Zap size={11} />
            AI
          </span>
        </div>
        <nav className="header-steps">
          <span className={`step ${['cv_input'].includes(state.phase) ? 'active' : ['searching','awaiting_approval','summarizing','done'].includes(state.phase) ? 'done' : ''}`}>
            1. קורות חיים
          </span>
          <span className="step-divider">→</span>
          <span className={`step ${['awaiting_approval'].includes(state.phase) ? 'active' : ['summarizing','done'].includes(state.phase) ? 'done' : ''}`}>
            2. בחר מקורות
          </span>
          <span className="step-divider">→</span>
          <span className={`step ${state.phase === 'done' ? 'active done' : ''}`}>
            3. סיכום
          </span>
        </nav>
      </header>

      {/* Main content */}
      <main className="app-main">
        {state.error && (
          <div className="error-banner">{state.error}</div>
        )}

        {(state.phase === 'cv_input') && (
          <CVInput onSubmit={handleCvSubmit} loading={loading} />
        )}

        {(state.phase === 'searching' || state.phase === 'summarizing') && (
          <SearchingAnimation />
        )}

        {state.phase === 'awaiting_approval' && (
          <SourceSelector
            sources={state.sources}
            onApprove={handleApprove}
            loading={loading}
          />
        )}

        {state.phase === 'done' && (
          <Summary
            summary={state.summary}
            approvedSources={state.approvedSources}
            onRestart={handleRestart}
          />
        )}
      </main>
    </div>
  );
}
