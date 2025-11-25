import { useQuery } from '@tanstack/react-query';
import { dashboardApi, documentsApi } from '../services/api';

export interface DashboardData {
  stats: {
    totalDocuments: number;
    monthlyUploads: number;
    totalQuestions: number;
    successRate: number;
  };
  activity: {
    labels: string[];
    documents: number[];
    questions: number[];
  };
  documentTypes: {
    labels: string[];
    data: number[];
  };
  recentActivities: Array<{
    id: number;
    type: 'upload' | 'question' | 'complete';
    title: string;
    time: string;
    color: string;
  }>;
}

export function useDashboardData() {
  return useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      try {
        // Fetch dashboard stats from backend
        const stats = await dashboardApi.getStats();
        const recentActivity = await dashboardApi.getRecentActivity(3);
        let weeklyActivity = { documents: [0, 0, 0, 0, 0, 0, 0], questions: [0, 0, 0, 0, 0, 0, 0] };
        
        try {
          weeklyActivity = await dashboardApi.getWeeklyActivity();
        } catch (err) {
          console.warn('Failed to fetch weekly activity, using defaults:', err);
        }
        
        console.log('Dashboard stats:', stats);
        console.log('Recent activity:', recentActivity);
        console.log('Weekly activity:', weeklyActivity);
        const documents = await documentsApi.list({ limit: 100 });

        // Calculate monthly uploads (documents from this month)
        const now = new Date();
        const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
        const monthlyDocs = documents.data?.filter((doc: any) => {
          const docDate = new Date(doc.created_at);
          return docDate >= firstDayOfMonth;
        }) || [];

        // Use document types from backend stats (more accurate)
        const documentsByType = stats.documentsByType || {};
        
        // Format labels with proper display names
        const typeLabels: Record<string, string> = {
          'pdf': 'PDF',
          'docx': 'DOCX',
          'txt': 'TXT',
          'hl7': 'HL7',
          'fhir': 'FHIR/JSON',
          'other': 'Autres'
        };

        const documentTypeLabels = Object.keys(documentsByType).map(key => typeLabels[key] || key.toUpperCase());
        const documentTypeCounts = Object.values(documentsByType);

        // Generate actual day labels for the last 7 days
        const today = new Date();
        const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
        const weekDays = [];
        for (let i = 6; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(today.getDate() - i);
          weekDays.push(dayNames[date.getDay()]);
        }

        // Format recent activities
        const formattedActivities = recentActivity.map((activity: any, index: number) => ({
          id: index + 1,
          type: activity.type === 'document_upload' || activity.type === 'upload' ? 'upload' as const :
                activity.type === 'question_asked' || activity.type === 'question' ? 'question' as const :
                'complete' as const,
          title: activity.details,
          time: formatTimeAgo(activity.timestamp),
          color: activity.type === 'document_upload' || activity.type === 'upload' ? '#3b82f6' :
                 activity.type === 'question_asked' || activity.type === 'question' ? '#8b5cf6' : '#10b981',
        }));

        return {
          stats: {
            totalDocuments: stats.totalDocuments || documents.total || 0,
            monthlyUploads: monthlyDocs.length,
            totalQuestions: stats.totalQuestions || 0,
            successRate: Math.round(stats.averageConfidence || 0), // API already returns percentage
          },
          activity: {
            labels: weekDays,
            documents: weeklyActivity.documents || [0, 0, 0, 0, 0, 0, 0],
            questions: weeklyActivity.questions || [0, 0, 0, 0, 0, 0, 0],
          },
          documentTypes: {
            labels: documentTypeLabels.length > 0 ? documentTypeLabels : ['PDF', 'DOCX', 'HL7', 'FHIR', 'Autres'],
            data: documentTypeCounts.length > 0 ? documentTypeCounts : [0, 0, 0, 0, 0],
          },
          recentActivities: formattedActivities,
        };
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Return fallback data if API fails
        return {
          stats: {
            totalDocuments: 0,
            monthlyUploads: 0,
            totalQuestions: 0,
            successRate: 0,
          },
          activity: {
            labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
            documents: [0, 0, 0, 0, 0, 0, 0],
            questions: [0, 0, 0, 0, 0, 0, 0],
          },
          documentTypes: {
            labels: ['PDF', 'DOCX', 'HL7', 'FHIR', 'Autres'],
            data: [0, 0, 0, 0, 0],
          },
          recentActivities: [],
        };
      }
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Data is fresh for 10 seconds
  });
}

function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const past = new Date(timestamp);
  const diffMs = now.getTime() - past.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) {
    return `Il y a ${diffMins}min`;
  } else if (diffHours < 24) {
    return `Il y a ${diffHours}h`;
  } else if (diffDays === 1) {
    return 'Hier';
  } else {
    return `Il y a ${diffDays}j`;
  }
}
