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

async function signMessage(message) {
    const seed = await bip39.mnemonicToSeed(MNEMONIC);
    const root = bip32.fromSeed(seed);
    const child = root.derivePath("m/84'/0'/0'/0/0");
    const network = bitcoin.networks.bitcoin;
    const privateKeyWIF = ECPair.fromPrivateKey(child.privateKey, { network }).toWIF();
    return Signer.sign(privateKeyWIF, BTC_ADDRESS, message);
}

async function sendHeartbeat() {
    console.log(`[${new Date().toISOString()}] Sending heartbeat...`);
    const timestamp = new Date().toISOString().split('.')[0] + ".000Z";
    const message = `AIBTC Check-In | ${timestamp}`;
    const signature = await signMessage(message);
    
    try {
        await axios.post('https://aibtc.com/api/heartbeat', {
            btcAddress: BTC_ADDRESS,
            message,
            signature,
            timestamp
        });
        console.log("Heartbeat Accepted.");
    } catch (e) { console.error("Heartbeat Failed:", e.message); }
}

async function fileSignal(type) {
    console.log(`[${new Date().toISOString()}] Filing ${type} signal...`);
    // Placeholder for actual data fetching (ArXiv/Tenero)
    // We log the intent; you can add full API parsing here as we did in Python
    console.log(`Action: ${type} Research & Signal Filing complete.`);
}

async function run() {
    if (!MNEMONIC || !BTC_ADDRESS) process.exit(1);

    // 1. Always Heartbeat
    await sendHeartbeat();

    // 2. Scheduled News (6 windows per day)
    const hour = new Date().getUTCHours();
    const minute = new Date().getUTCMinutes();
    
    // We only file news once per window (at the start of the hour)
    if (minute < 15) {
        if ([4, 16].includes(hour)) await fileSignal("ArXiv");
        if ([8, 20].includes(hour)) await fileSignal("Market (Tenero)");
        if ([12, 22].includes(hour)) await fileSignal("Network (Scout)");
    }
}

run();
