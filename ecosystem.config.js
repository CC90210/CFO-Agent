/**
 * PM2 Ecosystem Config — Atlas CFO Agent
 *
 * HARD RULES:
 *   - Cross-platform (Windows + macOS). Windows uses the system Python 3.12
 *     install; Mac uses the project's .venv (created via `python3.12 -m venv .venv`).
 *
 *   - Per-MACHINE single-instance enforcement is handled inside the bridge
 *     (telegram_bridge.py V3.3 _acquire_instance_lock at tmp/atlas_telegram.lock).
 *     Cross-machine arbitration (Mac vs Windows) is left to Telegram's 409
 *     Conflict on getUpdates — first to poll wins, the loser stays warm.
 *
 *   - Atlas and Bravo use DIFFERENT bot tokens so they can co-exist on the
 *     same machine; never duplicate the same token across PM2 apps.
 *
 *   - Secrets come from .env via python-dotenv in the bot itself. Do NOT
 *     paste API keys into this file. PM2 only sets process-level env vars.
 *
 * USAGE:
 *
 *   # First-time setup (run once)
 *   cd /c/Users/User/APPS/CFO-Agent
 *   pm2 start ecosystem.config.js
 *   pm2 save
 *   pm2-startup install    # Auto-start on Windows boot (one time)
 *
 *   # Day-to-day
 *   pm2 status             # See atlas-telegram + bravo-* running
 *   pm2 logs atlas-telegram
 *   pm2 restart atlas-telegram
 *   pm2 stop atlas-telegram
 *
 *   # After code edits
 *   pm2 restart atlas-telegram
 *
 * HEALTHCHECK:
 *   Bot logs "Atlas Telegram Bridge v3.1.0 starting — polling..." on boot.
 *   If pm2 shows `restart_count > 3` in an hour, tail the error log.
 */

const os = require('os');
const path = require('path');

const IS_WIN = process.platform === 'win32';

// Project root is this file's directory
const PROJECT_ROOT = __dirname;

// Windows uses the system Python 3.12; Mac uses the project venv so all
// research/CFO deps (tenacity, ccxt, anthropic, etc.) are on the path.
const PYTHON = IS_WIN
    ? 'C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
    : path.join(PROJECT_ROOT, '.venv', 'bin', 'python');

module.exports = {
    apps: [
        {
            name: 'atlas-telegram',
            script: 'telegram_bridge.py',
            interpreter: PYTHON,
            cwd: PROJECT_ROOT,
            watch: false,                    // Don't auto-restart on file change — use `pm2 restart` explicitly
            autorestart: true,               // Recover from crashes
            max_restarts: 10,                // Stop flapping after 10 restarts in a row
            restart_delay: 5000,             // Wait 5s between restart attempts
            kill_timeout: 8000,              // Give Python time to close Telegram polling cleanly
            min_uptime: 10000,               // Must run 10s before counting as "started"
            env: {
                PYTHONIOENCODING: 'utf-8',   // Avoids Windows CP1252 UnicodeEncodeError in logs
                PYTHONUNBUFFERED: '1',       // Stream logs immediately to pm2
            },
            log_date_format: 'YYYY-MM-DD HH:mm:ss',
            error_file: path.join(PROJECT_ROOT, 'logs', 'pm2-atlas-error.log'),
            out_file: path.join(PROJECT_ROOT, 'logs', 'pm2-atlas-out.log'),
            merge_logs: true,
            max_size: '10M',
            time: true,
        },
    ],
};
