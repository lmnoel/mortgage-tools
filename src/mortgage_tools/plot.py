from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame

from mortgage_tools.calculation import LoanSummary
from mortgage_tools.optimization import interest_rate_curve, principal_curve

pd.set_option('display.float_format', '{:.2f}'.format)


def plot_amortization_components(df: DataFrame, figure_output: str = None):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['remaining_principal'], label='Remaining principal')
    plt.plot(df.index, df['cumulative_principal_paid'], label='Cumulative principal paid')
    plt.plot(df.index, df['cumulative_interest_paid'], label='Cumulative interest paid')
    plt.ylabel('Money')
    plt.xlabel('Months')
    plt.title('Mortgage Amortization')
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    # x-axis ticks every 2 years
    plt.xticks(np.arange(0, len(df) + 1, 24))
    plt.legend()

    _render_plot(figure_output)


def plot_monthly_payments(df: DataFrame, figure_output: str = None):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['principal'], label='Amount paid to principal')
    plt.plot(df.index, df['interest'], label='Amount paid to interest')
    plt.plot(df.index, df['payment'], label='Payment')
    plt.ylabel('Money')
    plt.xlabel('Months')
    plt.title('Monthly Payments')
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    # x-axis ticks every 2 years
    plt.xticks(np.arange(0, len(df) + 1, 24))
    plt.legend()

    _render_plot(figure_output)


def plot_monthly_payments_relative(df: DataFrame, figure_output: str = None):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['principal'] / df['payment'] * 100)
    plt.ylabel('%')
    plt.xlabel('Months')
    plt.title('Percent of monthly payment going toward principal')
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    # x-axis ticks every 2 years
    plt.xticks(np.arange(0, len(df) + 1, 24))

    _render_plot(figure_output)


def plot_relative_amortization_tables(table_1: DataFrame, table_2: DataFrame, figure_output: str = None):
    plt.figure(figsize=(12, 6))
    plt.plot(table_1.index, table_1['remaining_principal'], label='Remaining Principal (Option 1 schedule)',
             color='blue')
    plt.plot(table_2.index, table_2['remaining_principal'], label='Remaining Principal (Option 2 schedule)',
             color='blue', linestyle='--')
    plt.plot(table_1.index, table_1['cumulative_principal_paid'], label='Cumulative Principal paid (Option 1 schedule)',
             color='green')
    plt.plot(table_2.index, table_2['cumulative_principal_paid'],
             label='Cumulative Principal paid (Option 2 schedule)', color='green', linestyle='--')
    plt.plot(table_1.index, table_1['cumulative_interest_paid'], label='Cumulative Interest paid (Option 1 schedule)',
             color='red')
    plt.plot(table_2.index, table_2['cumulative_interest_paid'],
             label='Cumulative Interest paid (Option 2 schedule)', color='red', linestyle='--')
    plt.ylabel('Money')
    plt.xlabel('Months')
    plt.title('Mortgage Amortization')
    plt.ticklabel_format(style='plain', axis='y')
    plt.grid(True)
    # x-axis ticks every 2 years
    plt.xticks(np.arange(0, len(table_1) + 1, 24))
    plt.legend()

    _render_plot(figure_output)


def plot_payoff_curve(payoff_curve: DataFrame, figure_output: str = None):
    plt.figure(figsize=(12, 6))
    plt.plot(payoff_curve.index, payoff_curve['payoff_period'], label='Monthly additional payment to principal',
             color='blue')
    plt.ylabel('Months')
    plt.xlabel('Extra principal payment per month')
    plt.title('Reduction in lifetime of loan per marginal extra principal payment')
    plt.grid(True)

    _render_plot(figure_output)


def plot_interest_rate_curve(initial_principal: int, term_in_months: int, min_interest_rate: float,
                             max_interest_rate: float, figure_output: str = None):
    df = interest_rate_curve(initial_principal, min_interest_rate, max_interest_rate, term_in_months)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(df.index, df['standard_monthly_payment'], label='Standard monthly payment',
             color='blue')
    ax2 = ax1.twinx()
    ax2.plot(df.index, df['cumulative_interest_paid'], label='Total interest cost',
             color='red')
    ax1.set_ylabel('Standard monthly payment (P&I)')
    ax2.set_ylabel('Total payments to interest over the lifetime of the loan')
    ax1.set_xlabel('Annual interest rate (out of 1.00)')
    plt.title('Impact of higher interest rates on loan costs')
    plt.ticklabel_format(style='plain', axis='y')
    plt.grid(True)

    _render_plot(figure_output)


def plot_principal_curve(min_principal: int, max_principal: int, interest_rate: float, term_in_months: int,
                         figure_output: str = None):
    df = principal_curve(min_principal, max_principal, interest_rate, term_in_months)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(df.index, df['standard_monthly_payment'], label='Standard monthly payment',
             color='blue')
    ax2 = ax1.twinx()
    ax2.plot(df.index, df['cumulative_interest_paid'], label='Total interest cost',
             color='red')
    ax1.set_ylabel('Standard monthly payment (P&I)')
    ax2.set_ylabel('Total payments to interest over the lifetime of the loan')
    ax1.set_xlabel('Initial principal')
    plt.title('Impact of higher initial principal amount on loan costs')
    plt.ticklabel_format(style='plain', axis='y')
    plt.ticklabel_format(style='plain', axis='x')
    plt.grid(True)

    _render_plot(figure_output)


def _df_from_loan_summaries(loan_summaries: List[LoanSummary], index: str, selected_columns: List[str]) -> DataFrame:
    data_points = []
    for loan_summary in loan_summaries:
        data_point = {index: getattr(loan_summary, index)} | {col: getattr(loan_summary, col) for col in
                                                              selected_columns}
        data_points.append(data_point)
    df = DataFrame.from_records(data_points)
    df.set_index(index, inplace=True)
    return df


def _render_plot(file: Optional[str]):
    if file:
        plt.savefig(file)
    else:
        plt.show()
