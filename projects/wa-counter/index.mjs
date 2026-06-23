import { makeWASocket, useMultiFileAuthState, DisconnectReason, Browsers } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import { createInterface } from 'readline';
import pino from 'pino';

async function askPhone() {
    return new Promise(resolve => {
        const rl = createInterface({ input: process.stdin, output: process.stdout });
        rl.question('הכנס מספר טלפון: ', answer => {
            rl.close();
            resolve(answer.trim());
        });
    });
}

const logger = pino({ level: 'silent' });
const { state, saveCreds } = await useMultiFileAuthState('./auth');
const needsPairing = !state.creds.registered;
const phone = needsPairing ? await askPhone() : null;

let codeShown = false;

const sock = makeWASocket({
    auth: state,
    logger,
    printQRInTerminal: false,
    browser: Browsers.macOS('Chrome'),
    defaultQueryTimeoutMs: undefined,
});

sock.ev.on('creds.update', saveCreds);

sock.ev.on('connection.update', async ({ connection, lastDisconnect }) => {
    if (connection === 'connecting' && needsPairing && !codeShown) {
        codeShown = true;
        setTimeout(async () => {
            try {
                const code = await sock.requestPairingCode(phone);
                console.log('\n══════════════════════════════');
                console.log(`  קוד: ${code}`);
                console.log('══════════════════════════════');
                console.log('WhatsApp ← Linked Devices ← Link a Device ← Link with phone number');
                console.log('יש לך ~60 שניות להכניס את הקוד\n');
            } catch (e) {
                console.error('שגיאה:', e.message);
            }
        }, 1000);
    }

    if (connection === 'open') {
        console.log('מחובר! סופר קבוצות...');
        const chats = await sock.groupFetchAllParticipating();
        console.log(`\nיש לך ${Object.keys(chats).length} קבוצות!`);
        process.exit(0);
    }

    if (connection === 'close') {
        const code = new Boom(lastDisconnect?.error)?.output?.statusCode;
        if (code === DisconnectReason.loggedOut) {
            console.log('נותק. מחק auth והרץ מחדש.');
            process.exit(1);
        }
        if (codeShown) {
            console.log('ממתין לאישור הקוד...');
        }
        // baileys יתחבר מחדש אוטומטית
        const { state: newState } = await useMultiFileAuthState('./auth');
        const newSock = makeWASocket({
            auth: newState,
            logger,
            printQRInTerminal: false,
            browser: Browsers.macOS('Chrome'),
            defaultQueryTimeoutMs: undefined,
        });
        newSock.ev.on('creds.update', saveCreds);
        newSock.ev.on('connection.update', sock.ev.emit.bind(sock.ev, 'connection.update'));
    }
});

console.log('מתחבר...');
