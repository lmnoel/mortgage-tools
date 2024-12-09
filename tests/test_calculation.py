import unittest

from mortgage_tools.calculation import Loan


class TestCalculation(unittest.TestCase):

    def setUp(self):
        self.LOAN_TEST_CASE_1 = Loan(initial_principal=100_000, term_in_months=360, annual_interest_rate=0.05)
        self.LOAN_TEST_CASE_2 = Loan(initial_principal=2_000_000, term_in_months=180, annual_interest_rate=0.02)
        self.LOAN_TEST_CASE_3 = Loan(initial_principal=50_000, term_in_months=12, annual_interest_rate=0.00)
        self.LOAN_TEST_CASE_4 = Loan(initial_principal=50_000, term_in_months=12, annual_interest_rate=1.00)

    def test_standard_monthly_payment(self):
        test_cases = [
            (self.LOAN_TEST_CASE_1, 536.82),
            (self.LOAN_TEST_CASE_2, 12_870.17),
            (self.LOAN_TEST_CASE_3, 4_166.67),
            (self.LOAN_TEST_CASE_4, 6_749.79)
        ]
        for loan, monthly_payment in test_cases:
            with self.subTest(loan=loan, monthly_payment=monthly_payment):
                self.assertAlmostEqual(loan.standard_monthly_payment(), monthly_payment, delta=.01)

    def test_cumulative_interest(self):
        test_cases = [
            (self.LOAN_TEST_CASE_1, 93_255.78),
            (self.LOAN_TEST_CASE_2, 316_631.32),
            (self.LOAN_TEST_CASE_3, 0),
            (self.LOAN_TEST_CASE_4, 30_997.46)
        ]
        for loan, cumulative_interest in test_cases:
            with self.subTest(loan=loan, cumulative_interest=cumulative_interest):
                loan_summary = loan.summarize()
                self.assertAlmostEqual(loan_summary.cumulative_interest_paid, cumulative_interest, delta=.01)

    def test_monthly_recurring_payments(self):
        test_cases = [
            (self.LOAN_TEST_CASE_1, 93_255.78),
            (self.LOAN_TEST_CASE_2, 316_631.32),
            (self.LOAN_TEST_CASE_3, 0),
            (self.LOAN_TEST_CASE_4, 30_997.46)
        ]
        for loan, cumulative_interest in test_cases:
            with self.subTest(loan=loan,
                              cumulative_interest=cumulative_interest):
                loan_summary = loan.summarize()
                self.assertAlmostEqual(loan_summary.cumulative_interest_paid, cumulative_interest, delta=.01)

    def test_early_payment_monthly(self):
        test_cases = [
            (self.LOAN_TEST_CASE_1, 100, 21 * 12 + 4),
            (self.LOAN_TEST_CASE_1, 0, 30 * 12),
            (self.LOAN_TEST_CASE_2, 1_000, 13 * 12 + 10),
            (self.LOAN_TEST_CASE_2, 0, 15 * 12),
            (self.LOAN_TEST_CASE_3, 0, 1 * 12),
            (self.LOAN_TEST_CASE_4, 200, 1 * 12)
        ]
        for loan, extra_monthly_payment, payoff_period in test_cases:
            loan._reset_payment_schedule()
            with self.subTest(loan=loan,
                              extra_monthly_payment=extra_monthly_payment, payoff_period=payoff_period):
                loan.apply_monthly_recurring_payment(extra_monthly_payment)
                self.assertEqual(loan.payoff_period_months(), payoff_period)

    def test_early_payment_annual(self):
        test_cases = [
            (self.LOAN_TEST_CASE_1, 1_200, 21 * 12 + 1),
            (self.LOAN_TEST_CASE_1, 0, 30 * 12),
            (self.LOAN_TEST_CASE_2, 12_000, 13 * 12 + 9),
            (self.LOAN_TEST_CASE_2, 0, 15 * 12),
            (self.LOAN_TEST_CASE_3, 0, 1 * 12),
            (self.LOAN_TEST_CASE_4, 2_400, 1 * 12)
        ]
        for loan, extra_annual_payment, payoff_period in test_cases:
            loan._reset_payment_schedule()
            with self.subTest(loan=loan,
                              extra_monthly_payment=extra_annual_payment, payoff_period=payoff_period):
                loan.apply_annual_recurring_payment(extra_annual_payment)
                self.assertEqual(loan.payoff_period_months(), payoff_period)

    def test_early_payment_ad_hoc(self):
        test_cases = [
            (self.LOAN_TEST_CASE_1, 10_000, 3 * 12, 24 * 12 + 10),
            (self.LOAN_TEST_CASE_1, 10_000, 10 * 12 + 8, 26 * 12 + 4)
        ]
        for loan, extra_annual_payment, early_payment_time, payoff_period in test_cases:
            loan._reset_payment_schedule()
            with self.subTest(loan=loan,
                              extra_monthly_payment=extra_annual_payment, early_payment_time=early_payment_time,
                              payoff_period=payoff_period):
                loan.apply_ad_hoc_payment(extra_annual_payment, early_payment_time)
                self.assertEqual(loan.payoff_period_months(), payoff_period)

    def test_early_payment_combination(self):
        self.LOAN_TEST_CASE_1.apply_monthly_recurring_payment(additional_payment=200)
        self.LOAN_TEST_CASE_1.apply_monthly_recurring_payment(additional_payment=100, start_month=45, end_month=48)
        self.LOAN_TEST_CASE_1.apply_annual_recurring_payment(additional_payment=5_000)
        self.LOAN_TEST_CASE_1.apply_ad_hoc_payment(additional_payment=100_000, month=200)

        self.assertEqual(self.LOAN_TEST_CASE_1.payoff_period_months(), 106)

    def test_loan_delta(self):
        loan_delta = self.LOAN_TEST_CASE_4.summarize() - self.LOAN_TEST_CASE_3.summarize()

        self.assertAlmostEqual(loan_delta.cumulative_interest_delta, 30997.46, 2)
        self.assertEqual(loan_delta.payoff_period_delta, 0)
        self.assertEqual(loan_delta.cumulative_principal_delta, 0)

    def test_preconditions(self):
        self.assertRaises(AssertionError, lambda: Loan(-1, 10, .3))
        self.assertRaises(AssertionError, lambda: Loan(1, -1, .3))
        self.assertRaises(AssertionError, lambda: Loan(1, 10, -.3))
