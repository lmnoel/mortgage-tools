# Mortgage Tools

[![Build Status](https://github.com/lmnoel/mortgage-tools/actions/workflows/python-package.yml/badge.svg)](https://github.com/lmnoel/mortgage-tools/actions/workflows/python-package.yml)
[![PyPI Latest Release](https://img.shields.io/pypi/v/mortgage_tools.svg)](https://pypi.org/project/mortgage_tools/)
![License](https://img.shields.io/pypi/l/mortgage_tools)
![Python versions](https://img.shields.io/pypi/pyversions/mortgage_tools)

Mortgage cost/payoff calculators online are a dime a dozen, but they tend to assume you are making consistent extra
payments each month, or a single one-time payment. I could not find a single one that was flexible and detailed enough
to answer the questions I had about my mortgage.

This package includes some sensible default plots for visualizing generated data, but exposes all of the underlying 
primitives for manipulation as needed.

## Questions you can answer using Mortgage Tools
 * [What will my total costs be over the lifetime of the loan?](#what-will-my-total-costs-be-over-the-lifetime-of-the-loan)
 * [What will my monthly costs be?](#what-will-my-monthly-costs-be)
 * [How do two loan options compare?](#how-do-two-loan-options-compare)
 * [When will the loan be paid off if I pay C extra every month/3 months/year?](#when-will-the-loan-be-paid-off-if-I-pay-c-extra-every-month3-monthsyear)
 * [When will the loan be paid off, given the current remaining principal and current loan period?](#when-will-the-loan-be-paid-off-given-the-current-remaining-principal-and-current-loan-period)
 * [What is the impact of a marginal X dollars in reducing the loan payoff period?](#what-is-the-impact-of-a-marginal-x-dollars-in-reducing-the-loan-payoff-period)
 * [How will changes in interest rates affect my total costs?](#how-will-changes-in-interest-rates-affect-my-total-costs)
 * [How will different initial principal amounts affect my total costs?](#how-will-different-initial-principal-amounts-affect-my-total-costs)
 * [If I want to pay off a loan by month X how much extra do I need to pay per month?](#if-I-want-to-pay-off-a-loan-by-month-x-how-much-extra-do-I-need-to-pay-per-month)


### What will my total costs be over the lifetime of the loan?

```python
from mortgage_tools.calculation import Loan
from mortgage_tools.plot import plot_amortization_components

loan = Loan(initial_principal=1_000_000, term_in_months=360, annual_interest_rate=.065)

loan.summarize()
>>            Interest rate: 6.50%
>>            Payoff period: 360 months [30 year(s), 0 month(s)]
>>            Cumulative interest paid: $1275444.88
>>            Cumulative P&I paid: $2275444.88
>>            Percent of total payments to principal: 43.95%

plot_amortization_components(loan.amortization_table())
```
![Amortization components](images/fig1.png)

### What will my monthly costs be?

```python
from mortgage_tools.calculation import Loan
from mortgage_tools.plot import plot_monthly_payments, plot_monthly_payments_relative

loan = Loan(initial_principal=1_000_000, term_in_months=360, annual_interest_rate=.065)

loan.standard_monthly_payment()
>> 6320.68

amortization_table = loan.amortization_table()
plot_monthly_payments(amortization_table)
plot_monthly_payments_relative(amortization_table)
```
![Monthly payments](images/fig2.png)
![Relative monthly payments](images/fig3.png)

### How do two loan options compare?

```python
from mortgage_tools.calculation import Loan
from mortgage_tools.plot import plot_relative_amortization_tables

loan1 = Loan(initial_principal=1_000_000, term_in_months=360, annual_interest_rate=.065)
loan2 = Loan(initial_principal=1_200_000, term_in_months=360, annual_interest_rate=.065)

loan2.summarize() - loan1.summarize()
>>             Payoff period: 0 months less [0 year(s), 0 month(s)]
>>             Cumulative interest paid: $255086.03 more
>>             Cumulative P&I paid: $455086.03 more
plot_relative_amortization_tables(loan1.amortization_table(),loan2.amortization_table())
```
![Compare loan option 1 to loan option 2](images/fig4.png)

### When will the loan be paid off if I pay C extra every month/3 months/year?

```python
from mortgage_tools.calculation import Loan
from mortgage_tools.plot import plot_relative_amortization_tables

loan = Loan(initial_principal=1_000_000, term_in_months=360, annual_interest_rate=.065)
default_amortization_table = loan.amortization_table()
default_loan_summary = loan.summarize()

# model any combination of early payments to principal
loan.apply_monthly_recurring_payment(additional_payment=200)
loan.apply_monthly_recurring_payment(additional_payment=100, start_month=45, end_month=48)
loan.apply_annual_recurring_payment(additional_payment=5_000)
loan.apply_ad_hoc_payment(additional_payment=100_000, month=200)

loan.summarize() - default_loan_summary
>>             Payoff period: 101 months less [9 year(s), 7 month(s)]
>>             Cumulative interest paid: $380652.76 less
>>             Cumulative P&I paid: $380652.76 less

plot_relative_amortization_tables(default_amortization_table, loan.amortization_table())
```
![Loan comparisons with early payments applied](images/fig5.png)

### When will the loan be paid off, given the current remaining principal and current loan period?

```python
from mortgage_tools.calculation import Loan
from mortgage_tools.plot import plot_relative_amortization_tables

loan = Loan(initial_principal=1_000_000, term_in_months=360, annual_interest_rate=.065)
default_amortization_table = loan.amortization_table()
default_loan_summary = loan.summarize()

# no need to specify when each additional principal payment was made
loan.set_current_status(current_month=55, remaining_principal=784_892, interest_paid=200_368)

loan.payoff_period_months()
>> 261

loan.summarize()
>>             Interest rate: 6.50%
>>             Payoff period: 261 months [21 year(s), 9 month(s)]
>>             Cumulative interest paid: $722045.96
>>             Cumulative P&I paid: $1722045.96
>>             Percent of total payments to principal: 58.07%

loan.summarize() - default_loan_summary
>>            Payoff period: 99 months less [9 year(s), 9 month(s)]
>>            Cumulative interest paid: $553399.10 less
>>            Cumulative P&I paid: $553399.10 less

plot_relative_amortization_tables(default_amortization_table, loan.amortization_table(), "../../images/fig5.png")
```
![Current loan status with early payments applied](images/fig6.png)
* Precise amortization info for loans with a current status applied cannot be determined, so are omitted from any plots.

### What is the impact of a marginal X dollars in reducing the loan payoff period?
```python3
from mortgage_tools.calculation import Loan
from mortgage_tools.optimization import payoff_curve
from mortgage_tools.plot import plot_payoff_curve

loan = Loan(initial_principal=1_000_000, term_in_months=360, annual_interest_rate=.065)
curve = payoff_curve(loan)
curve.head(3)
>>                payoff_period
>> monthly_extra               
>> 0                        360
>> 100                      344
>> 200                      329
plot_payoff_curve(curve)
```
![Impact of additional monthly payments on length of loan](images/fig7.png)

### How will changes in interest rates affect my total costs?
```python3
from mortgage_tools.plot import plot_interest_rate_curve

plot_interest_rate_curve(initial_principal=1_000_000, term_in_months=360, min_interest_rate=0.05, max_interest_rate=0.06)
```
![Interest rate curve](images/fig8.png)

### How will different initial principal amounts affect my total costs?
```python3
from mortgage_tools.plot import plot_principal_curve

plot_principal_curve(min_principal=1_000_000, max_principal=1_200_000, interest_rate=0.034, term_in_months=360)
```
![Principal curve](images/fig9.png)

### If I want to pay off a loan by month X how much extra do I need to pay per month?
```python3
from mortgage_tools.calculation import Loan
from mortgage_tools.optimization import payoff_by_date

loan = Loan(initial_principal=1_000_000, term_in_months=360, annual_interest_rate=.065)

# payoff by year 22 month 6 (starting from the beginning)
payoff_by_date(loan, desired_payoff_month=270)
>> 744.63

# already made some additional payments
loan.set_current_status(current_month=8, remaining_principal=955_000, interest_paid=45_000)
payoff_by_date(loan, desired_payoff_month=270)
>> 500.49
```

## Disclaimer

You should verify any facts and figures with a financial professional before making any financial decisions based on these results.