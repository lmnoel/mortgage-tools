from typing import Dict

from pandas import DataFrame


class InterestRate:
    """
    Convenience class for converting between monthly and annual interest rates.
    """

    def __init__(self, annual_interest_rate: float):
        self.annual_rate = annual_interest_rate
        self.monthly_rate = annual_interest_rate / 12


class LoanSummaryDelta:
    """
    Compare the difference between two loans.
    """

    def __init__(self, payoff_period_delta: int, cumulative_interest_delta: float, cumulative_principal_delta: float
                 ):
        self.payoff_period_delta = payoff_period_delta
        self.cumulative_interest_delta = cumulative_interest_delta
        self.cumulative_principal_delta = cumulative_principal_delta

    def __repr__(self):
        y, m = divmod(abs(self.payoff_period_delta), 12)
        cumulative_principle_and_interest_delta = self.cumulative_interest_delta + self.cumulative_principal_delta
        return f"""
            Payoff period: {abs(self.payoff_period_delta)} months {'more' if self.payoff_period_delta > 0 else 'less'} [{abs(int(y))} year(s), {abs(int(m))} month(s)]
            Cumulative interest paid: ${abs(self.cumulative_interest_delta):.2f} {'more' if self.cumulative_interest_delta > 0 else 'less'}
            Cumulative P&I paid: ${abs(cumulative_principle_and_interest_delta):.2f} {'more' if cumulative_principle_and_interest_delta > 0 else 'less'}"""


class LoanSummary:
    """
    Summary statistics for a loan.
    """

    def __init__(self, amortization_table: DataFrame, interest_rate: InterestRate, standard_monthly_payment: float):
        self.interest_rate = interest_rate
        self.standard_monthly_payment = standard_monthly_payment
        self.payoff_period = amortization_table.index[-1]
        self.cumulative_interest_paid = round(amortization_table.iloc[-1]['cumulative_interest_paid'], 2)
        self.cumulative_principal_paid = round(amortization_table.iloc[-1]['cumulative_principal_paid'], 2)
        self.principal_ratio = self.cumulative_principal_paid / (
                self.cumulative_principal_paid + self.cumulative_interest_paid)

    def __repr__(self):
        y, m = divmod(self.payoff_period, 12)
        return f"""
            Interest rate: {self.interest_rate.annual_rate * 100 :.2f}%
            Payoff period: {self.payoff_period} months [{int(y)} year(s), {int(m)} month(s)]
            Cumulative interest paid: ${self.cumulative_interest_paid:.2f}
            Cumulative P&I paid: ${self.cumulative_interest_paid + self.cumulative_principal_paid:.2f}
            Percent of total payments to principal: {self.principal_ratio * 100 :.2f}%"""

    def __sub__(self, other) -> LoanSummaryDelta:
        return LoanSummaryDelta(self.payoff_period - other.payoff_period,
                                round(self.cumulative_interest_paid - other.cumulative_interest_paid, 2),
                                round(self.cumulative_principal_paid - other.cumulative_principal_paid, 2))

    def __getattr__(self, item):
        if item == 'interest_rate':
            return self.interest_rate.annual_rate
        return self.__getattribute__(item)


