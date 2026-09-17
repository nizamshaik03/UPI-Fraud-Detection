import pandas as pd
import numpy as np
import random

def generate_data(n_samples=50000):
    """
    Generates a synthetic UPI fraud detection dataset with realistic patterns.
    """
    np.random.seed(42)
    random.seed(42)

    data = []
    
    # Feature configurations
    transaction_types = ['P2P', 'P2M', 'Bill Payment', 'Recharge', 'Cashback']
    merchant_categories = ['Grocery', 'Electronics', 'Fashion', 'Utilities', 'Travel', 'Dining', 'Entertainment', 'Gambling', 'Crypto', 'Unknown']
    banks = ['SBI', 'HDFC', 'ICICI', 'Axis', 'Paytm Bank', 'Kotak', 'PNB', 'Yono', 'Unknown Bank']
    devices = ['Android', 'iOS', 'Windows', 'Linux', 'Emulator', 'Unknown']
    networks = ['4G', '5G', 'WiFi', 'VPN', 'Tor', 'Public WiFi']

    for i in range(n_samples):
        t_id = f"TXN{str(i).zfill(10)}"
        
        # Default: Legit
        is_fraud = 0
        t_type = np.random.choice(transaction_types, p=[0.4, 0.3, 0.15, 0.1, 0.05])
        amount = round(random.uniform(10, 5000), 2)
        merchant = np.random.choice(['Grocery', 'Dining', 'Utilities', 'Fashion'], p=[0.4, 0.3, 0.2, 0.1])
        sender_bank = np.random.choice(banks[:7]) # Reputable banks
        receiver_bank = np.random.choice(banks[:7])
        device = np.random.choice(['Android', 'iOS'], p=[0.7, 0.3])
        network = np.random.choice(['4G', '5G', 'WiFi'], p=[0.4, 0.3, 0.3])

        # Inject Fraud Patterns (Approx 5%)
        if random.random() < 0.05:
            is_fraud = 1
            
            # Pattern 1: High Value Transfer (The "Whale")
            if random.random() < 0.4:
                t_type = 'P2P'
                amount = round(random.uniform(50000, 200000), 2)
                device = 'Unknown'
                network = 'VPN'
            
            # Pattern 2: Suspicious Merchant (The "Gambler")
            elif random.random() < 0.4:
                t_type = 'P2M'
                amount = round(random.uniform(5000, 50000), 2)
                merchant = np.random.choice(['Gambling', 'Crypto'])
                network = np.random.choice(['Tor', 'VPN'])
                
            # Pattern 3: Tech Fraud (The "Hacker")
            else:
                amount = round(random.uniform(100, 10000), 2)
                device = 'Emulator'
                sender_bank = 'Unknown Bank'

        # Additional randomization for variety in legit data
        if is_fraud == 0:
            if random.random() < 0.1: merchant = 'Electronics' # Buying a phone isn't fraud
            if random.random() < 0.1: amount = round(random.uniform(5000, 20000), 2) # Legit high exp
            
        data.append({
            'transaction id': t_id,
            'transaction type': t_type,
            'amount (INR)': amount,
            'merchant_category': merchant,
            'sender_bank': sender_bank,
            'receiver_bank': receiver_bank,
            'device_type': device,
            'network_type': network,
            'fraud_flag': is_fraud
        })

    df = pd.DataFrame(data)
    
    # Save
    output_file = 'upi_transactions_2024.csv'
    df.to_csv(output_file, index=False)
    print(f"Generated {n_samples} transactions.")
    print(f"Fraud count: {df['fraud_flag'].sum()}")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    generate_data()
