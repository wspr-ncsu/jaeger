import argparse, json
from jager import groupsig, witenc, label_mgr

env = {}

def load_env():
    print('Loading keys from .env...')
    # if .env file does not exists, duplicate the .env.example file to .env
    try:
        with open('.env', 'r') as f:
            pass
    except FileNotFoundError:
        with open('.env.example', 'r') as f:
            with open('.env', 'w') as f2:
                f2.write(f.read())
                
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            
            data = line.split('=')
            env[data[0]] = data[1].strip() if len(data) > 1 else ''
            
def save_env():
    print('Saving keys to .env...')
    with open('.env', 'w') as f:
        for key, value in env.items():
            f.write(f'{key}={value}\n')

def generate_carrier_keys(msk, gpk, gml):
    keys = {}
    
    for carrier in range(7000):
        print(f'Generating keys for carrier-{carrier}...', end='\r')
        keys[str(carrier)] = groupsig.mgr_generate_member_keys(msk=msk, gpk=gpk, gml=gml)
    
    # write to membership-keys.json
    with open('membership-keys.json', 'w') as f:
        f.write(json.dumps(keys, indent=4))

def gm_keygen():
    print('Generating keys for Group Manager...')
    msk, gpk, gml = groupsig.setup()
    env['GM_MSK'], env['GM_GPK'], env['GM_GML'] = msk, gpk, gml
    generate_carrier_keys(msk, gpk, gml)
    
def lm_setup():
    print('Generating keys for Label Manager...')
    env['LM_SK'] = label_mgr.setup()

def ta_keygen():
    print('Generating keys for Traceback Authorizer...')
    privk, pubk = witenc.setup()
    env['TA_PRIVK'], env['TA_PUBK'] = privk, pubk

    
def main(args):
    load_env()
    
    if args.all or args.group_manager:
        gm_keygen()
    if args.all or args.label_manager:
        lm_setup()
    if args.all or args.traceback_authorizer:
        ta_keygen()
        
    save_env()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Key generation')
    parser.add_argument('-gm', '--group_manager', action='store_true', help='Generate keys for Group Manager', default=False, required=False)
    parser.add_argument('-lm', '--label_manager', action='store_true', help='Generate keys for Label Manager', default=False, required=False)
    parser.add_argument('-ta', '--traceback_authorizer', action='store_true', help='Generate keys for Traceback Authorizer', default=False, required=False)
    parser.add_argument('-a', '--all', action='store_true', help='Generate keys for GM, LM and TA', default=False, required=False)
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        main(args)