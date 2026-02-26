<<<<<<< HEAD
class RiskManager:
    def __init__(self, total_balance, risk_per_trade=0.01):
        self.total_balance = total_balance
        self.risk_per_trade = risk_per_trade

    def calculate_position(self, current_price, atr):
        # Stop Loss a 2 veces la volatilidad (ATR)
        stop_loss_dist = atr * 2
        stop_loss_price = current_price - stop_loss_dist
        
        # Dinero que estamos dispuestos a perder
        cash_to_risk = self.total_balance * self.risk_per_trade
        
        # Cálculo de unidades (N)
        if stop_loss_dist > 0:
            units = int(cash_to_risk / stop_loss_dist)
        else:
            units = 0
            
        return {
            "units": units,
            "stop_loss": round(stop_loss_price, 2),
            "take_profit": round(current_price + (stop_loss_dist * 1.5), 2),
            "risk_amount": round(cash_to_risk, 2)
=======
class RiskManager:
    def __init__(self, total_balance, risk_per_trade=0.01):
        self.total_balance = total_balance
        self.risk_per_trade = risk_per_trade

    def calculate_position(self, current_price, atr):
        # Stop Loss a 2 veces la volatilidad (ATR)
        stop_loss_dist = atr * 2
        stop_loss_price = current_price - stop_loss_dist
        
        # Dinero que estamos dispuestos a perder
        cash_to_risk = self.total_balance * self.risk_per_trade
        
        # Cálculo de unidades (N)
        if stop_loss_dist > 0:
            units = int(cash_to_risk / stop_loss_dist)
        else:
            units = 0
            
        return {
            "units": units,
            "stop_loss": round(stop_loss_price, 2),
            "take_profit": round(current_price + (stop_loss_dist * 1.5), 2),
            "risk_amount": round(cash_to_risk, 2)
>>>>>>> f166bfe0cf293ddad91f7123819bf678ce1e708d
        }