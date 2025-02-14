from models.config_model import ConfigOrm
from models import User, Config
from datetime import datetime
from typing import Optional

class ConfigService:
    """Emby配置相关"""

    async def first_or_create_emby_config(self) -> Config:
        """获取或创建 Emby 配置。"""
        emby_config = await ConfigOrm().query_one(conds=[Config.id == 1])
        if not emby_config:
            emby_config = Config(
                register_public_user=0,
                register_public_time=0,
                total_register_user=0
            )
            await ConfigOrm().add(emby_config)
        return emby_config

    async def emby_create_user(self, telegram_id: int, username: str, password: str) -> User:
        """创建 Emby 用户（外部调用入口），先判断各种配置是否允许注册，然后调用内部的 _emby_create_user"""
        user = await self.get_or_create_user_by_telegram_id(telegram_id)
        if user.has_emby_account():
            raise Exception("该 Telegram 用户已经绑定过 Emby 账号，无法重复创建。")

        emby_config = await self.first_or_create_emby_config()
        if not emby_config:
            raise Exception("未找到 Emby 配置，无法创建账号。")

        if not await self._check_register_permission(user, emby_config):
            raise Exception("当前没有可用的注册权限或名额，创建账号被拒绝。")

        async with ConfigOrm().transaction() as session:
            if not user.enable_register and emby_config.register_public_user > 0:
                emby_config.register_public_user -= 1

            emby_config.total_register_user += 1
            new_user = await self._emby_create_user(telegram_id, username, password)

            session.add(new_user)
            session.add(emby_config)
            await session.commit()
        return new_user

    async def _check_register_permission(self, user: User, emby_config: Config) -> bool:
        """检查用户是否有权限注册 Emby 账号"""
        enable_register = user.enable_register
        if not enable_register and emby_config.register_public_user > 0:
            enable_register = True
        if (
            not enable_register
            and emby_config.register_public_time > 0
            and datetime.now().timestamp() < emby_config.register_public_time
        ):
            enable_register = True
        if 0 < emby_config.register_public_time < datetime.now().timestamp():
            await ConfigOrm().update(
                values={'register_public_time': 0},
                conds=[Config.id == 1]
            )
        return enable_register

    async def set_emby_config(self, telegram_id: int, register_public_user: Optional[int] = None,
                              register_public_time: Optional[int] = None) -> Config:
        """设置 Emby 注册相关配置，如公共注册名额和公共注册截止时间"""
        user = await self.must_get_user(telegram_id)
        user.check_set_emby_config()

        emby_config = await self.first_or_create_emby_config()
        if not emby_config:
            raise Exception("未找到全局 Emby 配置，无法设置。")

        if register_public_user is not None:
            emby_config.register_public_user = register_public_user
        if register_public_time is not None:
            emby_config.register_public_time = register_public_time

        await ConfigOrm().update(
            values={
                'register_public_user': emby_config.register_public_user,
                'register_public_time': emby_config.register_public_time
            },
            conds=[Config.id == 1]
        )
        return emby_config