import os
import tempfile
import unittest

from mortgage_tools.calculation import Loan
from mortgage_tools.optimization import payoff_curve
from mortgage_tools.plot import plot_amortization_components, plot_monthly_payments, plot_monthly_payments_relative, \
    plot_relative_amortization_tables, plot_payoff_curve, plot_interest_rate_curve, plot_principal_curve


class TestPlot(unittest.TestCase):

    def setUp(self):
        self.LOAN_TEST_CASE = Loan(initial_principal=800_000, term_in_months=360, annual_interest_rate=0.05)

    def test_plot_amortization_components(self):
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, 'test_file.png')
            plot_amortization_components(self.LOAN_TEST_CASE.amortization_table(), temp_file_path)
            self.assertTrue(os.path.exists(temp_file_path))

    def test_plot_monthly_payments(self):
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, 'test_file.png')
            plot_monthly_payments(self.LOAN_TEST_CASE.amortization_table(), temp_file_path)
            self.assertTrue(os.path.exists(temp_file_path))

    def test_plot_monthly_payments_relative(self):
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, 'test_file.png')
            plot_monthly_payments_relative(self.LOAN_TEST_CASE.amortization_table(), temp_file_path)
            self.assertTrue(os.path.exists(temp_file_path))

    def test_plot_relative_amortization_tables(self):
        default_table = self.LOAN_TEST_CASE.amortization_table()
        self.LOAN_TEST_CASE.apply_ad_hoc_payment(10_000, 45)
        adjusted_table = self.LOAN_TEST_CASE.amortization_table()
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, 'test_file.png')
            plot_relative_amortization_tables(default_table, adjusted_table, temp_file_path)
            self.assertTrue(os.path.exists(temp_file_path))

    def test_plot_payoff_curve(self):
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, 'test_file.png')
            plot_payoff_curve(payoff_curve(self.LOAN_TEST_CASE), temp_file_path)
            self.assertTrue(os.path.exists(temp_file_path))

    def test_plot_interest_rate_curve(self):
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, 'test_file.png')
            plot_interest_rate_curve(900_000, 360, .06, .075, temp_file_path)
            self.assertTrue(os.path.exists(temp_file_path))

    def test_plot_principal_curve(self):
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, 'test_file.png')
            plot_principal_curve(1_100_000, 1_300_000, .0425, 180, temp_file_path)
            self.assertTrue(os.path.exists(temp_file_path))
