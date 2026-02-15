/**
 * Vitest 测试配置
 * 用于前端组件单元测试
 */

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  // 插件配置
  plugins: [react()],

  // 测试配置
  test: {
    // 测试环境
    environment: 'jsdom',

    // 全局变量
    globals: true,

    // 设置文件
    setupFiles: ['./__tests__/setup.ts'],

    // 包含的测试文件
    include: ['__tests__/**/*.test.{ts,tsx}'],

    // 排除的文件
    exclude: ['node_modules', 'dist', '.next'],

    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['components/**/*.{ts,tsx}'],
      exclude: ['node_modules', '__tests__'],
    },

    // 超时时间
    testTimeout: 10000,
  },

  // 路径别名
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
});
