"""Functions to download files directly from a CaltechData record.

A CaltechData record ID is the ten characters, separated into two groups
of five by a dash, found at the end of a CaltechData URL or default DOI.
For instance, in the URL ``https://data.caltech.edu/records/4rgh7-zss31``
or DOI ``10.22002/4rgh7-zss31``, the record ID is ``4rgh7-zss31``.

The same functions can download from CaltechAUTHORS by passing
``authors=True``, and from the test (development) instances of either
repository by passing ``production=False``.
"""
import argparse
import os
import requests
from tqdm.auto import tqdm

from typing import Any, Dict, Optional, Sequence


def get_base_url(production: bool = True, authors: bool = False) -> str:
    """Get the base URL of the repository to download from.

    Parameters
    ----------
    production
        Whether to use the production repository. If ``False``, the
        test (development) instance is used instead.

    authors
        Whether to use CaltechAUTHORS instead of CaltechDATA.

    Returns
    -------
    str
        The base URL, without a trailing slash.
    """
    if production:
        if authors:
            return 'https://authors.library.caltech.edu'
        return 'https://data.caltech.edu'
    else:
        if authors:
            return 'https://authors.caltechlibrary.dev'
        return 'https://data.caltechlibrary.dev'


def get_files_from_record(
    record_id: str, production: bool = True, authors: bool = False
) -> Dict[str, Any]:
    """Get a dictionary of files associated with a record.

    Parameters
    ----------
    record_id
        The record ID for which to obtain the list of files. See
        the module documentation for how to find the record ID.

    production
        Whether to query the production repository. If ``False``, the
        test (development) instance is used instead.

    authors
        Whether to query CaltechAUTHORS instead of CaltechDATA.

    Returns
    -------
    dict
        A dictionary with the file names as keys and the metadata
        associated with those files as values.
    """
    base_url = get_base_url(production=production, authors=authors)
    with requests.get(f'{base_url}/api/records/{record_id}/files') as r:
        r.raise_for_status()
        files = dict()
        for entry in r.json().get('entries', []):
            key = entry.pop('key')
            files[key] = entry

        return files


def download_files_from_record(
    record_id: str, output_path: os.PathLike,
    filenames: Optional[Sequence[str]] = None,
    max_redirects: int = 5,
    production: bool = True,
    authors: bool = False
):
    """Download one or more files from a record.

    Parameters
    ----------
    record_id
        The record ID from which to download the file. See
        the module documentation for how to find the record ID.

    output_path
        Where to download the files. Must be an existing directory.
        If you want control over exactly how each file is named,
        use :func:`get_files_from_record` to get the URLs for each
        file, then manually call :func:`download_content` for each
        file you wish to download.

    filenames
        The name of the files in the record. Must match exactly.
        If you are not sure of the filenames in the record,
        they are the keys of the dictionary returned by
        :func:`get_files_from_record`. If omitted, all files
        are downloaded.

    max_redirects
        If the record's link to the file content returns a
        redirection to another location, this function will follow
        that redirection. This parameter sets the maximum number of
        hops that the function can take. Usually, only a single
        redirection should be necessary (from the record to the file
        provider), but the default allows for a few extra hops.

    production
        Whether to download from the production repository. If ``False``,
        the test (development) instance is used instead.

    authors
        Whether to download from CaltechAUTHORS instead of CaltechDATA.
    """
    if not os.path.isdir(output_path):
        raise IOError(f'{output_path} is not an extant directory')

    files = get_files_from_record(
        record_id, production=production, authors=authors)
    if filenames is None:
        filenames = sorted(files.keys())

    for filename in filenames:
        output_file = os.path.join(output_path, filename)
        if filename not in files:
            raise KeyError(
                f'File "{filename}" not found in record {record_id}')

        entry = files[filename]
        if 'links' not in entry or 'content' not in entry['links']:
            raise NotImplementedError(
                f'Metadata for file "{filename}" in record {record_id} is '
                'missing the content link'
            )

        content_url = entry['links']['content']
        download_content(content_url, output_file, max_redirects=max_redirects)


def download_content(content_url: str, fname: os.PathLike, max_redirects=5):
    """Download the contents of a file.

    Parameters
    ----------
    content_url
        The URL pointing to the contents of the file. In the dictionary
        returned by :func:`get_files_from_record` (call it ``D``), this
        is usually the value at ``D[FILENAME]["links"]["content"]``.

    fname
        The path to which to save the file contents. Will be overwritten!


    max_redirects
        If the ``content_url`` returns a redirection to another location,
        this function will follow that redirection. This parameter sets
        the maximum number of hops that the function can take. Usually,
        only a single redirection should be necessary (from the record to
        the file provider), but the default allows for a few extra hops.
    """
    url = content_url
    # If max_redirects == 0, then this loop will never run. Since the
    # likely expected behavior for ``max_redirects = 0`` is to only
    # look at the link directly given back by the record, we add 1
    # for the loop to ensure it runs once in that case.
    for _ in range(max_redirects+1):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            if 'Location' in r.headers:
                # Redirection - follow to the next URL
                url = r.headers['Location']
            else:
                with open(fname, 'wb') as f:
                    content_length = r.headers.get('content-length', None)
                    if content_length is not None:
                        content_length = int(content_length)
                    pbar = tqdm(total=content_length // 1024, unit='kB')
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            pbar.update()
                            f.write(chunk)
                    print(f'Download to {fname} complete.')
                    return
    raise RuntimeError(
        f'Exceeded maximum number of redirects ({max_redirects})'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='download_from_record downloads the files attached to a '
        'CaltechDATA or CaltechAUTHORS record'
    )
    parser.add_argument(
        'record_id',
        help='The record ID for the record to download files from'
    )
    parser.add_argument(
        'filenames',
        nargs='*',
        default=None,
        help='The names of the files to download. If omitted, all files in '
        'the record are downloaded.'
    )
    parser.add_argument(
        '-output_path', default='.',
        help='Existing directory to download the files into'
    )
    parser.add_argument(
        '-max_redirects', type=int, default=5,
        help='Maximum number of redirects to follow per file'
    )
    parser.add_argument('-test', dest='production', action='store_false')
    parser.add_argument('-authors', dest='authors', action='store_true')

    args = parser.parse_args()

    download_files_from_record(
        args.record_id,
        args.output_path,
        filenames=args.filenames or None,
        max_redirects=args.max_redirects,
        production=args.production,
        authors=args.authors,
    )
