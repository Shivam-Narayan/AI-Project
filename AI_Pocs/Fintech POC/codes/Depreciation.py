import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go
import numpy_financial as npf
import numpy as np

#----------------- Depreciation of Assets -----------------

def straight_line_method(cost, salvage_value, useful_life, quantity):
    annual_depreciation = (cost - salvage_value) / useful_life
    total_annual_depreciation = annual_depreciation * quantity
    depreciation_rate = (annual_depreciation / cost) * 100
    return total_annual_depreciation, depreciation_rate

def declining_balance_method(cost, rate, quantity):
    depreciation_values = []
    depreciation_rates = []
    book_value = cost
    while book_value > 0:
        annual_depreciation = book_value * rate
        depreciation_values.append(annual_depreciation * quantity)
        depreciation_rate = (annual_depreciation / cost) * 100
        depreciation_rates.append(depreciation_rate)
        book_value -= annual_depreciation
        if book_value < 0:
            book_value = 0
    return depreciation_values, depreciation_rates

def sum_of_years_digits_method(cost, salvage_value, useful_life, quantity):
    depreciation_values = []
    depreciation_rates = []
    sum_of_years = sum(range(1, useful_life + 1))
    remaining_life = useful_life
    for year in range(1, useful_life + 1):
        depreciation = (remaining_life / sum_of_years) * (cost - salvage_value)
        depreciation_values.append(depreciation * quantity)
        depreciation_rate = (depreciation / cost) * 100
        depreciation_rates.append(depreciation_rate)
        remaining_life -= 1
    return depreciation_values, depreciation_rates

def units_of_production_method(cost, salvage_value, total_units, annual_units, quantity):
    depreciation_per_unit = (cost - salvage_value) / total_units
    depreciation_values = [depreciation_per_unit * units * quantity for units in annual_units]
    depreciation_rates = [(depreciation / (cost * quantity)) * 100 for depreciation in depreciation_values]
    return depreciation_values, depreciation_rates

#----------------- Investment Recommendation Engine -----------------

def get_cagr(business_category):
    search_query = f"{business_category} CAGR India and global 2024"
    url = f"https://www.google.com/search?q={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    india_cagr = "Not found"
    global_cagr = "Not found"

    for result in soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd'):
        text = result.get_text()
        if "India" in text:
            india_cagr_match = re.search(r'CAGR of (\d+%?)', text)
            if india_cagr_match:
                india_cagr = india_cagr_match.group(1)
        elif "global" in text or "worldwide" in text:
            global_cagr_match = re.search(r'CAGR of (\d+%?)', text)
            if global_cagr_match:
                global_cagr = global_cagr_match.group(1)

    return india_cagr, global_cagr

def get_competitor_data(business_category):
    search_query = f"{business_category} competitor analysis 2024"
    url = f"https://www.google.com/search?q={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    competitor_data = []
    for result in soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd'):
        text = result.get_text()
        competitor_data.append(text)

    return competitor_data

def npv(rate, cash_flows):
    npv_value = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows, start=1))
    return npv_value

def calculate_irr(cash_flows):
    return npf.irr(cash_flows)

def summarize_competitor_data(competitor_data):
    summary = {}
    for data in competitor_data:
        lines = data.split('. ')
        for line in lines:
            if "market share" in line.lower():
                summary["Market Share"] = summary.get("Market Share", []) + [line]
            elif "growth" in line.lower():
                summary["Growth"] = summary.get("Growth", []) + [line]
            elif "strategy" in line.lower():
                summary["Strategy"] = summary.get("Strategy", []) + [line]
            elif "product" in line.lower():
                summary["Products"] = summary.get("Products", []) + [line]
    return summary

def analyze_competitor_data(summary):
    analysis = []
    if "Market Share" in summary:
        analysis.append("Competitors have notable market shares.")
    if "Growth" in summary:
        analysis.append("Competitors are experiencing growth.")
    if "Strategy" in summary:
        analysis.append("Competitors are implementing various strategies.")
    if "Products" in summary:
        analysis.append("Competitors offer a diverse range of products.")
    return analysis

