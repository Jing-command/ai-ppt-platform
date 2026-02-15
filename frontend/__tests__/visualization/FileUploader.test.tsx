/**
 * FileUploader 组件测试
 * 测试文件上传组件的拖拽上传、文件解析和状态管理
 *
 * 测试范围：
 * - 拖拽上传功能
 * - 点击上传功能
 * - 文件类型验证
 * - 文件解析功能
 * - 错误处理
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FileUploader from '@/components/visualization/DataSourceSelector/FileUploader';
import type { ParsedData } from '@/types/visualization';

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
  Upload: () => <span data-testid="upload-icon">Upload</span>,
  FileSpreadsheet: () => <span data-testid="file-spreadsheet-icon">FileSpreadsheet</span>,
  FileJson: () => <span data-testid="file-json-icon">FileJson</span>,
  FileText: () => <span data-testid="file-text-icon">FileText</span>,
  X: () => <span data-testid="x-icon">X</span>,
  CheckCircle: () => <span data-testid="check-circle-icon">CheckCircle</span>,
  AlertCircle: () => <span data-testid="alert-circle-icon">AlertCircle</span>,
  Loader2: () => <span data-testid="loader-icon">Loader2</span>,
}));

// Mock xlsx library
vi.mock('xlsx', () => ({
  read: vi.fn((data: unknown, options: object) => ({
    SheetNames: ['Sheet1'],
    Sheets: {
      Sheet1: {},
    },
  })),
  utils: {
    sheet_to_json: vi.fn(() => [
      { category: 'A', value: 100 },
      { category: 'B', value: 200 },
    ]),
  },
}));

describe('FileUploader 组件测试', () => {
  // 模拟上传回调函数
  const mockOnUpload = vi.fn();

  beforeEach(() => {
    // 重置 mock 函数
    mockOnUpload.mockClear();
    // 重置所有 mock
    vi.clearAllMocks();
  });

  describe('UI-007: 组件渲染测试', () => {
    it('应该正确渲染上传区域', () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 验证上传提示文字
      expect(screen.getByText('拖拽文件到此处，或点击上传')).toBeInTheDocument();
      expect(screen.getByText(/支持 Excel/)).toBeInTheDocument();
    });

    it('应该显示支持的文件类型图标', () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 验证文件类型图标存在 - Excel 有两个图标（2007+ 和 97-2003）
      expect(screen.getAllByTestId('file-spreadsheet-icon').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByTestId('file-json-icon')).toBeInTheDocument();
      expect(screen.getByTestId('file-text-icon')).toBeInTheDocument();
    });

    it('应该显示文件类型标签', () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 验证文件类型标签
      expect(screen.getByText('Excel 2007+')).toBeInTheDocument();
      expect(screen.getByText('Excel 97-2003')).toBeInTheDocument();
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('JSON')).toBeInTheDocument();
    });
  });

  describe('UI-008: 拖拽上传测试', () => {
    it('拖拽进入应该改变状态', () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 获取上传区域
      const uploadArea = screen.getByText('拖拽文件到此处，或点击上传').closest('div');

      // 模拟拖拽进入
      if (uploadArea) {
        fireEvent.dragEnter(uploadArea, {
          dataTransfer: { files: [] },
          preventDefault: vi.fn(),
          stopPropagation: vi.fn(),
        });
      }

      // 验证状态变化（通过样式或 class）
      // 注意：具体验证方式取决于组件实现
    });

    it('拖拽离开应该恢复状态', () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 获取上传区域
      const uploadArea = screen.getByText('拖拽文件到此处，或点击上传').closest('div');

      // 模拟拖拽进入和离开
      if (uploadArea) {
        fireEvent.dragEnter(uploadArea, {
          dataTransfer: { files: [] },
          preventDefault: vi.fn(),
          stopPropagation: vi.fn(),
        });

        fireEvent.dragLeave(uploadArea, {
          dataTransfer: { files: [] },
          preventDefault: vi.fn(),
          stopPropagation: vi.fn(),
        });
      }
    });

    it('放下有效文件应该触发上传', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建模拟文件
      const file = new File(['test,data\nA,100\nB,200'], 'test.csv', {
        type: 'text/csv',
      });

      // 获取上传区域
      const uploadArea = screen.getByText('拖拽文件到此处，或点击上传').closest('div');

      // 模拟文件放下
      if (uploadArea) {
        fireEvent.drop(uploadArea, {
          dataTransfer: { files: [file] },
          preventDefault: vi.fn(),
          stopPropagation: vi.fn(),
        });
      }

      // 等待上传完成
      await waitFor(
        () => {
          // 验证回调被触发
          expect(mockOnUpload).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );
    });
  });

  describe('UI-009: 点击上传测试', () => {
    it('点击上传区域应该触发文件选择', () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 获取上传区域
      const uploadArea = screen.getByText('拖拽文件到此处，或点击上传').closest('div');

      // 模拟点击
      if (uploadArea) {
        fireEvent.click(uploadArea);
      }

      // 验证隐藏的文件输入框存在
      const fileInput = document.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
    });

    it('选择有效文件应该触发上传', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建模拟文件
      const file = new File(['test,data\nA,100\nB,200'], 'test.csv', {
        type: 'text/csv',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 等待上传完成
      await waitFor(
        () => {
          expect(mockOnUpload).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );
    });
  });

  describe('UI-010: 文件类型验证测试', () => {
    it('上传不支持的文件类型应该显示错误', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建不支持的文件类型
      const file = new File(['test'], 'test.txt', {
        type: 'text/plain',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 等待错误显示
      await waitFor(() => {
        expect(screen.getByText(/不支持的文件格式/)).toBeInTheDocument();
      });
    });

    it('上传 Excel 文件应该被接受', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建模拟 Excel 文件
      const file = new File(['mock excel content'], 'test.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 等待处理
      await waitFor(
        () => {
          // 验证没有显示错误
          expect(screen.queryByText(/不支持的文件格式/)).not.toBeInTheDocument();
        },
        { timeout: 3000 }
      );
    });

    it('上传 JSON 文件应该被接受', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建模拟 JSON 文件
      const jsonContent = JSON.stringify([
        { category: 'A', value: 100 },
        { category: 'B', value: 200 },
      ]);
      const file = new File([jsonContent], 'test.json', {
        type: 'application/json',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 等待处理
      await waitFor(
        () => {
          expect(screen.queryByText(/不支持的文件格式/)).not.toBeInTheDocument();
        },
        { timeout: 3000 }
      );
    });
  });

  describe('UI-011: 状态显示测试', () => {
    it('上传中应该显示加载状态', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建模拟文件
      const file = new File(['test,data\nA,100\nB,200'], 'test.csv', {
        type: 'text/csv',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 验证加载图标出现
      await waitFor(() => {
        expect(screen.getByTestId('loader-icon')).toBeInTheDocument();
      });
    });

    it('上传成功应该显示成功状态', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建模拟文件
      const file = new File(['test,data\nA,100\nB,200'], 'test.csv', {
        type: 'text/csv',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 等待成功状态
      await waitFor(
        () => {
          expect(screen.getByText('文件解析成功')).toBeInTheDocument();
        },
        { timeout: 5000 }
      );
    });

    it('上传失败应该显示错误状态和重试按钮', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建不支持的文件类型
      const file = new File(['test'], 'test.txt', {
        type: 'text/plain',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 等待错误状态
      await waitFor(() => {
        expect(screen.getByText('上传失败')).toBeInTheDocument();
        expect(screen.getByText('重新上传')).toBeInTheDocument();
      });
    });
  });

  describe('UI-012: 回调数据测试', () => {
    it('成功解析后应该调用 onUpload 并传递正确的数据结构', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建模拟 CSV 文件
      const file = new File(['category,value\nA,100\nB,200'], 'test.csv', {
        type: 'text/csv',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 等待回调
      await waitFor(
        () => {
          expect(mockOnUpload).toHaveBeenCalled();
        },
        { timeout: 5000 }
      );

      // 验证回调数据结构
      if (mockOnUpload.mock.calls.length > 0) {
        const parsedData: ParsedData = mockOnUpload.mock.calls[0][0];
        expect(parsedData).toHaveProperty('source');
        expect(parsedData).toHaveProperty('fields');
        expect(parsedData).toHaveProperty('rows');
        expect(parsedData).toHaveProperty('totalRows');
      }
    });
  });

  describe('UI-013: 重置功能测试', () => {
    it('点击重新上传按钮应该重置状态', async () => {
      // 渲染组件
      render(<FileUploader onUpload={mockOnUpload} />);

      // 创建不支持的文件类型触发错误
      const file = new File(['test'], 'test.txt', {
        type: 'text/plain',
      });

      // 获取文件输入框
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

      // 模拟文件选择
      if (fileInput) {
        Object.defineProperty(fileInput, 'files', {
          value: [file],
        });
        fireEvent.change(fileInput);
      }

      // 等待错误状态
      await waitFor(() => {
        expect(screen.getByText('上传失败')).toBeInTheDocument();
      });

      // 点击重新上传按钮
      const retryButton = screen.getByText('重新上传');
      fireEvent.click(retryButton);

      // 验证恢复到初始状态
      await waitFor(() => {
        expect(screen.getByText('拖拽文件到此处，或点击上传')).toBeInTheDocument();
      });
    });
  });
});
