"""
Costa Rica Crypto Tax Calculator
Calculates capital gains tax (15%) from Binance trades
"""

import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

def calculate_crypto_tax(trades_csv_path: str, tax_year: int = 2025):
    """
    Calculate capital gains tax for Costa Rica

    Args:
        trades_csv_path: Path to Binance trade history CSV
        tax_year: Year to calculate taxes for

    Returns:
        DataFrame with tax summary
    """

    # Load trades
    try:
        df = pd.read_csv(trades_csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {trades_csv_path}")
        print("\nHow to get Binance trade history:")
        print("1. Login to Binance")
        print("2. Go to Orders > Trade History")
        print("3. Click 'Export Trade History'")
        print("4. Download CSV file")
        return None

    # Check required columns
    required_cols = ['Date(UTC)', 'Side', 'Coin', 'Executed', 'Price']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        return None

    # Parse dates
    df['Date'] = pd.to_datetime(df['Date(UTC)'])

    # Filter by year
    df = df[df['Date'].dt.year == tax_year]

    if df.empty:
        print(f"No trades found for year {tax_year}")
        return None

    # Separate buys and sells
    buys = df[df['Side'] == 'BUY'].copy()
    sells = df[df['Side'] == 'SELL'].copy()

    print(f"\nProcessing {len(buys)} buys and {len(sells)} sells for {tax_year}...")

    # FIFO method for cost basis
    gains = []

    for _, sell in sells.iterrows():
        coin = sell['Coin']
        sell_amount = sell['Executed']
        sell_price = sell['Price']
        sell_value = sell_amount * sell_price

        # Find matching buys (FIFO)
        coin_buys = buys[buys['Coin'] == coin].sort_values('Date')

        remaining = sell_amount
        cost_basis = 0

        for idx, buy in coin_buys.iterrows():
            if remaining <= 0:
                break

            available = buy['Executed']
            take_amount = min(available, remaining)

            cost_basis += take_amount * buy['Price']
            remaining -= take_amount

            # Update buy record
            buys.at[idx, 'Executed'] -= take_amount

        # Calculate gain
        capital_gain = sell_value - cost_basis

        gains.append({
            'Date': sell['Date'],
            'Coin': coin,
            'Amount_Sold': sell_amount,
            'Sale_Value': sell_value,
            'Cost_Basis': cost_basis,
            'Capital_Gain': capital_gain,
            'Tax_15%': capital_gain * 0.15
        })

    # Create summary
    if not gains:
        print("No gains calculated. Make sure you have both BUY and SELL transactions.")
        return None

    gains_df = pd.DataFrame(gains)

    # Display summary
    print("\n" + "="*60)
    print(f"COSTA RICA CRYPTO TAX SUMMARY - {tax_year}")
    print("="*60)
    print(f"\nTotal Transactions: {len(gains_df)}")
    print(f"Total Capital Gains: ${gains_df['Capital_Gain'].sum():,.2f}")
    print(f"Total Tax Due (15%): ${gains_df['Tax_15%'].sum():,.2f}")

    print("\n" + "-"*60)
    print("Breakdown by Coin:")
    print("-"*60)
    coin_summary = gains_df.groupby('Coin').agg({
        'Capital_Gain': 'sum',
        'Tax_15%': 'sum',
        'Amount_Sold': 'count'
    }).round(2)
    coin_summary.columns = ['Total Gain', 'Tax Due', 'Num Trades']
    print(coin_summary.to_string())

    print("\n" + "-"*60)
    print("Monthly Breakdown:")
    print("-"*60)
    gains_df['Month'] = pd.to_datetime(gains_df['Date']).dt.to_period('M')
    monthly_summary = gains_df.groupby('Month').agg({
        'Capital_Gain': 'sum',
        'Tax_15%': 'sum'
    }).round(2)
    monthly_summary.columns = ['Total Gain', 'Tax Due']
    print(monthly_summary.to_string())

    print("\n" + "="*60)

    # Save detailed report
    report_path = f'tax_report_{tax_year}.csv'
    gains_df.to_csv(report_path, index=False)
    print(f"\nDetailed report saved: {report_path}")

    # Save summary
    summary_path = f'tax_summary_{tax_year}.txt'
    with open(summary_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write(f"COSTA RICA CRYPTO TAX SUMMARY - {tax_year}\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Transactions: {len(gains_df)}\n")
        f.write(f"Total Capital Gains: ${gains_df['Capital_Gain'].sum():,.2f}\n")
        f.write(f"Total Tax Due (15%): ${gains_df['Tax_15%'].sum():,.2f}\n\n")
        f.write("-"*60 + "\n")
        f.write("Breakdown by Coin:\n")
        f.write("-"*60 + "\n")
        f.write(coin_summary.to_string())
        f.write("\n\n" + "-"*60 + "\n")
        f.write("Monthly Breakdown:\n")
        f.write("-"*60 + "\n")
        f.write(monthly_summary.to_string())
        f.write("\n\n")
        f.write("="*60 + "\n")
        f.write("IMPORTANT NOTES FOR COSTA RICA TAX FILING:\n")
        f.write("="*60 + "\n")
        f.write("1. File Form D-162 within 15 days of the month following each sale\n")
        f.write("2. Use FIFO (First-In-First-Out) method for cost basis\n")
        f.write("3. Capital gains tax rate: 15%\n")
        f.write("4. Keep all transaction records for at least 4 years\n")
        f.write("5. File via TRIBUTA-CR portal: https://ovitribucr.hacienda.go.cr\n")
        f.write("6. Consider consulting a CR tax professional for amounts >$10,000\n")

    print(f"Summary saved: {summary_path}")
    print("\n" + "="*60)
    print("TAX CALCULATION COMPLETE")
    print("="*60)

    return gains_df


def main():
    """Main function for command-line usage"""

    print("="*60)
    print("COSTA RICA CRYPTOCURRENCY TAX CALCULATOR")
    print("="*60)
    print()

    # Get input file
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = input("Enter path to Binance trade history CSV: ").strip()

    # Get tax year
    if len(sys.argv) > 2:
        tax_year = int(sys.argv[2])
    else:
        tax_year = int(input(f"Enter tax year (default: {datetime.now().year}): ") or datetime.now().year)

    # Calculate taxes
    result = calculate_crypto_tax(csv_path, tax_year)

    if result is not None:
        print("\n✓ Tax calculation successful!")
        print("\nNext steps:")
        print("1. Review the detailed report in tax_report_*.csv")
        print("2. File Form D-162 via TRIBUTA-CR portal")
        print("3. Pay taxes within 15 days of each transaction month")
        print("4. Keep all records for 4+ years")
        print("\nConsult a tax professional if you have questions!")


if __name__ == "__main__":
    main()
