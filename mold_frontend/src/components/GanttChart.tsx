import { useEffect, useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import api from '../api';

declare global {
  interface Window {
    Plotly: any;
  }
}

export const GanttChart = () => {
  const { currentProject, refreshNodes } = useProject();
  const [nodes, setNodes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const chartDivId = 'gantt-chart';

  useEffect(() => {
    if (currentProject) {
      fetchNodes();
    } else {
      setNodes([]);
    }
  }, [currentProject, refreshNodes]);

  const fetchNodes = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/projects/${currentProject!.id}/nodes`);
      setNodes(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!currentProject || loading || nodes.length === 0) return;
    if (!window.Plotly) {
      console.error('Plotly not loaded');
      return;
    }

    // 计算偏移基准
    const allDates = nodes.flatMap((node: any) => [
      node.planned_start,
      node.planned_end,
      node.actual_start,
      node.actual_end,
    ]).filter((d: string | null) => d !== null).map((d: string) => new Date(d));
    const minDate = new Date(Math.min(...allDates.map(d => d.getTime())));
    const getOffset = (dateStr: string | null) => {
      if (!dateStr) return 0;
      const d = new Date(dateStr);
      return Math.floor((d.getTime() - minDate.getTime()) / (1000 * 3600 * 24));
    };

    const plannedX = nodes.map((node: any) => {
      const start = getOffset(node.planned_start);
      const end = getOffset(node.planned_end);
      return end - start;
    });
    const actualX = nodes.map((node: any) => {
      if (node.actual_end) {
        const start = getOffset(node.actual_start);
        const end = getOffset(node.actual_end);
        return end - start;
      } else if (node.actual_start) {
        const start = getOffset(node.actual_start);
        const today = new Date();
        const todayOffset = Math.floor((today.getTime() - minDate.getTime()) / (1000 * 3600 * 24));
        return Math.max(0, todayOffset - start);
      } else {
        return 0;
      }
    });

    const plannedBase = nodes.map((node: any) => getOffset(node.planned_start));
    const actualBase = nodes.map((node: any) => getOffset(node.actual_start));
    const colors = nodes.map((node: any) => {
      if (node.status === 'overdue') return '#800000';
      if (node.status === 'delayed') return 'red';
      if (node.status === 'done') return 'green';
      if (node.actual_start && !node.actual_end) return 'orange';
      return 'lightgray';
    });
    const texts = nodes.map((node: any) => {
      if (node.actual_end) return '完成';
      if (node.actual_start && node.progress_percent) return `${node.progress_percent}%`;
      return '';
    });

    const data = [
      {
        x: plannedX,
        y: nodes.map((node: any) => node.node_name),
        type: 'bar',
        orientation: 'h',
        marker: { color: 'lightgray' },
        name: '计划',
        base: plannedBase,
        text: nodes.map(() => ''),
        hoverinfo: 'x+y',
      },
      {
        x: actualX,
        y: nodes.map((node: any) => node.node_name),
        type: 'bar',
        orientation: 'h',
        marker: { color: colors },
        name: '实际',
        base: actualBase,
        text: texts,
        textposition: 'auto',
        hoverinfo: 'text',
      },
    ];

    const layout = {
        title: '项目进度甘特图',
        xaxis: { title: '天数偏移（0 = 最早开始日期）' },
        yaxis: { title: '节点', autorange: 'reversed' },
        barmode: 'group',
        height: 600,
        paper_bgcolor: 'white',   // 图表外围背景白色
        plot_bgcolor: 'white',    // 绘图区背景白色
        margin: { t: 50, l: 80, r: 20, b: 50 }, // 可选，调整边距避免压缩
    };

    window.Plotly.newPlot(chartDivId, data, layout, { responsive: true });
  }, [currentProject, nodes, loading]);

  if (!currentProject) return null;
  if (loading) return <div>加载甘特图...</div>;
  if (nodes.length === 0) return <div>暂无节点数据</div>;

  return <div id={chartDivId} style={{ width: '100%', height: '600px' }} />;
};