
import argparse
import json
import logging
import arweave
import os
import sys
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', default='devnet', help='Solana cluster env name (default: "devnet")')
    parser.add_argument('-k', '--keypair', help='Arweave wallet location (default: "--keypair not provided")')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase output verbosity')
    parser.add_argument('-c', '--cache-name', default='temp', help='Cache file name (default: "temp")')
    parser.add_argument('--assets-from-json', action='store_true', help='If this flag is specified, assets file names are read from properties/files/uri (e.g. for uploading both png and svg), instead of the default pair nnn.json/nnn.png')
    parser.add_argument('directory', help='Directory containing images named from 0-n')
    args = parser.parse_args()
    levels = [logging.INFO, logging.DEBUG]
    level = levels[min(len(levels)-1,args.verbose)]  # capped to number of levels
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")

    # Load cache file
    CACHE_PATH = '.cache'
    filename = os.path.join(CACHE_PATH, args.env + "-" + args.cache_name)
    try:
        with open(filename, 'r') as f:
            cache_data = json.load(f)
    except Exception as ex:
        logging.error(ex)
        logging.error("Can't load cache file " + filename)
        sys.exit()

    # Enumerate assets
    jsonfiles = glob.glob(os.path.join(args.directory, "*.json"))
    logging.info("Starting the upload for {} assets".format(len(jsonfiles)))
    for jsonfile in jsonfiles:
        # Load json file
        try:
            with open(jsonfile, 'r') as f:
                asset_data = json.load(f)
        except Exception as ex:
            logging.error(ex)
            logging.error("Can't load json file " + jsonfile)
        
        # Locate asset files
        asset_files = []
        try:
            if args.assets_from_json:
                for files in asset_data["properties"]["files"]:
                        assetname = os.path.join(args.directory, files["uri"])
                        if os.path.isfile(assetname):
                            asset_files.append(assetname)
                        else:
                            raise Exception("Can't find asset file " + assetname)
            else:
                assetname = jsonfile.replace(".json", ".png")
                if os.path.isfile(assetname):
                    asset_files = [assetname]
                else:
                    raise Exception("Can't find asset file " + assetname)
        except Exception as ex:
            logging.error(ex)
            logging.error("Can't find all assets for json file " + jsonfile + ", skipping")
            continue
