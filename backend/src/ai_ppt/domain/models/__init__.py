"""
领域模型模块

包含所有 SQLAlchemy 实体模型
"""

from ai_ppt.domain.models.base import Base
from ai_ppt.domain.models.connector import Connector, ConnectorStatus
from ai_ppt.domain.models.outline import (Outline, OutlineBackground,
                                          OutlinePage, OutlineStatus)
from ai_ppt.domain.models.presentation import Presentation, PresentationStatus
from ai_ppt.domain.models.slide import Slide, SlideLayoutType

__all__ = [
    # 基础
    "Base",
    # Presentation
    "Presentation",
    "PresentationStatus",
    # Slide
    "Slide",
    "SlideLayoutType",
    # Outline
    "Outline",
    "OutlineStatus",
    "OutlinePage",
    "OutlineBackground",
    # Connector
    "Connector",
    "ConnectorStatus",
]
