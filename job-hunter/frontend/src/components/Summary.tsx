import { ExternalLink, MapPin, Building2, Star, RefreshCw } from 'lucide-react';
import { JobSource } from '../types';

interface Props {
  summary: string;
  approvedSources: JobSource[];
  onRestart: () => void;
}

const relevanceColor = (score: number) => {
  if (score >= 8) return '#4ade80';
  if (score >= 6) return '#facc15';
  return '#f87171';
};

export default function Summary({ summary, approvedSources, onRestart }: Props) {
  return (
    <div className="summary-container">
      <div className="summary-header">
        <div className="summary-badge">✓ החיפוש הושלם</div>
        <h2>סיכום תוצאות החיפוש</h2>
      </div>

      <div className="summary-box">
        <h3>ניתוח שוק העבודה עבורך</h3>
        <p>{summary}</p>
      </div>

      <div className="approved-section">
        <h3>{approvedSources.length} משרות נבחרו</h3>
        <div className="approved-list">
          {approvedSources.map((source, i) => (
            <div key={i} className="approved-card">
              <div className="approved-rank">#{i + 1}</div>
              <div className="approved-info">
                <div className="approved-title">{source.title}</div>
                <div className="source-meta">
                  {source.company && (
                    <span className="meta-item">
                      <Building2 size={13} />
                      {source.company}
                    </span>
                  )}
                  {source.location && (
                    <span className="meta-item">
                      <MapPin size={13} />
                      {source.location}
                    </span>
                  )}
                </div>
                <div className="source-snippet">{source.snippet}</div>
              </div>
              <div className="approved-actions">
                <div className="relevance-badge" style={{ borderColor: relevanceColor(source.relevance_score) }}>
                  <Star size={12} fill={relevanceColor(source.relevance_score)} stroke="none" />
                  <span style={{ color: relevanceColor(source.relevance_score) }}>
                    {source.relevance_score}/10
                  </span>
                </div>
                {source.url && (
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-apply"
                  >
                    הגש מועמדות
                    <ExternalLink size={14} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="restart-section">
        <button className="btn-secondary" onClick={onRestart}>
          <RefreshCw size={16} />
          חיפוש חדש
        </button>
      </div>
    </div>
  );
}
