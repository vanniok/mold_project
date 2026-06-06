// src/components/ProjectInfo.tsx
import { useProject } from '../contexts/ProjectContext';

export const ProjectInfo = () => {
  const { currentProject } = useProject();
  if (!currentProject) return null;
  return (
    <div>
      <h1>{currentProject.name}</h1>
      <p>客户：{currentProject.customer}</p>
    </div>
  );
};