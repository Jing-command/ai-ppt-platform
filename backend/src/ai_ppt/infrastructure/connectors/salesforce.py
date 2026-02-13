"""
Salesforce 数据连接器实现（API Key/Password 版本）
使用 Salesforce REST API 和 httpx
"""
from typing import Any, AsyncIterator, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from ai_ppt.infrastructure.connectors.base import (
    AuthenticationError,
    ColumnSchema,
    ConnectionError,
    DataConnector,
    DataRow,
    DataType,
    QueryError,
    TableSchema,
)


# Salesforce 类型映射到通用数据类型
SF_TYPE_MAPPING = {
    "string": DataType.STRING,
    "textarea": DataType.STRING,
    "picklist": DataType.STRING,
    "multipicklist": DataType.STRING,
    "reference": DataType.STRING,
    "url": DataType.STRING,
    "email": DataType.STRING,
    "phone": DataType.STRING,
    "encryptedstring": DataType.STRING,
    "int": DataType.INTEGER,
    "integer": DataType.INTEGER,
    "double": DataType.FLOAT,
    "currency": DataType.FLOAT,
    "percent": DataType.FLOAT,
    "date": DataType.DATETIME,
    "datetime": DataType.DATETIME,
    "time": DataType.DATETIME,
    "boolean": DataType.BOOLEAN,
    "address": DataType.JSON,
    "location": DataType.JSON,
    "anyType": DataType.STRING,
    "combobox": DataType.STRING,
    "id": DataType.STRING,
    "base64": DataType.STRING,
}


