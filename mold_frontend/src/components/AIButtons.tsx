import { useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import api from '../api';

interface Suggestion {
  node: string;
  new_planned_start: string;
  new_planned_end: string;
  reason: string;
}

export const AIButtons = () => {
  const { currentProject } = useProject();
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [message, setMessage] = useState('');

  const handleCompress = async () => {
    if (!currentProject) return;
    setLoading(true);
    setMessage('');
    setSuggestions([]);
    try {
      const res = await api.post('/ai/compress', { project_id: currentProject.id });
      if (res.data.error) {
        setMessage(res.data.error);
      } else if (res.data.message) {
        setMessage(res.data.message);
      } else if (res.data.suggestions) {
        setSuggestions(res.data.suggestions);
      }
    } catch (err) {
      setMessage('请求失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ margin: '1rem 0' }}>
      <button onClick={handleCompress} disabled={loading || !currentProject}>
        🤖 AI 压缩建议
      </button>
      {loading && <span style={{ marginLeft: '8px' }}>分析中...</span>}
      {message && <div style={{ color: 'red', marginTop: '8px' }}>{message}</div>}
      {suggestions.length > 0 && (
        <div style={{ marginTop: '8px', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}>
          <h4>📌 压缩建议</h4>
          <ul>
            {suggestions.map((s, idx) => (
              <li key={idx}>
                <strong>{s.node}</strong>：原计划结束 {s.new_planned_end}（{s.reason}）
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};