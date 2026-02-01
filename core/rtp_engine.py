import numpy as np
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger("RTP_Engine_Reels")

@dataclass
class Symbol:
    name: str
    id: int
    payout_multiplier: float
    # Type removed: Logic will depend on Payout (Vi) directly
    # Sensitivity removed: Not in flowchart

@dataclass
class PIDConfig:
    kp: float
    ki: float
    kd: float 

class Reel:
    def __init__(self, strip: List[Symbol], base_weights: List[float]):
        """
        Initialize a Reel.
        strip: The physical list of symbols.
        base_weights: The initial weight (Pi initialization).
        """
        self.strip = strip
        self.base_weights = np.array(base_weights, dtype=np.float64)
        self.current_weights = self.base_weights.copy()
        
    def adjust_weights(self, signal: float):
        """
        Adjust weights using Flowchart Logic.
        Equation: weight_new = weight_old * (1 + modified)
        
        Modified Equation (Identified):
        - Inputs: Signal (u), Payout (Vi)
        - Logic: If Vi > 0 (Win), move with signal. If Vi = 0 (Loss), move against.
        """
        new_weights = self.base_weights.copy()
        
        for i, symbol in enumerate(self.strip):
            # Identify Direction based on Vi (Payout)
            # If Payout > 0: It increases Player Return -> Correlates with Loosen (+Sig)
            # If Payout = 0: It decreases Player Return % -> Correlates with Tighten (-Sig)
            
            direction = 1.0 if symbol.payout_multiplier > 0 else -1.0
            
            # Modified term
            modified = signal * direction
            
            # Equation: weight_new = weight_old * (1 + modified)
            multiplier = 1.0 + modified
            multiplier = max(0.01, multiplier) 
            
            new_weights[i] *= multiplier

        self.current_weights = new_weights

    def spin(self) -> Symbol:
        """
        Spin the reel using current weights.
        """
        total_weight = np.sum(self.current_weights)
        if total_weight <= 0: return self.strip[0] 
        
        probs = self.current_weights / total_weight
        stop_index = np.random.choice(len(self.strip), p=probs)
        return self.strip[stop_index]

class SlotMachineController:
    def __init__(self, target_rtp: float, config: PIDConfig):
        """
        Variables:
        - Target(n) derived from H (house_edge)
        """
        self.target_rtp = target_rtp
        self.house_edge = 1.0 - target_rtp
        self.config = config
        
        # State Tracking
        self.total_wagered = 0.0
        self.current_profit = 0.0
        
        # PID State
        self._prev_error = 0.0
        self._integral = 0.0          # Long-term memory (Precision)
        self._reactive_integral = 0.0 # Short-term weighted memory (Response)
        
        # Initialize Symbols (Target-near payouts for Demo)
        self.sym_miss = Symbol("Miss", 0, 0.0)
        self.sym_lemon = Symbol("Lemon", 1, 2.0) # Medium win
        self.sym_bar = Symbol("Bar", 2, 10.0)    # Major win
        self.sym_seven = Symbol("777", 3, 40.0)
        self.sym_jackpot = Symbol("Jackpot", 4, 200.0)
        
        # Construct Reel Strips (92% Natural RTP base)
        self.strip_template = (
            [self.sym_miss] * 1 +   # 5% Miss
            [self.sym_lemon] * 15 + # 75% Lemon
            [self.sym_bar] * 4      # 20% Bar
        )
        base_weights = [10.0] * len(self.strip_template)
        
        self.reels = [
            Reel(self.strip_template, base_weights),
            Reel(self.strip_template, base_weights),
            Reel(self.strip_template, base_weights)
        ]

    def calculate_step(self, payout: float, wager: float):
        """
        Update state and calculate PID signal based on Flowchart.
        
        Flowchart Logic:
        1. Turnover = Sum(Bet)
        2. Target = HouseEdge * Turnover
        3. ActualProfit = Sum(Bet - Payout)
        4. Error(%) = ((ActualProfit - Target) / Turnover) * 100
        5. PID -> u
        6. Clamping -> [-0.7, 0.425]
        """
        self.total_wagered += wager
        self.current_profit += (wager - payout)
        
        # Avoid divide by zero on first spin
        if self.total_wagered == 0:
            return self.current_profit, 0.0, 0.0
        
        # 1. Target (H * Tn)
        target_profit = self.total_wagered * self.house_edge
        
        # 2. Error (%) 
        # e(n) = (Pn - Target(n)) / Tn * 100
        error_percent = ((self.current_profit - target_profit) / self.total_wagered) * 100.0
        
        # PID Logic (Faster response for demo)
        dt = 1.0 
        
        # P-Term
        p_out = 0.15 * error_percent
        
        # Dual-Path Memory Logic (Weighted Memory)
        # 1. Base Integrator: 100% precision (No leak, keeps long-term target)
        self._integral += (error_percent * dt)
        self._integral = max(-20.0, min(20.0, self._integral))
        
        # 2. Reactive Integrator: Focused on recent "Emotional" response
        # Weight recent error 2x but decay old memory (0.99)
        self._reactive_integral = (self._reactive_integral * 0.99) + (error_percent * 2.0 * dt)
        self._reactive_integral = max(-15.0, min(15.0, self._reactive_integral))
        
        # Combined I-Term
        i_out = self.config.ki * (self._integral + self._reactive_integral)
        
        # D-Term
        derivative = (error_percent - self._prev_error) / dt
        d_out = self.config.kd * derivative
        
        self._prev_error = error_percent
        
        # Total Signal u
        u = p_out + i_out + d_out
        
        # Widened Clamping for Demo (Allow more aggressive loosening)
        # Upper: 2.0 (Loosen), Lower: -0.9 (Tighten)
        if u > 2.0:
            u_clamped = 2.0
        elif u < -0.9:
            u_clamped = -0.9
        else:
            u_clamped = u
            
        return self.current_profit, target_profit, u_clamped



    def spin_batch(self, batch_size: int, bet_amount: float = 1.0) -> Tuple[float, float, float, float]:
        bet_size = bet_amount
        batch_wagered = batch_size * bet_size
        batch_payout = 0.0
        
        # We need to execute the loop one by one to simulate real-time PID
        last_signal = 0.0
        last_target = 0.0
        
        for _ in range(batch_size):
            # 1. Update State & Get Signal (Based on previous result)
            curr, last_target, last_signal = self.calculate_step(0, bet_size) # Pre-wager update
            
            # 2. Adjust Reels
            for reel in self.reels:
                reel.adjust_weights(last_signal)
            
            # 3. Spin
            r1 = self.reels[0].spin()
            r2 = self.reels[1].spin()
            r3 = self.reels[2].spin()
            
            spin_payout = 0.0
            if r1.id == r2.id == r3.id:
                spin_payout = bet_size * r1.payout_multiplier
            
            # Update profit with payout
            self.current_profit -= spin_payout # Payout reduces profit
            batch_payout += spin_payout
            
    
        return self.current_profit, last_target, last_signal, self.reels[0].current_weights[0]
        



