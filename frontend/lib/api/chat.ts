// lib/api/chat.ts
// 聊天 API 客户端 - 处理 AI 提示词助手的流式响应

/**
 * 聊天消息类型定义
 */
export interface ChatMessage {
    role: 'user' | 'assistant';  // 消息角色：用户或助手
    content: string;             // 消息内容
}

/**
 * SSE 流式响应数据类型
 */
export interface ChatStreamChunk {
    content: string;             // 部分内容
    isFinished: boolean;         // 是否完成
    hasOptimizedPrompt: boolean; // 是否包含优化后的提示词
    optimizedPrompt?: string;    // 优化后的提示词（可选）
}

/**
 * 发送聊天请求的参数类型
 */
export interface SendMessageParams {
    messages: ChatMessage[];     // 消息历史
    onChunk: (chunk: ChatStreamChunk) => void;  // 接收到数据块时的回调
    onError?: (error: Error) => void;           // 错误回调
    onComplete?: () => void;                    // 完成回调
}

// API 基础地址
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

/**
 * 获取认证头信息
 * @returns 包含认证 token 的请求头
 */
function getAuthHeaders(): HeadersInit {
    // 从本地存储获取访问令牌
    const token = localStorage.getItem('accessToken');
    return {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
    };
}

/**
 * 发送聊天消息并处理流式响应
 * 使用 Server-Sent Events (SSE) 处理 AI 的流式输出
 *
 * @param params - 发送消息的参数配置
 */
export async function sendMessage(params: SendMessageParams): Promise<void> {
    const { messages, onChunk, onError, onComplete } = params;

    try {
        // 发送 POST 请求到聊天 API
        const response = await fetch(`${API_BASE}/api/v1/chat`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ messages })
        });

        // 检查响应状态
        if (!response.ok) {
            // 尝试解析错误信息
            const errorData = await response.json().catch(() => ({
                message: '请求失败'
            }));
            throw new Error(errorData.message || '请求失败');
        }

        // 获取响应体的读取器
        const reader = response.body?.getReader();
        if (!reader) {
            throw new Error('无法读取响应流');
        }

        // 创建解码器用于解析 UTF-8 数据
        const decoder = new TextDecoder();
        let buffer = '';  // 缓冲区，用于存储不完整的数据

        // 持续读取数据流
        while (true) {
            // 读取下一个数据块
            const { done, value } = await reader.read();

            // 流结束
            if (done) {
                break;
            }

            // 解码数据块并添加到缓冲区
            buffer += decoder.decode(value, { stream: true });

            // 按行分割数据（SSE 格式每行以 "data: " 开头）
            const lines = buffer.split('\n');
            // 保留最后一个可能不完整的行
            buffer = lines.pop() || '';

            // 处理每一行数据
            for (const line of lines) {
                // 跳过空行
                if (!line.trim()) {
                    continue;
                }

                // 检查是否是 SSE 数据行
                if (line.startsWith('data: ')) {
                    try {
                        // 提取 JSON 数据部分
                        const jsonStr = line.slice(6);
                        // 解析 JSON 数据
                        const chunk: ChatStreamChunk = JSON.parse(jsonStr);
                        // 调用回调函数处理数据块
                        onChunk(chunk);

                        // 如果响应完成，调用完成回调
                        if (chunk.isFinished && onComplete) {
                            onComplete();
                        }
                    } catch (parseError) {
                        // JSON 解析失败，记录错误但继续处理
                        console.error('解析 SSE 数据失败:', parseError);
                    }
                }
            }
        }

        // 处理缓冲区中剩余的数据
        if (buffer.trim() && buffer.startsWith('data: ')) {
            try {
                const jsonStr = buffer.slice(6);
                const chunk: ChatStreamChunk = JSON.parse(jsonStr);
                onChunk(chunk);
                if (chunk.isFinished && onComplete) {
                    onComplete();
                }
            } catch (parseError) {
                console.error('解析缓冲区数据失败:', parseError);
            }
        }
    } catch (error) {
        // 调用错误回调
        if (onError) {
            onError(error instanceof Error ? error : new Error('未知错误'));
        } else {
            // 如果没有错误回调，抛出错误
            throw error;
        }
    }
}
