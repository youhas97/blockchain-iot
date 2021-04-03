from iroha import IrohaCrypto
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("ERROR: YOU NEED TO ENTER THE NAME OF THE KEYPAIR.")

    keyname = sys.argv[1]

    # these first two lines are enough to create the keys
    private_key = IrohaCrypto.private_key()
    public_key = IrohaCrypto.derive_public_key(private_key)

    # the rest of the code writes them into the file
    with open('{}.priv'.format(keyname), 'wb') as f:
        f.write(private_key)

    with open('{}.pub'.format(keyname), 'wb') as f:
        f.write(public_key)