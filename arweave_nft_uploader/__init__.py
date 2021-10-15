import argparse
import json
import logging
from arweave import Wallet, Transaction
from arweave.transaction_uploader import get_uploader
import os
import sys
import glob


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', default='devnet', help='Solana cluster env name (default: "devnet")')
    parser.add_argument('-k', '--keypair', help='Arweave wallet location (default: "--keypair not provided")')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase output verbosity')
    parser.add_argument('-c', '--cache-name', default='temp', help='Cache file name (default: "temp")')
    parser.add_argument('--force-upload', action='store_true',
                        help='Force upload all assets, even the ones that have already been uploaded')
    parser.add_argument('--assets-from-json', action='store_true',
                        help='If this flag is specified, assets file names are read from properties.files.uri/type'
                             ' (e.g. for uploading both png and svg), instead of the default pair NNN.json/NNN.png')
    parser.add_argument('directory', help='Directory containing images named from 0-n')
    args = parser.parse_args()
    levels = [logging.INFO, logging.DEBUG]
    level = levels[min(len(levels) - 1, args.verbose)]  # capped to number of levels
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")

    # Enumerate assets
    try:
        jsonfiles_raw = glob.glob(os.path.join(args.directory, "*.json"))
        jsonfiles = []
        for jsonfile in jsonfiles_raw:
            # Filename without extension is the cache item
            cache_item, tmp = os.path.splitext(os.path.basename(jsonfile))
            if cache_item.isdigit():
                jsonfiles.append(jsonfile)
            else:
                logging.warning("Json file: " + str(jsonfile) + " is not in the format <number>.json, skipping")
    except Exception as ex:
        logging.error(ex)
        logging.error("Can't enumerate assets in directory: " + str(args.directory))
        sys.exit(1)

    # Load cache file
    cache_filename = ""
    try:
        cache_filename = os.path.join('.cache', args.env + "-" + args.cache_name)
        with open(cache_filename, 'r') as f:
            cache_data = json.load(f)
    except Exception as ex:
        cache_data = {}
    if "program" not in cache_data or "items" not in cache_data or "0" not in cache_data["items"]:
        logging.error("")
        logging.error("Cache file " + str(cache_filename) + " is not initialized with a candy machine program")
        logging.error("")
        logging.error("You must initialize the candy machine program with a single 0.json and 0.png file,")
        logging.error("specifying the total number of NFTs with the -n option, like this:")
        logging.error("")
        logging.error("ts-node ~/metaplex-foundation/metaplex/js/packages/cli/src/candy-machine-cli.ts"
                      " upload <single asset dir> -n {} --keypair <keypair file> --env <env name>".format(
            len(jsonfiles)))
        logging.error("")
        logging.error("*** It is VERY important that <single asset dir> ONLY contains 0.json and 0.png ***")
        logging.error("*** to avoid uploading all the assets with candy-machine-cli.ts                 ***")
        sys.exit(1)

    # Load arweave wallet
    try:
        wallet = Wallet(args.keypair)
        logging.info("Initial Arweave wallet balance: {}".format(wallet.balance))
    except Exception as ex:
        logging.error(ex)
        logging.error("Can't load Arweave wallet: " + str(args.keypair))
        sys.exit(1)

    # Upload assets
    num_upload_errors = 0
    logging.info("Starting the upload for {} assets".format(len(jsonfiles)))
    for idx, jsonfile in enumerate(jsonfiles):
        # Filename without extension is the cache item
        cache_item, tmp = os.path.splitext(os.path.basename(jsonfile))
        if not cache_item.isdigit():
            logging.warning("Json file: " + str(jsonfile) + " is not in the format <number>.json, skipping")
            continue

        # Check if the asset is already in cache and already uploaded, unless --force-upload flag is specified
        if not args.force_upload:
            if cache_item in cache_data["items"] and "uploadedToArweave" in cache_data["items"][cache_item] \
                    and cache_data["items"][cache_item]["uploadedToArweave"]:
                logging.debug("Skipping already uploaded file: " + str(jsonfile))
                continue

        # Load json file
        msg = "Processing file: {}".format(idx)
        if idx % 50 == 0:
            logging.info(msg)
        else:
            logging.debug(msg)
        try:
            with open(jsonfile, 'r') as f:
                asset_data = json.load(f)
        except Exception as ex:
            logging.error(ex)
            logging.error("Can't load json file: " + str(jsonfile)) + ", skipping"
            num_upload_errors += 1
            continue

        # Get asset name
        try:
            asset_name = asset_data["name"]
        except Exception as ex:
            logging.error(ex)
            logging.error("Json file: " + str(jsonfile)) + " has no name, skipping"
            num_upload_errors += 1
            continue

        # Locate asset files
        asset_files = []
        try:
            if args.assets_from_json:
                files = asset_data["properties"]["files"]
                for idx2, tmp in enumerate(asset_data["properties"]["files"]):
                    asset_file = os.path.join(args.directory, files[idx2]["uri"])
                    if os.path.isfile(asset_file):
                        asset_files.append({"file": asset_file, "type": files[idx2]["type"], "idx": idx2})
                    else:
                        raise Exception("Can't find asset file: " + str(asset_file))
            else:
                asset_file = jsonfile.replace(".json", ".png")
                if os.path.isfile(asset_file):
                    asset_files = [{"file": asset_file, "type": "image/png", "idx": 0}]
                else:
                    raise Exception("Can't find asset file: " + str(asset_file))
                asset_data["properties"]["files"] = [{"uri": "", "type": "image/png"}]
        except Exception as ex:
            logging.error(ex)
            logging.error("Can't find all assets for json file: " + str(jsonfile) + ", skipping")
            num_upload_errors += 1
            continue

        try:
            # Upload asset files
            has_asset_image = False
            for asset in asset_files:
                asset_filename, asset_fileext = os.path.splitext(asset["file"])
                asset_fileext = asset_fileext.lstrip(".")
                with open(asset["file"], 'rb', buffering=0) as file_handler:
                    tx = Transaction(wallet, file_handler=file_handler, file_path=asset["file"])
                    tx.add_tag('Content-Type', asset["type"])
                    tx.sign()
                    uploader = get_uploader(tx, file_handler)
                    while not uploader.is_complete:
                        uploader.upload_chunk()
                    txdict = tx.to_dict()
                    uri = "https://arweave.net/{}?ext={}".format(txdict["id"], asset_fileext)
                    asset_data["properties"]["files"][asset["idx"]]["uri"] = uri
                    if not has_asset_image and asset_fileext == "png":
                        has_asset_image = True
                        asset_data["image"] = uri
            if not has_asset_image:
                logging.error(ex)
                logging.error("At least one png image is required for json file: " + str(jsonfile) + ", skipping")
                num_upload_errors += 1
                continue

            # Upload metadata
            tx = Transaction(wallet, data=json.dumps(asset_data))
            tx.add_tag('Content-Type', "application/json")
            tx.sign()
            tx.send()
            txdict = tx.to_dict()
            uri = "https://arweave.net/{}".format(txdict["id"])
            cache_data["items"][cache_item] = {"link": uri,
                                               "name": asset_name,
                                               "onChain": False,
                                               "uploadedToArweave": True}
            with open(cache_filename, 'w') as f:
                json.dump(cache_data, f)
        except Exception as ex:
            logging.error(ex)
            logging.error("Can't upload assets for json file: " + str(jsonfile) + ", skipping")
            num_upload_errors += 1
            continue

    logging.info("")
    logging.info("Ending Arweave wallet balance: {}".format(wallet.balance))
    if num_upload_errors > 0:
        logging.warning("There have been {} upload errors. "
                     "Please review them and retry the upload with the same command".format(num_upload_errors))
    else:
        logging.info("Upload complete! Now you can update the index with 'candy-machine-cli.ts upload'"
                     " using the full assets directory (see documentation)")
