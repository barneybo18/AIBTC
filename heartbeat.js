const axios = require('axios');
const bitcoin = require('bitcoinjs-lib');
const bip39 = require('bip39');
const { BIP32Factory } = require('bip32');
const { ECPairFactory } = require('ecpair');
const ecc = require('tiny-secp256k1');
const { Signer } = require('bip322-js');

const bip32 = BIP32Factory(ecc);
const ECPair = ECPairFactory(ecc);

const BTC_ADDRESS = process.env.BTC_ADDRESS;
const MNEMONIC = process.env.MNEMONIC;

async function run() {
    if (!MNEMONIC || !BTC_ADDRESS) {
        console.error("Missing Secrets (MNEMONIC or BTC_ADDRESS)!");
        process.exit(1);
    }

    const timestamp = new Date().toISOString().split('.')[0] + ".000Z";
    const message = `AIBTC Check-In | ${timestamp}`;
    
    console.log(`[${new Date().toISOString()}] Preparing heartbeat for ${BTC_ADDRESS}...`);

    try {
        // 1. Derive Private Key from Mnemonic (BIP-84 path for bc1q)
        const seed = await bip39.mnemonicToSeed(MNEMONIC);
        const root = bip32.fromSeed(seed);
        
        // Use m/84'/0'/0'/0/0 for native SegWit (bc1q)
        const child = root.derivePath("m/84'/0'/0'/0/0");
        
        // Convert to WIF (Wallet Import Format) which bip322-js expects
        const network = bitcoin.networks.bitcoin;
        const privateKeyWIF = ECPair.fromPrivateKey(child.privateKey, { network }).toWIF();

        // 2. Generate BIP-322 Signature (Version 3 API)
        const signature = Signer.sign(privateKeyWIF, BTC_ADDRESS, message);

        console.log(`Generated BIP-322 signature for message: "${message}"`);

        const payload = {
            btcAddress: BTC_ADDRESS,
            message: message,
            signature: signature,
            timestamp: timestamp
        };

        // 3. POST to AIBTC Heartbeat
        const response = await axios.post('https://aibtc.com/api/heartbeat', payload, {
            headers: { 'User-Agent': 'AIBTC-Agent-Automation/1.0' }
        });

        console.log(`Server Success: ${response.status} - ${JSON.stringify(response.data)}`);
    } catch (error) {
        if (error.response) {
            console.error(`Server Error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
        } else {
            console.error(`Execution Error: ${error.message}`);
        }
        process.exit(1);
    }
}

run();
