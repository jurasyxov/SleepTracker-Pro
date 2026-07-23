// sleep_tracker_cs.cs — трекер сна с анализом циклов на C#

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

class SleepTracker
{
    private class SleepEntry
    {
        public string Date { get; set; }
        public double Hours { get; set; }
        public int Cycles { get; set; }
        public double RemPhase { get; set; }
        public double DeepPhase { get; set; }
        public double Quality { get; set; }
    }

    private List<SleepEntry> history = new List<SleepEntry>();
    private string dataFile = "sleep_data.json";

    public SleepTracker() => LoadData();

    private void LoadData()
    {
        if (File.Exists(dataFile))
        {
            try
            {
                string json = File.ReadAllText(dataFile);
                history = JsonSerializer.Deserialize<List<SleepEntry>>(json) ?? new List<SleepEntry>();
            }
            catch { history = new List<SleepEntry>(); }
        }
    }

    private void SaveData()
    {
        string json = JsonSerializer.Serialize(history, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(dataFile, json);
    }

    public void AddSleep(double hours)
    {
        var e = new SleepEntry
        {
            Date = DateTime.Now.ToString("o"),
            Hours = hours,
            Cycles = (int)(hours / 1.5) + (hours % 1.5 > 0.75 ? 1 : 0),
            RemPhase = hours * 0.22,
            DeepPhase = hours - hours * 0.22
        };
        // Качество
        if (hours >= 7 && hours <= 8) e.Quality = 8 + (8 - hours) * 0.5;
        else if (hours >= 6) e.Quality = 6 + (hours - 6) * 2;
        else e.Quality = Math.Max(1, 4 + (hours - 5) * 0.8);
        e.Quality = Math.Min(10, Math.Max(1, e.Quality));

        history.Add(e);
        SaveData();
        Console.WriteLine($"✅ Добавлено: {hours:F1}ч, качество {e.Quality:F1}/10, циклов: {e.Cycles}");
    }

    public void Stats(int days = 7)
    {
        if (!history.Any()) { Console.WriteLine("Нет данных."); return; }
        var recent = history.TakeLast(Math.Min(days, history.Count)).ToList();
        Console.WriteLine($"📊 Статистика за {recent.Count} дней:");
        Console.WriteLine($"  Среднее: {recent.Average(e => e.Hours):F1}ч");
        Console.WriteLine($"  Лучшее: {recent.Max(e => e.Hours):F1}ч");
        Console.WriteLine($"  Худшее: {recent.Min(e => e.Hours):F1}ч");
        Console.WriteLine($"  Качество: {recent.Average(e => e.Quality):F1}/10");
    }

    public void Recommendations()
    {
        if (!history.Any())
        {
            Console.WriteLine("Начните отслеживать сон, чтобы получить рекомендации.");
            return;
        }
        double avg = history.Average(e => e.Hours);
        Console.WriteLine("💡 Рекомендации:");
        if (avg < 7) Console.WriteLine("  🕒 Старайтесь спать не менее 7 часов.");
        if (history.Count > 1)
        {
            bool irregular = false;
            for (int i = 1; i < history.Count; i++)
                if (Math.Abs(history[i].Hours - history[i-1].Hours) > 1.5) { irregular = true; break; }
            if (irregular) Console.WriteLine("  📅 Ложитесь спать в одно и то же время.");
        }
        if (avg < 6) Console.WriteLine("  🌿 Проветривайте комнату перед сном.");
        if (avg >= 7) Console.WriteLine("  ✅ Отличный режим сна! Продолжайте в том же духе.");
    }

    public void Interactive()
    {
        Console.WriteLine("🌙 SleepTracker Pro — C# Edition");
        Console.WriteLine("Команды: add <часы>, stats, recs, exit");
        while (true)
        {
            Console.Write("> ");
            string cmd = Console.ReadLine()?.Trim().ToLower() ?? "";
            if (cmd == "exit") break;
            else if (cmd.StartsWith("add"))
            {
                var parts = cmd.Split(' ');
                if (parts.Length > 1 && double.TryParse(parts[1], out double hours))
                    AddSleep(hours);
                else
                {
                    Console.Write("Время сна (часы): ");
                    if (double.TryParse(Console.ReadLine(), out hours))
                        AddSleep(hours);
                    else Console.WriteLine("Ошибка ввода.");
                }
            }
            else if (cmd == "stats") Stats();
            else if (cmd == "recs") Recommendations();
            else Console.WriteLine("Неизвестная команда.");
        }
    }

    public static void Main() => new SleepTracker().Interactive();
}
