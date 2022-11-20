import os
import platform
import subprocess
import sys

VERSION_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__), 'version.py'))


class Version:
    @staticmethod
    def generate():
        with subprocess.Popen(["git", "describe", "--always", "--tags"],
                              stdout=subprocess.PIPE,
                              stderr=None) as process:
            last_tag = process.communicate()[0].decode('ascii').strip()
            version = last_tag.split('-g', maxsplit=1)[0].replace('-', '.') if '-g' in last_tag else last_tag
            with open(VERSION_FILENAME, 'w',encoding='utf-8') as file:
                file.write(f'SUNSYNK_API_CLIENT_VERSION = "{version}"\n')
            return version

    @staticmethod
    def get(retry=True):
        try:
            # pylint: disable=C0415
            from sunsynk.version import SUNSYNK_API_CLIENT_VERSION
            return SUNSYNK_API_CLIENT_VERSION
        except ModuleNotFoundError:
            if retry:
                Version.generate()
                return Version.get(False)
            return 'unknown'
        except ImportError:
            if retry:
                Version.generate()
                return Version.get(False)
            return 'unknown'

    @staticmethod
    def get_env_info():
        os_info = f"Release: {platform.release()}, Platform: {platform.platform()}"
        return f"(Python: {platform.python_version()}), OS: ({os_info}). Default Encoding: {sys.getdefaultencoding()}"
