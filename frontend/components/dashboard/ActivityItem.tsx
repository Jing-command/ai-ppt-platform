'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { FileText, Layers, ChevronRight } from 'lucide-react';
import { RecentActivity } from '@/lib/api/dashboard';

interface ActivityItemProps {
  activity: RecentActivity;
  index: number;
}

export function ActivityItem({ activity, index }: ActivityItemProps) {
  const getActivityHref = () => {
    return activity.type === 'outline'
      ? `/outlines/${activity.id}`
      : `/presentations/${activity.id}`;
  };

  const getStatusText = () => {
    const statusMap: Record<string, string> = {
      completed: '已完成',
      draft: '草稿',
      published: '已发布',
      generating: '生成中',
      archived: '已归档'
    };
    return statusMap[activity.status] || activity.status;
  };

  const isCompleted = activity.status === 'completed' || activity.status === 'published';

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.5 + index * 0.1 }}
      className="group flex items-center justify-between p-4 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer"
    >
      <Link href={getActivityHref()} className="flex items-center gap-4 flex-1">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
          activity.type === 'outline'
            ? 'bg-blue-50 text-blue-600'
            : 'bg-purple-50 text-purple-600'
        }`}>
          {activity.type === 'outline' ? (
            <FileText className="w-5 h-5" />
          ) : (
            <Layers className="w-5 h-5" />
          )}
        </div>
        <div>
          <h4 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
            {activity.title}
          </h4>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-xs text-gray-500">{activity.updatedAt}</span>
            <span className="w-1 h-1 rounded-full bg-gray-300" />
            <span className={`text-xs ${
              isCompleted ? 'text-green-600' : 'text-amber-600'
            }`}>
              {getStatusText()}
            </span>
          </div>
        </div>
      </Link>
      <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
    </motion.div>
  );
}
