import React, { createContext, useState, useContext } from 'react';

interface Project {
  id: number;
  name: string;
  customer: string;
  start_date?: string;   // 可选，格式 "2026-05-21T00:00:00"
}

interface ProjectContextType {
  currentProject: Project | null;
  setCurrentProject: (project: Project | null) => void;
  refreshNodes: boolean;
  triggerRefreshNodes: () => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [refreshNodes, setRefreshNodes] = useState(false);
  const triggerRefreshNodes = () => setRefreshNodes(prev => !prev);
  return (
    <ProjectContext.Provider value={{ currentProject, setCurrentProject, refreshNodes, triggerRefreshNodes }}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = () => {
  const ctx = useContext(ProjectContext);
  if (!ctx) throw new Error('useProject must be used within ProjectProvider');
  return ctx;
};