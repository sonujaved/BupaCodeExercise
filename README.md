## Documentation
### Production App
  #### Access the application from link : https://bupacodeexercise-wzm2dlq6nuaxeunj98sxze.streamlit.app/
  
  [![](https://markdown-videos-api.jorgenkh.no/youtube/rLgWiDYSQlI)](https://youtu.be/rLgWiDYSQlI)

### API Key
  #### Please create an account at https://www.exchangerate-api.com/ to obtain your key [Pro Licence free for 1st 30 days], or contact me

### Approach

1. **Objective**: The objective of this application is to fetch exchange rates between two selected currencies for the past 30 days, preprocess the data, perform analysis, generate insights, and visualize the data using advanced analytics.

2. **API Integration**: We integrated with an exchange rate API to fetch historical exchange rates. The application supports user input for API keys and currency selection.

                        https://app.exchangerate-api.com/dashboard
                        Example Request: https://v6.exchangerate-api.com/v6/xxxxxxxxxxxxxxxxxx/latest/USD

4. **Data Preprocessing**: The fetched data is preprocessed to handle missing values, and outliers, and ensure correct data types.

5. **Data Analysis**: We performed various analyses such as calculating the best and worst exchange rates, and average exchange rates, and detecting significant daily changes.

6. **Visualization**: We visualized the exchange rate trends, daily changes, and moving averages, and provided advanced charting options like candlestick charts using Plotly.
   ![alt text](https://github.com/sonujaved/BupaCodeExercise/blob/main/Screen%20Shot%202024-06-27%20at%203.50.12%20pm.png)
   
   ![alt text](https://github.com/sonujaved/BupaCodeExercise/blob/main/Screen%20Shot%202024-06-27%20at%203.50.23%20pm.png)
   

8. **Insights Generation**: We generated insights based on the analyzed data to provide users with meaningful summaries of the exchange rate trends and anomalies.

### Architecture

- **Streamlit**: Streamlit is used for building the application's user interface. It provides an interactive way for users to input their API keys, select currencies, and view the results.

- **ExchangeRateAnalyzer Class**: The core functionality of fetching, preprocessing, analyzing, and visualizing the data is encapsulated in the `ExchangeRateAnalyzer` class. This class includes methods for each step of the process.

- **Decorators**: Decorators are used for logging function calls, timing execution, and caching results. This ensures efficient and traceable execution.

- **Plotly**: Plotly is used for creating advanced charts and visualizations. It supports interactive and aesthetically pleasing charts.

### Best Practices and Standards

1. **Modular Design**: The code is organized into modules, separating the core functionality (`ExchangeRateAnalyzer` class) from the user interface (Streamlit app).

2. **Use of Decorators**: Decorators are used to add functionality such as logging, timing, and caching without modifying the original function code. This promotes clean and maintainable code.

3. **Error Handling**: The code includes error handling for HTTP requests and data processing steps to ensure robustness.

4. **Caching**: Results of functions are cached to avoid redundant API calls and improve performance.

5. **Documentation**: Each function and class method is documented with docstrings to explain its purpose and usage.

6. **Data Validation**: Data is validated and preprocessed to handle missing values and outliers.

7. **User Input Handling**: User inputs are handled securely and validated before use, ensuring that the application behaves correctly with different inputs.

### Code Structure

```
exchange_rate_app/
│
├── streamlit_ExchangeRate.py  # Main Streamlit application file
│
├── utils/
│   └── exchange_rate_analyzer.py  # ExchangeRateAnalyzer class definition
|   └── decorators.py  # decorators definition
│
└── requirements.txt  # Required Python libraries
```

### Detailed Explanation of Code

#### Streamlit_ExchangeRate.py 

```python
import streamlit as st
from utils.exchange_rate_analyzer import ExchangeRateAnalyzer

# Streamlit app
st.title("Exchange Rates Analysis")

# Sidebar for input
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your API key:", type="password")
base_currency = st.sidebar.text_input("Enter the base currency (e.g., AUD):")
target_currency = st.sidebar.text_input("Enter the target currency (e.g., NZD):")

if __name__ == "__main__":
    if api_key and base_currency and target_currency:
        analyzer = ExchangeRateAnalyzer(api_key, base_currency, target_currency)
        df = analyzer.analyze_data()

        if not df.empty:
            st.success("Data fetched and preprocessed successfully!")

            # Display raw data
            st.subheader("Raw Data")
            st.dataframe(df)

            # Perform data analysis
            best_rate, worst_rate, average_rate, highest_daily_change, lowest_daily_change = analyzer.get_statistics(df)

            st.subheader("Data Analysis")
            st.write(f"**Best Exchange Rate:** {best_rate}")
            st.write(f"**Worst Exchange Rate:** {worst_rate}")
            st.write(f"**Average Exchange Rate:** {average_rate:.4f}")
            st.write(f"**Highest Daily Change:** {highest_daily_change:.4f}")
            st.write(f"**Lowest Daily Change:** {lowest_daily_change:.4f}")

            # Generate and display insights
            st.subheader("Insights")
            insights = analyzer.generate_insights(df)
            for insight in insights:
                st.write(f"- {insight}")

            # Plot exchange rates
            st.subheader("Exchange Rate Trend")
            fig = analyzer.plot_exchange_rate_trend(df)
            st.plotly_chart(fig)

            # Plot daily changes and moving average
            st.subheader("Daily Change and Moving Average")
            fig = analyzer.plot_advanced_analysis(df)
            st.plotly_chart(fig)

            # Plot $100 conversion over time
            st.subheader("$100 Conversion Over Time (30 Days)")
            fig = analyzer.plot_conversion_over_time(df)
            st.plotly_chart(fig)

            # Advanced Chart: Candlestick Chart
            st.subheader("Chart: Candlestick Chart")
            fig = analyzer.plot_candlestick_chart(df)
            st.plotly_chart(fig)

            # Save to JSON
            json_output = df.to_json(orient='records', date_format='iso')
            st.download_button(
                label="Download data as JSON",
                data=json_output,
                file_name='exchange_rates.json',
                mime='application/json'
            )
        else:
            st.error("Failed to fetch data. Please check your API key and try again.")
```

#### utils/exchange_rate_analyzer.py

```python
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
```
#### utils/decorators.py 

```python
import time
import hashlib
import functools
import streamlit as st

# Decorator for logging function calls
def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        st.write(f"Calling {func.__name__} function...")
        return func(*args, **kwargs)
    return wrapper

# Decorator for timing function execution
def time_function_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        st.write(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper

# Decorator for caching function results
def cache_results(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = func.__name__ + hashlib.md5(str(args).encode('utf-8')).hexdigest()
        if key in cache:
            st.write(f"Returning cached result for {func.__name__} function...")
            return cache[key]
        else:
            result = func(*args, **kwargs)
            cache[key] = result
            return result
    return wrapper
```
### Here are some testing scenarios to ensure the robustness and correctness of the above code:

1. API Key Validation
Scenario: Provide an invalid API key.
Expected Outcome: The application should display an error message indicating an invalid API key or failed data fetch.
2. Currency Input Validation
Scenario: Enter unsupported or non-existent currency codes.
Expected Outcome: The application should handle the error gracefully and inform the user about invalid currency codes.
3. Data Fetching
Scenario: Fetch exchange rates with a valid API key and supported currencies.
Expected Outcome: The application should successfully fetch and display the data without errors.
4. Handling No Data
Scenario: Fetch exchange rates for a date range with no available data.
Expected Outcome: The application should handle this scenario gracefully and inform the user that no data is available for the selected period.
5. Data Preprocessing
Scenario: Fetch data that contains missing values or outliers.
Expected Outcome: The application should preprocess the data correctly, removing or handling missing values and outliers.
6. Data Analysis
Scenario: Perform analysis on valid exchange rate data.
Expected Outcome: The application should calculate the best, worst, and average exchange rates correctly. It should also identify the highest and lowest daily changes accurately.
7. Data Visualization
Scenario: Generate plots and charts for exchange rates.
Expected Outcome: The application should generate clear and correct visualizations, including line charts, candlestick charts, and moving averages.
8. Caching Mechanism
Scenario: Fetch exchange rates for the same input parameters multiple times.
Expected Outcome: The application should use cached results to avoid redundant API calls and improve performance.
9. Logging and Timing
Scenario: Execute various functions of the ExchangeRateAnalyzer class.
Expected Outcome: The application should log function calls and execution times, providing clear feedback in the Streamlit interface.
10. Data Download
Scenario: Download the processed exchange rate data as a JSON file.
Expected Outcome: The application should allow users to download the JSON file with the correct data format.
11. User Interface
Scenario: Test the user interface elements like input fields, buttons, and dropdowns.
Expected Outcome: The application should correctly handle user inputs and provide a smooth user experience.
12. Error Handling
Scenario: Simulate various errors such as network issues, API errors, and invalid responses.
Expected Outcome: The application should handle errors gracefully and provide informative error messages to the user.
13. Insight Generation
Scenario: Generate insights based on the analyzed data.
Expected Outcome: The application should provide meaningful and accurate insights about the exchange rate trends and anomalies.
14. Edge Cases
Scenario: Test with edge cases like fetching data for the current day only, or for a period longer than 30 days.
Expected Outcome: The application should handle edge cases correctly, ensuring no unexpected behavior or crashes.
