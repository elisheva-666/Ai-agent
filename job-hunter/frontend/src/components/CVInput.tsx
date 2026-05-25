import { useState } from 'react';
import { FileText, Sparkles } from 'lucide-react';

interface Props {
  onSubmit: (cv: string) => void;
  loading: boolean;
}

const EXAMPLE_CV = `שם: דניאל כהן
תפקיד מבוקש: Full Stack Developer

ניסיון:
• 3 שנות ניסיון בפיתוח Full Stack
• React, TypeScript, Node.js, Python
• PostgreSQL, MongoDB, Redis
• Docker, AWS, CI/CD

השכלה:
• B.Sc מדעי המחשב - אוניברסיטת תל אביב (2021)

שפות: עברית (שפת אם), אנגלית (שוטפת)`;

export default function CVInput({ onSubmit, loading }: Props) {
  const [cv, setCv] = useState('');

  return (
    <div className="cv-input-container">
      <div className="cv-header">
        <FileText size={28} />
        <h2>הדבק את קורות החיים שלך</h2>
        <p>ה-Agent ינתח את הניסיון שלך וימצא משרות מותאמות אישית</p>
      </div>

      <textarea
        className="cv-textarea"
        value={cv}
        onChange={e => setCv(e.target.value)}
        placeholder="הדבק כאן את קורות החיים שלך בכל פורמט..."
        rows={16}
        dir="rtl"
      />

      <div className="cv-actions">
        <button
          className="btn-secondary"
          onClick={() => setCv(EXAMPLE_CV)}
          type="button"
        >
          טען דוגמה
        </button>
        <button
          className="btn-primary"
          onClick={() => onSubmit(cv)}
          disabled={cv.trim().length < 50 || loading}
          type="button"
        >
          {loading ? (
            <span className="loading-dots">מחפש משרות<span>.</span><span>.</span><span>.</span></span>
          ) : (
            <>
              <Sparkles size={18} />
              התחל חיפוש
            </>
          )}
        </button>
      </div>
    </div>
  );
}
