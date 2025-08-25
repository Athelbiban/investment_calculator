import os
import platform
from passwd.directories import MyDirectory


def get_directory():

    system = platform.system()

    if system == 'Linux':
        directory = MyDirectory.LINUX1
    elif system == 'Windows':
        dir1 = MyDirectory.WINDOWS1
        dir2 = MyDirectory.WINDOWS2

        if os.path.isdir(dir1):
            directory = dir1
        elif os.path.isdir(dir2):
            directory = dir2
        else:
            raise Exception('Директория отсутствует')

    else:
        raise Exception('Пока не умею работать с данной ОС: ' + system)

    return directory


if __name__ == '__main__':
    get_directory()
