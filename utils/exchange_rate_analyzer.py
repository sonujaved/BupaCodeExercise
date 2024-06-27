import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from .decorators import log_function_call, time_function_execution, cache_results
import streamlit as st

class ExchangeRateAnalyzer:
    """
    A class used to analyze exchange rates between two currencies over a specified period.

    Attributes
    ----------
    api_key : str
        The API key for accessing the exchange rate service.
    base_currency : str
        The base currency code (e.g., 'AUD').
    target_currency : str
        The target currency code (e.g., 'NZD').
    days : int, optional
        The number of days for which to fetch exchange rates (default is 30).

    Methods
    -------
    fetch_exchange_rates():
        Fetches exchange rates from the API for the past specified number of days.
    preprocess_data(df):
        Preprocesses the fetched data, including handling missing values and outliers.
    analyze_data():
        Analyzes the fetched exchange rate data and calculates additional metrics.
    get_statistics(df):
        Calculates statistics like the best, worst, and average exchange rates, as well as daily changes.
    plot_exchange_rate_trend(df):
        Plots the trend of exchange rates over the specified period.
    plot_advanced_analysis(df):
        Plots advanced analysis charts including daily changes and moving averages.
    plot_conversion_over_time(df, initial_amount=100):
        Plots the conversion of a specified amount of base currency to the target currency over time.
    plot_candlestick_chart(df):
        Plots a candlestick chart of the exchange rates over the specified period.
    """
    def __init__(self, api_key, base_currency, target_currency, days=30):
        """
        Initializes the ExchangeRateAnalyzer with the given parameters.

        Parameters
        ----------
        api_key : str
            The API key for accessing the exchange rate service.
        base_currency : str
            The base currency code (e.g., 'AUD').
        target_currency : str
            The target currency code (e.g., 'NZD').
        days : int, optional
            The number of days for which to fetch exchange rates (default is 30).
        """
        self.api_key = api_key
        self.base_currency = base_currency
        self.target_currency = target_currency
        self.days = days

    @cache_results
    @time_function_execution
   # @log_function_call
    def fetch_exchange_rates(self):
        """
        Fetches exchange rates from the API for the past specified number of days.

        Returns
        -------
        dict
            A dictionary with dates as keys and exchange rates as values.
        """
        rates = {}
        end_date = datetime.now()
        for i in range(self.days):
            date = end_date - timedelta(days=i)
            year, month, day = date.year, date.month, date.day
            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/history/{self.base_currency}/{year}/{month}/{day}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data["result"] == "success":
                    rate = data["conversion_rates"].get(self.target_currency)
                    if rate:
                        rates[date.strftime("%Y-%m-%d")] = rate
                else:
                    st.error("Error fetching data: " + data["error-type"])
            else:
                st.error(f"HTTP error: {response.status_code}")
        return rates

    @cache_results
    @time_function_execution
    # @log_function_call
    def preprocess_data(self, df):
        """
        Preprocesses the fetched data, including handling missing values and outliers.

        Parameters
        ----------
        df : pandas.DataFrame
            The data frame containing the exchange rate data.

        Returns
        -------
        pandas.DataFrame
            The preprocessed data frame.
        """
        df["Date"] = pd.to_datetime(df["Date"])
        df.dropna(inplace=True)
        return df

    @cache_results
    @time_function_execution
    # @log_function_call
    def analyze_data(self):
        """
        Analyzes the fetched exchange rate data and calculates additional metrics.

        Returns
        -------
        pandas.DataFrame
            A data frame containing the analyzed exchange rate data with additional metrics.
        """
        rates = self.fetch_exchange_rates()
        df = pd.DataFrame(list(rates.items()), columns=["Date", "Exchange Rate"])
        df = self.preprocess_data(df)
        df.sort_values("Date", inplace=True)
        df['Daily Change'] = df["Exchange Rate"].diff()
        df['7-Day Moving Average'] = df["Exchange Rate"].rolling(window=7).mean()
        return df

    @cache_results
    @time_function_execution
    # @log_function_call
    def get_statistics(self, df):
        """
        Calculates statistics like the best, worst, and average exchange rates, as well as daily changes.

        Parameters
        ----------
        df : pandas.DataFrame
            The data frame containing the analyzed exchange rate data.

        Returns
        -------
        tuple
            A tuple containing the best exchange rate, worst exchange rate, average exchange rate, 
            highest daily change, and lowest daily change.
        """
        best_rate = df["Exchange Rate"].max()
        worst_rate = df["Exchange Rate"].min()
        average_rate = df["Exchange Rate"].mean()
        highest_daily_change = df["Daily Change"].max()
        lowest_daily_change = df["Daily Change"].min()
        return best_rate, worst_rate, average_rate, highest_daily_change, lowest_daily_change

    def plot_exchange_rate_trend(self, df):
        """
        Plots the trend of exchange rates over the specified period.

        Parameters
        ----------
        df : pandas.DataFrame
            The data frame containing the analyzed exchange rate data.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object representing the exchange rate trend.
        """
        fig = px.line(df, x="Date", y="Exchange Rate",
                      title=f"{self.base_currency} to {self.target_currency} Exchange Rate Over the Past 30 Days")
        return fig

    def plot_advanced_analysis(self, df):
        """
        Plots advanced analysis charts including daily changes and moving averages.

        Parameters
        ----------
        df : pandas.DataFrame
            The data frame containing the analyzed exchange rate data.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object representing the advanced analysis.
        """
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Daily Change"], mode='lines+markers', name='Daily Change',
                                 line=dict(color='red')))
        fig.add_trace(
            go.Scatter(x=df["Date"], y=df["7-Day Moving Average"], mode='lines+markers', name='7-Day Moving Average',
                       line=dict(color='green')))
        fig.update_layout(
            title=f"Daily Change and 7-Day Moving Average of {self.base_currency} to {self.target_currency} Exchange Rate",
            xaxis_title="Date", yaxis_title="Value")
        return fig

    def plot_conversion_over_time(self, df, initial_amount=100):
        """
        Plots the conversion of a specified amount of base currency to the target currency over time.

        Parameters
        ----------
        df : pandas.DataFrame
            The data frame containing the analyzed exchange rate data.
        initial_amount : float, optional
            The initial amount of base currency to convert (default is 100).

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object representing the conversion over time.
        """
        df["Conversion Amount"] = initial_amount / df["Exchange Rate"]
        fig = px.line(df, x="Date", y="Conversion Amount", title=f"${initial_amount} {self.target_currency} to {self.base_currency} Conversion Over Time (30 Days)")
        return fig

    def plot_candlestick_chart(self, df):
        """
        Plots a candlestick chart of the exchange rates over the specified period.

        Parameters
        ----------
        df : pandas.DataFrame
            The data frame containing the analyzed exchange rate data.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object representing the candlestick chart.
        """
        fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                             open=df['Exchange Rate'].shift(1).fillna(df['Exchange Rate']),
                                             high=df['Exchange Rate'],
                                             low=df['Exchange Rate'],
                                             close=df['Exchange Rate'])])
        fig.update_layout(
            title=f"{self.base_currency} to {self.target_currency} Candlestick Chart Over the Past 30 Days",
            xaxis_title="Date", yaxis_title="Exchange Rate")
        return fig

    @cache_results
    @time_function_execution
    # @log_function_call
    def generate_insights(self, df):
        """
        Generates insights based on the exchange rate data.
    
        Parameters
        ----------
        df : pandas.DataFrame
            The data frame containing the analyzed exchange rate data.
    
        Returns
        -------
        list of str
            A list of insights generated from the data analysis.
    
        Insights
        --------
        - Trend Analysis: Determines if the exchange rate has increased or decreased over the period.
        - Significant Changes: Identifies days with significant changes in the exchange rate.
        - Highest and Lowest Rates: Provides dates with the highest and lowest exchange rates.
        - Volatility Analysis: Assesses the volatility of the exchange rate based on the standard deviation of daily changes.
        """
        insights = []

        # Trend Analysis
        if df["Exchange Rate"].iloc[-1] > df["Exchange Rate"].iloc[0]:
            insights.append("The exchange rate has increased over the past 30 days.")
        else:
            insights.append("The exchange rate has decreased over the past 30 days.")

        # Significant Changes
        significant_changes = df[
            df["Daily Change"].abs() > df["Daily Change"].abs().mean() + 2 * df["Daily Change"].abs().std()]
        if not significant_changes.empty:
            insights.append(
                f"There were {len(significant_changes)} days with significant changes in the exchange rate.")

        # Highest and Lowest Rates
        best_rate_date = df[df["Exchange Rate"] == df["Exchange Rate"].max()]["Date"].values[0]
        worst_rate_date = df[df["Exchange Rate"] == df["Exchange Rate"].min()]["Date"].values[0]
        insights.append(f"The highest exchange rate was on {best_rate_date}.")
        insights.append(f"The lowest exchange rate was on {worst_rate_date}.")

        # Volatility Analysis
        if df["Daily Change"].std() > 0.01:
            insights.append("The exchange rate has been quite volatile.")
        else:
            insights.append("The exchange rate has been relatively stable.")

        return insights

if __name__ == "__main__":
    print(" --test--")
