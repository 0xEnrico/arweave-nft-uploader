from distutils.core import setup

setup(
  name="arweave-nft-uploader",
  packages = ['arweave_nft_uploader'],
  version="0.0.1",
  description="Client interface for sending NFTs to the Arweave permaweb",
  author="0xEnrico",
  author_email="0xEnrico@gmail.com",
  url="https://github.com/0xEnrico/arweave-nft-uploader",
  download_url="https://github.com/0xEnrico/arweave-nft-uploader",
  keywords=['arweave', 'crypto'],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  install_requires=[
    'arweave-python-client>=1.0.15.dev0'
  ],
  entry_points={
      'console_scripts': [
          'arweave-nft=arweave_nft_uploader:main',
      ],
  },
)
