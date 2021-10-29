# arweave-nft-uploader

``arweave-nft-uploader`` is a Python tool to improve the experience of uploading NFTs to the
Arweave storage for use with the Metaplex Candy Machine.

The tool has an additional (optional) feature to manage complex NFTs with multiple asset files
(e.g. a PNG and an SVG). See more about it in this [section](#complex-nfts-with-multiple-asset-files).

**This tool is for experienced users. I decline any responsibility for unneeded expenses caused by
the incorrect usage of this tool. Read this guide carefully before using it.**

## Prerequisites
* an Arweave wallet with enough tokens for the upload:
  * you can get a wallet here https://faucet.arweave.net/
  * you can buy Arweave tokens from exchanges
  * you can estimate your total upload cost to Arweave with this fee calculator: https://jcx2olqdzwgm.arweave.net/71giX-OY-3LwXtfr44B2dDyzW8mPHEAKA-q0wGT0aRM
* assets in the same directory structure as required by Metaplex (``0.json``, ``0.png``, ``1.json``, ``1.png``, ...)

## Installing
To install this tool run:
```bash
pip install -U git+https://github.com/0xEnrico/arweave-nft-uploader.git
```

## Creating the Metaplex Candy Machine

The Metaplex Candy Machine can be created in the standard way, with a few differences
in the command line and the asset folder, since we will manage the upload ourselves:
* Prepare a ``<single asset directory>`` which should contain only the first asset: ``0.json`` and ``0.png``.
Do **NOT** put other assets in that directory.
* Initialize the Candy Machine program with the addition of the ``-n`` switch that specifies
the total number of NFTs that will be uploaded, with a command line like this
(for other command line options please refer to the Metaplex Candy Machine documentation):
```bash
ts-node ~/metaplex-foundation/metaplex/js/packages/cli/src/candy-machine-cli.ts upload <single asset directory> -n <total number of NFTs> --keypair <Solana keypair file> --env <Solana cluster env name>
```

## Uploading assets to Arweave

From the same folder where you run ``candy-machine-cli.ts``, you can invoke this command
to start the upload from the ``<full assets dir>`` which should contain ALL assets to be uploaded:
```bash
arweave-nft -e <Solana env name> -k <Arweave wallet json file> <full assets dir>
```
e.g.:
```bash
arweave-nft -e mainnet-beta -k my_arweave_wallet.json /path/to/my/asset/dir
```

Invoke ``arweave-nft -h`` to get a full list of the available options:
```console
usage: arweave-nft [-h] [-e ENV] [-k KEYPAIR] [-v] [-c CACHE_NAME] [--force-upload] [--assets-from-json] directory

positional arguments:
  directory             Directory containing images named from 0-n

optional arguments:
  -h, --help            show this help message and exit
  -e ENV, --env ENV     Solana cluster env name (default: "devnet")
  -k KEYPAIR, --keypair KEYPAIR
                        Arweave wallet location (default: "--keypair not provided")
  -v, --verbose         increase output verbosity
  -c CACHE_NAME, --cache-name CACHE_NAME
                        Cache file name (default: "temp")
  --force-upload        Force upload all assets, even the ones that have already been uploaded
  --assets-from-json    If this flag is specified, assets file names are read from properties.files.uri/type (e.g. for
                        uploading both png and svg), instead of the default pair NNN.json/NNN.png
```

In case you get an error like this at the end, it could be caused by upload errors or
invalid asset structure in the json file:
```console
WARNING There have been 6 upload errors. Please review them and retry the upload with the same command
```

Please review the preceeding errors, fix the json files content if needed, then run
``arweave-nft`` again with the same command line to retry.

At the end, you should get this message, and you can proceed to the next section:

```console
INFO Upload complete! Now you can update the index with 'candy-machine-cli.ts upload' using the full assets directory (see documentation)
```

## Rebuilding the Candy Machine index

After the upload has completed successfully, you need to rebuild the Candy Machine index.

This time you have to run ``candy-machine-cli.ts upload`` using the ``<full assets directory>``:
```bash
ts-node ~/metaplex-foundation/metaplex/js/packages/cli/src/candy-machine-cli.ts upload <full assets directory> -n <total number of NFTs> --keypair <Solana keypair file> --env <Solana cluster env name>
```
:warning: **When you run this command, the command prompt MUST be in the same folder where you ran it previously to create the Candy Machine.** :warning:

Failure to do this will incur in unneeded expenses as you will recreate the Candy Machine and start upload assets
through the Candy Machine itself.

The only thing you need to change is the argument of the command from
``<single asset directory>`` to ``<full assets directory>``.

If you have done everything correctly at this point, it will not re-upload.

You will see a very quick ``Processing file`` log:
```console
Processing file: 0
Processing file: 50
Processing file: 100
...
Processing file: 850
Processing file: 900
Processing file: 950
```

Then a slower set of ``Writing indices`` lines:

```console
Writing indices 0-9
Writing indices 10-19
Writing indices 20-29
...
Writing indices 970-979
Writing indices 980-989
Writing indices 990-999
Done. Successful = true.
```

At this point the process is complete, and you can run ``candy-machine-cli.ts verify``:
```bash
ts-node ~/metaplex-foundation/metaplex/js/packages/cli/src/candy-machine-cli.ts verify --keypair <Solana keypair file> --env <Solana cluster env name>
```

If you have followed everything correctly, verify will succeed for all files, and your upload will be done!

## Complex NFTs with multiple asset files

You can upload complex NFTs with multiple asset files using the ``--assets-from-json`` option.

Your json files must contain a ``files`` section like the one below, where you specify the asset
files (in this example ``0.png`` and ``0.svg``, which must be in the same directory as the json file)
in the ``uri`` fields and the corresponding MIME type in the ``type`` fields:

```json
"properties": {
    "files": [
        {
            "uri": "0.png",
            "type": "image/png"
        },
        {
            "uri": "0.svg",
            "type": "image/svg+xml"
        }
    ],
...
```
``arweave-nft-uploader`` will manage the upload of all the referenced files and will create a correct json file
on the Arweave blockchain with all the links.

## Donations

If this project provides you a smoother experience while uploading your NFT assets to Arweave, I will appreciate a small donation :)
```
SOL: 3qdHbM9ZHFFn4M7E9GZBNdA6wi7idqgGHrXZ4xYgpu66
AR: bxQ7fygEV2meOp_z_3TZyy-VWbSCuzYRWnIE0FANQZo
```
