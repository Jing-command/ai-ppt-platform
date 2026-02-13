"""
日期时间工具
"""

from datetime import datetime, timezone


def utcnow_aware() -> datetime:
    """
    获取当前 UTC 时间的带时区 aware 的 datetime 对象
    
    Returns:
        当前 UTC 时间
    """
    return datetime.now(timezone.utc)


def ensure_aware(dt: datetime) -> datetime:
    """
    确保 datetime 对象是带时区的
    
    Args:
        dt: 输入的 datetime 对象
    
    Returns:
        带时区的 datetime 对象
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
