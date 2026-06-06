import { useState } from 'react';
import api from '../api';
import { useProject } from '../contexts/ProjectContext';

interface NewProjectFormProps {
  onSuccess: () => void;
}

export const NewProjectForm = ({ onSuccess }: NewProjectFormProps) => {
  const { setCurrentProject } = useProject();
  const [name, setName] = useState('');
  const [customer, setCustomer] = useState('');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [template, setTemplate] = useState('标准版');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    setLoading(true);
    try {
      const res = await api.post('/projects', {
        name,
        customer,
        template_version: template,
        start_date: startDate,
      });
      // 创建成功后，将新项目ID存入localStorage，以便刷新后自动选中
      const newProjectId = res.data.id;
      if (newProjectId) {
        const newProject = { id: newProjectId, name, customer, start_date: startDate };
        setCurrentProject(newProject);
        localStorage.setItem('lastProjectId', String(newProjectId));
      }
      onSuccess();
      setName('');
      setCustomer('');
      setStartDate(new Date().toISOString().split('T')[0]);
      setTemplate('标准版');
    } catch (err) {
      console.error('创建失败', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginBottom: '1rem', border: '1px solid #ccc', padding: '0.5rem', borderRadius: '4px' }}>
      <h4 style={{ margin: '0 0 0.5rem 0' }}>➕ 新建项目</h4>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        <input type="text" placeholder="项目名称" value={name} onChange={e => setName(e.target.value)} required style={{ flex: '1 1 120px' }} />
        <input type="text" placeholder="客户名称" value={customer} onChange={e => setCustomer(e.target.value)} style={{ flex: '1 1 100px' }} />
        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} style={{ width: '130px' }} />
        <select value={template} onChange={e => setTemplate(e.target.value)} style={{ width: '100px' }}>
          <option>标准版</option>
          <option>加急版</option>
        </select>
        <button type="submit" disabled={loading}>创建</button>
      </form>
    </div>
  );
};