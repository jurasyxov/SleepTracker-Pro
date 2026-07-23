// sleep_tracker_rs.rs — трекер сна с анализом циклов на Rust

use std::io::{self, Write, BufRead};
use std::fs;
use std::path::Path;
use serde::{Serialize, Deserialize};
use chrono::Local;
use std::collections::VecDeque;

#[derive(Serialize, Deserialize, Clone)]
struct SleepEntry {
    date: String,
    hours: f64,
    cycles: u32,
    rem_phase: f64,
    deep_phase: f64,
    quality: f64,
}

struct SleepTracker {
    history: Vec<SleepEntry>,
    data_file: String,
}

impl SleepTracker {
    fn new() -> Self {
        let mut st = SleepTracker {
            history: Vec::new(),
            data_file: "sleep_data.json".to_string(),
        };
        st.load_data();
        st
    }

    fn load_data(&mut self) {
        if let Ok(data) = fs::read_to_string(&self.data_file) {
            if let Ok(history) = serde_json::from_str(&data) {
                self.history = history;
            }
        }
    }

    fn save_data(&self) {
        if let Ok(json) = serde_json::to_string_pretty(&self.history) {
            let _ = fs::write(&self.data_file, json);
        }
    }

    fn add_sleep(&mut self, hours: f64) {
        let cycles = (hours / 1.5).floor() as u32 + if hours % 1.5 > 0.75 { 1 } else { 0 };
        let rem_phase = hours * 0.22;
        let deep_phase = hours - rem_phase;
        let quality = if hours >= 7.0 && hours <= 8.0 {
            8.0 + (8.0 - hours) * 0.5
        } else if hours >= 6.0 {
            6.0 + (hours - 6.0) * 2.0
        } else {
            4.0 + (hours - 5.0) * 0.8
        };
        let quality = quality.max(1.0).min(10.0);

        let entry = SleepEntry {
            date: Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
            hours,
            cycles,
            rem_phase: (rem_phase * 100.0).round() / 100.0,
            deep_phase: (deep_phase * 100.0).round() / 100.0,
            quality: (quality * 10.0).round() / 10.0,
        };
        self.history.push(entry);
        self.save_data();
        println!("✅ Добавлено: {:.1}ч, качество {:.1}/10, циклов: {}", hours, quality, cycles);
    }

    fn stats(&self, days: usize) {
        if self.history.is_empty() {
            println!("Нет данных.");
            return;
        }
        let n = days.min(self.history.len());
        let recent = &self.history[self.history.len()-n..];
        let avg_hours = recent.iter().map(|e| e.hours).sum::<f64>() / n as f64;
        let avg_quality = recent.iter().map(|e| e.quality).sum::<f64>() / n as f64;
        let best = recent.iter().map(|e| e.hours).fold(0.0, |a, b| a.max(b));
        let worst = recent.iter().map(|e| e.hours).fold(100.0, |a, b| a.min(b));
        println!("📊 Статистика за {} дней:", n);
        println!("  Среднее: {:.1}ч", avg_hours);
        println!("  Лучшее: {:.1}ч", best);
        println!("  Худшее: {:.1}ч", worst);
        println!("  Качество: {:.1}/10", avg_quality);
    }

    fn recommendations(&self) {
        if self.history.is_empty() {
            println!("Начните отслеживать сон, чтобы получить рекомендации.");
            return;
        }
        let avg = self.history.iter().map(|e| e.hours).sum::<f64>() / self.history.len() as f64;
        println!("💡 Рекомендации:");
        if avg < 7.0 { println!("  🕒 Старайтесь спать не менее 7 часов."); }
        if self.history.len() > 1 {
            let irregular = self.history.windows(2).any(|w| (w[1].hours - w[0].hours).abs() > 1.5);
            if irregular { println!("  📅 Ложитесь спать в одно и то же время."); }
        }
        if avg < 6.0 { println!("  🌿 Проветривайте комнату перед сном."); }
        if avg >= 7.0 { println!("  ✅ Отличный режим сна! Продолжайте в том же духе."); }
    }

    fn interactive(&mut self) {
        let stdin = io::stdin();
        let mut reader = stdin.lock();
        println!("🌙 SleepTracker Pro — Rust Edition");
        println!("Команды: add <часы>, stats, recs, exit");
        loop {
            print!("> ");
            io::stdout().flush().unwrap();
            let mut line = String::new();
            if reader.read_line(&mut line).is_err() { break; }
            let parts: Vec<&str> = line.trim().split_whitespace().collect();
            if parts.is_empty() { continue; }
            match parts[0] {
                "exit" => break,
                "add" => {
                    if parts.len() > 1 {
                        if let Ok(hours) = parts[1].parse::<f64>() {
                            self.add_sleep(hours);
                        } else { println!("Ошибка ввода."); }
                    } else {
                        print!("Время сна (часы): ");
                        io::stdout().flush().unwrap();
                        let mut input = String::new();
                        reader.read_line(&mut input).unwrap();
                        if let Ok(hours) = input.trim().parse::<f64>() {
                            self.add_sleep(hours);
                        } else { println!("Ошибка ввода."); }
                    }
                }
                "stats" => self.stats(7),
                "recs" => self.recommendations(),
                _ => println!("Неизвестная команда."),
            }
        }
    }
}

fn main() {
    let mut st = SleepTracker::new();
    st.interactive();
}
