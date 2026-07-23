// sleep_tracker_java.java — трекер сна с анализом циклов на Java

import java.io.*;
import java.nio.file.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.*;

public class SleepTracker {
    private static class SleepEntry {
        String date;
        double hours;
        int cycles;
        double remPhase;
        double deepPhase;
        double quality;
    }

    private List<SleepEntry> history = new ArrayList<>();
    private String dataFile = "sleep_data.json";
    private DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    public SleepTracker() {
        loadData();
    }

    private void loadData() {
        try {
            String content = new String(Files.readAllBytes(Paths.get(dataFile)));
            // упрощённый парсинг (пропускаем для демонстрации)
        } catch (IOException e) {}
    }

    private void saveData() {
        // упрощённо сохраняем в JSON
        try (PrintWriter pw = new PrintWriter(dataFile)) {
            pw.println("[");
            for (int i = 0; i < history.size(); i++) {
                SleepEntry e = history.get(i);
                pw.printf("{\"date\":\"%s\",\"hours\":%.1f,\"cycles\":%d,\"remPhase\":%.2f,\"deepPhase\":%.2f,\"quality\":%.1f}%s\n",
                    e.date, e.hours, e.cycles, e.remPhase, e.deepPhase, e.quality,
                    i < history.size()-1 ? "," : "");
            }
            pw.println("]");
        } catch (IOException e) {}
    }

    private String now() {
        return LocalDateTime.now().format(formatter);
    }

    public void addSleep(double hours) {
        SleepEntry e = new SleepEntry();
        e.date = now();
        e.hours = hours;
        e.cycles = (int)(hours / 1.5);
        if (hours - e.cycles * 1.5 > 0.75) e.cycles++;
        e.remPhase = hours * 0.22;
        e.deepPhase = hours - e.remPhase;
        if (hours >= 7 && hours <= 8) e.quality = 8 + (8 - hours) * 0.5;
        else if (hours >= 6) e.quality = 6 + (hours - 6) * 2;
        else e.quality = Math.max(1, 4 + (hours - 5) * 0.8);
        e.quality = Math.min(10, Math.max(1, e.quality));

        history.add(e);
        saveData();
        System.out.printf("✅ Добавлено: %.1fч, качество %.1f/10, циклов: %d%n", hours, e.quality, e.cycles);
    }

    public void stats(int days) {
        if (history.isEmpty()) { System.out.println("Нет данных."); return; }
        int n = Math.min(days, history.size());
        List<SleepEntry> recent = history.subList(history.size()-n, history.size());
        double avgHours = recent.stream().mapToDouble(e -> e.hours).average().orElse(0);
        double avgQuality = recent.stream().mapToDouble(e -> e.quality).average().orElse(0);
        double best = recent.stream().mapToDouble(e -> e.hours).max().orElse(0);
        double worst = recent.stream().mapToDouble(e -> e.hours).min().orElse(0);
        System.out.printf("📊 Статистика за %d дней:%n", n);
        System.out.printf("  Среднее: %.1fч%n", avgHours);
        System.out.printf("  Лучшее: %.1fч%n", best);
        System.out.printf("  Худшее: %.1fч%n", worst);
        System.out.printf("  Качество: %.1f/10%n", avgQuality);
    }

    public void recommendations() {
        if (history.isEmpty()) {
            System.out.println("Начните отслеживать сон, чтобы получить рекомендации.");
            return;
        }
        double avg = history.stream().mapToDouble(e -> e.hours).average().orElse(0);
        System.out.println("💡 Рекомендации:");
        if (avg < 7) System.out.println("  🕒 Старайтесь спать не менее 7 часов.");
        if (history.size() > 1) {
            boolean irregular = false;
            for (int i = 1; i < history.size(); i++) {
                if (Math.abs(history.get(i).hours - history.get(i-1).hours) > 1.5) {
                    irregular = true;
                    break;
                }
            }
            if (irregular) System.out.println("  📅 Ложитесь спать в одно и то же время.");
        }
        if (avg < 6) System.out.println("  🌿 Проветривайте комнату перед сном.");
        if (avg >= 7) System.out.println("  ✅ Отличный режим сна! Продолжайте в том же духе.");
    }

    public void interactive() {
        System.out.println("🌙 SleepTracker Pro — Java Edition");
        System.out.println("Команды: add <часы>, stats, recs, exit");
        Scanner sc = new Scanner(System.in);
        while (true) {
            System.out.print("> ");
            String cmd = sc.nextLine().trim().toLowerCase();
            if (cmd.equals("exit")) break;
            else if (cmd.startsWith("add")) {
                String[] parts = cmd.split(" ");
                if (parts.length > 1) {
                    try {
                        double hours = Double.parseDouble(parts[1]);
                        addSleep(hours);
                    } catch (NumberFormatException e) {
                        System.out.println("Введите число.");
                    }
                } else {
                    System.out.print("Время сна (часы): ");
                    try {
                        double hours = Double.parseDouble(sc.nextLine());
                        addSleep(hours);
                    } catch (Exception e) {}
                }
            } else if (cmd.equals("stats")) {
                stats(7);
            } else if (cmd.equals("recs")) {
                recommendations();
            } else {
                System.out.println("Неизвестная команда.");
            }
        }
        sc.close();
    }

    public static void main(String[] args) {
        new SleepTracker().interactive();
    }
}
