#!/usr/bin/env python3
"""
Blockchain Forensics Analysis for RICO Evidence Processing
Analyzes 26,931 transactions for money laundering patterns
"""

import pandas as pd
import json
from datetime import datetime

# File paths
CSV_FILES = [
    "/Users/breydentaylor/certainly/noteworthy-raw/shurka123.eth-self-owned&self-controlled.csv",
    "/Users/breydentaylor/certainly/noteworthy-raw/fund_transactions_10k^1_export-0x66b870ddf78c975af5cd8edc6de25eca81791de1.csv",
    "/Users/breydentaylor/certainly/noteworthy-raw/gang_10k^2_export-0x4f368e2d4612fef0b923667d19183785a5d3c950.csv"
]

OUTPUT_FILE = "/Users/breydentaylor/certainly/visualizations/blockchain_analysis.json"

# Target addresses
STAKE_ADDRESS = "0xa1a50f693a3893dfec3750d38eb2fc458d5004a4"
MEXC_ADDRESS = "0xf8c448c9b9adb89fcf2ff95100314d2ec1d7a9e2"

# ETH price for USD conversion (approximate average)
ETH_PRICE_USD = 2500

def parse_amount(amount_str):
    """Parse amount string, removing commas and converting to float"""
    if pd.isna(amount_str) or amount_str == '':
        return 0.0
    # Remove commas and convert to float
    return float(str(amount_str).replace(',', ''))

def load_and_combine_csvs():
    """Load all CSVs and combine into single DataFrame"""
    all_data = []

    # Load shurka123.eth file (different structure)
    print(f"Loading shurka123.eth transactions...")
    df1 = pd.read_csv(CSV_FILES[0])
    # Standardize columns
    df1_standardized = pd.DataFrame({
        'Hash': df1.get('Hash', ''),
        'From': df1.get('From', ''),
        'To': df1.get('To', ''),
        'Amount': df1['Amount'].apply(parse_amount) if 'Amount' in df1.columns else 0,
        'Token_symbol': df1.get('Token_symbol', ''),
        'Date': df1.get('Date', ''),
        'Chain': df1.get('Chain', 'eth')
    })
    all_data.append(df1_standardized)
    print(f"  Loaded {len(df1)} transactions from shurka123.eth")

    # Load fund transactions
    print(f"Loading fund transactions...")
    df2 = pd.read_csv(CSV_FILES[1])
    # Standardize columns
    df2_standardized = pd.DataFrame({
        'Hash': df2.get('Transaction Hash', ''),
        'From': df2.get('From', ''),
        'To': df2.get('To', ''),
        'Amount': df2['Value_IN(ETH)'].apply(parse_amount) if 'Value_IN(ETH)' in df2.columns else 0,
        'Token_symbol': 'ETH',
        'Date': df2.get('DateTime (UTC)', ''),
        'Chain': 'eth'
    })
    all_data.append(df2_standardized)
    print(f"  Loaded {len(df2)} transactions from fund wallet")

    # Load gang transactions
    print(f"Loading gang transactions...")
    df3 = pd.read_csv(CSV_FILES[2])
    # Standardize columns
    df3_standardized = pd.DataFrame({
        'Hash': df3.get('Transaction Hash', ''),
        'From': df3.get('From', ''),
        'To': df3.get('To', ''),
        'Amount': df3['Value_IN(ETH)'].apply(parse_amount) if 'Value_IN(ETH)' in df3.columns else 0,
        'Token_symbol': 'ETH',
        'Date': df3.get('DateTime (UTC)', ''),
        'Chain': 'eth'
    })
    all_data.append(df3_standardized)
    print(f"  Loaded {len(df3)} transactions from gang wallet")

    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)

    # Ensure From/To addresses are lowercase for comparison
    combined_df['From'] = combined_df['From'].str.lower()
    combined_df['To'] = combined_df['To'].str.lower()

    print(f"\nTotal combined transactions: {len(combined_df)}")

    return combined_df

def identify_large_transfers(df, threshold_eth=200):
    """Identify transactions >= threshold ETH"""
    print(f"\n=== Identifying transfers >= {threshold_eth} ETH ===")

    # Filter for ETH/AVAX transactions
    eth_txs = df[df['Token_symbol'].isin(['ETH', 'AVAX', 'Ether'])].copy()

    # Filter by threshold
    large_txs = eth_txs[eth_txs['Amount'] >= threshold_eth].copy()

    # Calculate USD value
    large_txs['Amount_USD'] = large_txs['Amount'] * ETH_PRICE_USD

    # Sort by amount
    large_txs = large_txs.sort_values('Amount', ascending=False)

    print(f"Found {len(large_txs)} large transfers (>= {threshold_eth} ETH)")

    # Convert to list of dicts
    large_transfers_list = []
    for _, row in large_txs.iterrows():
        large_transfers_list.append({
            'hash': row['Hash'],
            'amount_eth': float(row['Amount']),
            'amount_usd': float(row['Amount_USD']),
            'from': row['From'],
            'to': row['To'],
            'date': str(row['Date']),
            'chain': row['Chain']
        })

    return large_transfers_list

def identify_stake_deposits(df):
    """Identify Stake.com deposits"""
    print(f"\n=== Identifying Stake.com deposits ===")

    stake_txs = df[df['To'] == STAKE_ADDRESS.lower()].copy()

    # Calculate totals
    total_eth = stake_txs['Amount'].sum()
    total_usd = total_eth * ETH_PRICE_USD

    print(f"Found {len(stake_txs)} deposits to Stake.com")
    print(f"Total ETH: {total_eth:.4f}")
    print(f"Total USD: ${total_usd:,.2f}")

    return {
        'count': len(stake_txs),
        'total_eth': float(total_eth),
        'total_usd': float(total_usd),
        'transactions': [
            {
                'hash': row['Hash'],
                'amount_eth': float(row['Amount']),
                'from': row['From'],
                'date': str(row['Date'])
            }
            for _, row in stake_txs.iterrows()
        ]
    }

