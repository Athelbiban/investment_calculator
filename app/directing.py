import os
import platform
from passwd.directories import LINUX1, WINDOWS1, WINDOWS2


def get_directory():

    system = platform.system()

    if system == 'Linux':
        directory = LINUX1
    elif system == 'Windows':
        dir1 = WINDOWS1
        dir2 = WINDOWS2

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
