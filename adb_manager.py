import os
import subprocess
import sys
import urllib.request
import zipfile
from shutil import which

class ADBManager:
    """
    负责检查电脑环境和程序目录下是否有 adb，如果都没有，
    自动从谷歌下载并解压并删除下载的解压包并作为本地依赖使用。
    同时，在使用 adb 前自动执行 `adb connect 127.0.0.1:16384`。
    """
    def __init__(self, logger, adb_address):
        """
        初始化ADB管理器。

        :param logger: FormattedLogger实例，用于记录日志
        :param adb_address: ADB服务器地址，例如 "127.0.0.1:16384"
        """
        self.logger = logger
        self.platform = sys.platform
        self.adb_executable = self.get_adb_executable_name()
        self.adb_address = adb_address
        self.repo_dir = os.path.dirname(os.path.abspath(__file__))  # 假设在repo内
        self.adb_path = self.check_adb()

        if not self.adb_path:
            self.logger.log('INFO', 'ADBManager: __init__', "未找到ADB，开始下载ADB。")
            try:
                self.adb_path = self.download_and_setup_adb()
            except Exception as e:
                self.logger.log('CRITICAL', 'ADBManager: __init__', f"ADB下载和设置失败，程序将终止。原因: {e}")
                raise RuntimeError("ADB setup failed.") from e

            if self.adb_path:
                self.logger.log('INFO', 'ADBManager: __init__', f"ADB已设置在: {self.adb_path}")
        
        # 连接到指定的 ADB 地址
        self.connect_adb()

    def get_adb_executable_name(self):
        """根据操作系统获取adb可执行文件的名称。"""
        return 'adb.exe' if self.platform.startswith('win') else 'adb'

    def is_adb_in_path(self):
        """
        检查adb是否在系统的环境变量PATH中。

        :return: 如果adb在PATH中，返回adb命令的完整路径；否则，返回None
        """
        adb_cmd = which('adb')
        if adb_cmd:
            self.logger.log('DEBUG', 'ADBManager: is_adb_in_path', f"在PATH中找到ADB: {adb_cmd}")
        return adb_cmd

    def is_adb_in_local(self):
        """
        检查项目目录下是否存在adb。

        :return: 如果adb存在于本地，返回adb的完整路径；否则，返回None
        """
        local_adb = os.path.join(self.repo_dir, 'adb', 'platform-tools', self.adb_executable)
        if os.path.exists(local_adb):
            self.logger.log('DEBUG', 'ADBManager: is_adb_in_local', f"在本地找到ADB: {local_adb}")
            return local_adb
        return None

    def check_adb(self):
        adb_in_path = self.is_adb_in_path()
        if adb_in_path:
            return adb_in_path

        adb_in_local = self.is_adb_in_local()
        if adb_in_local:
            return adb_in_local

        return None

    def download_and_setup_adb(self):
        try:
            # 根据操作系统设置下载URL
            if self.platform.startswith('win'):
                download_url = 'https://dl.google.com/android/repository/platform-tools_r34.0.0-windows.zip'
            elif self.platform.startswith('darwin'):
                download_url = 'https://dl.google.com/android/repository/platform-tools_r34.0.0-darwin.zip'
            elif self.platform.startswith('linux'):
                download_url = 'https://dl.google.com/android/repository/platform-tools_r34.0.0-linux.zip'
            else:
                self.logger.log('CRITICAL', 'ADBManager: download_and_setup_adb', f"不支持的操作系统: {self.platform}")
                return None

            extract_dir = os.path.join(self.repo_dir, 'adb')
            zip_filename = 'platform-tools.zip'

            # 下载平台工具
            self.logger.log('INFO', 'ADBManager: download_and_setup_adb', f"开始下载ADB平台工具: {download_url}")
            urllib.request.urlretrieve(download_url, zip_filename)
            self.logger.log('INFO', 'ADBManager: download_and_setup_adb', f"下载完成: {zip_filename}")

            # 解压缩
            self.logger.log('INFO', 'ADBManager: download_and_setup_adb', f"开始解压缩: {zip_filename}")
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            self.logger.log('INFO', 'ADBManager: download_and_setup_adb', f"解压缩完成: {extract_dir}")

            # 删除压缩包
            os.remove(zip_filename)
            self.logger.log('DEBUG', 'ADBManager: download_and_setup_adb', f"已删除压缩包: {zip_filename}")

            # 返回本地adb路径，修正为platform-tools子目录
            local_adb = os.path.join(extract_dir, 'platform-tools', self.adb_executable)
            if os.path.exists(local_adb):
                self.logger.log('DEBUG', 'ADBManager: download_and_setup_adb', f"找到本地ADB: {local_adb}")
                return local_adb
            else:
                self.logger.log('ERROR', 'ADBManager: download_and_setup_adb', f"解压后的ADB未找到: {local_adb}")
                return None
        except Exception as e:
            self.logger.log('ERROR', 'ADBManager: download_and_setup_adb', f"下载或设置ADB时出错: {e}")
            return None

    def connect_adb(self):
        """
        执行 adb connect 命令连接到指定的 ADB 地址。
        """
        try:
            self.logger.log('INFO', 'ADBManager: connect_adb', f"尝试连接到 ADB 地址: {self.adb_address}")
            command = [self.adb_path, 'connect', self.adb_address]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            if result.returncode == 0:
                output = result.stdout.decode('utf-8').strip()
                self.logger.log('INFO', 'ADBManager: connect_adb', f"连接输出: {output}")
                if 'connected to' in output.lower():
                    self.logger.log('INFO', 'ADBManager: connect_adb', f"成功连接到 {self.adb_address}")
                elif 'already connected' in output.lower():
                    self.logger.log('INFO', 'ADBManager: connect_adb', f"已连接到 {self.adb_address}")
                else:
                    self.logger.log('WARNING', 'ADBManager: connect_adb', f"连接到 {self.adb_address} 可能不成功，输出: {output}")
            else:
                error_msg = result.stderr.decode('utf-8').strip()
                self.logger.log('ERROR', 'ADBManager: connect_adb', f"连接到 {self.adb_address} 失败: {error_msg}")
        except subprocess.TimeoutExpired:
            self.logger.log('ERROR', 'ADBManager: connect_adb', f"连接到 {self.adb_address} 超时。")
        except Exception as e:
            self.logger.log('ERROR', 'ADBManager: connect_adb', f"连接到 {self.adb_address} 时出错: {e}")

    def get_adb_command(self):
        """
        获取adb命令列表。

        :return: adb命令列表，例如 ['C:\\path\\to\\adb.exe']
        """
        if self.adb_path:
            return [os.path.abspath(self.adb_path)]
        else:
            return ['adb']  # 默认使用系统adb
