import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Offset vs Investment Mortgage Strategy Simulator")

# Sidebar inputs
st.sidebar.header("Adjustable Parameters")
initial_offset = st.sidebar.number_input("Initial Offset Amount ($)", value=100000.0, step=10000.0)
initial_investment = st.sidebar.number_input("Initial Investment Amount ($)", value=0.0, step=10000.0)
monthly_contribution = st.sidebar.number_input("Monthly Surplus ($)", value=18278.0, step=500.0)
loan_balance = st.sidebar.number_input("Initial Home Loan ($)", value=1203515.23, step=10000.0)
mortgage_rate = st.sidebar.slider("Mortgage Interest Rate (Annual %)", 0.0, 10.0, 5.89)
investment_rate = st.sidebar.slider("Investment Return (Annual %)", 0.0, 15.0, 7.0)
years = st.sidebar.slider("Simulation Length (Years)", 5, 40, 30)

# Fixed parameters
tax_rate = 45.0  # Fixed investment tax rate in %
res_invest_loan_rate = 6.74  # Investment loan interest rate (fixed)
effective_invest_loan_rate = res_invest_loan_rate * (1 - tax_rate / 100)  # After-tax cost of investment loan

# Calculations
months = years * 12
monthly_mortgage_rate = (1 + mortgage_rate / 100) ** (1/12) - 1
monthly_investment_rate = ((1 + investment_rate / 100) ** (1/12) - 1) * (1 - tax_rate / 100)

# Initialize variables
offset_bal = initial_offset
investment_bal = initial_investment
remaining_loan = loan_balance

offset_values = []
investment_values = []
loan_values = []
stage = []

for month in range(months):
    if remaining_loan > 0:
        if offset_bal < loan_balance:
            # Stage 1: build offset
            offset_bal = (offset_bal + monthly_contribution) * (1 + monthly_mortgage_rate)
            current_stage = 'Build Offset'
        else:
            # Stage 2: repay principal
            repayment = monthly_contribution
            interest = remaining_loan * monthly_mortgage_rate
            principal_payment = repayment - interest
            remaining_loan -= principal_payment
            remaining_loan = max(0, remaining_loan)
            current_stage = 'Pay Loan'
    else:
        # Stage 3: invest
        investment_bal = (investment_bal + monthly_contribution) * (1 + monthly_investment_rate)
        current_stage = 'Invest'

    offset_values.append(offset_bal)
    investment_values.append(investment_bal)
    loan_values.append(remaining_loan)
    stage.append(current_stage)

# Create DataFrame
months_range = np.arange(1, months + 1)
df = pd.DataFrame({
    'Month': months_range,
    'Offset Balance': offset_values,
    'Investment Balance': investment_values,
    'Remaining Loan': loan_values,
    'Stage': stage
})
df['Year'] = df['Month'] / 12

# Line Chart
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df['Year'], df['Offset Balance'], label='Offset Balance')
ax.plot(df['Year'], df['Investment Balance'], label='Investment Balance')
ax.plot(df['Year'], df['Remaining Loan'], label='Mortgage Principal Remaining')
ax.set_title("Mortgage Strategy Projection")
ax.set_xlabel("Years")
ax.set_ylabel("Balance ($)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Show Table
st.subheader("Yearly Snapshot")
st.dataframe(df[df['Month'] % 12 == 0][['Year', 'Offset Balance', 'Investment Balance', 'Remaining Loan', 'Stage']].reset_index(drop=True))
