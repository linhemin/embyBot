from core.emby_api import EmbyRouterAPI
from typing import List, Dict

class UserRouter:
    """用户线路相关操作"""

    def __init__(self, emby_router_api: EmbyRouterAPI):
        self.emby_router_api = emby_router_api

    async def get_user_router(self, telegram_id: int) -> Dict:
        """获取用户的线路信息"""
        user = await self.must_get_emby_user(telegram_id)
        return self.emby_router_api.query_user_route(user.emby_id)

    async def update_user_router(self, telegram_id: int, new_index: str) -> bool:
        """更新用户线路信息"""
        user = await self.must_get_emby_user(telegram_id)
        return self.emby_router_api.update_user_route(str(user.emby_id), str(new_index))

    async def get_router_list(self, telegram_id: int) -> List[Dict]:
        """获取所有可用线路"""
        await self.must_get_emby_user(telegram_id)
        return self.emby_router_api.query_all_route()