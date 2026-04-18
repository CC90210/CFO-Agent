/**
 * PM2 Ecosystem Config — Atlas CFO Agent
 *
 * HARD RULES:
 *   - Windows-only. The bot uses Git Bash paths + Windows-native python.exe.
 *     Don't try to run this on Mac/Linux without a matching venv.
 *
 *   - Only ONE atlas-telegram process may run at a time. Two processes on
 *     the same TELEGRAM_BOT_TOKEN = random message routing. Atlas and Bravo
 *     use DIFFERENT bot tokens so they can co-exist; never duplicate the
 *     same token across PM2 apps.
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

// System Python 3.12 on Windows (no venv — requirements installed globally)
const PYTHON = IS_WIN
    ? 'C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
    : '/usr/bin/python3';

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
