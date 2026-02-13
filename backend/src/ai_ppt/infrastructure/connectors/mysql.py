"""
MySQL 数据连接器实现
使用 aiomysql 进行异步连接
"""
from typing import Any, AsyncIterator, Dict, List, Optional

import aiomysql

from ai_ppt.infrastructure.connectors.base import (
    ColumnSchema,
    ConnectionError,
    DataConnector,
    DataRow,
    DataType,
    QueryError,
    TableSchema,
)


# MySQL 类型映射到通用数据类型
MYSQL_TYPE_MAPPING = {
    "varchar": DataType.STRING,
    "text": DataType.STRING,
    "longtext": DataType.STRING,
    "mediumtext": DataType.STRING,
    "tinytext": DataType.STRING,
    "char": DataType.STRING,
    "enum": DataType.STRING,
    "set": DataType.STRING,
    "int": DataType.INTEGER,
    "integer": DataType.INTEGER,
    "bigint": DataType.INTEGER,
    "smallint": DataType.INTEGER,
    "tinyint": DataType.INTEGER,
    "mediumint": DataType.INTEGER,
    "float": DataType.FLOAT,
    "double": DataType.FLOAT,
    "decimal": DataType.FLOAT,
    "numeric": DataType.FLOAT,
    "datetime": DataType.DATETIME,
    "timestamp": DataType.DATETIME,
    "date": DataType.DATETIME,
    "time": DataType.DATETIME,
    "year": DataType.INTEGER,
    "json": DataType.JSON,
    "bool": DataType.BOOLEAN,
    "boolean": DataType.BOOLEAN,
    "blob": DataType.STRING,
    "longblob": DataType.STRING,
    "mediumblob": DataType.STRING,
    "tinyblob": DataType.STRING,
    "binary": DataType.STRING,
    "varbinary": DataType.STRING,
}


class MySQLConnector(DataConnector):
    """
    MySQL 连接器实现
    
    使用 aiomysql 连接池管理 MySQL 连接
    支持标准 SQL 查询和流式查询
    """
    
    def __init__(
        self,
        config_id: str,
        name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        ssl: Optional[Dict[str, Any]] = None,
        connect_timeout: int = 30,
    ) -> None:
        """
        初始化 MySQL 连接器
        
        Args:
            config_id: 配置 ID
            name: 连接器名称
            host: MySQL 主机地址
            port: MySQL 端口
            username: 用户名
            password: 密码
            database: 数据库名
            pool_size: 连接池最小大小
            max_overflow: 连接池最大溢出
            ssl: SSL 配置
            connect_timeout: 连接超时（秒）
        """
        super().__init__(config_id, name)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.ssl = ssl
        self.connect_timeout = connect_timeout
        self._pool: Optional[aiomysql.Pool] = None
    
    async def connect(self) -> None:
        """建立连接池"""
        try:
            self._pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                db=self.database,
                ssl=self.ssl,
                minsize=1,
                maxsize=self.pool_size + self.max_overflow,
                autocommit=True,
                connect_timeout=self.connect_timeout,
            )
            self._connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MySQL: {e}")
    
    async def disconnect(self) -> None:
        """关闭连接池"""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
        self._connected = False
    
    async def test_connection(self) -> bool:
        """测试连接"""
        if not self._pool:
            return False
        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()
                    return result is not None and result[0] == 1
        except Exception:
            return False
    
    async def get_schema(self) -> List[TableSchema]:
        """获取数据库表结构"""
        if not self._pool:
            raise ConnectionError("Not connected to database")
        
        schemas: List[TableSchema] = []
        
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                # 获取所有表
                await cur.execute("""
                    SELECT TABLE_NAME, TABLE_COMMENT 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
                """, (self.database,))
                tables = await cur.fetchall()
                
                for table in tables:
                    table_name = table["TABLE_NAME"]
                    description = table["TABLE_COMMENT"] or None
                    
                    # 获取列信息
                    await cur.execute("""
                        SELECT 
                            COLUMN_NAME,
                            DATA_TYPE,
                            IS_NULLABLE,
                            COLUMN_COMMENT
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                        ORDER BY ORDINAL_POSITION
                    """, (self.database, table_name))
                    columns_data = await cur.fetchall()
                    
                    columns = [
                        ColumnSchema(
                            name=col["COLUMN_NAME"],
                            data_type=MYSQL_TYPE_MAPPING.get(
                                col["DATA_TYPE"].lower(), 
                                DataType.STRING
                            ),
                            nullable=col["IS_NULLABLE"] == "YES",
                            description=col["COLUMN_COMMENT"] or None,
                        )
                        for col in columns_data
                    ]
                    
                    schemas.append(TableSchema(
                        name=table_name,
                        columns=columns,
                        description=description,
                    ))
        
        return schemas
    
    async def query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[DataRow]:
        """执行查询"""
        if not self._pool:
            raise ConnectionError("Not connected to database")
        
        if limit and "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        
        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(query, params)
                    rows = await cur.fetchall()
                    return [DataRow(data=dict(row)) for row in rows]
        except Exception as e:
            raise QueryError(f"Query failed: {e}", query=query)
    
    async def query_stream(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
    ) -> AsyncIterator[DataRow]:
        """
        流式查询
        
        使用 LIMIT/OFFSET 分页处理大数据集
        """
        if not self._pool:
            raise ConnectionError("Not connected to database")
        
        # 检查查询是否包含 ORDER BY，如果没有则添加以避免分页不一致
        if "ORDER BY" not in query.upper():
            # 尝试获取主键列
            pass  # 简化处理，依赖外部传入正确的排序
        
        offset = 0
        while True:
            paginated_query = f"{query} LIMIT {batch_size} OFFSET {offset}"
            rows = await self.query(paginated_query, params)
            
            if not rows:
                break
            
            for row in rows:
                yield row
            
            offset += batch_size
            
            if len(rows) < batch_size:
                break
