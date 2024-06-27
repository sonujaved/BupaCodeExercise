import streamlit as st
from utils.exchange_rate_analyzer import ExchangeRateAnalyzer

# Streamlit app
st.title("Exchange Rates Analysis")

# Sidebar for input
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your API key:", type="password")
base_currency = st.sidebar.text_input("Enter the base currency (e.g., AUD):")
target_currency = st.sidebar.text_input("Enter the target currency (e.g., NZD):")

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
