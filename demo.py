import numpy as np
import time
import sys
import os
import random
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from core.rtp_engine import SlotMachineController, PIDConfig, Symbol

def print_header():
    print("\033[1;36m" + "="*60)
    print("      🏰  THE CHAMELOT - OpenRTP Engine  🏰")
    print("           Author: Katunyu Boonchumjai")
    print("="*60 + "\033[0m")

def get_input(label, default, value_type=float):
    # Align prompt text to 40 characters
    prompt_text = f"{label:<40}"
    try:
        user_input = input(f"\033[1;33m{prompt_text}\033[0m [Default {default}]: ").strip()
        if not user_input:
            return default
        return value_type(user_input)
    except ValueError:
        print(f"\033[1;31mInvalid input. Using default {default}.\033[0m")
        return default

def test_black_swan():
    print_header()
    
    # 1. Configuration Inputs
    target_rtp = get_input("🎯 Input Target RTP (0.0-1.0 or %)", 0.95)
    if target_rtp > 1.0:
        print(f"\033[1;33m⚠️  Detected input > 1.0. Assuming Percentage: {target_rtp}% -> {target_rtp/100:.2f}\033[0m")
        target_rtp /= 100.0
        
    win_multiplier = get_input("💥 Input Win Multiplier (0=Normal Run)", 100.0)
    
    hit_interval = 0
    consecutive_hits = 1
    
    if win_multiplier > 0:
        consecutive_hits = get_input("🔄 Input Consecutive Hits", 1, int)
        hit_interval = get_input("⏲️  Repeat Hit Every N Spins (0=Once)", 0, int)
    else:
        print("\033[1;32m🌿 NORMAL RUN MODE: No forced events. Just standard RTP testing.\033[0m")
        
    print("-" * 60)
    sim_mode = get_input("⏱️  Simulation Mode (1=Auto, 2=Fixed, 3=Chaos)", 1, int)
    
    # Optional: Toggle markers on graph
    show_markers = False
    if win_multiplier > 0:
        show_markers = get_input("📍 Show event markers on graph? (1=Yes, 0=No)", 1, int) == 1

    # Initialize defaults
    bet_size = 1.0
    chaos_min = 0.0
    chaos_max = 0.0
    
    if sim_mode == 3:
        # CHAOS MODE
        chaos_min = get_input("📉 Input Min Chaos Bet", 1.0)
        chaos_max = get_input("📈 Input Max Chaos Bet", 3000.0)
        max_spins = get_input("⏳ Input Total Spins to Run", 10000, int)
        print(f"\033[1;35m🎲 CHAOS MODE ACTIVATED: Random Bets between ${chaos_min} - ${chaos_max}\033[0m")
        stop_on_recovery = False
        bet_size = chaos_min # Base for initialization
    elif sim_mode == 2:
        # FIXED MODE
        bet_size = get_input("💰 Input Fixed Bet Size", 1.0)
        max_spins = get_input("⏳ Input Total Spins to Run", 5000, int)
        stop_on_recovery = False
    else:
        # AUTO-RECOVERY MODE
        bet_size = get_input("💰 Input Base Bet Size", 1.0)
        max_spins = 20000 
        stop_on_recovery = True
        
    print("-" * 60)
    
    mode_names = {1: "Auto-Recovery", 2: "Fixed Duration", 3: "Chaos Stress Test"}
    active_mode_name = mode_names.get(sim_mode, "Unknown")
    
    print(f"\033[1;32m⚙️  Configuring Engine [{active_mode_name}]: Target={target_rtp*100:.1f}%, Event={win_multiplier}x\033[0m")

    # Aggressive PID for testing recovery (Tuned K values)
    config = PIDConfig(kp=0.06, ki=0.015, kd=0.15) 
    machine = SlotMachineController(target_rtp=target_rtp, config=config)
    
    # 2. Initial State Setup
    if win_multiplier > 0 and hit_interval == 0:
        # CLASSIC MODE: Single initial hit
        total_payout = win_multiplier * consecutive_hits * bet_size
        wager_init = 10.0 * consecutive_hits * bet_size
        machine.total_wagered = wager_init
        machine.current_profit = (machine.total_wagered - total_payout) 
        print(f"\n📉 START STATE: Wagered={machine.total_wagered:.2f} | Profit=\033[1;31m{machine.current_profit:.2f}\033[0m (Forced Loss)")
    else:
        # NORMAL/PERIODIC MODE: Start fresh
        machine.total_wagered = 0.0
        machine.current_profit = 0.0
        print(f"\n🌱 START STATE: Fresh Machine (0 Spins)")

    print("-" * 60)
    
    # 3. Simulation Loop
    recovery_spin = 0
    limit_spins = max_spins
    
    # Data for Graphing
    history_x = [0] # Spin Count for X-axis
    history_profit = [machine.current_profit]
    history_target = [machine.total_wagered * machine.house_edge]
    
    # Calculate initial RTP (avoid div by zero)
    init_rtp = 0.0
    if machine.total_wagered > 0:
        init_payout = machine.total_wagered - machine.current_profit
        init_rtp = (init_payout / machine.total_wagered) * 100.0
    
    history_rtp_actual = [init_rtp]
    history_signal = [0.0]
    chaos_history = []  # Track bets for distribution analysis
    event_indices = []  # Track when a "Black Swan" event happens
    
    print("🔄 Running Simulation...", end="", flush=True)
    
    for i in range(max_spins):
        
        # PERIODIC HIT LOGIC
        # If interval defined, trigger event at specific spins
        if win_multiplier > 0 and hit_interval > 0:
            if i > 0 and i % hit_interval == 0:
                event_payout = win_multiplier * consecutive_hits * bet_size
                machine.current_profit -= event_payout
                event_indices.append(i) # Mark this spin
                # Visual marker in log
                print(f"\n💥 EVENT TRIGGERED at Spin {i}: Paid {event_payout:.2f}!", end="")
        elif win_multiplier > 0 and i == 0 and hit_interval == 0:
            # Single initial event case
            event_indices.append(0)

        # CHAOS LOGIC: Randomize bet size per spin
        current_bet = bet_size
        if sim_mode == 3:
            current_bet = random.uniform(chaos_min, chaos_max)
            chaos_history.append(current_bet)
            
        curr, target, sig, _ = machine.spin_batch(1, bet_amount=current_bet) # Real-time batch
        
        # Collect Data (Every single spin per user request)
        history_x.append(i + 1)
        history_profit.append(curr)
        history_target.append(target)
        
        payout = machine.total_wagered - curr
        actual_rtp = (payout / machine.total_wagered) * 100.0 if machine.total_wagered > 0 else 0.0
        history_rtp_actual.append(actual_rtp)
        history_signal.append(sig)

        # Feedback animation
        if i % 100 == 0:
            print(".", end="", flush=True)
        
        # Check if recovered (Actual > Target)
        if curr >= target:
            if recovery_spin == 0: 
                # Only mark as 'Recovered' if we actually started below zero (Black Swan)
                if win_multiplier > 0 and hit_interval == 0:
                    recovery_spin = i + 1
                    limit_spins = i + 1000 # Add 1000 spins buffer to show stabilization
                    print(f"✅ Recovered at spin {i+1}. Run 1000 more spins to show stability...", end="", flush=True)
                else:
                    # In Normal or Periodic mode, 'Recovery' isn't a single point, it's stabilization
                    # So we just keep running until max_spins
                    pass
            
            if stop_on_recovery and recovery_spin > 0 and i >= limit_spins:
                break
            
    print("\n" + "-" * 60)
            
    # 4. Analyze Results
    is_recovery_test = (win_multiplier > 0 and hit_interval == 0)
    
    if is_recovery_test:
        if recovery_spin > 0:
            print(f"\033[1;32m✅ RECOVERED in {recovery_spin} spins!\033[0m")
        else:
            print(f"\033[1;31m❌ FAILED to recover in {max_spins} spins.\033[0m")
    else:
        print(f"\033[1;32m✅ SIMULATION COMPLETE ({i+1} spins)\033[0m")
        
    print(f"Final Profit: {curr:.2f} (Target: {target:.2f})")
    print(f"Peak PID Signal: {min(history_signal):.4f} (Max Tightening)") # Min because tightening is negative
    
    avg_sig = np.mean(history_signal)
    print(f"Avg Signal Load: {avg_sig:.4f}")
    
    if avg_sig < -0.6: 
        print("⚠️  WARNING: System panicked! (Game was practically dead)")
    elif avg_sig < -0.3:
        print("🛡️  QUALITY: Aggressive but playable recovery.")
    else:
        print("🕊️  QUALITY: Smooth/Stealthy recovery (Hard to detect).")

    # 4.5. Final Summary Metrics (Requested by user)
    print("\n" + "="*60)
    print(f"📊 FINAL SIMULATION SUMMARY")
    print("-" * 60)
    print(f"💰 Actual House Profit:    \033[1;32m${curr:.2f}\033[0m")
    print(f"🎯 Target House Profit:    ${target:.2f}")
    
    # Calculate Final RTP
    final_payout = machine.total_wagered - curr
    final_rtp = (final_payout / machine.total_wagered) * 100.0 if machine.total_wagered > 0 else 0.0
    
    print(f"📈 Final Realized RTP:     \033[1;36m{final_rtp:.2f}%\033[0m (Target: {target_rtp*100:.1f}%)")
    print(f"🔄 Total Turnover:         ${machine.total_wagered:.2f}")
    
    # 4.6. Chaos Mode Distribution (Requested by user)
    if sim_mode == 3 and chaos_history:
        print("-" * 60)
        print("🎲 CHAOS BET DISTRIBUTION (10 Bins)")
        print("-" * 60)
        counts, bin_edges = np.histogram(chaos_history, bins=10)
        total_bets = len(chaos_history)
        for bin_idx in range(10):
            percent = (counts[bin_idx] / total_bets) * 100
            bin_label = f"${bin_edges[bin_idx]:.0f} - ${bin_edges[bin_idx+1]:.0f}"
            bar = "█" * int(percent / 2) # Basic ASCII bar
            print(f"{bin_label:<20} | {percent:>5.1f}% {bar}")
            
    print("="*60)

    # 5. Generate Graph
    if plt is None:
        print("\n⚠️  Matplotlib not found. Install it to see graphs: pip install matplotlib")
        return

    try:
        print(f"\n📊 Generating Dashboard...", end="")
        
        # Create 3 subplots sharing X axis
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        plt.subplots_adjust(hspace=0.3)
        
        # Plot 1: House Profit
        ax1.set_title("House Profit: Actual vs Target", fontsize=12, fontweight='bold')
        ax1.plot(history_x, history_target, 'r--', label='Target Profit (Expected)', linewidth=1.5)
        ax1.plot(history_x, history_profit, 'g-', label='Actual Profit (Real)', linewidth=1.5)
        
        # Markers for Black Swan Events
        if show_markers:
            for idx in event_indices:
                label = "Black Swan" if idx == event_indices[0] else ""
                ax1.axvline(x=idx, color='orange', linestyle=':', alpha=0.8, linewidth=1.5, label=label)
                # Add a small text box or arrow
                ax1.annotate('💥 EVENT', xy=(idx, history_profit[idx] if idx < len(history_profit) else history_profit[-1]), 
                             xytext=(10, 20), textcoords='offset points',
                             arrowprops=dict(arrowstyle='->', color='orange'),
                             fontsize=8, color='orange', fontweight='bold',
                             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="orange", alpha=0.8))

        ax1.fill_between(history_x, history_profit, history_target, where=[a < b for a,b in zip(history_profit, history_target)], color='red', alpha=0.1, label='Loss Area')
        ax1.fill_between(history_x, history_profit, history_target, where=[a >= b for a,b in zip(history_profit, history_target)], color='green', alpha=0.1, label='Profit Area')
        ax1.set_ylabel("Profit ($)")
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)

        # Plot 2: PID Modifier M(x)
        ax2.set_title("PID Control Signal (M(x))", fontsize=12, fontweight='bold')
        ax2.plot(history_x, history_signal, color='#1f77b4', linewidth=1, label='Signal u')
        ax2.axhline(y=2.0, color='green', linestyle=':', label='Max (+2.0)')
        ax2.axhline(y=-0.9, color='red', linestyle=':', label='Min (-0.9)')
        ax2.set_ylabel("Signal Strength")
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: RTP Convergence
        ax3.set_title("RTP Convergence", fontsize=12, fontweight='bold')
        ax3.plot(history_x, history_rtp_actual, color='purple', linewidth=1.5, label='Actual RTP')
        ax3.axhline(y=target_rtp*100, color='red', linestyle='--', linewidth=2, label=f'Target ({target_rtp*100}%)')
        ax3.set_ylabel("RTP (%)")
        ax3.set_ylim(0, max(200, max(history_rtp_actual)*1.1)) # Dynamic limit but cap at 200% min for readability
        ax3.set_xlabel("Spin Count")
        ax3.legend(loc='lower right')
        ax3.grid(True, alpha=0.3)
        
        # Format X-axis to avoid scientific notation (e.g., 1e6) per user request
        from matplotlib.ticker import ScalarFormatter
        for ax in [ax1, ax2, ax3]:
            formatter = ScalarFormatter()
            formatter.set_scientific(False)
            ax.xaxis.set_major_formatter(formatter)
            ax.ticklabel_format(style='plain', axis='x')
        
        # Add a big title
        if is_recovery_test:
            status_text = f"Recovered in {recovery_spin} spins" if recovery_spin > 0 else f"Failed to recover in {max_spins} spins"
        else:
            status_text = f"Soak Test Completion: RTP {final_rtp:.2f}%"
            
        event_info = f"Event: {win_multiplier}x | Hits: {consecutive_hits} | Interval: {hit_interval}" if win_multiplier > 0 else "No Forced Events"
        # Use \$ to escape dollar signs for Matplotlib, preventing accidental math-mode font changes
        bet_info = f"Chaos Range: \${chaos_min} - \${chaos_max}" if sim_mode == 3 else f"Fixed Bet: \${bet_size}"
        
        total_spins_run = len(history_x) - 1
        header_title = f"OpenRTP Engine: {active_mode_name}\n{event_info} | {bet_info}\nTotal Spins: {total_spins_run:,} | {status_text}"
        
        fig.suptitle(header_title, fontsize=14, fontweight='bold', y=0.98)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.93]) # Make room for suptitle

        # Ensure output directory exists
        import os
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"{output_dir}/recovery_dashboard.png"
        plt.savefig(filename, dpi=150)
        print(f" Saved to \033[1;33m{filename}\033[0m")
        plt.close()
        
        # Auto-open the graph (Mac specific)
        print("🖼️  Opening graph...")
        os.system(f"open {filename}")
        
    except Exception as e:
        print(f"\n❌ Error generating graph: {e}")

if __name__ == "__main__":
    try:
        test_black_swan()
        print("\n\033[1;36m" + "="*60)
        print("      🏰 THE CHAMELOT: OpenRTP Engine Professional")
        print("           Built by Katunyu Boonchumjai")
        print("     GitHub: github.com/Katunyu-Boonchumjai")
        print("="*60 + "\033[0m")
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation Aborted.")
