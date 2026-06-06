import { ExternalTasks } from '../components/ExternalTasks';

import { ProjectSidebar } from '../components/ProjectSidebar';
import { NodeTable } from '../components/NodeTable';
import { ProjectProvider, useProject } from '../contexts/ProjectContext';
import { GanttChart } from '../components/GanttChart';
import { AIButtons } from '../components/AIButtons';
import { VoiceAlert } from '../components/VoiceAlert';
import { OverdueReminders } from '../components/OverdueReminders';
import { HistorySearch } from '../components/HistorySearch';
import { GlobalStats } from '../components/GlobalStats';
import { NewProjectForm } from '../components/NewProjectForm';


const DashboardContent = () => {
  const { currentProject, setCurrentProject, triggerRefreshNodes } = useProject();

  const handleSetStartDate = async () => {
    if (!currentProject) return;
    const input = document.getElementById('projectStartDate') as HTMLInputElement;
    const newDate = input.value;
    if (!newDate) return;

    const projectId = Number(currentProject.id);
    const url = 'http://localhost:8000/projects/' + projectId + '/start-date';
    console.log('请求URL:', url);

    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_date: newDate })
      });
      if (response.ok) {
        setCurrentProject({ ...currentProject, start_date: newDate });
        triggerRefreshNodes();
      } else {
        console.error('更新失败：', response.status);
      }
    } catch (err) {
      console.error('请求异常', err);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ width: 280, padding: '1rem', borderRight: '1px solid #ccc', overflowY: 'auto', backgroundColor: '#fafafa' }}>
        <GlobalStats />
        <NewProjectForm onSuccess={() => window.location.reload()} />
        <ProjectSidebar />
      </div>
      <div style={{ flex: 1, padding: '1rem', overflowY: 'auto' }}>
        {currentProject ? (
          <>
            <h1>{currentProject.name}</h1>
            <p>客户：{currentProject.customer}</p>

            <GanttChart />

            <div style={{ marginBottom: '1rem', display: 'flex', gap: '8px', alignItems: 'center' }}>
              <label>项目开始日期：</label>
              <input
                type="date"
                id="projectStartDate"
                defaultValue={currentProject.start_date ? currentProject.start_date.split('T')[0] : ''}
              />
              <button onClick={handleSetStartDate}>📅 设定开始日期</button>
            </div>

            <AIButtons />
            <HistorySearch />
            <VoiceAlert />
            <OverdueReminders />
            <NodeTable />
            <ExternalTasks />
          </>
        ) : (
          <p>请从左侧选择一个项目</p>
        )}
      </div>
    </div>
  );
};

export const Dashboard = () => {
  return (
    <ProjectProvider>
      <DashboardContent />
    </ProjectProvider>
  );
};