def identify_mexc_usage(df):
    """Identify MEXC exchange usage"""
    print(f"\n=== Identifying MEXC exchange usage ===")

    mexc_txs = df[(df['To'] == MEXC_ADDRESS.lower()) | (df['From'] == MEXC_ADDRESS.lower())].copy()

    # Calculate totals
    total_eth = mexc_txs['Amount'].sum()

    print(f"Found {len(mexc_txs)} transactions with MEXC")
    print(f"Total ETH: {total_eth:.4f}")

    return {
        'count': len(mexc_txs),
        'total_eth': float(total_eth),
        'transactions': [
            {
                'hash': row['Hash'],
                'amount_eth': float(row['Amount']),
                'from': row['From'],
                'to': row['To'],
                'date': str(row['Date'])
            }
            for _, row in mexc_txs.iterrows()
        ]
    }

def cluster_wallets(df):
    """Cluster wallets by transaction patterns"""
    print(f"\n=== Clustering wallets by activity ===")

    # Filter for ETH/AVAX only to avoid token distortion
    eth_only = df[df['Token_symbol'].isin(['ETH', 'AVAX', 'Ether'])].copy()

    # Group by From address
    wallet_groups = eth_only.groupby('From').agg({
        'Amount': 'sum',
        'Hash': 'count',
        'To': lambda x: list(set(x))
    }).reset_index()

    wallet_groups.columns = ['wallet', 'total_volume_eth', 'tx_count', 'related_wallets']

    # Calculate USD value
    wallet_groups['total_volume_usd'] = wallet_groups['total_volume_eth'] * ETH_PRICE_USD

    # Sort by volume
    wallet_groups = wallet_groups.sort_values('total_volume_eth', ascending=False)

    print(f"Identified {len(wallet_groups)} unique wallets (ETH/AVAX only)")

    # Convert to list of dicts (top 50 only)
    wallet_clusters = []
    for _, row in wallet_groups.head(50).iterrows():
        wallet_clusters.append({
            'main_wallet': row['wallet'],
            'related_wallets': row['related_wallets'][:20],  # Limit related wallets
            'total_volume_eth': float(row['total_volume_eth']),
            'total_volume_usd': float(row['total_volume_usd']),
            'transaction_count': int(row['tx_count'])
        })

    return wallet_clusters

def calculate_total_proceeds(df):
    """Calculate total proceeds in USD"""
    print(f"\n=== Calculating total proceeds ===")

    # Sum all ETH/AVAX amounts
    eth_txs = df[df['Token_symbol'].isin(['ETH', 'AVAX', 'Ether'])]
    total_eth = eth_txs['Amount'].sum()
    total_usd = total_eth * ETH_PRICE_USD

    print(f"Total ETH volume: {total_eth:,.4f}")
    print(f"Total USD value: ${total_usd:,.2f}")

    return float(total_usd)

def main():
    print("=" * 80)
    print("BLOCKCHAIN FORENSICS ANALYSIS FOR RICO EVIDENCE")
    print("=" * 80)

    # Step 1: Load and combine data
    df = load_and_combine_csvs()

    # Step 2: Identify large transfers (>= 200 ETH)
    large_transfers = identify_large_transfers(df, threshold_eth=200)

    # Step 3: Identify Stake.com deposits
    stake_deposits = identify_stake_deposits(df)

    # Step 4: Identify MEXC usage
    mexc_usage = identify_mexc_usage(df)

    # Step 5: Cluster wallets
    wallet_clusters = cluster_wallets(df)

    # Step 6: Calculate total proceeds
    total_proceeds = calculate_total_proceeds(df)

    # Step 7: Generate analysis JSON
    print(f"\n=== Generating blockchain_analysis.json ===")

    analysis_data = {
        'analysis_date': datetime.now().isoformat(),
        'total_transactions': len(df),
        'large_transfers': large_transfers,
        'stake_deposits': stake_deposits,
        'mexc_usage': mexc_usage,
        'wallet_clusters': wallet_clusters,
        'total_proceeds_usd': total_proceeds,
        'summary': {
            'large_transfers_count': len(large_transfers),
            'stake_deposits_count': stake_deposits['count'],
            'mexc_usage_count': mexc_usage['count'],
            'unique_wallets': len(wallet_clusters),
            'total_volume_eth': float(df[df['Token_symbol'].isin(['ETH', 'AVAX', 'Ether'])]['Amount'].sum()),
            'tier1_threshold_eth': 200
        }
    }

    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(analysis_data, f, indent=2)

    print(f"Analysis saved to: {OUTPUT_FILE}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total Transactions Analyzed: {len(df):,}")
    print(f"Large Transfers (>= 200 ETH): {len(large_transfers)}")
    print(f"Stake.com Deposits: {stake_deposits['count']} (${stake_deposits['total_usd']:,.2f})")
    print(f"MEXC Exchange Usage: {mexc_usage['count']} transactions")
    print(f"Total Proceeds: ${total_proceeds:,.2f}")

    print("\n=== TOP 5 LARGEST TRANSFERS ===")
    for i, tx in enumerate(large_transfers[:5], 1):
        print(f"{i}. {tx['amount_eth']:.4f} ETH (${tx['amount_usd']:,.2f}) - {tx['date']}")
        print(f"   From: {tx['from'][:20]}...")
        print(f"   To: {tx['to'][:20]}...")
        print(f"   Hash: {tx['hash'][:20]}...")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
