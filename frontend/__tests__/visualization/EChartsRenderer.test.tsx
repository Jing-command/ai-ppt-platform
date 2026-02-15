/**
 * EChartsRenderer 组件测试
 * 测试 ECharts 图表渲染组件的渲染、事件处理和响应式功能
 *
 * 测试范围：
 * - 图表渲染
 * - 配置传递
 * - 事件处理
 * - 加载状态
 * - 响应式调整
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import EChartsRenderer from '@/components/visualization/ChartPreview/EChartsRenderer';
import type { EChartsOption } from 'echarts';

// Mock echarts-for-react
vi.mock('echarts-for-react', () => ({
  default: vi.fn((props: object) => (
    <div
      data-testid="echarts-mock"
      data-option={JSON.stringify((props as { option?: object }).option)}
      data-loading={(props as { showLoading?: boolean }).showLoading}
    />
  )),
}));

describe('EChartsRenderer 组件测试', () => {
  // 基础测试配置
  const basicOption: EChartsOption = {
    xAxis: { type: 'category', data: ['A', 'B', 'C'] },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: [100, 200, 150] }],
  };

  // 模拟回调函数
  const mockOnChartReady = vi.fn();
  const mockOnChartClick = vi.fn();

  beforeEach(() => {
    // 重置 mock 函数
    mockOnChartReady.mockClear();
    mockOnChartClick.mockClear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    // 清理
    vi.restoreAllMocks();
  });

  describe('UI-014: 组件渲染测试', () => {
    it('应该正确渲染图表容器', () => {
      // 渲染组件
      render(<EChartsRenderer option={basicOption} />);

      // 验证图表容器存在
      const chartContainer = screen.getByTestId('echarts-mock');
      expect(chartContainer).toBeInTheDocument();
    });

    it('应该正确传递配置项', () => {
      // 渲染组件
      render(<EChartsRenderer option={basicOption} />);

      // 获取图表组件
      const chartComponent = screen.getByTestId('echarts-mock');

      // 验证配置项被传递
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption).toHaveProperty('xAxis');
      expect(passedOption).toHaveProperty('yAxis');
      expect(passedOption).toHaveProperty('series');
    });

    it('应该应用自定义类名', () => {
      // 渲染组件
      render(<EChartsRenderer option={basicOption} className="custom-chart" />);

      // 验证类名被应用
      const container = screen.getByTestId('echarts-mock').parentElement;
      expect(container).toHaveClass('custom-chart');
    });
  });

  describe('UI-015: 配置传递测试', () => {
    it('应该正确传递柱状图配置', () => {
      // 构造柱状图配置
      const barOption: EChartsOption = {
        title: { text: '柱状图测试' },
        xAxis: { type: 'category', data: ['A', 'B', 'C'] },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: [100, 200, 150] }],
      };

      // 渲染组件
      render(<EChartsRenderer option={barOption} />);

      // 验证配置被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption.title.text).toBe('柱状图测试');
      expect(passedOption.series[0].type).toBe('bar');
    });

    it('应该正确传递折线图配置', () => {
      // 构造折线图配置
      const lineOption: EChartsOption = {
        xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed'] },
        yAxis: { type: 'value' },
        series: [{ type: 'line', data: [120, 200, 150] }],
      };

      // 渲染组件
      render(<EChartsRenderer option={lineOption} />);

      // 验证配置被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption.series[0].type).toBe('line');
    });

    it('应该正确传递饼图配置', () => {
      // 构造饼图配置
      const pieOption: EChartsOption = {
        series: [
          {
            type: 'pie',
            data: [
              { value: 1048, name: 'Search Engine' },
              { value: 735, name: 'Direct' },
            ],
          },
        ],
      };

      // 渲染组件
      render(<EChartsRenderer option={pieOption} />);

      // 验证配置被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption.series[0].type).toBe('pie');
    });

    it('应该正确传递主题配置', () => {
      // 渲染组件带主题
      render(<EChartsRenderer option={basicOption} theme="dark" />);

      // 验证组件被渲染
      const chartComponent = screen.getByTestId('echarts-mock');
      expect(chartComponent).toBeInTheDocument();
    });
  });

  describe('UI-016: 加载状态测试', () => {
    it('loading=true 应该显示加载状态', () => {
      // 渲染组件带加载状态
      render(<EChartsRenderer option={basicOption} loading={true} />);

      // 验证加载状态被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      expect(chartComponent.getAttribute('data-loading')).toBe('true');
    });

    it('loading=false 应该不显示加载状态', () => {
      // 渲染组件不带加载状态
      render(<EChartsRenderer option={basicOption} loading={false} />);

      // 验证加载状态被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      expect(chartComponent.getAttribute('data-loading')).toBe('false');
    });

    it('应该接受自定义加载配置', () => {
      // 自定义加载配置
      const customLoadingOption = {
        text: '正在加载图表...',
        color: '#ff0000',
      };

      // 渲染组件
      render(
        <EChartsRenderer
          option={basicOption}
          loading={true}
          loadingOption={customLoadingOption}
        />
      );

      // 验证组件被渲染
      const chartComponent = screen.getByTestId('echarts-mock');
      expect(chartComponent).toBeInTheDocument();
    });
  });

  describe('UI-017: 事件处理测试', () => {
    it('应该接受 onChartReady 回调', () => {
      // 渲染组件带就绪回调
      render(<EChartsRenderer option={basicOption} onChartReady={mockOnChartReady} />);

      // 验证组件被渲染
      const chartComponent = screen.getByTestId('echarts-mock');
      expect(chartComponent).toBeInTheDocument();
    });

    it('应该接受 onChartClick 回调', () => {
      // 渲染组件带点击回调
      render(<EChartsRenderer option={basicOption} onChartClick={mockOnChartClick} />);

      // 验证组件被渲染
      const chartComponent = screen.getByTestId('echarts-mock');
      expect(chartComponent).toBeInTheDocument();
    });
  });

  describe('UI-018: 样式测试', () => {
    it('应该应用默认样式', () => {
      // 渲染组件
      render(<EChartsRenderer option={basicOption} />);

      // 验证容器存在
      const container = screen.getByTestId('echarts-mock').parentElement;
      expect(container).toBeInTheDocument();
    });

    it('应该接受自定义样式', () => {
      // 自定义样式
      const customStyle = {
        width: '500px',
        height: '400px',
        border: '1px solid #ccc',
      };

      // 渲染组件
      render(<EChartsRenderer option={basicOption} style={customStyle} />);

      // 验证容器存在
      const container = screen.getByTestId('echarts-mock').parentElement;
      expect(container).toBeInTheDocument();
    });
  });

  describe('UI-019: 复杂配置测试', () => {
    it('应该正确处理包含多个系列的配置', () => {
      // 构造多系列配置
      const multiSeriesOption: EChartsOption = {
        xAxis: { type: 'category', data: ['A', 'B', 'C'] },
        yAxis: { type: 'value' },
        series: [
          { type: 'bar', data: [100, 200, 150] },
          { type: 'line', data: [120, 180, 160] },
        ],
      };

      // 渲染组件
      render(<EChartsRenderer option={multiSeriesOption} />);

      // 验证配置被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption.series).toHaveLength(2);
    });

    it('应该正确处理包含图例的配置', () => {
      // 构造带图例的配置
      const legendOption: EChartsOption = {
        title: { text: '测试图表' },
        legend: { data: ['系列A', '系列B'] },
        xAxis: { type: 'category', data: ['A', 'B', 'C'] },
        yAxis: { type: 'value' },
        series: [
          { name: '系列A', type: 'bar', data: [100, 200, 150] },
          { name: '系列B', type: 'bar', data: [120, 180, 160] },
        ],
      };

      // 渲染组件
      render(<EChartsRenderer option={legendOption} />);

      // 验证配置被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption).toHaveProperty('legend');
    });

    it('应该正确处理包含工具提示的配置', () => {
      // 构造带工具提示的配置
      const tooltipOption: EChartsOption = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}',
        },
        xAxis: { type: 'category', data: ['A', 'B', 'C'] },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: [100, 200, 150] }],
      };

      // 渲染组件
      render(<EChartsRenderer option={tooltipOption} />);

      // 验证配置被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption).toHaveProperty('tooltip');
    });

    it('应该正确处理包含数据缩放的配置', () => {
      // 构造带数据缩放的配置
      const dataZoomOption: EChartsOption = {
        xAxis: { type: 'category', data: Array.from({ length: 100 }, (_, i) => `Item ${i}`) },
        yAxis: { type: 'value' },
        series: [{ type: 'line', data: Array.from({ length: 100 }, () => Math.random() * 100) }],
        dataZoom: [
          { type: 'slider', start: 0, end: 50 },
          { type: 'inside', start: 0, end: 50 },
        ],
      };

      // 渲染组件
      render(<EChartsRenderer option={dataZoomOption} />);

      // 验证配置被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption).toHaveProperty('dataZoom');
    });
  });

  describe('UI-020: 边界情况测试', () => {
    it('应该处理空配置', () => {
      // 渲染组件带空配置
      render(<EChartsRenderer option={{}} />);

      // 验证组件被渲染
      const chartComponent = screen.getByTestId('echarts-mock');
      expect(chartComponent).toBeInTheDocument();
    });

    it('应该处理仅包含 series 的配置', () => {
      // 构造最小配置
      const minimalOption: EChartsOption = {
        series: [{ type: 'pie', data: [{ value: 100, name: 'A' }] }],
      };

      // 渲染组件
      render(<EChartsRenderer option={minimalOption} />);

      // 验证组件被渲染
      const chartComponent = screen.getByTestId('echarts-mock');
      expect(chartComponent).toBeInTheDocument();
    });

    it('应该处理包含嵌套对象的配置', () => {
      // 构造嵌套配置
      const nestedOption: EChartsOption = {
        title: {
          text: '主标题',
          subtext: '副标题',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold',
          },
        },
        xAxis: { type: 'category', data: ['A', 'B', 'C'] },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: [100, 200, 150] }],
      };

      // 渲染组件
      render(<EChartsRenderer option={nestedOption} />);

      // 验证配置被传递
      const chartComponent = screen.getByTestId('echarts-mock');
      const passedOption = JSON.parse(chartComponent.getAttribute('data-option') || '{}');
      expect(passedOption.title.text).toBe('主标题');
      expect(passedOption.title.textStyle.fontSize).toBe(18);
    });
  });
});
