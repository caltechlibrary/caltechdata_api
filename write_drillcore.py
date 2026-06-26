import argparse, os, json
import s3fs
from caltechdata_api import caltechdata_write

# Get access token as environment variable
token = os.environ["RDMTOK"]

metaf = open("h790j-6ar55.json", "r")
metadata = json.load(metaf)

drill_holes = ["BA1B", "BA3A", "BA4A"]
methods = ["VNIR", "SWIR"]

endpoint = "https://caltech2.osn.mghpcc.org"
s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})

for hole in drill_holes:
    for method in methods:
        metadata["metadata"]["title"] = (
            f"Hole {hole} - {method} Imaging spectroscopy of the Oman Drilling Project mantle"
        )
        if method == "VNIR":
            image = "visible and near-infrared (VNIR)"
        if method == "SWIR":
            image = "shortwave infrared (SWIR)"
        metadata["metadata"]["description"] = f"""This record contains {image} data of the
        archive halves of the borehole {hole} core recovered by the Integrated 
        International Continental Scientific Drilling Project  (ICDP) Oman Drilling Project (OmanDP; Kelemen et al., 2020).

        For additional details, see the full record for this project at
        https://doi.org/10.22002/h790j-6ar55. Please cite this DOI is you use
        this dataset.

        Available data are data cubes as described in Kelemen et al. (2020) processed 
        to reflectance (Mandon et al., 2026, JGR: Solid Earth). Data are paired
        .img and .hdr files."""

        files = s3.ls(f"caltechdata-public/h790j-6ar55/{hole}/{method}")
        file_links = [f"{endpoint}/{f}" for f in files]

        production = True
        publish = False

        response = caltechdata_write(
            metadata,
            token,
            production=production,
            publish=publish,
            file_links=file_links,
        )
        print(response)
