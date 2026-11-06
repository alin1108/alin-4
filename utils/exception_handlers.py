from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from utils import exception

def register_exception_handlers(app):
    """
    注册全局异常处理：子类在前，父类在后；具体在前，抽象在后
    """
    # 业务
    app.add_exception_handler(HTTPException,exception.http_exception_handler)
    # 数据库完整性约束
    app.add_exception_handler(IntegrityError,exception.integrity_error_handler)
    # 数据库
    app.add_exception_handler(SQLAlchemyError,exception.sqlalchemy_error_handler)
    # 其他
    app.add_exception_handler(Exception,exception.general_exception_handler)