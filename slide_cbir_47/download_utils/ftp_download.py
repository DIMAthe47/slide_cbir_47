from ftplib import FTP
import os


def get_filenames(host, dir):
    with FTP(host, timeout=10 * 60 * 60) as ftp:
        ftp.login()
        ftp.cwd(dir)
        filenames = ftp.nlst()
        return filenames


def download_file(host, dir, filename, destination_dir):
    """
    ftp reopening is intended to avoid timeout
    :return:
    """
    filepath = os.path.join(destination_dir, filename)
    if not os.path.isfile(filepath):
        with FTP(host) as ftp:
            ftp.login()
            ftp.set_debuglevel(2)
            ftp.cwd(dir)
            with open(filepath, 'wb') as fp:
                ftp.retrbinary('RETR {}'.format(filename), fp.write, blocksize=2 ** 16)


def main():
    destination_dir = r"C:\Users\DIMA\PycharmProjects\slide_cbir_47\temp\slides\hydroxyzine\Kidney"
    host = 'ftp.biosciencedbc.jp'
    ftp_dir = "archive/open-tggates-pathological-images/LATEST/images/hydroxyzine/Kidney"
    filenames = get_filenames(host, ftp_dir)
    for filename in filenames:
        download_file(host, ftp_dir, filename, destination_dir)


if __name__ == '__main__':
    main()
