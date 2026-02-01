# 📖 The Chamelot: OpenRTP Engine User Manual
**Author:** Katunyu Boonchumjai | [GitHub](https://github.com/Katunyu-Boonchumjai) | [LinkedIn](https://www.linkedin.com/in/katunyu-boonchumjai-12ba6334b/)

This manual provides instructions for running simulations, interpreting analytics, and tuning the PID brain of the **OpenRTP Engine**.

---

## 🎮 Running a Simulation

Launch the simulator using:
```bash
python3 demo.py
```

### 1. Configuration Sequence
1. **Target RTP:** Enter your math model's target (e.g., `0.95` or `95%`).
2. **Event Trigger:** Set a Win Multiplier (e.g., `500x`) and occurrence frequency.
3. **Simulation Mode:** Choose how you want to test the engine (Auto, Fixed, or Chaos).
4. **Bet Size:** Based on your selected mode, enter either a **Fixed Bet** or a **Chaos Bet Range** ($Min - $Max).

### 2. Simulation Modes & Analytics

| Mode | Input | Key Feature |
| :--- | :--- | :--- |
| **Auto-Recovery** | `1` | Tests the engine's ability to return to the profit line automatically. |
| **Fixed Duration** | `2` | Ideal for soak testing specific turnover volumes. |
| **Chaos Mode** | `3` | **Transparency Verified:** Randomizes bets per spin and generates a **10-Bin Bet Distribution Table** to prove true randomness. |

---

## 📊 Interpreting the Analytics Dashboard

After a run, a dashboard (`output/recovery_dashboard.png`) will open. It contains three critical charts:

### 🏠 House Profit (Top)
- **Red Dashed:** Theoretical profit the house *should* have.
- **Green Solid:** Actual profit the house *has*.
- **Gap:** OpenRTP's primary mission is to close this gap. If the green line is above red, the house is in surplus.

### 🧠 Control Signal M(x) (Middle)
This shows how the PID is "thinking":
- **+0.1 to +2.0:** Machine is "Loosening" (Increasing win weights).
- **-0.1 to -0.9:** Machine is "Tightening" (Decreasing win weights).
- **Steady State:** A flat line near 0 indicates a perfectly balanced game.

### 🎯 RTP Convergence (Bottom)
This tracks the percentage return over time. In long runs (100k+ spins), the purple line should "stick" to the red target line like a magnet.

---

## 🛠️ Advanced Engineering Tips

### Tuning the "Brain"
You can adjust the PID sensitivity in `demo.py` (Line 73):
- **Kp (Proportional):** High value = Instant reaction to every spin (Very jittery).
- **Ki (Integral):** High value = Aggressively removes long-term error (Eliminates widening gaps).
- **Kd (Derivative):** High value = Dampens the reaction (Prevents overshooting).

### High-Volume Testing
When running **10,000,000 spins**, the terminal will display a `.` every 100 spins. The engine is optimized for speed; 10M spins typically conclude in ~60 seconds on modern hardware.

---
## 💼 Commercial Licensing & Support

If you wish to use the **OpenRTP Engine** for commercial purposes, production-grade deployment, or require professional consulting, please reach out:

- **LinkedIn:** [Katunyu Boonchumjai](https://www.linkedin.com/in/katunyu-boonchumjai-12ba6334b/)
- **GitHub:** [Katunyu-Boonchumjai](https://github.com/Katunyu-Boonchumjai)

**Happy Testing!** 🎰🚀
