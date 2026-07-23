# sleep_tracker_python.py — трекер сна с анализом циклов на Python

import json
import os
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import deque

class SleepTracker:
    def __init__(self):
        self.data_file = "sleep_data.json"
        self.history = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def add_sleep(self, hours, date=None):
        if date is None:
            date = datetime.now().isoformat()
        # Анализ циклов (каждый цикл ~1.5 часа)
        cycles = int(hours // 1.5)
        rem_cycles = hours % 1.5
        if rem_cycles > 0.75:
            cycles += 1
        # Фазы: быстрый сон (20-25% времени), медленный сон (75-80%)
        rem_phase = hours * 0.22
        deep_phase = hours - rem_phase
        # Оценка качества: 8-10 если 7-8ч, 6-8 если 6-7ч, <6 если меньше
        if 7 <= hours <= 8:
            quality = 8 + (8 - hours) * 0.5
        elif 6 <= hours < 7:
            quality = 6 + (hours - 6) * 2
        else:
            quality = max(1, 4 + (hours - 5) * 0.8)
        quality = min(10, max(1, quality))

        entry = {
            'date': date,
            'hours': hours,
            'cycles': cycles,
            'rem_phase': round(rem_phase, 2),
            'deep_phase': round(deep_phase, 2),
            'quality': round(quality, 1)
        }
        self.history.append(entry)
        self.save_data()
        return entry

    def get_stats(self, days=7):
        if not self.history:
            return None
        recent = self.history[-days:]
        avg_hours = sum(e['hours'] for e in recent) / len(recent)
        avg_quality = sum(e['quality'] for e in recent) / len(recent)
        best = max(e['hours'] for e in recent)
        worst = min(e['hours'] for e in recent)
        best_quality = max(e['quality'] for e in recent)
        return {
            'avg_hours': avg_hours,
            'avg_quality': avg_quality,
            'best': best,
            'worst': worst,
            'best_quality': best_quality,
            'total_entries': len(recent)
        }

    def get_recommendations(self):
        recs = []
        if not self.history:
            return ["Начните отслеживать сон, чтобы получить рекомендации."]
        avg = sum(e['hours'] for e in self.history) / len(self.history)
        if avg < 7:
            recs.append("🕒 Старайтесь спать не менее 7 часов.")
        if len(self.history) > 1:
            diff = [self.history[i]['hours'] - self.history[i-1]['hours'] for i in range(1, len(self.history))]
            if any(abs(d) > 1.5 for d in diff):
                recs.append("📅 Ложитесь спать в одно и то же время.")
        if avg < 6:
            recs.append("🌿 Проветривайте комнату перед сном.")
        if not recs:
            recs.append("✅ Отличный режим сна! Продолжайте в том же духе.")
        return recs

    def export_csv(self, filename="sleep_export.csv"):
        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Дата', 'Часы', 'Циклы', 'Быстрый сон', 'Глубокий сон', 'Качество'])
            for e in self.history:
                writer.writerow([e['date'], e['hours'], e['cycles'], e['rem_phase'], e['deep_phase'], e['quality']])
        print(f"Экспортировано в {filename}")

    def plot_trend(self):
        if len(self.history) < 2:
            print("Недостаточно данных для графика.")
            return
        dates = [datetime.fromisoformat(e['date']) for e in self.history]
        hours = [e['hours'] for e in self.history]
        qualities = [e['quality'] for e in self.history]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        ax1.plot(dates, hours, 'b-o', label='Часы сна')
        ax1.axhline(y=7, color='g', linestyle='--', label='Норма 7ч')
        ax1.set_ylabel('Часы')
        ax1.legend()
        ax1.grid(True)

        ax2.plot(dates, qualities, 'r-o', label='Качество')
        ax2.axhline(y=8, color='g', linestyle='--', label='Хорошо')
        ax2.set_ylabel('Качество (1-10)')
        ax2.legend()
        ax2.grid(True)

        plt.xlabel('Дата')
        plt.tight_layout()
        plt.show()

    def interactive(self):
        print("🌙 SleepTracker Pro — Python Edition")
        print("Команды: add [часы], stats, recs, plot, export, exit")
        while True:
            cmd = input("> ").strip().lower()
            if cmd == 'exit':
                break
            elif cmd.startswith('add'):
                parts = cmd.split()
                if len(parts) > 1:
                    try:
                        hours = float(parts[1])
                        entry = self.add_sleep(hours)
                        print(f"✅ Добавлено: {hours}ч, качество {entry['quality']}/10, циклов: {entry['cycles']}")
                    except:
                        print("Введите число.")
                else:
                    try:
                        hours = float(input("Время сна (часы): "))
                        entry = self.add_sleep(hours)
                        print(f"✅ Добавлено: {hours}ч, качество {entry['quality']}/10, циклов: {entry['cycles']}")
                    except:
                        print("Ошибка ввода.")
            elif cmd == 'stats':
                stats = self.get_stats()
                if stats:
                    print(f"📊 Статистика за {stats['total_entries']} дней:")
                    print(f"  Среднее: {stats['avg_hours']:.1f}ч")
                    print(f"  Лучшее: {stats['best']:.1f}ч")
                    print(f"  Худшее: {stats['worst']:.1f}ч")
                    print(f"  Качество: {stats['avg_quality']:.1f}/10")
                else:
                    print("Нет данных.")
            elif cmd == 'recs':
                recs = self.get_recommendations()
                print("💡 Рекомендации:")
                for r in recs:
                    print(f"  {r}")
            elif cmd == 'plot':
                self.plot_trend()
            elif cmd == 'export':
                self.export_csv()
            else:
                print("Неизвестная команда.")

if __name__ == "__main__":
    st = SleepTracker()
    st.interactive()
