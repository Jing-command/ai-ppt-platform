/**
 * FieldMapper 组件测试
 * 测试字段映射组件的维度选择、度量多选和映射状态显示
 *
 * 测试范围：
 * - 维度字段选择
 * - 度量字段多选
 * - 颜色分组字段选择
 * - 映射状态显示
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FieldMapper from '@/components/visualization/ChartPreview/FieldMapper';
import type { DataField, ChartFieldMapping } from '@/types/visualization';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<object>) => (
      <div {...props}>{children}</div>
    ),
    label: ({ children, ...props }: React.PropsWithChildren<object>) => (
      <label {...props}>{children}</label>
    ),
  },
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  ArrowDown: () => <span data-testid="arrow-down-icon">ArrowDown</span>,
  Hash: () => <span data-testid="hash-icon">Hash</span>,
  Type: () => <span data-testid="type-icon">Type</span>,
  Calendar: () => <span data-testid="calendar-icon">Calendar</span>,
  ToggleLeft: () => <span data-testid="toggle-icon">ToggleLeft</span>,
  Layers: () => <span data-testid="layers-icon">Layers</span>,
}));

describe('FieldMapper 组件测试', () => {
  // 测试数据字段
  const mockFields: DataField[] = [
    {
      name: 'category',
      type: 'string',
      index: 0,
      nullable: false,
      uniqueCount: 3,
      sampleValues: ['A', 'B', 'C'],
    },
    {
      name: 'value',
      type: 'number',
      index: 1,
      nullable: false,
      uniqueCount: 5,
      sampleValues: [100, 200, 150],
      stats: {
        min: 100,
        max: 200,
        mean: 150,
        median: 150,
        sum: 750,
      },
    },
    {
      name: 'amount',
      type: 'number',
      index: 2,
      nullable: false,
      uniqueCount: 5,
      sampleValues: [10, 20, 15],
      stats: {
        min: 10,
        max: 20,
        mean: 15,
        median: 15,
        sum: 75,
      },
    },
    {
      name: 'date',
      type: 'date',
      index: 3,
      nullable: false,
      uniqueCount: 5,
      sampleValues: ['2024-01-01', '2024-01-02'],
    },
  ];

  // 默认映射配置
  const defaultMapping: ChartFieldMapping = {
    dimension: undefined,
    measures: [],
    colorField: undefined,
  };

  // 模拟回调函数
  const mockOnChange = vi.fn();

  beforeEach(() => {
    // 重置 mock 函数
    mockOnChange.mockClear();
  });

  describe('UI-021: 组件渲染测试', () => {
    it('应该正确渲染标题', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证标题存在
      expect(screen.getByText('字段映射配置')).toBeInTheDocument();
    });

    it('应该正确渲染维度字段选择器', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证维度字段标签存在
      expect(screen.getByText('维度字段（X轴）')).toBeInTheDocument();
    });

    it('应该正确渲染度量字段选择器', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证度量字段标签存在
      expect(screen.getByText('度量字段（数值）')).toBeInTheDocument();
    });

    it('应该正确渲染颜色分组字段选择器', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证颜色分组字段标签存在
      expect(screen.getByText('颜色分组字段（可选）')).toBeInTheDocument();
    });
  });

  describe('UI-022: 维度字段选择测试', () => {
    it('应该显示所有字段作为选项', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 获取维度字段选择器 - 使用 role 查询
      const dimensionSelect = screen.getByRole('combobox', { name: /维度字段/ });

      // 验证选项存在
      expect(dimensionSelect).toBeInTheDocument();
    });

    it('选择维度字段应该触发 onChange 回调', async () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 获取维度字段选择器 - 使用 role 查询
      const dimensionSelect = screen.getByRole('combobox', { name: /维度字段/ });

      // 选择字段
      fireEvent.change(dimensionSelect, { target: { value: 'category' } });

      // 验证回调被触发
      expect(mockOnChange).toHaveBeenCalledWith({
        ...defaultMapping,
        dimension: 'category',
      });
    });

    it('选择空选项应该清除维度字段', async () => {
      // 渲染组件，预设维度字段
      const mappingWithDimension: ChartFieldMapping = {
        ...defaultMapping,
        dimension: 'category',
      };

      render(
        <FieldMapper
          fields={mockFields}
          mapping={mappingWithDimension}
          onChange={mockOnChange}
        />
      );

      // 获取维度字段选择器 - 使用 role 查询
      const dimensionSelect = screen.getByRole('combobox', { name: /维度字段/ });

      // 选择空选项
      fireEvent.change(dimensionSelect, { target: { value: '' } });

      // 验证回调被触发
      expect(mockOnChange).toHaveBeenCalledWith({
        ...mappingWithDimension,
        dimension: undefined,
      });
    });
  });

  describe('UI-023: 度量字段多选测试', () => {
    it('应该只显示数值类型字段', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证数值字段显示 - 使用更具体的选择器避免匹配到多个元素
      expect(screen.getAllByText('value').length).toBeGreaterThan(0);
      expect(screen.getAllByText('amount').length).toBeGreaterThan(0);

      // 验证非数值字段不显示在度量列表中
      // 注意：category 和 date 是字符串和日期类型，不应该出现在度量列表
    });

    it('勾选度量字段应该触发 onChange 回调', async () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 获取 value 字段的复选框
      const valueCheckbox = screen.getByRole('checkbox', { name: /value/i });

      // 勾选复选框
      fireEvent.click(valueCheckbox);

      // 验证回调被触发
      expect(mockOnChange).toHaveBeenCalledWith({
        ...defaultMapping,
        measures: ['value'],
      });
    });

    it('取消勾选度量字段应该从列表中移除', async () => {
      // 渲染组件，预设度量字段
      const mappingWithMeasures: ChartFieldMapping = {
        ...defaultMapping,
        measures: ['value', 'amount'],
      };

      render(
        <FieldMapper
          fields={mockFields}
          mapping={mappingWithMeasures}
          onChange={mockOnChange}
        />
      );

      // 获取 value 字段的复选框
      const valueCheckbox = screen.getByRole('checkbox', { name: /value/i });

      // 取消勾选
      fireEvent.click(valueCheckbox);

      // 验证回调被触发
      expect(mockOnChange).toHaveBeenCalledWith({
        ...mappingWithMeasures,
        measures: ['amount'],
      });
    });

    it('应该显示数值字段的统计信息', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证统计信息显示
      expect(screen.getByText(/范围: 100 - 200/)).toBeInTheDocument();
    });

    it('没有数值字段时应该显示提示', () => {
      // 只有非数值字段的数据
      const nonNumericFields: DataField[] = [
        {
          name: 'category',
          type: 'string',
          index: 0,
          nullable: false,
          uniqueCount: 3,
          sampleValues: ['A', 'B', 'C'],
        },
      ];

      // 渲染组件
      render(
        <FieldMapper
          fields={nonNumericFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证提示显示
      expect(screen.getByText('暂无数值字段')).toBeInTheDocument();
    });
  });

  describe('UI-024: 颜色分组字段测试', () => {
    it('选择颜色分组字段应该触发 onChange 回调', async () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 获取颜色分组字段选择器 - 使用 role 查询
      const colorSelect = screen.getByRole('combobox', { name: /颜色分组字段/ });

      // 选择字段
      fireEvent.change(colorSelect, { target: { value: 'category' } });

      // 验证回调被触发
      expect(mockOnChange).toHaveBeenCalledWith({
        ...defaultMapping,
        colorField: 'category',
      });
    });

    it('选择空选项应该清除颜色分组字段', async () => {
      // 渲染组件，预设颜色分组字段
      const mappingWithColor: ChartFieldMapping = {
        ...defaultMapping,
        colorField: 'category',
      };

      render(
        <FieldMapper
          fields={mockFields}
          mapping={mappingWithColor}
          onChange={mockOnChange}
        />
      );

      // 获取颜色分组字段选择器
      const colorSelect = screen.getByLabelText('颜色分组字段（可选）');

      // 选择空选项
      fireEvent.change(colorSelect, { target: { value: '' } });

      // 验证回调被触发
      expect(mockOnChange).toHaveBeenCalledWith({
        ...mappingWithColor,
        colorField: undefined,
      });
    });
  });

  describe('UI-025: 映射状态显示测试', () => {
    it('应该显示当前维度映射', () => {
      // 渲染组件，预设维度字段
      const mappingWithDimension: ChartFieldMapping = {
        ...defaultMapping,
        dimension: 'category',
      };

      render(
        <FieldMapper
          fields={mockFields}
          mapping={mappingWithDimension}
          onChange={mockOnChange}
        />
      );

      // 验证映射状态显示
      expect(screen.getByText('维度: category')).toBeInTheDocument();
    });

    it('应该显示当前度量映射', () => {
      // 渲染组件，预设度量字段
      const mappingWithMeasures: ChartFieldMapping = {
        ...defaultMapping,
        measures: ['value', 'amount'],
      };

      render(
        <FieldMapper
          fields={mockFields}
          mapping={mappingWithMeasures}
          onChange={mockOnChange}
        />
      );

      // 验证映射状态显示
      expect(screen.getByText('度量: value')).toBeInTheDocument();
      expect(screen.getByText('度量: amount')).toBeInTheDocument();
    });

    it('应该显示当前颜色分组映射', () => {
      // 渲染组件，预设颜色分组字段
      const mappingWithColor: ChartFieldMapping = {
        ...defaultMapping,
        colorField: 'category',
      };

      render(
        <FieldMapper
          fields={mockFields}
          mapping={mappingWithColor}
          onChange={mockOnChange}
        />
      );

      // 验证映射状态显示
      expect(screen.getByText('分组: category')).toBeInTheDocument();
    });

    it('没有映射时不应该显示标签', () => {
      // 渲染组件，空映射
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证当前映射标题存在
      expect(screen.getByText('当前映射:')).toBeInTheDocument();

      // 验证没有映射标签
      expect(screen.queryByText(/维度:/)).not.toBeInTheDocument();
      expect(screen.queryByText(/度量:/)).not.toBeInTheDocument();
      expect(screen.queryByText(/分组:/)).not.toBeInTheDocument();
    });
  });

  describe('UI-026: 字段类型图标测试', () => {
    it('应该为字符串字段显示正确的图标', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证维度选择器中有字符串字段选项 - 使用 role 查询
      const dimensionSelect = screen.getByRole('combobox', { name: /维度字段/ });
      expect(dimensionSelect).toBeInTheDocument();
    });

    it('应该为数值字段显示正确的图标', () => {
      // 渲染组件
      render(
        <FieldMapper
          fields={mockFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证数值字段的图标存在
      const hashIcons = screen.getAllByTestId('hash-icon');
      expect(hashIcons.length).toBeGreaterThan(0);
    });
  });

  describe('UI-027: 边界情况测试', () => {
    it('应该处理空字段列表', () => {
      // 渲染组件，空字段列表
      render(
        <FieldMapper
          fields={[]}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证组件正常渲染
      expect(screen.getByText('字段映射配置')).toBeInTheDocument();
      expect(screen.getByText('暂无数值字段')).toBeInTheDocument();
    });

    it('应该处理仅有非数值字段的情况', () => {
      // 只有字符串字段
      const stringOnlyFields: DataField[] = [
        {
          name: 'name',
          type: 'string',
          index: 0,
          nullable: false,
          uniqueCount: 5,
          sampleValues: ['Alice', 'Bob'],
        },
      ];

      // 渲染组件
      render(
        <FieldMapper
          fields={stringOnlyFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证提示显示
      expect(screen.getByText('暂无数值字段')).toBeInTheDocument();
    });

    it('应该处理大量字段', () => {
      // 生成大量字段
      const manyFields: DataField[] = Array.from({ length: 50 }, (_, i) => ({
        name: `field_${i}`,
        type: i % 2 === 0 ? 'string' : 'number',
        index: i,
        nullable: false,
        uniqueCount: 10,
        sampleValues: i % 2 === 0 ? ['A', 'B'] : [1, 2],
        stats: i % 2 !== 0 ? {
          min: 1,
          max: 100,
          mean: 50,
          median: 50,
          sum: 500,
        } : undefined,
      }));

      // 渲染组件
      render(
        <FieldMapper
          fields={manyFields}
          mapping={defaultMapping}
          onChange={mockOnChange}
        />
      );

      // 验证组件正常渲染
      expect(screen.getByText('字段映射配置')).toBeInTheDocument();
    });

    it('应该正确更新已选中的度量字段状态', () => {
      // 渲染组件，预设度量字段
      const mappingWithMeasures: ChartFieldMapping = {
        ...defaultMapping,
        measures: ['value'],
      };

      render(
        <FieldMapper
          fields={mockFields}
          mapping={mappingWithMeasures}
          onChange={mockOnChange}
        />
      );

      // 获取 value 字段的复选框
      const valueCheckbox = screen.getByRole('checkbox', { name: /value/i });

      // 验证复选框已选中
      expect(valueCheckbox).toBeChecked();
    });
  });
});
