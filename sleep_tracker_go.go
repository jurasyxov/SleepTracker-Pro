// sleep_tracker_go.go — трекер сна с анализом циклов на Go

package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math"
	"os"
	"strconv"
	"strings"
	"time"
)

type SleepEntry struct {
	Date      string  `json:"date"`
	Hours     float64 `json:"hours"`
	Cycles    int     `json:"cycles"`
	RemPhase  float64 `json:"rem_phase"`
	DeepPhase float64 `json:"deep_phase"`
	Quality   float64 `json:"quality"`
}

type SleepTracker struct {
	history  []SleepEntry
	dataFile string
}

func NewSleepTracker() *SleepTracker {
	st := &SleepTracker{dataFile: "sleep_data.json"}
	st.loadData()
	return st
}

func (st *SleepTracker) loadData() {
	data, err := ioutil.ReadFile(st.dataFile)
	if err != nil {
		return
	}
	json.Unmarshal(data, &st.history)
}

func (st *SleepTracker) saveData() {
	data, _ := json.MarshalIndent(st.history, "", "  ")
	ioutil.WriteFile(st.dataFile, data, 0644)
}

func (st *SleepTracker) addSleep(hours float64) {
	cycles := int(hours / 1.5)
	if hours-float64(cycles)*1.5 > 0.75 {
		cycles++
	}
	remPhase := hours * 0.22
	deepPhase := hours - remPhase
	var quality float64
	if hours >= 7 && hours <= 8 {
		quality = 8 + (8-hours)*0.5
	} else if hours >= 6 {
		quality = 6 + (hours-6)*2
	} else {
		quality = 4 + (hours-5)*0.8
	}
	quality = math.Max(1, math.Min(10, quality))

	entry := SleepEntry{
		Date:      time.Now().Format(time.RFC3339),
		Hours:     hours,
		Cycles:    cycles,
		RemPhase:  math.Round(remPhase*100) / 100,
		DeepPhase: math.Round(deepPhase*100) / 100,
		Quality:   math.Round(quality*10) / 10,
	}
	st.history = append(st.history, entry)
	st.saveData()
	fmt.Printf("✅ Добавлено: %.1fч, качество %.1f/10, циклов: %d\n", hours, entry.Quality, cycles)
}

func (st *SleepTracker) stats(days int) {
	if len(st.history) == 0 {
		fmt.Println("Нет данных.")
		return
	}
	n := days
	if n > len(st.history) {
		n = len(st.history)
	}
	recent := st.history[len(st.history)-n:]
	avgHours := 0.0
	avgQuality := 0.0
	best := 0.0
	worst := 100.0
	for _, e := range recent {
		avgHours += e.Hours
		avgQuality += e.Quality
		if e.Hours > best {
			best = e.Hours
		}
		if e.Hours < worst {
			worst = e.Hours
		}
	}
	avgHours /= float64(n)
	avgQuality /= float64(n)
	fmt.Printf("📊 Статистика за %d дней:\n", n)
	fmt.Printf("  Среднее: %.1fч\n", avgHours)
	fmt.Printf("  Лучшее: %.1fч\n", best)
	fmt.Printf("  Худшее: %.1fч\n", worst)
	fmt.Printf("  Качество: %.1f/10\n", avgQuality)
}

func (st *SleepTracker) recommendations() {
	if len(st.history) == 0 {
		fmt.Println("Начните отслеживать сон, чтобы получить рекомендации.")
		return
	}
	avg := 0.0
	for _, e := range st.history {
		avg += e.Hours
	}
	avg /= float64(len(st.history))
	fmt.Println("💡 Рекомендации:")
	if avg < 7 {
		fmt.Println("  🕒 Старайтесь спать не менее 7 часов.")
	}
	if len(st.history) > 1 {
		irregular := false
		for i := 1; i < len(st.history); i++ {
			if math.Abs(st.history[i].Hours-st.history[i-1].Hours) > 1.5 {
				irregular = true
				break
			}
		}
		if irregular {
			fmt.Println("  📅 Ложитесь спать в одно и то же время.")
		}
	}
	if avg < 6 {
		fmt.Println("  🌿 Проветривайте комнату перед сном.")
	}
	if avg >= 7 {
		fmt.Println("  ✅ Отличный режим сна! Продолжайте в том же духе.")
	}
}

func (st *SleepTracker) interactive() {
	scanner := bufio.NewScanner(os.Stdin)
	fmt.Println("🌙 SleepTracker Pro — Go Edition")
	fmt.Println("Команды: add <часы>, stats, recs, exit")
	for {
		fmt.Print("> ")
		if !scanner.Scan() {
			break
		}
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		cmd := parts[0]
		switch cmd {
		case "exit":
			return
		case "add":
			if len(parts) > 1 {
				if hours, err := strconv.ParseFloat(parts[1], 64); err == nil {
					st.addSleep(hours)
				} else {
					fmt.Println("Ошибка ввода.")
				}
			} else {
				fmt.Print("Время сна (часы): ")
				scanner.Scan()
				hours, err := strconv.ParseFloat(strings.TrimSpace(scanner.Text()), 64)
				if err == nil {
					st.addSleep(hours)
				} else {
					fmt.Println("Ошибка ввода.")
				}
			}
		case "stats":
			st.stats(7)
		case "recs":
			st.recommendations()
		default:
			fmt.Println("Неизвестная команда.")
		}
	}
}

func main() {
	NewSleepTracker().interactive()
}
