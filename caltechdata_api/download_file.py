import requests, argparse
from tqdm.auto import tqdm


def download_url(doi, media_type=None):
    """Get a download link for a file listed in the media API for a DataCite DOI"""
    api_url = "https://api.datacite.org/dois/" + doi + "/media"
    r = requests.get(api_url).json()
    data = r["data"]
    if media_type == None:
        url = data[0]["attributes"]["url"]
    else:
        for media in data:
            if media["attributes"]["mediaType"] == media_type:
                url = media["attributes"]
    return url


def download_file(doi, fname=None, media_type=None):
    """Download a file  listed in the media API for a DataCite DOI"""
    url = download_url(doi, media_type)
    r = requests.get(url, stream=True)
    # Set file name
    if fname == None:
        fname = doi.replace("/", "-")
    # Download file with progress bar
    if r.status_code == 403:
        print("File Unavailable")
    if "content-length" not in r.headers:
        print("Did not get file")
    else:
        with open(fname, "wb") as f:
            total_length = int(r.headers.get("content-length"))
            pbar = tqdm(total=int(total_length / 1024), unit="B")
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    pbar.update()
                    f.write(chunk)
        return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="download_file queries the DaiaCite Media API\
    and downloads the file associated with a DOI"
    )
    parser.add_argument(
        "dois",
        nargs="+",
        help="The DOI for files to be downloaded",
    )
    parser.add_argument(
        "-fname", default=None, help="File name to be used for downloaded file"
    )
    parser.add_argument(
        "-media_type", default=None, help="File (media) type to be downloaded"
    )

    args = parser.parse_args()

    for doi in args.dois:
        download_file(doi, args.fname, args.media_type)