def analyze_investment(proposed_revenue, median_revenue, india_cagr, global_cagr, business_category, investment_period, discount_rate, monthly_expenses, total_investment, competitor_data):
    st.write(f"\n**Analysis for {business_category}:**\n")
    st.write(f"**Proposed Revenue:** {proposed_revenue}")
    st.write(f"**Median Revenue:** {median_revenue}")
    st.write(f"**CAGR in India:** {india_cagr}")
    st.write(f"**CAGR Globally:** {global_cagr}%")
    st.write(f"**Discount Rate:** {round(discount_rate * 100,1)}%")

    if "Not found" in [india_cagr, global_cagr]:
        st.write("\nInsufficient data to make a recommendation.")
        return

    cash_flows = [-total_investment] + [proposed_revenue for _ in range(1, investment_period + 1)]
    npv_value = round(npf.npv(discount_rate, cash_flows), 2)

    # Calculate IRR
    irr_value = calculate_irr(cash_flows)

    cumulative_cash_flows = np.cumsum(cash_flows)
    breakeven_year = next((year for year, value in enumerate(cumulative_cash_flows, start=0) if value >= 0), "Never")

    return_on_capital = (proposed_revenue / total_investment) * 100
    burn_rate_percent = (monthly_expenses * 12 / proposed_revenue) * 100

    st.write(f"\n**NPV of Cash Flows:** {npv_value}")
    st.write(f"**IRR:** {irr_value * 100:.2f}%")
    st.write(f"**Breakeven Point:** Year {breakeven_year}")
    st.write(f"**Return on Capital (RoC):** {return_on_capital:.1f}%")
    st.write(f"**Burn Rate:** {burn_rate_percent:.2f}%")

    if proposed_revenue > median_revenue:
        st.write("\nThe proposed revenue is higher than the median revenue, indicating potential profitability.")
    else:
        st.write("\nThe proposed revenue is lower than the median revenue, indicating potential risk.")

    st.write("\nCompetitor Analysis Summary:")
    summary = summarize_competitor_data(competitor_data)
    competitor_analysis = analyze_competitor_data(summary)
    for key, value in summary.items():
        st.write(f"\n**{key}:**")
        for point in value:
            st.write(f" - {point}")

    st.write("\nCompetitor Analysis Consideration:")
    for point in competitor_analysis:
        st.write(f" - {point}")

    return npv_value, burn_rate_percent

def recommend_equity_or_debt(npv_value, burn_rate, proposed_revenue, median_revenue, irr_value):
    recommendation = ""
    if npv_value > 0 and proposed_revenue > median_revenue:
        if burn_rate < proposed_revenue * 0.5:
            recommendation = ("Equity", "The company is profitable with a positive NPV and reasonable burn rate. Equity investment is recommended.")
        else:
            recommendation = ("Debt", "The company is profitable but has a high burn rate. Debt investment is recommended to control expenses.")
    else:
        recommendation = ("Debt", "The company has a high risk with low or negative NPV. Debt investment is recommended.")
    
    #st.write("\n**Importance of IRR:**")
    #st.write("IRR (Internal Rate of Return) is a key metric in investment analysis. It represents the annualized effective compounded return rate that makes the NPV of all cash flows from an investment equal to zero. A higher IRR indicates a more profitable investment, and it is used to compare the profitability of multiple investments.")

    return recommendation

def recommend_minimum_investment(proposed_revenue, investment_period, discount_rate, minimum_acceptable_npv):
    increment = 1000  # Increment for adjusting the proposed revenue
    while True:
        cash_flows = [proposed_revenue * (1 + discount_rate) ** year for year in range(investment_period)]
        npv_value = npv(discount_rate, cash_flows)
        if npv_value >= minimum_acceptable_npv:
            break
        proposed_revenue += increment

    return proposed_revenue

