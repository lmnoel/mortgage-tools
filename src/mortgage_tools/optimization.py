from copy import deepcopy
from typing import Generator, List

from pandas import DataFrame

from mortgage_tools.calculation import Loan, LoanSummary

PAYOFF_CURVE_STEP_SIZE_DOLLARS = 100
INTEREST_RATE_STEP_SIZE = .001
PRINCIPAL_STEP_SIZE = 1_000


def payoff_curve(loan: Loan, min_extra_payoff: int = 0, max_extra_payoff: int = None) -> DataFrame:
    """
    Analyze the impact of a marginal increase in monthly extra payments to principal on decreasing
    the payoff period of the loan.

    :param loan: a Loan object
    :param min_extra_payoff: (optional, defaults to 0) minimum additional monthly payment to principal to consider
    :param max_extra_payoff: (optional, defaults to 3x the standard monthly payment) minimum additional monthly payment
        to principal to consider
    :return: A DataFrame indexed by the monthly additional payment to principal with the column 'monthly_extra'
    """
    results = []
    extra = min_extra_payoff
    if max_extra_payoff is None:
        max_extra_payoff = 3 * loan.standard_monthly_payment()
    loan.apply_monthly_recurring_payment(1, loan.term_in_months, min_extra_payoff)
    while extra < max_extra_payoff:
        payoff_months = loan.payoff_period_months()
        results.append({'payoff_period': payoff_months, 'monthly_extra': extra})
        loan.apply_monthly_recurring_payment(PAYOFF_CURVE_STEP_SIZE_DOLLARS, 1, loan.term_in_months)
        extra += PAYOFF_CURVE_STEP_SIZE_DOLLARS
    df = DataFrame.from_records(results)
    df.set_index('monthly_extra', inplace=True)
    return df


def interest_rate_curve(initial_principal: int, min_interest_rate: float,
                        max_interest_rate: float, term_in_months: int) -> DataFrame:
    """
    Analyze the impact of higher interest rates on the standard monthly payment and total interest cost of a loan.

    :param initial_principal:
    :param min_interest_rate:
    :param max_interest_rate:
    :param term_in_months:
    :return: DataFrame indexed by interest rates with the columns 'standard_monthly_payment' and 'cumulative_interest_paid'
    """
    values: List[LoanSummary] = []
    for interest_rate in _float_range(min_interest_rate, max_interest_rate, INTEREST_RATE_STEP_SIZE):
        loan = Loan(initial_principal, term_in_months, interest_rate)
        values.append(loan.summarize())
    return _df_from_loan_summaries(values, 'interest_rate', ['standard_monthly_payment', 'cumulative_interest_paid'])


def principal_curve(min_principal: int, max_principal: int, interest_rate: float, term_in_months: int) -> DataFrame:
    """
    Analyze the impact of additional principal on the standard monthly payment and total interest cost of a loan.

    :param min_principal:
    :param max_principal:
    :param interest_rate:
    :param term_in_months:
    :return: DataFrame indexed by the principal amount with the columns 'standard_monthly_payment' and 'cumulative_interest_paid'
    """
    values: List[LoanSummary] = []
    for principal in range(min_principal, max_principal, PRINCIPAL_STEP_SIZE):
        loan = Loan(principal, term_in_months, interest_rate)
        values.append(loan.summarize())
    df =  _df_from_loan_summaries(values, 'cumulative_principal_paid',
                                   ['standard_monthly_payment', 'cumulative_interest_paid'])
    return df.rename(columns={'cumulative_principal_paid': 'initial_principal'})



def payoff_by_date(loan: Loan, desired_payoff_month: int) -> float:
    """
    Performs a binary search to find the additional principal each month required to pay off a loan in the desired timeframe.

    :param loan: a Loan object
    :param desired_payoff_month: 1-indexed month you wish to be the final month of the loan term (example: 15 years 7 months after origination -> 187)
    :return: The additional principal required each month in order to payoff the loan in the desired timeframe.
    """
    lb = 0
    rb = 100_000
    monthly_extra = 0

    # make a deep copy to avoid mutating the state of the passed in Loan object
    local_copy = deepcopy(loan)
    while lb < rb:
        local_copy._reset_payment_schedule()
        monthly_extra = (rb - lb) / 2 + lb
        local_copy.apply_monthly_recurring_payment(monthly_extra, 1, local_copy.term_in_months)
        current_payoff_time_months = local_copy.payoff_period_months()
        if current_payoff_time_months > desired_payoff_month:
            lb = monthly_extra
        elif current_payoff_time_months < desired_payoff_month:
            rb = monthly_extra
        elif current_payoff_time_months == desired_payoff_month:
            return round(monthly_extra, 2)
    return round(monthly_extra, 2)


def _df_from_loan_summaries(loan_summaries: List[LoanSummary], index: str, selected_columns: List[str]) -> DataFrame:
    data_points = []
    for loan_summary in loan_summaries:
        data_point = {index: loan_summary.__getattr__(index)} | {col: loan_summary.__getattr__(col) for col in
                                                                 selected_columns}
        data_points.append(data_point)
    df = DataFrame.from_records(data_points)
    df.set_index(index, inplace=True)
    return df


def _float_range(start: float, stop: float, step: float) -> Generator[float, None, None]:
    x = start
    while x <= stop:
        yield x
        # enforce 4 sig figs to avoid floating point weirdness
        x = round(step + x, 4)