class Loan:
    """
    Generate detailed and summary statistics about the costs and options for repayment of a loan.
    """

    def __init__(self, initial_principal: int, term_in_months: int, annual_interest_rate: float):
        """
        :param initial_principal: Whole currency units (example: $300,000 -> 300_000)
        :param term_in_months: Length of the loan in months (example: 30 years -> 360)
        :param annual_interest_rate: Interest rate of the loan out of 1.00 (example: 6.5% -> 0.065)
        """
        assert initial_principal > 0, "initial_principal must be a positive value"
        assert term_in_months > 0, "term_in_months must be a positive integer"
        assert annual_interest_rate >= 0, "annual_interest rate cannot be negative"

        self.schedule: Dict[int, float] = {}

        # the initial conditions of the loan
        self.initial_principal = initial_principal
        self.term_in_months = term_in_months
        self.interest_rate = InterestRate(annual_interest_rate)
        self._reset_payment_schedule()

        # the following values reflect the "current" status of the loan
        self.current_month = 1
        self.remaining_principal = self.initial_principal
        self.interest_paid = 0

    def set_current_status(self, current_month: int, remaining_principal: float,
                           interest_paid: float):
        """
        Setting the current status of the loan will result in updated amortization tables,
        payoff periods, and interest amounts reflecting any additional payments that have been made thus far.
        """
        self.current_month = current_month
        self.remaining_principal = remaining_principal
        self.interest_paid = interest_paid

    def summarize(self) -> LoanSummary:
        """
        :return: a LoanSummary of the payoff period, cumulative interest and total cost of the loan.
        """
        return LoanSummary(self.amortization_table(), self.interest_rate, self.standard_monthly_payment())

    def standard_monthly_payment(self) -> float:
        """
        :return: the monthly P&I payment for the given loan parameters.
        """
        if self.interest_rate.annual_rate == 0.0:
            return self.initial_principal / self.term_in_months
        return self.initial_principal * (
                self.interest_rate.monthly_rate * (1 + self.interest_rate.monthly_rate) ** self.term_in_months) / (
                (1 + self.interest_rate.monthly_rate) ** self.term_in_months - 1)

    def apply_ad_hoc_payment(self, additional_payment: float, month: int):
        """
        Apply a one time additional principal payment to the given month.
        """
        self.schedule[month] += additional_payment

    def apply_monthly_recurring_payment(self, additional_payment: float, start_month: int = 1, end_month: int = None):
        """
        Apply a monthly recurring payment, by default starting in month 1 and ending in the final month,
        but can be overridden.
        """
        if not end_month:
            end_month = self.term_in_months
        self.apply_periodic_recurring_payment(additional_payment, start_month, end_month, 1)

    def apply_annual_recurring_payment(self, additional_payment: float, start_month: int = 1, end_month: int = None):
        """
        Apply an annual recurring payment, by default starting in month 1 of each year and ending in
        month 1 of the final year, but can be overridden.
        """
        if not end_month:
            end_month = self.term_in_months
        self.apply_periodic_recurring_payment(additional_payment, start_month, end_month, 12)

    def apply_periodic_recurring_payment(self, additional_payment: float, start_month: int = 1, end_month: int = None,
                                         period: int = 1):
        """
        Apply a recurring payment with a custom period, by default starting in month 1 of each year and ending in
        month 1 of the final year, every month, but can be overridden.
        """
        if not end_month:
            end_month = self.term_in_months
        for m in range(start_month, end_month, period):
            self.schedule[m] += additional_payment

    def payoff_period_months(self):
        """
        :return: The total number of months that it will take to pay off the loan,
        measured from the loan origination, taking into account additional payments.
        """
        return int(self.amortization_table().index[-1])

    def amortization_table(self) -> DataFrame:
        """
        :return: The amortization table for the loan as a DataFrame.
        The index is the month number, 1-indexed, and the included columns are:
            * interest: the portion of each month's payment that goes to interest
            * principal: the portion of each month's payment that goes to principal
            * payment: the sum of the standard monthly payment + any additional payments that have been applied
            * remaining_principal: how much principal is left after this month
            * cumulative_interest_paid: how much interest has been paid up to this point
            * cumulative_principal_paid: how much principal has been paid up to this point
        """
        results = []
        cumulative_interest_paid = self.interest_paid
        cumulative_principal_paid = self.initial_principal - self.remaining_principal
        running_remaining_principal = self.remaining_principal
        for m in range(self.current_month, self.term_in_months + 1):
            m_interest = running_remaining_principal * self.interest_rate.monthly_rate
            m_payment = self.schedule[m]
            final_payment = False
            if m_payment > running_remaining_principal:
                final_payment = True
                m_payment = running_remaining_principal + m_interest
            m_principal = m_payment - m_interest
            cumulative_interest_paid += m_interest
            cumulative_principal_paid += m_principal
            running_remaining_principal -= m_principal
            results.append({
                'month': m,
                'interest': m_interest,
                'principal': m_principal,
                'payment': m_payment,
                'remaining_principal': running_remaining_principal,
                'cumulative_interest_paid': cumulative_interest_paid,
                'cumulative_principal_paid': cumulative_principal_paid,
            })
            if final_payment:
                break

        df = DataFrame.from_records(results)
        df.set_index('month', inplace=True)
        return df

    def _reset_payment_schedule(self):
        """
        Resets the payment schedule to use the standard monthly payment.
        """
        self.schedule = self._calculate_default_payment_schedule()

    def _calculate_default_payment_schedule(self) -> Dict[int, float]:
        """
        Returns a month -> amount map for the default payment schedule using the standard monthly payment.
        """
        monthly_payment = self.standard_monthly_payment()
        return {m: monthly_payment for m in range(1, self.term_in_months + 1)}