def calculate_burn_rate(monthly_expenses):
    return monthly_expenses * 12

def forecast_revenue(proposed_revenue, cagr, irr, npv, years=5):
    cagr_decimal = float(re.findall(r'\d+', cagr)[0]) / 100
    irr_decimal = irr / 100
    npv_decimal = npv / 1000000  # Adjust NPV scale for weighting
    weights = [0.4, 0.3, 0.3]  # Weights for CAGR, IRR, NPV
    forecasted_revenues = [
        proposed_revenue * (1 + weights[0] * cagr_decimal + weights[1] * irr_decimal + weights[2] * npv_decimal) ** year 
        for year in range(1, years + 1)
    ]
    return forecasted_revenues

def plot_forecasted_revenue_with_median(forecasted_revenues, median_revenue, title):
    years = list(range(1, len(forecasted_revenues) + 1))
    median_revenue_in_crores = round(median_revenue / 10000000, 1)
    forecasted_revenues_in_crores = [round(rev / 10000000, 1) for rev in forecasted_revenues]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years, 
        y=forecasted_revenues_in_crores, 
        mode='lines+markers',
        name='Forecasted Revenue',
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=years, 
        y=[median_revenue_in_crores] * len(years), 
        mode='lines',
        name='Median Revenue',
        line=dict(color='red', dash='dash')
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Year',
        yaxis_title='Revenue (in crores)',
        hovermode='x unified'
    )

    st.plotly_chart(fig)



