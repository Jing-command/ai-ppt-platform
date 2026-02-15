import {
  FileText,
  Sparkles,
  Palette,
  Plug,
  Lightbulb,
  TrendingUp,
  Target,
  Clock,
  BarChart3,
  Zap,
  Layers
} from 'lucide-react';

export const QUICK_ACTIONS = [
  {
    title: 'AI 生成大纲',
    description: '智能生成演示文稿结构',
    iconName: 'Sparkles',
    href: '/outlines/new',
    gradient: 'from-blue-500 via-indigo-500 to-purple-600',
    featured: true
  },
  {
    title: '查看我的大纲',
    description: '管理和编辑现有大纲',
    iconName: 'FileText',
    href: '/outlines',
    gradient: 'from-emerald-500 to-teal-600',
    featured: false
  },
  {
    title: '我的 PPT',
    description: '查看和编辑演示文稿',
    iconName: 'Palette',
    href: '/presentations',
    gradient: 'from-purple-500 to-pink-600',
    featured: false
  },
  {
    title: '数据连接器',
    description: '管理数据库和 API 连接',
    iconName: 'Plug',
    href: '/connectors',
    gradient: 'from-orange-500 to-amber-600',
    featured: false
  }
] as const;

export const TIPS = [
  {
    iconName: 'Lightbulb',
    title: '提示词技巧',
    desc: '如何写出更有效的 AI 提示词',
    color: 'text-amber-500',
    bgColor: 'bg-amber-50',
    href: '/tips/prompts'
  },
  {
    iconName: 'BarChart3',
    title: '数据可视化',
    desc: '让图表更有说服力的方法',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50',
    href: '/tips/visualization'
  },
  {
    iconName: 'Zap',
    title: '快捷操作',
    desc: '提升制作效率的快捷键',
    color: 'text-purple-500',
    bgColor: 'bg-purple-50',
    href: '/help/shortcuts'
  }
] as const;

export const STATS_CONFIG = [
  {
    label: '总大纲数',
    key: 'totalOutlines' as const,
    iconName: 'FileText',
    gradient: 'from-blue-500 to-indigo-600',
    bgGradient: 'from-blue-50 to-indigo-50'
  },
  {
    label: '本周创建',
    key: 'createdThisWeek' as const,
    iconName: 'TrendingUp',
    gradient: 'from-emerald-500 to-teal-600',
    bgGradient: 'from-emerald-50 to-teal-50'
  },
  {
    label: '已完成PPT',
    key: 'completedPpts' as const,
    iconName: 'Target',
    gradient: 'from-purple-500 to-pink-600',
    bgGradient: 'from-purple-50 to-pink-50'
  },
  {
    label: '最近编辑',
    key: 'recentEdits' as const,
    iconName: 'Clock',
    gradient: 'from-orange-500 to-amber-600',
    bgGradient: 'from-orange-50 to-amber-50'
  }
] as const;

export const TEMPLATES = [
  { title: '工作周报', iconName: 'FileText', color: 'from-blue-500 to-indigo-600', desc: '简洁专业的周报结构' },
  { title: '商业计划', iconName: 'BarChart3', color: 'from-purple-500 to-pink-600', desc: '完整商业计划框架' },
  { title: '教育课件', iconName: 'Layers', color: 'from-emerald-500 to-teal-600', desc: '互动式教学设计' },
  { title: '营销方案', iconName: 'Target', color: 'from-orange-500 to-amber-600', desc: '营销活动策划模板' }
] as const;

export const ICON_MAP = {
  FileText,
  Sparkles,
  Palette,
  Plug,
  Lightbulb,
  TrendingUp,
  Target,
  Clock,
  BarChart3,
  Zap,
  Layers
} as const;

export type IconName = keyof typeof ICON_MAP;
