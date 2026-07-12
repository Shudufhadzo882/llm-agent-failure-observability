import json
import numpy as np
from confluent_kafka import Consumer

# Mock history to simulate rolling averages
account_history = {}

def trigger_alarm(transaction, z_score):
    """The Alarm: In production, this pushes to a webhook or Power BI dataset."""
    print("\n" + "="*50)
    print("!!! ALARM: LIQUIDITY RISK DETECTED !!!")
    print(f"Account:  {transaction['nameOrig']}")
    print(f"Amount:   ZAR {transaction['amount']:,.2f}")
    print(f"Z-Score:  {z_score:.2f} (Highly Anomalous)")
    print("="*50 + "\n")

def process_transaction(msg_value, account_key='nameOrig'):
    data = json.loads(msg_value)
    account = data[account_key]
    amount = float(data['amount'])
    
    # Initialize account history if new
    if account not in account_history:
        account_history[account] = []
        
    history = account_history[account]
    
    # Only calculate Z-score if we have enough historical data points
    if len(history) >= 5:
        mu = np.mean(history)
        sigma = np.std(history)
        
        # Avoid division by zero
        if sigma > 0:
            z_score = (amount - mu) / sigma
            
            # ALARM THRESHOLD: 3 Standard Deviations
            if z_score > 3:
                trigger_alarm(data, z_score)
                data['risk_flag'] = 'HIGH' # Tag it before sending to the database
                
    # Update history and keep a rolling window of the last 20 transactions
    history.append(amount)
    account_history[account] = history[-20:]

# Note: Kafka consumer connection code omitted for brevity; simulated using local dataset instead.

alarm_count = 0

def trigger_alarm_with_counter(transaction, z_score):
    global alarm_count
    alarm_count += 1
    if alarm_count <= 10:
        original_trigger_alarm(transaction, z_score)
    elif alarm_count == 11:
        print("... (further alarms of this run silenced to avoid log spam) ...")

# Override trigger_alarm to count them
original_trigger_alarm = trigger_alarm
trigger_alarm = trigger_alarm_with_counter

if __name__ == "__main__":
    import pandas as pd
    import kagglehub
    from kagglehub import KaggleDatasetAdapter

    print("Loading Paysim dataset...")
    file_path = "paysim.csv"
    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        "moonknightmarvel/paysim",
        file_path,
        pandas_kwargs={"nrows": 100000}
    )
    print(f"Loaded {len(df)} transactions.")
    
    # Run 1: Sender Accounts (nameOrig)
    print("\n--- RUN 1: Analyzing Sender Accounts (nameOrig) ---")
    alarm_count = 0
    account_history.clear()
    
    for index, row in df.iterrows():
        transaction_dict = row.to_dict()
        for k, v in transaction_dict.items():
            if isinstance(v, (np.integer, np.int64)):
                transaction_dict[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                transaction_dict[k] = float(v)
        
        msg_value = json.dumps(transaction_dict)
        process_transaction(msg_value, account_key='nameOrig')
        
    print(f"Run 1 Complete! Total anomalies detected for Senders (nameOrig): {alarm_count}")
    
    # Run 2: Recipient Accounts (nameDest)
    print("\n--- RUN 2: Analyzing Recipient Accounts (nameDest) ---")
    alarm_count = 0
    account_history.clear()
    
    for index, row in df.iterrows():
        transaction_dict = row.to_dict()
        for k, v in transaction_dict.items():
            if isinstance(v, (np.integer, np.int64)):
                transaction_dict[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                transaction_dict[k] = float(v)
        
        msg_value = json.dumps(transaction_dict)
        process_transaction(msg_value, account_key='nameDest')
        
    print(f"Run 2 Complete! Total anomalies detected for Recipients (nameDest): {alarm_count}")