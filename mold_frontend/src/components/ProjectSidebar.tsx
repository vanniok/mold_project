import { useEffect, useState } from 'react';
import api from '../api';
import { useProject } from '../contexts/ProjectContext';

interface Project {
  id: number;
  name: string;
  customer: string;
}

export const ProjectSidebar = () => {
  const { currentProject, setCurrentProject } = useProject();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const loadProjects = () => {
    api.get('/projects')
      .then(res => {
        setProjects(res.data);
        setLoading(false);
        // 加载完成后尝试恢复上次选中的项目
        const lastProjectId = localStorage.getItem('lastProjectId');
        if (lastProjectId && !currentProject) {
          const lastProject = res.data.find((p: Project) => p.id === parseInt(lastProjectId));
          if (lastProject) {
            setCurrentProject(lastProject);
          } else {
            // 如果存储的项目ID不存在（已被删除），清除存储
            localStorage.removeItem('lastProjectId');
          }
        }
      })
      .catch(err => {
        console.error('加载项目失败', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleSelectProject = (project: Project) => {
    setCurrentProject(project);
    localStorage.setItem('lastProjectId', String(project.id));
  };

  const handleEdit = async (project: Project) => {
    const newName = prompt('请输入新项目名称', project.name);
    if (newName === null) return;
    const newCustomer = prompt('请输入新客户名称', project.customer);
    if (newCustomer === null) return;
    try {
      await api.put(`/projects/${project.id}`, { name: newName, customer: newCustomer });
      loadProjects();
      if (currentProject?.id === project.id) {
        setCurrentProject({ ...project, name: newName, customer: newCustomer });
      }
    } catch (err) {
      console.error('编辑失败', err);
    }
  };

  const handleDelete = async (projectId: number) => {
    try {
      await api.delete(`/projects/${projectId}`);
      loadProjects();
      if (currentProject?.id === projectId) {
        setCurrentProject(null);
        localStorage.removeItem('lastProjectId');
      }
    } catch (err) {
      console.error('删除失败', err);
    }
  };

  if (loading) return <div>加载项目...</div>;

  return (
    <div>
      <h3>项目列表</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {projects.map(p => (
          <li
            key={p.id}
            style={{
              padding: '8px 12px',
              marginBottom: '4px',
              cursor: 'pointer',
              backgroundColor: currentProject?.id === p.id ? '#e6f7ff' : 'transparent',
              borderRadius: '4px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <span onClick={() => handleSelectProject(p)} style={{ flex: 1 }}>
              {p.name} <span style={{ fontSize: '0.8rem', color: '#666' }}>({p.customer})</span>
            </span>
            <div>
              <button onClick={(e) => { e.stopPropagation(); handleEdit(p); }} style={{ marginRight: '4px', fontSize: '12px' }}>✏️</button>
              <button onClick={(e) => { e.stopPropagation(); handleDelete(p.id); }} style={{ fontSize: '12px', color: 'red' }}>🗑️</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};