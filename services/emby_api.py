from typing import Optional, Dict, Tuple
from models.user_model import UserOrm
from core.emby_api import EmbyApi
from datetime import datetime
from models import User
import logging

logger = logging.getLogger(__name__)

class ServiceApi:
    """EmbyAPI相关操作"""

    def __init__(self, emby_api: EmbyApi):
        self.emby_api = emby_api

    async def _emby_create_user(self, telegram_id: int, username: str, password: str) -> User:
        """内部使用：真正调用 Emby API 创建用户，并设置初始密码"""
        user = await self.get_or_create_user_by_telegram_id(telegram_id)
        emby_user = self.emby_api.create_user(username)
        if not emby_user or not emby_user.get("Id"):
            raise Exception("在 Emby 系统中创建账号失败，请检查 Emby 服务是否正常。")

        emby_id = emby_user["Id"]
        user.emby_id = emby_id
        user.emby_name = username
        user.enable_register = False

        # 设置初始密码 & 默认Policy
        self.emby_api.set_user_password(emby_id, password)
        self.emby_api.set_default_policy(emby_id)
        return user

    async def emby_info(self, telegram_id: int) -> Tuple[User, Dict]:
        """获取当前用户在 Emby 的信息"""
        user = await self.must_get_user(telegram_id)
        if not user.has_emby_account():
            raise Exception("该用户尚未绑定 Emby 账号。")
        emby_user = self.emby_api.get_user(str(user.emby_id))
        if not emby_user:
            raise Exception("从 Emby 服务器获取用户信息失败，请检查 Emby 服务是否正常。")
        return user, emby_user
    
    async def reset_password(self, telegram_id: int, password: str = '') -> bool:
        """重置用户的 Emby 密码。"""
        user = await self.must_get_emby_user(telegram_id)
        try:
            self.emby_api.reset_user_password(user.emby_id)
            self.emby_api.set_user_password(user.emby_id, password)
            return True
        except Exception as e:
            logger.error(f"重置密码失败: {e}")
            return False

    async def emby_ban(self, telegram_id: int, reason: str, operator_telegram_id: Optional[int] = None) -> bool:
        """禁用用户"""
        if operator_telegram_id is not None:
            admin_user = await self.must_get_user(operator_telegram_id)
            if not admin_user.is_admin:
                raise Exception("您没有管理员权限，无法执行禁用操作。")

        user = await self.must_get_user(telegram_id)
        user.check_emby_ban()

        try:
            self.emby_api.ban_user(str(user.emby_id))
            user.ban_time = int(datetime.now().timestamp())
            user.reason = reason
            await UserOrm().update(
                {"ban_time": user.ban_time, "reason": reason},
                conds=[User.id == user.id]
            )
            return True
        except Exception as e:
            logger.error(f"禁用用户失败: {e}")
            return False
    
    async def emby_unban(self, telegram_id: int, operator_telegram_id: Optional[int] = None) -> bool:
        """解禁用户"""
        if operator_telegram_id is not None:
            admin_user = await self.must_get_user(operator_telegram_id)
            if not admin_user.is_admin:
                raise Exception("您没有管理员权限，无法执行解禁操作。")

        user = await self.must_get_user(telegram_id)
        user.check_emby_unban()

        try:
            self.emby_api.set_default_policy(str(user.emby_id))
            user.ban_time = 0
            user.reason = ""
            await UserOrm().update(
                {"ban_time": 0, "reason": None},
                conds=[User.id == user.id]
            )
            return True
        except Exception as e:
            logger.error(f"解禁用户失败: {e}")
            return False

    def emby_count(self) -> Dict:
        """从 Emby API 获取当前影片数量统计"""
        return self.emby_api.count()