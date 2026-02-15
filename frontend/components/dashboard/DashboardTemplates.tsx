'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, FileText, BarChart3, Layers, Target } from 'lucide-react';

const templates = [
  { title: '工作周报', icon: FileText, color: 'from-blue-500 to-indigo-600', desc: '简洁专业的周报结构' },
  { title: '商业计划', icon: BarChart3, color: 'from-purple-500 to-pink-600', desc: '完整商业计划框架' },
  { title: '教育课件', icon: Layers, color: 'from-emerald-500 to-teal-600', desc: '互动式教学设计' },
  { title: '营销方案', icon: Target, color: 'from-orange-500 to-amber-600', desc: '营销活动策划模板' }
];

export function DashboardTemplates() {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5, duration: 0.1 }}
      className="h-full"
    >
      <div className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 border border-gray-100 overflow-hidden h-full">
        {/* 标题 */}
        <div className="px-6 py-5 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-100 to-pink-100 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-rose-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">热门模板</h3>
                <p className="text-sm text-gray-500">快速开始</p>
              </div>
            </div>
            <Link
              href="/templates"
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1 transition-colors"
            >
              全部
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* 模板列表 */}
        <div className="p-4 space-y-3">
          {templates.map((template, index) => {
            const Icon = template.icon;
            return (
              <motion.div
                key={template.title}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.05, duration: 0.1 }}
                whileHover={{ x: 4 }}
                className="group"
              >
                <Link
                  href="/outlines/new"
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${template.color} flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-100`}>
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900 text-sm group-hover:text-blue-600 transition-colors">
                      {template.title}
                    </h4>
                    <p className="text-xs text-gray-500 truncate">{template.desc}</p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-blue-600 transition-colors" />
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.section>
  );
}
