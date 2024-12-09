import unittest

from mortgage_tools.calculation import Loan
from mortgage_tools.optimization import payoff_curve, interest_rate_curve, principal_curve, payoff_by_date


class TestOptimization(unittest.TestCase):

    def setUp(self):
        self.LOAN_TEST_CASE = Loan(initial_principal=800_000, term_in_months=360, annual_interest_rate=0.05)

    def test_payoff_curve(self):
        curve = payoff_curve(self.LOAN_TEST_CASE)

        # with no extra monthly payments, the term equals the standard initial term
        self.assertEqual(curve.loc[0]['payoff_period'], self.LOAN_TEST_CASE.term_in_months)

        self.assertEqual(curve.loc[100]['payoff_period'], 342)
        self.assertEqual(curve.loc[1000]['payoff_period'], 239)

    def test_interest_rate_curve(self):
        curve = interest_rate_curve(900_000, .06, .075, 360)
        self.assertLess(curve.iloc[0]['standard_monthly_payment'], curve.iloc[5]['standard_monthly_payment'])
        self.assertLess(curve.iloc[0]['cumulative_interest_paid'], curve.iloc[5]['cumulative_interest_paid'])

    def test_principal_curve(self):
        curve = principal_curve(1_100_000, 1_300_000, .0425, 180)
        self.assertLess(curve.iloc[0]['standard_monthly_payment'], curve.iloc[5]['standard_monthly_payment'])
        self.assertLess(curve.iloc[0]['cumulative_interest_paid'], curve.iloc[5]['cumulative_interest_paid'])

    def test_payoff_by_date(self):
        self.assertAlmostEqual(payoff_by_date(self.LOAN_TEST_CASE, 180), 2_050.78, 2)
        self.assertAlmostEqual(payoff_by_date(self.LOAN_TEST_CASE, 200), 1611.33, 2)
        self.assertAlmostEqual(payoff_by_date(self.LOAN_TEST_CASE, 250), 866.7, 2)
        self.assertAlmostEqual(payoff_by_date(self.LOAN_TEST_CASE, 300), 384.52, 2)

    def test_payoff_by_date_for_in_progress_loan(self):
        self.LOAN_TEST_CASE.set_current_status(10, 750_000, 45_000)

        self.assertAlmostEqual(payoff_by_date(self.LOAN_TEST_CASE, 180), 1855.47, 2)
        self.assertAlmostEqual(payoff_by_date(self.LOAN_TEST_CASE, 200), 1416.02, 2)
        self.assertAlmostEqual(payoff_by_date(self.LOAN_TEST_CASE, 250), 646.97, 2)
        self.assertAlmostEqual(payoff_by_date(self.LOAN_TEST_CASE, 300), 158.69, 2)
