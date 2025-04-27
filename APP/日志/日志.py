import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
import time
import threading


class 安全滚动文件处理器(TimedRotatingFileHandler):
    """自定义的日志滚动处理器，处理文件被占用的情况"""

    def __init__(self, *args, **kwargs):
        self.lock = threading.RLock()
        super().__init__(*args, **kwargs)

    def doRollover(self):
        """重写滚动方法，添加文件占用处理"""
        with self.lock:
            try:
                # 尝试执行原始的滚动逻辑
                super().doRollover()
            except (PermissionError, OSError) as e:
                当前时间 = datetime.now().strftime("%Y%m%d-%H%M%S")
                新文件名 = f"{self.baseFilename}.{当前时间}.log"

                try:
                    # 创建新的日志文件
                    with open(新文件名, 'w', encoding='utf-8') as _:
                        pass

                    # 安全关闭原始日志流
                    if self.stream:
                        try:
                            self.stream.close()
                        except Exception as close_e:
                            print(f"关闭旧日志流失败: {close_e}")

                    # 使用新的日志文件
                    self.baseFilename = 新文件名
                    self.stream = self._open()
                    print(f"日志滚动失败，创建新文件: {新文件名}")
                except Exception as inner_e:
                    print(f"严重错误：无法创建新的日志文件: {inner_e}")


def 配置日志(日志目录="logs", 控制台日志级别=logging.DEBUG, 文件日志级别=logging.INFO, 保留天数=30):
    # 创建日志目录（如果不存在）
    if not os.path.exists(日志目录):
        os.makedirs(日志目录)

    # 初始化日志记录器
    logger = logging.getLogger('myLogger')
    logger.setLevel(logging.DEBUG)  # 设置最低级别为DEBUG，由处理器过滤

    # 清除已有的处理器，避免重复添加
    if logger.handlers:
        for handler in logger.handlers[:]:
            try:
                handler.close()
            except:
                pass
        logger.handlers.clear()

    # 配置控制台日志处理器
    控制台处理器 = logging.StreamHandler()
    控制台处理器.setLevel(控制台日志级别)
    控制台处理器.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(控制台处理器)

    # 配置文件日志处理器（带滚动机制）
    文件路径 = os.path.join(日志目录, 'app.log')
    try:
        文件处理器 = 安全滚动文件处理器(
            filename=文件路径,
            when='midnight',  # 每天午夜滚动
            interval=1,  # 每1天滚动
            backupCount=保留天数,  # 保留指定天数的日志（自动删除旧文件）
            encoding='utf-8',
            utc=False  # 使用本地时间
        )
        文件处理器.setLevel(文件日志级别)
        文件处理器.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(文件处理器)
    except Exception as e:
        print(f"无法创建日志文件处理器: {e}")

    # 禁止日志传播到父记录器
    logger.propagate = False

    # 立即清理过期日志（避免初始时旧文件残留）
    try:
        删除过期日志(日志目录, 保留天数)
    except Exception as e:
        print(f"清理过期日志失败: {e}")


def 删除过期日志(日志目录, 保留天数):
    """删除超过保留天数的日志文件，避免文件被占用导致删除失败"""
    if not os.path.exists(日志目录):
        return

    截止时间 = datetime.now() - timedelta(days=保留天数)

    for 文件名 in os.listdir(日志目录):
        文件路径 = os.path.join(日志目录, 文件名)

        # 过滤非日志文件
        if not (文件名.endswith('.log') or 文件名.startswith('app.log.')):
            continue

        # 获取文件最后修改时间
        try:
            文件时间戳 = os.path.getmtime(文件路径)
            文件最后修改时间 = datetime.fromtimestamp(文件时间戳)
        except (FileNotFoundError, OSError):
            continue  # 文件可能已被其他进程删除或无法访问

        # 如果文件超过保留天数，尝试删除
        if 文件最后修改时间 < 截止时间:
            # 尝试删除（最多3次，每次间隔递增）
            for 尝试次数 in range(3):
                try:
                    if not 文件被占用(文件路径):
                        os.remove(文件路径)
                        print(f"已删除过期日志文件: {文件路径}")
                        break
                    else:
                        print(f"文件 {文件路径} 正在被占用，等待后重试")
                        time.sleep(尝试次数 + 1)
                except (PermissionError, OSError) as e:
                    print(f"删除文件 {文件路径} 失败，等待后重试：{e}")
                    time.sleep(尝试次数 + 1)  # 指数退避


def 文件被占用(文件路径):
    """检查文件是否被其他进程占用"""
    if not os.path.exists(文件路径):
        return False

    try:
        # 在Windows上，如果文件被占用，这将引发异常
        os.rename(文件路径, 文件路径)
        return False
    except (IOError, PermissionError, OSError):
        return True


def 记录日志(级别, 消息):
    """统一的日志记录接口"""
    logger = logging.getLogger('myLogger')
    有效级别 = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical
    }

    try:
        # 使用字典查找而不是getattr，更安全
        日志方法 = 有效级别.get(级别.lower(), logger.info)
        日志方法(消息)
    except Exception as e:
        # 如果记录日志本身出错，尝试使用基本方法记录
        try:
            print(f"记录日志时出错: {e}, 原始消息: {消息}")
        except:
            pass  # 如果连打印都失败，静默失败