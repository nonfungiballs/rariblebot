with open('private_keys.txt', 'r') as file:
    WALLETS = [row.strip() for row in file]