import { useState } from 'react';
import { CheckCircle, Circle, ExternalLink, MapPin, Building2, Star, ChevronDown, ChevronUp } from 'lucide-react';
import { JobSource } from '../types';

interface Props {
  sources: JobSource[];
  onApprove: (indices: number[]) => void;
  loading: boolean;
}

export default function SourceSelector({ sources, onApprove, loading }: Props) {
  const [selected, setSelected] = useState<Set<number>>(
    new Set(sources.map((_, i) => i)) // all selected by default
  );
  const [expanded, setExpanded] = useState<number | null>(null);

  const toggle = (i: number) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  };

  const toggleAll = () => {
    if (selected.size === sources.length) setSelected(new Set());
    else setSelected(new Set(sources.map((_, i) => i)));
  };

  const relevanceColor = (score: number) => {
    if (score >= 8) return '#4ade80';
    if (score >= 6) return '#facc15';
    return '#f87171';
  };

  return (
    <div className="source-selector">
      <div className="selector-header">
        <div className="selector-title">
          <h2>נמצאו {sources.length} משרות רלוונטיות</h2>
          <p>בחר את המשרות שברצונך לכלול בסיכום הסופי</p>
        </div>
        <div className="selector-controls">
          <button className="btn-ghost" onClick={toggleAll}>
            {selected.size === sources.length ? 'בטל הכל' : 'בחר הכל'}
          </button>
          <span className="selected-count">{selected.size} נבחרו</span>
        </div>
      </div>

      <div className="sources-grid">
        {sources.map((source, i) => (
          <div
            key={i}
            className={`source-card ${selected.has(i) ? 'selected' : ''}`}
            onClick={() => toggle(i)}
          >
            <div className="source-card-main">
              <div className="source-checkbox">
                {selected.has(i)
                  ? <CheckCircle size={22} className="check-icon" />
                  : <Circle size={22} className="circle-icon" />
                }
              </div>

              <div className="source-info">
                <div className="source-title">{source.title || 'משרה רלוונטית'}</div>
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

              <div className="source-right">
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
                    className="source-link"
                    onClick={e => e.stopPropagation()}
                  >
                    <ExternalLink size={14} />
                  </a>
                )}

                <button
                  className="expand-btn"
                  onClick={e => { e.stopPropagation(); setExpanded(expanded === i ? null : i); }}
                >
                  {expanded === i ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
              </div>
            </div>

            {expanded === i && source.relevance_reason && (
              <div className="source-expanded" onClick={e => e.stopPropagation()}>
                <strong>למה זה מתאים לך:</strong> {source.relevance_reason}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="approve-actions">
        <button
          className="btn-primary btn-large"
          onClick={() => onApprove(Array.from(selected))}
          disabled={selected.size === 0 || loading}
        >
          {loading ? (
            <span className="loading-dots">מכין סיכום<span>.</span><span>.</span><span>.</span></span>
          ) : (
            `צור סיכום עבור ${selected.size} משרות →`
          )}
        </button>
      </div>
    </div>
  );
}
