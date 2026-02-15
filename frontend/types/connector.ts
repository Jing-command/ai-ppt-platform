// 连接器类型定义
// 基于 API_CONTRACT.md

export type ConnectorType = 'mysql' | 'salesforce' | 'postgresql' | 'mongodb' | 'csv' | 'api';
export type ConnectorStatus = 'connected' | 'disconnected' | 'error';
export type TestStatus = 'success' | 'failed';

// MySQL 配置
export interface MySQLConfig {
  host: string;
  port: number;
  username: string;
  password: string;
  database: string;
}

// Salesforce 配置
export interface SalesforceConfig {
  username: string;
  password: string;
  securityToken: string;
  apiKey: string;
}

// 连接器基础接口
export interface ConnectorBase {
  name: string;
  type: ConnectorType;
  description?: string;
}

// 连接器创建请求
export interface CreateConnectorRequest extends ConnectorBase {
  config: MySQLConfig | SalesforceConfig | Record<string, any>;
}

// 连接器更新请求
export interface UpdateConnectorRequest {
  name?: string;
  description?: string;
  config?: Record<string, any>;
  isActive?: boolean;
}

// 连接器响应
export interface Connector {
  id: string;
  name: string;
  type: ConnectorType;
  description?: string;
  userId: string;
  config: Record<string, any>;
  isActive: boolean;
  lastTestedAt?: string;
  lastTestStatus?: TestStatus;
  createdAt: string;
  updatedAt: string;
}

// 连接器列表项（用于列表展示）
export interface ConnectorListItem {
  id: string;
  name: string;
  type: ConnectorType;
  status: ConnectorStatus;
  lastTestedAt?: string;
  createdAt: string;
}

// 测试连接请求
export interface TestConnectorRequest {
  config?: Record<string, any>;
}

// 测试连接响应
export interface TestConnectorResponse {
  success: boolean;
  message: string;
  latencyMs?: number;
  serverVersion?: string;
  errorDetails?: string;
}

// 分页元数据
export interface PaginationMeta {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

// 分页响应
export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

// 连接器类型配置定义
export interface ConnectorTypeConfig {
  value: ConnectorType;
  label: string;
  icon: string;
  description: string;
  fields: ConnectorFieldConfig[];
}

// 连接器字段配置
export interface ConnectorFieldConfig {
  name: string;
  label: string;
  type: 'text' | 'number' | 'password';
  placeholder?: string;
  required: boolean;
  defaultValue?: string | number;
}

// 连接器类型配置映射
export const CONNECTOR_TYPE_CONFIGS: Record<string, ConnectorTypeConfig> = {
  mysql: {
    value: 'mysql',
    label: 'MySQL',
    icon: 'Database',
    description: '连接 MySQL 数据库',
    fields: [
      {name: 'host', label: '主机地址', type: 'text', placeholder: 'localhost', required: true},
      {name: 'port', label: '端口', type: 'number', placeholder: '3306', required: true, defaultValue: 3306},
      {name: 'database', label: '数据库名', type: 'text', placeholder: 'my_database', required: true},
      {name: 'username', label: '用户名', type: 'text', placeholder: 'root', required: true},
      {name: 'password', label: '密码', type: 'password', placeholder: '••••••••', required: true}
    ]
  },
  salesforce: {
    value: 'salesforce',
    label: 'Salesforce',
    icon: 'Cloud',
    description: '连接 Salesforce CRM',
    fields: [
      {name: 'username', label: '用户名', type: 'text', placeholder: 'user@example.com', required: true},
      {name: 'password', label: '密码', type: 'password', placeholder: '••••••••', required: true},
      {name: 'securityToken', label: '安全令牌', type: 'password', placeholder: '••••••••', required: true},
      {name: 'apiKey', label: 'API Key', type: 'password', placeholder: '••••••••', required: true}
    ]
  },
  postgresql: {
    value: 'postgresql',
    label: 'PostgreSQL',
    icon: 'Database',
    description: '连接 PostgreSQL 数据库',
    fields: [
      {name: 'host', label: '主机地址', type: 'text', placeholder: 'localhost', required: true},
      {name: 'port', label: '端口', type: 'number', placeholder: '5432', required: true, defaultValue: 5432},
      {name: 'database', label: '数据库名', type: 'text', placeholder: 'my_database', required: true},
      {name: 'username', label: '用户名', type: 'text', placeholder: 'postgres', required: true},
      {name: 'password', label: '密码', type: 'password', placeholder: '••••••••', required: true}
    ]
  }
};

// 获取连接器显示状态
export function getConnectorDisplayStatus(
  connector: Connector
): { status: ConnectorStatus; label: string; color: string } {
  if (!connector.lastTestedAt) {
    return {status: 'disconnected', label: '未测试', color: '#9ca3af'};
  }

  if (connector.lastTestStatus === 'success') {
    return {status: 'connected', label: '已连接', color: '#10b981'};
  }

  return {status: 'error', label: '连接错误', color: '#ef4444'};
}

// 获取连接器类型标签
export function getConnectorTypeLabel(type: ConnectorType): string {
  const config = CONNECTOR_TYPE_CONFIGS[type];
  return config?.label || type.toUpperCase();
}
