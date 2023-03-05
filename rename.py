import os
import stat
import argparse

RS = '\033[0m'
R = '\033[91m'
G = '\033[92m'

IGNORED_FILENAME_LIST = [
    'rename.py',
    'readme.md',
    '.gitignore',
    '.git',
    'scripts',
    '.vscode',
    '.vs',
]

IGNORED_FILENAME_LIST = list(map(lambda x: x.upper(), IGNORED_FILENAME_LIST))


def indexing_files(
    inpath: str,
    outlog: list,
    filename=None,
):
    if filename is None:
        filename = os.path.split(os.path.abspath(inpath))[1]

    if filename.upper() in IGNORED_FILENAME_LIST:
        return

    file_stat = os.stat(inpath)
    outlog.append((inpath, filename, file_stat,))
    if stat.S_ISLNK(file_stat.st_mode):
        return

    if stat.S_ISDIR(file_stat.st_mode):
        child_filename_list = os.listdir(inpath)
        for child_filename in child_filename_list:
            child_filepath = os.path.join(inpath, child_filename)
            indexing_files(
                inpath=child_filepath,
                outlog=outlog,
                filename=child_filename,
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=str, nargs='?', default='.')
    parser.add_argument('-r', '--r', '-run', '--run', dest='run', action='store_true')


if __name__ == '__main__':
    main()
