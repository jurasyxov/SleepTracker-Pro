// sleep_tracker_js.js — трекер сна с анализом циклов на JavaScript (Node.js)

const fs = require('fs');
const readline = require('readline');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: '> '
});

class SleepTracker {
    constructor() {
        this.history = [];
        this.dataFile = 'sleep_data.json';
        this.loadData();
    }

    loadData() {
        try {
            const data = fs.readFileSync(this.dataFile, 'utf8');
            this.history = JSON.parse(data);
        } catch (e) {
            this.history = [];
        }
    }

    saveData() {
        fs.writeFileSync(this.dataFile, JSON.stringify(this.history, null, 2));
    }

    addSleep(hours) {
        const cycles = Math.floor(hours / 1.5) + (hours % 1.5 > 0.75 ? 1 : 0);
        const remPhase = hours * 0.22;
        const deepPhase = hours - remPhase;
        let quality;
        if (hours >= 7 && hours <= 8) quality = 8 + (8 - hours) * 0.5;
        else if (hours >= 6) quality = 6 + (hours - 6) * 2;
        else quality = Math.max(1, 4 + (hours - 5) * 0.8);
        quality = Math.min(10, Math.max(1, quality));

        const entry = {
            date: new Date().toISOString(),
            hours: Math.round(hours * 10) / 10,
            cycles,
            remPhase: Math.round(remPhase * 100) / 100,
            deepPhase: Math.round(deepPhase * 100) / 100,
            quality: Math.round(quality * 10) / 10
        };
        this.history.push(entry);
        this.saveData();
        console.log(`✅ Добавлено: ${hours.toFixed(1)}ч, качество ${entry.quality.toFixed(1)}/10, циклов: ${cycles}`);
    }

    stats(days = 7) {
        if (this.history.length === 0) {
            console.log('Нет данных.');
            return;
        }
        const n = Math.min(days, this.history.length);
        const recent = this.history.slice(-n);
        const avgHours = recent.reduce((s, e) => s + e.hours, 0) / n;
        const avgQuality = recent.reduce((s, e) => s + e.quality, 0) / n;
        const best = Math.max(...recent.map(e => e.hours));
        const worst = Math.min(...recent.map(e => e.hours));
        console.log(`📊 Статистика за ${n} дней:`);
        console.log(`  Среднее: ${avgHours.toFixed(1)}ч`);
        console.log(`  Лучшее: ${best.toFixed(1)}ч`);
        console.log(`  Худшее: ${worst.toFixed(1)}ч`);
        console.log(`  Качество: ${avgQuality.toFixed(1)}/10`);
    }

    recommendations() {
        if (this.history.length === 0) {
            console.log('Начните отслеживать сон, чтобы получить рекомендации.');
            return;
        }
        const avg = this.history.reduce((s, e) => s + e.hours, 0) / this.history.length;
        console.log('💡 Рекомендации:');
        if (avg < 7) console.log('  🕒 Старайтесь спать не менее 7 часов.');
        if (this.history.length > 1) {
            let irregular = false;
            for (let i = 1; i < this.history.length; i++) {
                if (Math.abs(this.history[i].hours - this.history[i-1].hours) > 1.5) {
                    irregular = true;
                    break;
                }
            }
            if (irregular) console.log('  📅 Ложитесь спать в одно и то же время.');
        }
        if (avg < 6) console.log('  🌿 Проветривайте комнату перед сном.');
        if (avg >= 7) console.log('  ✅ Отличный режим сна! Продолжайте в том же духе.');
    }

    interactive() {
        console.log('🌙 SleepTracker Pro — JavaScript Edition');
        console.log('Команды: add <часы>, stats, recs, exit');
        rl.prompt();

        rl.on('line', (line) => {
            const parts = line.trim().split(' ');
            const cmd = parts[0];
            if (cmd === 'exit') {
                rl.close();
                return;
            }
            if (cmd === 'add') {
                if (parts.length > 1) {
                    const hours = parseFloat(parts[1]);
                    if (!isNaN(hours)) {
                        this.addSleep(hours);
                        rl.prompt();
                        return;
                    }
                }
                rl.question('Время сна (часы): ', (answer) => {
                    const hours = parseFloat(answer);
                    if (!isNaN(hours)) this.addSleep(hours);
                    else console.log('Ошибка ввода.');
                    rl.prompt();
                });
                return;
            }
            if (cmd === 'stats') {
                this.stats(7);
            } else if (cmd === 'recs') {
                this.recommendations();
            } else {
                console.log('Неизвестная команда.');
            }
            rl.prompt();
        }).on('close', () => {
            console.log('До свидания!');
            process.exit(0);
        });
    }
}

const st = new SleepTracker();
st.interactive();
