WORKDIR=$(pwd)
git clone https://github.com/wspr-ncsu/BLS-Witness-Encryption.git bls-witness-encryption
cd bls-witness-encryption && python setup.py install
cd $WORKDIR
rm -rf bls-witness-encryption
