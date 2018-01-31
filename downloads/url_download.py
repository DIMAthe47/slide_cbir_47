from ftplib import FTP
import os
import urllib.request as req


def copy_bytes(fp_read, fp_write, chunksize=8192):
    while True:
        chunk = fp_read.read(chunksize)
        if chunk:
            fp_write.write(chunk)
        else:
            break


def download_file(url, destination_path):
    with req.urlopen(url) as urldata, open(destination_path, 'wb') as f:
        copy_bytes(urldata, f)


def main():
    base_url = "http://openslide.cs.cmu.edu/download/openslide-testdata/Aperio"

    slide_names = [
        "CMU-1-JP2K-33005.svs",
        "CMU-1-Small-Region.svs",
        "CMU-1.svs",
        "CMU-2.svs",
        "CMU-3.svs",
        "JP2K-33003-1.svs",
        "JP2K-33003-2.svs",
    ]

    destination_dir = r"slides/Aperio"

    slide_urls = [base_url + "/" + slide_name for slide_name in slide_names]
    file_pathes = [os.path.join(destination_dir, slide_name) for slide_name in slide_names]
    for slide_url, file_path in zip(slide_urls, file_pathes):
        download_file(slide_url, file_path)


if __name__ == '__main__':
    main()
