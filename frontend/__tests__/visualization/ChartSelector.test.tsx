/**
 * ChartSelector 组件测试
 * 测试图表选择器的分类筛选、搜索功能和图表卡片展示
 *
 * 测试范围：
 * - 分类标签切换
 * - 搜索功能
 * - 图表卡片点击选择
 * - 空状态展示
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChartSelector from '@/components/visualization/ChartSelector/index';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<object>) => (
      <div {...props}>{children}</div>
    ),
    button: ({ children, ...props }: React.PropsWithChildren<object>) => (
      <button {...props}>{children}</button>
    ),
  },
  AnimatePresence: ({ children }: React.PropsWithChildren<object>) => (
    <>{children}</>
  ),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Search: () => <span data-testid="search-icon">Search</span>,
  X: () => <span data-testid="x-icon">X</span>,
  Check: () => <span data-testid="check-icon">Check</span>,
  BarChart3: () => <span data-testid="bar-chart-3-icon">BarChart3</span>,
  TrendingUp: () => <span data-testid="trending-up-icon">TrendingUp</span>,
  PieChart: () => <span data-testid="pie-chart-icon">PieChart</span>,
  ScatterChart: () => <span data-testid="scatter-chart-icon">ScatterChart</span>,
  AreaChart: () => <span data-testid="area-chart-icon">AreaChart</span>,
  Radar: () => <span data-testid="radar-icon">Radar</span>,
  Gauge: () => <span data-testid="gauge-icon">Gauge</span>,
  BarChart2: () => <span data-testid="bar-chart-2-icon">BarChart2</span>,
  BoxSelect: () => <span data-testid="box-select-icon">BoxSelect</span>,
  Grid3x3: () => <span data-testid="grid-3x3-icon">Grid3x3</span>,
  Square: () => <span data-testid="square-icon">Square</span>,
  Sun: () => <span data-testid="sun-icon">Sun</span>,
  Filter: () => <span data-testid="filter-icon">Filter</span>,
  GitMerge: () => <span data-testid="git-merge-icon">GitMerge</span>,
  Share2: () => <span data-testid="share-2-icon">Share2</span>,
  GitBranch: () => <span data-testid="git-branch-icon">GitBranch</span>,
  AlignJustify: () => <span data-testid="align-justify-icon">AlignJustify</span>,
  Map: () => <span data-testid="map-icon">Map</span>,
  Globe: () => <span data-testid="globe-icon">Globe</span>,
  MapPin: () => <span data-testid="map-pin-icon">MapPin</span>,
  Target: () => <span data-testid="target-icon">Target</span>,
  CandlestickChart: () => <span data-testid="candlestick-chart-icon">CandlestickChart</span>,
  Sparkles: () => <span data-testid="sparkles-icon">Sparkles</span>,
  Route: () => <span data-testid="route-icon">Route</span>,
  Waves: () => <span data-testid="waves-icon">Waves</span>,
  Puzzle: () => <span data-testid="puzzle-icon">Puzzle</span>,
}));

describe('ChartSelector 组件测试', () => {
  // 模拟选择回调函数
  const mockOnSelect = vi.fn();

  beforeEach(() => {
    // 重置 mock 函数
    mockOnSelect.mockClear();
  });

  describe('UI-001: 组件渲染测试', () => {
    it('应该正确渲染分类标签', () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 验证分类标签存在
      expect(screen.getByText('基础图表')).toBeInTheDocument();
      expect(screen.getByText('统计图表')).toBeInTheDocument();
      expect(screen.getByText('关系图')).toBeInTheDocument();
      expect(screen.getByText('地图')).toBeInTheDocument();
      expect(screen.getByText('特殊图表')).toBeInTheDocument();
    });

    it('应该正确渲染搜索框', () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 验证搜索框存在
      const searchInput = screen.getByPlaceholderText('搜索图表...');
      expect(searchInput).toBeInTheDocument();
    });

    it('应该默认显示基础图表分类', () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 验证基础图表存在
      expect(screen.getByText('柱状图')).toBeInTheDocument();
      expect(screen.getByText('折线图')).toBeInTheDocument();
      expect(screen.getByText('饼图')).toBeInTheDocument();
    });
  });

  describe('UI-002: 分类切换测试', () => {
    it('点击统计图表标签应该切换到统计图表分类', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 点击统计图表标签
      const statisticalTab = screen.getByText('统计图表');
      fireEvent.click(statisticalTab);

      // 验证统计图表内容显示
      await waitFor(() => {
        expect(screen.getByText('直方图')).toBeInTheDocument();
        expect(screen.getByText('箱线图')).toBeInTheDocument();
        expect(screen.getByText('热力图')).toBeInTheDocument();
      });
    });

    it('点击地图图表标签应该切换到地图图表分类', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 点击地图图表标签
      const mapTab = screen.getByText('地图');
      fireEvent.click(mapTab);

      // 验证地图图表内容显示
      await waitFor(() => {
        expect(screen.getByText('中国地图')).toBeInTheDocument();
        expect(screen.getByText('世界地图')).toBeInTheDocument();
      });
    });

    it('点击关系图表标签应该切换到关系图表分类', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 点击关系图表标签
      const relationTab = screen.getByText('关系图');
      fireEvent.click(relationTab);

      // 验证关系图表内容显示
      await waitFor(() => {
        expect(screen.getByText('树图')).toBeInTheDocument();
      });
    });

    it('点击特殊图表标签应该切换到特殊图表分类', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 点击特殊图表标签
      const specialTab = screen.getByText('特殊图表');
      fireEvent.click(specialTab);

      // 验证特殊图表内容显示
      await waitFor(() => {
        expect(screen.getByText('极坐标图')).toBeInTheDocument();
        expect(screen.getByText('K线图')).toBeInTheDocument();
      });
    });
  });

  describe('UI-003: 搜索功能测试', () => {
    it('输入搜索关键词应该过滤图表列表', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 获取搜索输入框
      const searchInput = screen.getByPlaceholderText('搜索图表...');

      // 输入搜索关键词
      await userEvent.type(searchInput, '柱状');

      // 验证过滤结果
      await waitFor(() => {
        expect(screen.getByText('柱状图')).toBeInTheDocument();
        // 折线图不应该显示
        expect(screen.queryByText('折线图')).not.toBeInTheDocument();
      });
    });

    it('输入不匹配的关键词应该显示空状态', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 获取搜索输入框
      const searchInput = screen.getByPlaceholderText('搜索图表...');

      // 输入不匹配的关键词
      await userEvent.type(searchInput, '不存在的图表类型');

      // 验证空状态显示
      await waitFor(() => {
        expect(screen.getByText('未找到匹配的图表')).toBeInTheDocument();
      });
    });

    it('点击清空按钮应该清空搜索关键词', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 获取搜索输入框
      const searchInput = screen.getByPlaceholderText('搜索图表...');

      // 输入搜索关键词
      await userEvent.type(searchInput, '柱状');

      // 验证清空按钮出现
      await waitFor(() => {
        expect(screen.getByTestId('x-icon')).toBeInTheDocument();
      });

      // 点击清空按钮
      const clearButton = screen.getByTestId('x-icon').closest('button');
      if (clearButton) {
        fireEvent.click(clearButton);
      }

      // 验证搜索框被清空
      await waitFor(() => {
        expect(searchInput).toHaveValue('');
      });
    });

    it('搜索应该匹配图表描述', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 获取搜索输入框
      const searchInput = screen.getByPlaceholderText('搜索图表...');

      // 输入描述中的关键词
      await userEvent.type(searchInput, '趋势');

      // 验证匹配结果
      await waitFor(() => {
        expect(screen.getByText('折线图')).toBeInTheDocument();
      });
    });
  });

  describe('UI-004: 图表选择测试', () => {
    it('点击图表卡片应该触发 onSelect 回调', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 点击柱状图卡片
      const barChartCard = screen.getByText('柱状图').closest('div');
      if (barChartCard) {
        fireEvent.click(barChartCard);
      }

      // 验证回调被触发
      expect(mockOnSelect).toHaveBeenCalledWith('bar');
    });

    it('点击折线图卡片应该触发正确的图表类型', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 点击折线图卡片
      const lineChartCard = screen.getByText('折线图').closest('div');
      if (lineChartCard) {
        fireEvent.click(lineChartCard);
      }

      // 验证回调被触发
      expect(mockOnSelect).toHaveBeenCalledWith('line');
    });

    it('点击饼图卡片应该触发正确的图表类型', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 点击饼图卡片
      const pieChartCard = screen.getByText('饼图').closest('div');
      if (pieChartCard) {
        fireEvent.click(pieChartCard);
      }

      // 验证回调被触发
      expect(mockOnSelect).toHaveBeenCalledWith('pie');
    });
  });

  describe('UI-005: 选中状态测试', () => {
    it('传入 selectedType 应该高亮对应的图表卡片', () => {
      // 渲染组件，选中柱状图
      render(<ChartSelector onSelect={mockOnSelect} selectedType="bar" />);

      // 验证柱状图卡片有选中样式 - 使用 border-blue-500 而不是 ring-2
      const barChartCard = screen.getByText('柱状图').closest('div');
      expect(barChartCard).toHaveClass('border-blue-500');
    });

    it('切换选中类型应该更新高亮状态', () => {
      // 渲染组件，选中柱状图
      const { rerender } = render(
        <ChartSelector onSelect={mockOnSelect} selectedType="bar" />
      );

      // 验证柱状图选中
      let barChartCard = screen.getByText('柱状图').closest('div');
      expect(barChartCard).toHaveClass('border-blue-500');

      // 重新渲染，选中折线图
      rerender(<ChartSelector onSelect={mockOnSelect} selectedType="line" />);

      // 验证折线图选中
      const lineChartCard = screen.getByText('折线图').closest('div');
      expect(lineChartCard).toHaveClass('border-blue-500');
    });
  });

  describe('UI-006: 边界情况测试', () => {
    it('快速切换分类应该正常工作', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 快速点击多个分类标签
      const statisticalTab = screen.getByText('统计图表');
      const mapTab = screen.getByText('地图');
      const basicTab = screen.getByText('基础图表');

      fireEvent.click(statisticalTab);
      fireEvent.click(mapTab);
      fireEvent.click(basicTab);

      // 验证最终显示基础图表
      await waitFor(() => {
        expect(screen.getByText('柱状图')).toBeInTheDocument();
      });
    });

    it('搜索后再切换分类应该清空搜索', async () => {
      // 渲染组件
      render(<ChartSelector onSelect={mockOnSelect} />);

      // 输入搜索关键词
      const searchInput = screen.getByPlaceholderText('搜索图表...');
      await userEvent.type(searchInput, '柱状');

      // 切换到统计图表分类
      const statisticalTab = screen.getByText('统计图表');
      fireEvent.click(statisticalTab);

      // 验证搜索框被清空
      // 注意：组件实现会清空搜索并显示统计图表
      await waitFor(() => {
        expect(searchInput).toHaveValue('');
      });
    });
  });
});
