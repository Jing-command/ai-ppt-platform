import apiClient from './client';
import {
    Connector,
    CreateConnectorRequest,
    UpdateConnectorRequest,
    TestConnectorRequest,
    TestConnectorResponse,
    PaginatedResponse
} from '@/types/connector';

const CONNECTORS_BASE = '/connectors';

/**
 * 获取连接器列表
 * @param page 页码，默认 1
 * @param pageSize 每页数量，默认 20
 * @param connectorType 可选的连接器类型过滤
 */
export async function getConnectors(
    page: number = 1,
    pageSize: number = 20,
    connectorType?: string
): Promise<PaginatedResponse<Connector>> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('pageSize', pageSize.toString());
    if (connectorType) {
        params.append('connectorType', connectorType);
    }

    const response = await apiClient.get<PaginatedResponse<Connector>>(
        `${CONNECTORS_BASE}?${params.toString()}`
    );
    return response.data;
}

/**
 * 获取连接器详情
 * @param id 连接器 ID
 */
export async function getConnector(id: string): Promise<Connector> {
    const response = await apiClient.get<Connector>(`${CONNECTORS_BASE}/${id}`);
    return response.data;
}

/**
 * 创建连接器
 * @param data 连接器创建数据
 */
export async function createConnector(data: CreateConnectorRequest): Promise<Connector> {
    const response = await apiClient.post<Connector>(CONNECTORS_BASE, data);
    return response.data;
}

/**
 * 更新连接器
 * @param id 连接器 ID
 * @param data 连接器更新数据
 */
export async function updateConnector(
    id: string,
    data: UpdateConnectorRequest
): Promise<Connector> {
    const response = await apiClient.put<Connector>(`${CONNECTORS_BASE}/${id}`, data);
    return response.data;
}

/**
 * 删除连接器
 * @param id 连接器 ID
 */
export async function deleteConnector(id: string): Promise<void> {
    await apiClient.delete(`${CONNECTORS_BASE}/${id}`);
}

/**
 * 测试连接
 * @param id 连接器 ID
 * @param config 可选的临时配置用于测试
 */
export async function testConnector(
    id: string,
    config?: Record<string, unknown>
): Promise<TestConnectorResponse> {
    const requestBody: TestConnectorRequest = config ? {config} : {};
    const response = await apiClient.post<TestConnectorResponse>(
        `${CONNECTORS_BASE}/${id}/test`,
        requestBody
    );
    return response.data;
}

/**
 * 测试新连接器的配置（无需保存）
 * 使用特殊的 'test' ID 来测试临时配置
 * @param type 连接器类型
 * @param config 连接配置
 */
export async function testConnectorConfig(
    type: string,
    config: Record<string, unknown>
): Promise<TestConnectorResponse> {
    // 使用特殊端点测试未保存的连接器配置
    const response = await apiClient.post<TestConnectorResponse>(
        `${CONNECTORS_BASE}/test-config`,
        {type, config}
    );
    return response.data;
}

/**
 * 获取数据源结构
 * @param id 连接器 ID
 * @param refresh 是否刷新缓存
 */
export async function getConnectorSchema(
    id: string,
    refresh: boolean = false
): Promise<unknown> {
    const params = new URLSearchParams();
    if (refresh) {
        params.append('refresh', 'true');
    }

    const response = await apiClient.get(
        `${CONNECTORS_BASE}/${id}/schema?${params.toString()}`
    );
    return response.data;
}

/**
 * 执行查询
 * @param id 连接器 ID
 * @param query SQL 查询
 * @param params 查询参数
 * @param limit 结果限制
 */
export async function executeQuery(
    id: string,
    query: string,
    params?: Record<string, unknown>,
    limit: number = 100
): Promise<unknown> {
    const response = await apiClient.post(`${CONNECTORS_BASE}/${id}/query`, {
        query,
        params,
        limit
    });
    return response.data;
}
