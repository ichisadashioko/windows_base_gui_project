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
    'x64',
]

IGNORED_EXTS = [
    '.bomb',
    '.map',
    # Microsoft Excel files
    '.xls',
    # known binary extensions
    '.dll',
    '.jpg',
    '.gif',
    '.png',
    '.jpeg',
    '.jar',
    '.jad',
    '.iso',
    '.mds',
    '.dat',
    # weird files from Visual Studio
    '.suo',
    '.exe',
    '.pdb',
    '.ilk',
    '.i64',
    '.idb',
    # Microsoft Windows files
    '.ini',
    # opencore binaries
    '.aml',
    '.bin',
    '.ico',
    '.woff',
    '.woff2',
    '.obj',
    '.bmp',
    '.ppm',
    #
    '.raw',
    '.pdf',
    '.chm',  # zlib class library documentation
    '.pk',  # zlib blast
    '.user',
]

IGNORED_FILENAME_LIST = list(map(lambda x: x.upper(), IGNORED_FILENAME_LIST))
IGNORED_EXTS = list(map(lambda x: x.upper(), IGNORED_EXTS))


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


def check_for_utf8_bom(bs: bytes):
    if len(bs) < 3:
        return False

    if (bs[0] == 0xEF) and (bs[1] == 0xBB) and (bs[2] == 0xBF):
        return True

    return False


def decode_text_content(bs: bytes):
    if check_for_utf8_bom(bs):
        try:
            encoding = 'utf-8-sig'
            decoded_content = bs.decode(encoding)
            return encoding, decoded_content
        except Exception as ex:
            # traceback.print_exc()
            pass

    try:
        encoding = 'utf-8'
        decoded_content = bs.decode(encoding)
        return encoding, decoded_content
    except Exception as ex:
        # traceback.print_exc()
        pass

    try:
        encoding = 'utf-16'
        decoded_content = bs.decode(encoding)
        return encoding, decoded_content
    except Exception as ex:
        # traceback.print_exc()
        pass

    try:
        encoding = 'gb2312'
        decoded_content = bs.decode(encoding)
        return encoding, decoded_content
    except Exception as ex:
        # traceback.print_exc()
        pass

    try:
        encoding = 'shift-jis'
        decoded_content = bs.decode(encoding)
        return encoding, decoded_content
    except Exception as ex:
        # traceback.print_exc()
        pass

    return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('newname', type=str)
    parser.add_argument('oldname', type=str, nargs='?', default='windows_base_gui_project')
    parser.add_argument('infile', type=str, nargs='?', default='.')
    parser.add_argument('-r', '--r', '-run', '--run', dest='run', action='store_true')

    args = parser.parse_args()
    print(f'args {G}{args}{RS}')

    newname = args.newname
    oldname = args.oldname
    inpath = args.infile
    is_run = args.run

    file_info_list = []
    indexing_files(
        inpath=inpath,
        outlog=file_info_list,
    )

    print(f'len(file_info_list) {G}{len(file_info_list)}{RS}')

    replace_text_content_task_list = []
    rename_filename_task_list = []
    for filepath, filename, file_stat in file_info_list:
        if os.path.abspath(os.getcwd()).upper() == os.path.abspath(filepath).upper():
            continue

        if oldname in filename:
            new_filename = filename.replace(oldname, newname)
            rename_filename_task_list.append((filepath, filename, new_filename,))

        if stat.S_ISREG(file_stat.st_mode):
            ext = os.path.splitext(filename)[1].upper()
            if ext not in IGNORED_EXTS:
                replace_text_content_task_list.append(filepath)

    print(f'{G}len(replace_text_content_task_list){RS} {R}{len(replace_text_content_task_list)}{RS}')
    print(f'{G}len(rename_filename_task_list){RS} {R}{len(rename_filename_task_list)}{RS}')

    for i, filepath in enumerate(replace_text_content_task_list):
        print(f'{i} {G}{filepath}{RS}', end='')
        original_content_bs = open(filepath, 'rb').read()
        if len(original_content_bs) == 0:
            print(f' {R}empty{RS}')
            continue

        encoding, decoded_content = decode_text_content(original_content_bs)
        if decoded_content is None:
            print(f' {R}decode failed{RS}')
            continue

        print(f' {R}{encoding}{RS}', end='')

        if oldname in decoded_content:
            print(f' {R}X{RS}', end='')
            if is_run:
                new_content = decoded_content.replace(oldname, newname)
                open(filepath, 'wb').write(new_content.encode('utf-8'))
                print(f' -> {G}OK{RS}')
            else:
                print('')
        else:
            print(' no match')

    for i, task in enumerate(rename_filename_task_list):
        filepath, filename, new_filename = task
        print(f'{i} {G}{filepath}{RS} {R}{filename}{RS} {G}{new_filename}{RS}')

    rename_filename_task_list.reverse()
    for i, task in enumerate(rename_filename_task_list):
        filepath, filename, new_filename = task
        new_filepath = os.path.join(
            os.path.split(filepath)[0],
            new_filename,
        )

        print(f'{i} {G}{filepath}{RS} {R}{filename}{RS} {G}{new_filepath}{RS}')
        if is_run:
            os.rename(filepath, new_filepath)


if __name__ == '__main__':
    main()
