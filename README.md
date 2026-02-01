# The Chamelot: OpenRTP Engine 🎰

**OpenRTP Engine** is a state-of-the-art, high-precision PID control system designed for stabilizing Return to Player (RTP) in gaming environments. It combines high-speed mathematical certainty with a natural, "human-like" payment feel through its unique **Dual-Path Weighted Memory** architecture.

---

## 🌟 Key Features

### 🧠 Dual-Path Weighted Memory (The "Balanced Brain")
OpenRTP solves the classic trade-off between long-term precision and short-term responsiveness:
- **Base Integrator (Precision Path):** A 100% accurate memory path that tracks every cent of house profit. It ensures zero steady-state error, meaning the machine will *always* converge perfectly to the target RTP, no matter how many millions of spins are run.
- **Reactive Integrator (Response Path):** A short-term, weighted path that reacts 2x more strongly to recent events (like Jackpots). It uses a 0.99 decay factor to ensure the machine responds "emotionally" to recent high-wins without being permanently stuck in the past.

### ⚖️ Asymmetric Stabilization
Tuned for real-world casino psychology:
- **Stealth Tightening (-0.9):** Recover house margins subtly without making the game feel "dead."
- **Aggressive Loosening (+2.0):** Allow the machine to pay out generously after a big event to maintain player engagement and "Hot Streak" sensations.

### 🌪️ Chaos Mode Stress Testing
The engine is verified for extreme volatility. Launch a **10 Million Spin** test with random bets ($1 to $3,000+) and watch the PID maintain sub-0.5% error margins.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.8+
- NumPy
- Matplotlib (Optional, for Dashboard visualization)

```bash
pip install -r requirements.txt
```

### 📜 License

This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](http://creativecommons.org/licenses/by-nc/4.0/).

- ✅ **Attribution:** You must give credit to the author.
- ❌ **Non-Commercial:** You may not use this material for commercial purposes.
- ⚠️ **Educational/Research only.**

> [!IMPORTANT]  
> **Commercial Use:** For commercial licensing, enterprise integration, or professional consulting, please contact the author directly via [LinkedIn](https://www.linkedin.com/in/katunyu-boonchumjai-12ba6334b/) or GitHub.

### 2. Launch the Simulator
Run the interactive CLI to stress-test your math:
```bash
python3 demo.py
```
### 🌪️ Chaos Mode Stress Testing
The engine is verified for extreme volatility. Below is a **10,000 Spin Chaos Stress Test** showcasing the PID's ability to maintain a 90.0% RTP target even during multiple "Black Swan" events and random bet spikes ($1.0 - $3000.0).

![OpenRTP Chaos Stress Test Result]<img width="1800" height="1500" alt="recovery_dashboard" src="https://github.com/user-attachments/assets/03f02e62-e355-452f-9473-1808ff51c52f" />


* **RTP Convergence:** Watch the Purple line (Actual RTP) snap onto the Red dashed line (Target) with extreme precision.
* **PID Response:** The control signal (Signal u) dynamically adjusts between our safety bounds (-0.9 to +2.0) to stabilize house profit without breaking the "natural" feel of the game.
---

##  Project Structure
- `core/rtp_engine.py`: The "Brain". Pure PID logic and weighted weight-adjustment equations.
- `demo.py`: Interactive CLI tool for "Black Swan", "Chaos", and "Soak" simulations.
- `output/`: Automated storage for high-resolution simulation dashboards (`recovery_dashboard.png`).

---
**Author:** [Katunyu Boonchumjai](https://github.com/Katunyu-Boonchumjai)  
**Connect:** [LinkedIn](https://www.linkedin.com/in/katunyu-boonchumjai-12ba6334b/)  
**Project:** The Chamelot  
## ⚖️ Legal Disclaimer

> [!CAUTION]
> **FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY.**  
> The author, **Katunyu Boonchumjai**, provides this software "as is" without any warranties. In no event shall the author be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.
>
> **Users are solely responsible for ensuring compliance with their local laws and regulations.**
