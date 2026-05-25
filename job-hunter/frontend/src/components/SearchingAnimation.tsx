import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';

const MESSAGES = [
  'מנתח את קורות החיים שלך...',
  'מחפש משרות ב-LinkedIn...',
  'סורק את AllJobs ו-Drushim...',
  'מחפש ב-Glassdoor...',
  'בודק התאמות בינלאומיות...',
  'מנתח דרישות משרות...',
  'מדרג לפי רלוונטיות...',
  'כמעט סיימנו...',
];

export default function SearchingAnimation() {
  const [msgIndex, setMsgIndex] = useState(0);
  const [dots, setDots] = useState(0);

  useEffect(() => {
    const msgInterval = setInterval(() => {
      setMsgIndex(prev => (prev + 1) % MESSAGES.length);
    }, 2500);
    const dotsInterval = setInterval(() => {
      setDots(prev => (prev + 1) % 4);
    }, 400);
    return () => {
      clearInterval(msgInterval);
      clearInterval(dotsInterval);
    };
  }, []);

  return (
    <div className="searching-container">
      <div className="searching-visual">
        <div className="radar-ring ring1" />
        <div className="radar-ring ring2" />
        <div className="radar-ring ring3" />
        <div className="radar-center">
          <Search size={28} />
        </div>
      </div>
      <div className="searching-message">
        {MESSAGES[msgIndex]}{'·'.repeat(dots)}
      </div>
      <div className="searching-sub">
        ה-Agent מחפש עשרות אתרי דרושים עבורך
      </div>
    </div>
  );
}
