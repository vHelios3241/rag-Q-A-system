
from typing import Optional, Dict, Any, List

class RetrievalConfig:
    """检索配置"""
    top_k: int=5
    min_score: float = 0.0        # 最低分数阈值
    namespace: Optional[str] = None    # 命名空间过滤
    metadata_filter: Optional[Dict] = None # 元数据过滤
