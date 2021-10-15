# arweave-nft-uploader

``arweave-nft-uploader`` is a Python tool to improve the experience of uploading NFTs to the
Arweave storage for use with the Metaplex Candy Machine.

The tool has an additional (optional) feature to manage complex NFTs with multiple asset files
(e.g. a PNG and an SVG). See more about it in this [section](#complex-nfts-with-multiple-asset-files).

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

## Rebuilding the Candy Machine index

After the upload has completed successfully, you need to rebuild the Candy Machine index.

This time you have to run ``candy-machine-cli.ts upload`` from the full assets directory:
```bash
ts-node ~/metaplex-foundation/metaplex/js/packages/cli/src/candy-machine-cli.ts upload <full assets dir> -n <total number of NFTs> --keypair <Solana keypair file> --env <Solana cluster env name>
```
Don't worry, it will not reupload.
If you have done everything correctly, you will see something like this:


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

If this project provides you a smoother experience while uploading your NFT assets to Arweave, I will appreciate a small donation to my Arweave wallet :)
```
bxQ7fygEV2meOp_z_3TZyy-VWbSCuzYRWnIE0FANQZo
```