#----------------- Streamlit App -----------------
def app():
    st.title("Depreciation and Investment Analysis App")

    tabs = ["Depreciation Calculation", "Investment Analysis"]
    selected_tab = st.sidebar.selectbox("Select a tab", tabs)

    if selected_tab == "Depreciation Calculation":
        st.header("Depreciation Calculation")

        method = st.selectbox("Select the depreciation method:", 
                            ("Straight Line Method", "Declining Balance Method", 
                            "Sum of the Years' Digits Method", "Units of Production Method"))

        cost = st.number_input("Enter the cost of the asset:", min_value=0.0, format="%.2f")
        salvage_value = st.number_input("Enter the salvage value of the asset:", min_value=0.0, format="%.2f")
        useful_life = st.number_input("Enter the useful life of the asset (years):", min_value=1, format="%d")
        quantity = st.number_input("Enter the quantity of machines:", min_value=1, format="%d")

        if method == "Straight Line Method":
            if st.button("Calculate"):
                total_annual_depreciation, depreciation_rate = straight_line_method(cost, salvage_value, useful_life, quantity)
                st.write(f"Total Annual Depreciation: {total_annual_depreciation:.2f}")
                st.write(f"Depreciation Rate: {depreciation_rate:.2f}%")

        elif method == "Declining Balance Method":
            rate = st.number_input("Enter the depreciation rate (as a decimal, e.g., 0.2 for 20%):", min_value=0.0, format="%.2f")
            if st.button("Calculate"):
                depreciation_values, depreciation_rates = declining_balance_method(cost, rate, quantity)
                for year, (depreciation, rate) in enumerate(zip(depreciation_values, depreciation_rates), start=1):
                    st.write(f"Year {year}: Total Depreciation = {depreciation}, Depreciation Rate = {rate:.2f}%")

        elif method == "Sum of the Years' Digits Method":
            if st.button("Calculate"):
                depreciation_values, depreciation_rates = sum_of_years_digits_method(cost, salvage_value, useful_life, quantity)
                for year, (depreciation, rate) in enumerate(zip(depreciation_values, depreciation_rates), start=1):
                    st.write(f"Year {year}: Total Depreciation = {depreciation}, Depreciation Rate = {rate:.2f}%")

        elif method == "Units of Production Method":
            total_units = st.number_input("Enter the total estimated units produced over the asset's life:", min_value=1, format="%d")
            annual_units = st.text_input("Enter the units produced each year separated by spaces:")
            if st.button("Calculate"):
                annual_units_list = list(map(int, annual_units.split()))
                depreciation_values, depreciation_rates = units_of_production_method(cost, salvage_value, total_units, annual_units_list, quantity)
                for year, (depreciation, rate) in enumerate(zip(depreciation_values, depreciation_rates), start=1):
                    st.write(f"Year {year}: Total Depreciation = {depreciation}, Depreciation Rate = {rate:.2f}%")

    elif selected_tab == "Investment Analysis":
        st.header("Investment Analysis")

        proposed_revenue = st.number_input("Enter the proposed revenue:", min_value=0.0, format="%.2f")
        business_category = st.text_input("Enter the business category:")
        investment_period = st.number_input("Enter the investment period (years):", min_value=1, format="%d")
        discount_rate = st.number_input("Enter the discount rate (as a decimal, e.g., 0.1 for 10%):", min_value=0.0, format="%.2f")
        monthly_expenses = st.number_input("Enter the monthly operating expenses:", min_value=0.0, format="%.2f")
        total_investment = st.number_input("Enter the total capital investment:", min_value=0.0, format="%.2f")

        if st.button("Analyze Investment"):
            median_revenue = proposed_revenue * 1.02  # This should be changed to automated Median Revenue from the training Financial Data
            india_cagr, global_cagr = get_cagr(business_category)
            competitor_data = get_competitor_data(business_category)

            # Calculate NPV and IRR
            initial_investment = -total_investment
            cash_flows = [initial_investment] + [proposed_revenue for _ in range(1, investment_period + 1)]
            npv_value = round(npf.npv(discount_rate, cash_flows), 2)
            irr_value = calculate_irr(cash_flows)

            # Analyze investment and calculate burn rate
            npv_value, burn_rate_percent = analyze_investment(proposed_revenue, median_revenue, india_cagr, global_cagr, business_category, investment_period, discount_rate, monthly_expenses, total_investment, competitor_data)
            minimum_investment_revenue = recommend_minimum_investment(proposed_revenue, investment_period, discount_rate, 0)  # minimum_acceptable_npv

            st.write(f"\nMinimum recommended investment revenue to meet the acceptable NPV threshold: {minimum_investment_revenue}")

            burn_rate = calculate_burn_rate(monthly_expenses)
            st.write(f"**Annual Burn:** {burn_rate}")

            # Ensure irr_value is passed to the recommendation function
            investment_type, recommendation_details = recommend_equity_or_debt(npv_value, burn_rate_percent, proposed_revenue, median_revenue, irr_value)

            st.write(f"**Investment Type Recommendation:** {investment_type}")
            st.write(f"**Recommendation Details:** {recommendation_details}")

            st.write("\n**Importance of IRR:**")
            st.write("IRR (Internal Rate of Return) is a key metric in investment analysis. It represents the annualized effective compounded return rate that makes the NPV of all cash flows from an investment equal to zero. A higher IRR indicates a more profitable investment, and it is used to compare the profitability of multiple investments.")

            if india_cagr != "Not found":
                forecasted_revenues_india = forecast_revenue(proposed_revenue, india_cagr, irr_value, npv_value)
                st.write(f"\nForecasted Revenues for the next 5 years in India based on CAGR:")
                plot_forecasted_revenue_with_median(forecasted_revenues_india, median_revenue, "Forecasted Revenues in India with Median Revenue")

            if global_cagr != "Not found":
                forecasted_revenues_global = forecast_revenue(proposed_revenue, global_cagr, irr_value, npv_value)
                st.write(f"\nForecasted Revenues for the next 5 years globally based on CAGR:")
                plot_forecasted_revenue_with_median(forecasted_revenues_global, median_revenue, "Forecasted Revenues Globally with Median Revenue")
