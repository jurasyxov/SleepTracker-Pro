// sleep_tracker_cpp.cpp — трекер сна с анализом циклов на C++

#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <ctime>
#include <cmath>

using namespace std;

struct SleepEntry {
    string date;
    double hours;
    int cycles;
    double rem_phase;
    double deep_phase;
    double quality;
};

class SleepTracker {
private:
    vector<SleepEntry> history;
    string dataFile = "sleep_data.csv";

    string currentDate() {
        time_t now = time(nullptr);
        char buf[20];
        strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", localtime(&now));
        return string(buf);
    }

    void loadData() {
        ifstream file(dataFile);
        if (!file.is_open()) return;
        string line;
        while (getline(file, line)) {
            stringstream ss(line);
            SleepEntry e;
            string token;
            getline(ss, e.date, ',');
            getline(ss, token, ','); e.hours = stod(token);
            getline(ss, token, ','); e.cycles = stoi(token);
            getline(ss, token, ','); e.rem_phase = stod(token);
            getline(ss, token, ','); e.deep_phase = stod(token);
            getline(ss, token, ','); e.quality = stod(token);
            history.push_back(e);
        }
        file.close();
    }

    void saveData() {
        ofstream file(dataFile);
        if (!file.is_open()) return;
        for (const auto& e : history) {
            file << e.date << "," << e.hours << "," << e.cycles << ","
                 << e.rem_phase << "," << e.deep_phase << "," << e.quality << "\n";
        }
        file.close();
    }

public:
    SleepTracker() { loadData(); }

    void addSleep(double hours) {
        SleepEntry e;
        e.date = currentDate();
        e.hours = hours;
        e.cycles = (int)(hours / 1.5);
        if (hours - e.cycles * 1.5 > 0.75) e.cycles++;
        e.rem_phase = hours * 0.22;
        e.deep_phase = hours - e.rem_phase;
        // Качество
        if (hours >= 7 && hours <= 8) e.quality = 8 + (8 - hours) * 0.5;
        else if (hours >= 6) e.quality = 6 + (hours - 6) * 2;
        else e.quality = max(1.0, 4 + (hours - 5) * 0.8);
        e.quality = min(10.0, max(1.0, e.quality));

        history.push_back(e);
        saveData();
        cout << "✅ Добавлено: " << hours << "ч, качество " << e.quality << "/10, циклов: " << e.cycles << endl;
    }

    void stats(int days = 7) {
        if (history.empty()) { cout << "Нет данных." << endl; return; }
        int n = min(days, (int)history.size());
        auto start = history.end() - n;
        double avg_hours = 0, avg_quality = 0;
        double best = 0, worst = 100;
        for (auto it = start; it != history.end(); ++it) {
            avg_hours += it->hours;
            avg_quality += it->quality;
            if (it->hours > best) best = it->hours;
            if (it->hours < worst) worst = it->hours;
        }
        avg_hours /= n;
        avg_quality /= n;
        cout << "📊 Статистика за " << n << " дней:" << endl;
        cout << "  Среднее: " << fixed << setprecision(1) << avg_hours << "ч" << endl;
        cout << "  Лучшее: " << best << "ч" << endl;
        cout << "  Худшее: " << worst << "ч" << endl;
        cout << "  Качество: " << avg_quality << "/10" << endl;
    }

    void recommendations() {
        if (history.empty()) {
            cout << "Начните отслеживать сон, чтобы получить рекомендации." << endl;
            return;
        }
        double avg = 0;
        for (const auto& e : history) avg += e.hours;
        avg /= history.size();
        cout << "💡 Рекомендации:" << endl;
        if (avg < 7) cout << "  🕒 Старайтесь спать не менее 7 часов." << endl;
        if (history.size() > 1) {
            bool irregular = false;
            for (size_t i = 1; i < history.size(); ++i) {
                if (abs(history[i].hours - history[i-1].hours) > 1.5) { irregular = true; break; }
            }
            if (irregular) cout << "  📅 Ложитесь спать в одно и то же время." << endl;
        }
        if (avg < 6) cout << "  🌿 Проветривайте комнату перед сном." << endl;
        if (avg >= 7) cout << "  ✅ Отличный режим сна! Продолжайте в том же духе." << endl;
    }

    void interactive() {
        cout << "🌙 SleepTracker Pro — C++ Edition" << endl;
        cout << "Команды: add <часы>, stats, recs, exit" << endl;
        string cmd;
        while (true) {
            cout << "> ";
            cin >> cmd;
            if (cmd == "exit") break;
            else if (cmd == "add") {
                double hours;
                cin >> hours;
                addSleep(hours);
            } else if (cmd == "stats") {
                stats();
            } else if (cmd == "recs") {
                recommendations();
            } else {
                cout << "Неизвестная команда." << endl;
            }
        }
    }
};

int main() {
    SleepTracker st;
    st.interactive();
    return 0;
}
