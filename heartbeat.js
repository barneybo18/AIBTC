const axios = require('axios');
const bitcoin = require('bitcoinjs-lib');
const bip39 = require('bip39');
const { BIP32Factory } = require('bip32');
const ecc = require('tiny-secp256k1');
const { Signer } = require('bip322-js');

const bip32 = BIP32Factory(ecc);

const BTC_ADDRESS = process.env.BTC_ADDRESS;
const MNEMONIC = process.env.MNEMONIC;

async function run() {
    if (!MNEMONIC || !BTC_ADDRESS) {
        console.error("Missing Secrets!");
        process.exit(1);
    }

    const timestamp = new Date().toISOString().split('.')[0] + ".000Z";
    const message = `AIBTC Check-In | ${timestamp}`;
    
    console.log(`Signing message for ${BTC_ADDRESS}: ${message}`);

    // Derive Private Key from Mnemonic (BIP-84 path for bc1q)
    const seed = await bip39.mnemonicToSeed(MNEMONIC);
    const root = bip32.fromSeed(seed);
    const child = root.derivePath("m/84'/0'/0'/0/0");
    const privateKey = child.privateKey;

    // Generate BIP-322 Simple Signature
    const signature = Signer.sign(privateKey.toString('hex'), BTC_ADDRESS, message);

    const payload = {
        btcAddress: BTC_ADDRESS,
        message: message,
        signature: signature,
        timestamp: timestamp
    };

    try {
        const response = await axios.post('https://aibtc.com/api/heartbeat', payload);
        console.log(`Server Success: ${response.status} - ${JSON.stringify(response.data)}`);
    } catch (error) {
        console.error(`Server Error: ${error.response ? JSON.stringify(error.response.data) : error.message}`);
        process.exit(1);
    }
}

run();