class SalesforceConnector(DataConnector):
    """
    Salesforce 连接器实现（Demo 版本）
    
    使用 API Key/Password 认证方式
    支持 SOQL 查询和流式查询
    """
    
    def __init__(
        self,
        config_id: str,
        name: str,
        api_key: str,
        username: str,
        password: str,
        security_token: Optional[str] = None,
        instance_url: Optional[str] = None,
        login_url: str = "https://login.salesforce.com",
        api_version: str = "v59.0",
        timeout: float = 30.0,
    ) -> None:
        """
        初始化 Salesforce 连接器
        
        Args:
            config_id: 配置 ID
            name: 连接器名称
            api_key: API Key（Consumer Key/Client ID）
            username: Salesforce 用户名
            password: Salesforce 密码
            security_token: 安全令牌（可选，取决于组织设置）
            instance_url: 实例 URL（可选，认证后自动获取）
            login_url: 登录 URL（默认为生产环境）
            api_version: Salesforce API 版本
            timeout: HTTP 请求超时（秒）
        """
        super().__init__(config_id, name)
        self.api_key = api_key
        self.username = username
        self.password = password
        self.security_token = security_token or ""
        self.instance_url = instance_url
        self.login_url = login_url
        self.api_version = api_version
        self.timeout = timeout
        self._access_token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._client_id: Optional[str] = None
        self._client_secret: Optional[str] = None
    
    def set_oauth_credentials(self, client_id: str, client_secret: str) -> None:
        """
        设置 OAuth 凭证
        
        如果使用完整的 OAuth2 流程，调用此方法设置 client_id 和 client_secret
        """
        self._client_id = client_id
        self._client_secret = client_secret
    
    async def connect(self) -> None:
        """建立连接并获取认证令牌"""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        
        try:
            # 使用密码流程（Password Flow）获取 OAuth token
            # 这是 Demo 版本的简化实现
            auth_url = f"{self.login_url}/services/oauth2/token"
            
            auth_data = {
                "grant_type": "password",
                "username": self.username,
                "password": f"{self.password}{self.security_token}",
            }
            
            # 优先使用 OAuth 凭证，否则使用 API Key
            if self._client_id and self._client_secret:
                auth_data["client_id"] = self._client_id
                auth_data["client_secret"] = self._client_secret
            else:
                auth_data["client_id"] = self.api_key
            
            response = await self._client.post(
                auth_url,
                data=auth_data,
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data["access_token"]
            self.instance_url = self.instance_url or token_data.get("instance_url")
            self._connected = True
            
        except httpx.HTTPError as e:
            raise ConnectionError(f"Failed to authenticate with Salesforce: {e}")
        except KeyError as e:
            raise AuthenticationError(f"Invalid authentication response: {e}")
    
    async def disconnect(self) -> None:
        """断开连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._access_token = None
        self._connected = False
    
    async def test_connection(self) -> bool:
        """测试连接"""
        if not self._client or not self._access_token:
            return False
        try:
            await self._api_request("GET", f"/services/data/{self.api_version}/limits")
            return True
        except Exception:
            return False
    
    async def _api_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点路径
            **kwargs: 额外请求参数
            
        Returns:
            API 响应数据
        """
        if not self._access_token:
            raise ConnectionError("Not authenticated")
        
        if not self.instance_url:
            raise ConnectionError("Instance URL not set")
        
        url = urljoin(self.instance_url, endpoint)
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # 合并 headers
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        response = await self._client.request(
            method,
            url,
            headers=headers,
            **kwargs,
        )
        response.raise_for_status()
        
        if response.content:
            return response.json()
        return {}
    
    async def get_schema(self) -> List[TableSchema]:
        """
        获取 Salesforce 对象列表
        
        获取所有可查询的 SObject 及其字段信息
        """
        if not self._client:
            raise ConnectionError("Not connected")
        
        # 获取所有可查询的对象
        data = await self._api_request(
            "GET",
            f"/services/data/{self.api_version}/sobjects/",
        )
        
        schemas: List[TableSchema] = []
        sobjects = data.get("sobjects", [])
        
        # 限制为可查询的业务对象
        for obj in sobjects:
            if not obj.get("queryable"):
                continue
            
            # 跳过系统对象
            name = obj.get("name", "")
            if name.endswith("__Share") or name.endswith("__History") or name.endswith("__Feed"):
                continue
            
            # 获取对象描述
            try:
                desc = await self._api_request(
                    "GET",
                    f"/services/data/{self.api_version}/sobjects/{name}/describe/",
                )
                
                columns = [
                    ColumnSchema(
                        name=field["name"],
                        data_type=SF_TYPE_MAPPING.get(
                            field.get("type", "string"),
                            DataType.STRING,
                        ),
                        nullable=field.get("nillable", True),
                        description=field.get("label"),
                    )
                    for field in desc.get("fields", [])
                ]
                
                schemas.append(TableSchema(
                    name=name,
                    columns=columns,
                    description=obj.get("label"),
                ))
            except Exception:
                # 跳过无法访问的对象
                continue
        
        return schemas
    
    async def query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[DataRow]:
        """
        执行 SOQL 查询
        
        Args:
            query: SOQL 查询语句
            params: 查询参数（Salesforce SOQL 不支持参数化查询，这里用于占位符替换）
            limit: 结果数量限制
            
        Returns:
            查询结果列表
        """
        if not self._client:
            raise ConnectionError("Not connected")
        
        # Salesforce SOQL 使用 LIMIT 子句
        if limit and "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        
        # 简单的参数替换（SOQL 不支持真正的参数化查询）
        if params:
            for key, value in params.items():
                placeholder = f":{key}"
                if isinstance(value, str):
                    escaped_value = value.replace("'", "\\'")
                    value = f"'{escaped_value}'"
                query = query.replace(placeholder, str(value))
        
        try:
            # URL 编码查询
            from urllib.parse import quote
            encoded_query = quote(query)
            endpoint = f"/services/data/{self.api_version}/query/?q={encoded_query}"
            
            data = await self._api_request("GET", endpoint)
            records = data.get("records", [])
            
            # 移除 Salesforce 系统字段
            for record in records:
                record.pop("attributes", None)
            
            return [DataRow(data=record) for record in records]
            
        except httpx.HTTPError as e:
            raise QueryError(f"SOQL query failed: {e}", query=query)
    
    async def query_stream(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        batch_size: int = 2000,
    ) -> AsyncIterator[DataRow]:
        """
        流式查询
        
        Salesforce 有 2000 条记录的查询限制，使用 queryMore 处理
        注意：batch_size 在 Salesforce 中最大为 2000
        
        Args:
            query: SOQL 查询语句
            params: 查询参数
            batch_size: 每批次数量（Salesforce 最大 2000）
        """
        if not self._client:
            raise ConnectionError("Not connected")
        
        # 限制 batch_size 不超过 2000
        effective_batch_size = min(batch_size, 2000)
        
        # 添加 LIMIT 如果查询中没有
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT {effective_batch_size}"
        
        next_url: Optional[str] = None
        total_yielded = 0
        
        while True:
            if next_url:
                # 使用相对路径
                data = await self._api_request("GET", next_url)
            else:
                # 首次查询
                from urllib.parse import quote
                encoded_query = quote(query)
                endpoint = f"/services/data/{self.api_version}/query/?q={encoded_query}"
                data = await self._api_request("GET", endpoint)
            
            records = data.get("records", [])
            
            for record in records:
                record.pop("attributes", None)
                yield DataRow(data=record)
                total_yielded += 1
                
                if total_yielded >= effective_batch_size:
                    return
            
            next_url = data.get("nextRecordsUrl")
            if not next_url or not records:
                break
