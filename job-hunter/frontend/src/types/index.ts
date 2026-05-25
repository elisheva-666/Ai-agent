export interface JobSource {
  title: string;
  url: string;
  snippet: string;
  company: string;
  location: string;
  relevance_score: number;
  relevance_reason: string;
}

export type AppPhase =
  | 'landing'
  | 'cv_input'
  | 'searching'
  | 'awaiting_approval'
  | 'summarizing'
  | 'done';

export interface AppState {
  phase: AppPhase;
  threadId: string;
  cvText: string;
  sources: JobSource[];
  approvedSources: JobSource[];
  summary: string;
  error: string | null;
}
