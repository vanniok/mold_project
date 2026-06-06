import { useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import api from '../api';

interface HistoryCase {
  project_name: string;
  customer: string;
  problem_node: string;
  solution: string;
  delay_days: number;
}

export const HistorySearch = () => {
  const { currentProject } = useProject();
  const [cases, setCases] = useState<HistoryCase[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!currentProject) return;
    setLoading(true);
    setError('');
    setCases([]);
    try {
      const res = await api.get('/history/cases', {
        params: {
          project_name: currentProject.name,
          customer: currentProject.customer || '',
        },
      });
      setCases(res.data);
      if (res.data.length === 0) {
        setError('未找到相似历史案例');
      }
    } catch (err) {
      setError('请求失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ margin: '1rem 0' }}>
      <button onClick={handleSearch} disabled={loading || !currentProject}>
        📚 检索历史库
      </button>
      {loading && <span> 搜索中...</span>}
      {error && <div style={{ color: 'red', marginTop: '8px' }}>{error}</div>}
      {cases.length > 0 && (
        <div style={{ marginTop: '8px', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}>
          <h4>📖 历史案例参考</h4>
          {cases.map((c, idx) => (
            <div key={idx} style={{ marginBottom: '12px' }}>
              <strong>{c.problem_node}</strong> 节点延期 {c.delay_days} 天（项目：{c.project_name}）
              <div style={{ fontSize: '0.9rem', color: '#555' }}>解决方案：{c.solution}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};