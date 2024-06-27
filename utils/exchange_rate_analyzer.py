import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from .decorators import log_function_call, time_function_execution, cache_results
import streamlit as st

class ExchangeRateAnalyzer:
    def __init__(self, api_key, base_currency, target_currency, days=30):
        self.api_key = api_key
        self.base_currency = base_currency
        self.target_currency = target_currency
        self.days = days

    @cache_results
    @time_function_execution
   # @log_function_call
    def fetch_exchange_rates(self):
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
        df["Date"] = pd.to_datetime(df["Date"])
        df.dropna(inplace=True)
        return df

    @cache_results
    @time_function_execution
    # @log_function_call
    def analyze_data(self):
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
        best_rate = df["Exchange Rate"].max()
        worst_rate = df["Exchange Rate"].min()
        average_rate = df["Exchange Rate"].mean()
        highest_daily_change = df["Daily Change"].max()
        lowest_daily_change = df["Daily Change"].min()
        return best_rate, worst_rate, average_rate, highest_daily_change, lowest_daily_change

    def plot_exchange_rate_trend(self, df):
        fig = px.line(df, x="Date", y="Exchange Rate",
                      title=f"{self.base_currency} to {self.target_currency} Exchange Rate Over the Past 30 Days")
        return fig

    def plot_advanced_analysis(self, df):
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
        df["Conversion Amount"] = initial_amount / df["Exchange Rate"]
        fig = px.line(df, x="Date", y="Conversion Amount", title=f"${initial_amount} {self.target_currency} to {self.base_currency} Conversion Over Time (30 Days)")
        return fig

    def plot_candlestick_chart(self, df):
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
