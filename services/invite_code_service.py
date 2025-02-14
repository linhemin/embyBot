from models import InviteCode
from models.invite_code_model import InviteCodeOrm, InviteCodeType
from models.user_model import User, UserOrm
from typing import List
from sqlalchemy import select
from datetime import datetime
from config import config
from random import sample
import shortuuid
import string
import re



class InviteCodeService:
    """邀请码服务"""

    @staticmethod
    async def get_or_create_user_by_telegram_id(telegram_id: int) -> User:
        """通过 telegram_id 从数据库获取用户，如果不存在则创建一个默认用户"""
        user = await UserOrm().query_one(conds=[User.telegram_id == telegram_id])
        if not user:
            default_user = User(
                telegram_id=telegram_id,
                is_admin=telegram_id in config.admin_list,
                telegram_name=config.group_members.get(telegram_id, {}).get('username'),
            )
            user_id = await UserOrm().add(default_user)
            user = default_user
            user.id = user_id
        return user

    async def is_admin(self,telegram_id: int) -> bool:
        """判断指定的 Telegram 用户是否为管理员"""
        user = await self.get_or_create_user_by_telegram_id(telegram_id)
        return user and user.is_admin

    async def must_get_user(self, telegram_id: int) -> User:
        """获取指定用户信息，不存在则抛出异常"""
        user = await self.get_or_create_user_by_telegram_id(telegram_id)
        if user is None:
            raise Exception("未找到该用户的信息。")
        return user

    async def must_get_emby_user(self, telegram_id: int) -> User:
        """确保用户存在且已创建 Emby 账号，若不存在则抛出异常"""
        user = await self.must_get_user(telegram_id)
        if user.emby_id is None:
            raise Exception("该用户尚未绑定 Emby 账号，无法执行此操作。")
        if user.ban_time is not None and user.ban_time > 0:
            raise Exception("该用户的 Emby 账号已被禁用，无法执行此操作。")
        return user

    @staticmethod
    def gen_default_passwd() -> str:
        """生成默认密码：随机6位的字母数字组合"""
        return ''.join(sample(string.ascii_letters + string.digits, 6))

    @staticmethod
    def gen_register_code(num: int) -> List[str]:
        """批量生成普通邀请码"""
        return [f'epr-{str(shortuuid.uuid())}' for _ in range(num)]

    @staticmethod
    def gen_whitelist_code(num: int) -> List[str]:
        """批量生成白名单邀请码"""
        return [f'epw-{str(shortuuid.uuid())}' for _ in range(num)]

    async def create_invite_code(self, telegram_id: int, count: int = 1) -> List[InviteCode]:
        """创建普通邀请码，需检测用户是否有权限"""
        user = await self.must_get_user(telegram_id)
        if not user.check_create_invite_code():
            raise Exception("您没有权限生成普通邀请码。")

        code_objs = [
            InviteCode(code=code, telegram_id=telegram_id, code_type=InviteCodeType.REGISTER)
            for code in self.gen_register_code(count)
        ]
        return await InviteCodeOrm().bulk_add(code_objs)

    async def create_whitelist_code(self, telegram_id: int, count: int = 1) -> List[InviteCode]:
        """创建白名单邀请码，需检测用户是否有权限"""
        user = await self.must_get_user(telegram_id)
        if not user.check_create_whitelist_code():
            raise Exception("您没有权限生成白名单邀请码。")

        code_objs = [
            InviteCode(code=code, telegram_id=telegram_id, code_type=InviteCodeType.WHITELIST)
            for code in self.gen_whitelist_code(count)
        ]
        return await InviteCodeOrm().bulk_add(code_objs)

    async def redeem_code(self, telegram_id: int, code: str):
        """使用邀请码，分为普通注册邀请码和白名单邀请码"""
        pattern = re.compile(r'^(epr|epw)-[A-Za-z0-9]+$')
        if not pattern.match(code):
            raise Exception("邀请码格式不正确。")

        user = await self.must_get_user(telegram_id)

        # 使用事务块，并通过行锁防止并发问题
        async with InviteCodeOrm().transaction() as session:
            # 构造 SELECT 语句，并加上 FOR UPDATE 行锁
            stmt = select(InviteCode).where(InviteCode.code == code).with_for_update()
            result = await session.execute(stmt)
            valid_code = result.scalars().first()

            if not valid_code or valid_code.is_used:
                raise Exception("该邀请码无效或已被使用。")

            # 根据邀请码类型执行不同的业务逻辑校验
            if valid_code.code_type == InviteCodeType.REGISTER:
                user.check_use_redeem_code()
            elif valid_code.code_type == InviteCodeType.WHITELIST:
                user.check_use_whitelist_code()
                if user.is_emby_baned():
                    await self.emby_unban(telegram_id)

            # 标记邀请码已使用，并记录使用时间和使用者
            valid_code.is_used = True
            valid_code.used_time = datetime.now().timestamp()
            valid_code.used_user_id = telegram_id

            # 根据邀请码类型更新用户状态
            if valid_code.code_type == InviteCodeType.REGISTER:
                user.enable_register = True
            elif valid_code.code_type == InviteCodeType.WHITELIST:
                user.is_whitelist = True

            session.add(valid_code)
            session.add(user)
            await session.commit()

        return valid_code