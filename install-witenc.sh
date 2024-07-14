WORKDIR=$(pwd)
git clone https://github.com/kofi-dalvik/bls-witness-encryption.git
cd bls-witness-encryption && python setup.py install
cd $WORKDIR
rm -rf bls-witness-encryption