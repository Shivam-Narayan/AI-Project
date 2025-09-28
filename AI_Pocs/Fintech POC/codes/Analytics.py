
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import newton
from sklearn.linear_model import LinearRegression

def app():

    # Load the dataset
    df = pd.read_excel('..\\templates\\P&L.xlsx')

    # Display the column names for debugging
    #st.write(df.columns)

    # Function to calculate IRR
    def calculate_irr(cash_flows):
        def npv(rate):
            return sum([cf / (1 + rate) ** t for t, cf in enumerate(cash_flows)])
        
        # Use Newton's method to find the root of the NPV function, which is the IRR
        try:
            return newton(npv, 0.1)  # Initial guess of 0.1 (10%)
        except (RuntimeError, OverflowError):
            return np.nan
        
    # Prepare the dataset for IRR calculation
    # Assuming operating profits can be treated as annual cash flows
    df['IRR'] = df.apply(lambda row: calculate_irr([-row['Sales (CR)']] + [row['Operating Profits (CR)']] * 5), axis=1)

    # Title of the application
    st.title("Financial Data Dashboard")
    st.subheader("1. Revenue Analysis")
    st.subheader("2. Competitor Benchmarking")
    st.subheader("3. Investment Analysis")
    # Sidebar for filtering
    industry_list = ['All'] + df['Industry'].unique().tolist()
    selected_industry = st.sidebar.selectbox('Select Industry', options=industry_list)

    # Filter dataframe based on selected industry
    if selected_industry == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['Industry'] == selected_industry]

    # Chart theme settings
    chart_theme = dict(
        layout=dict(
            title=dict(font=dict(size=24)),
            xaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
            yaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
            legend=dict(font=dict(size=14)),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    )
    c1,c2=st.columns(2)
    # 1. Industry wise Sales Figures
    industry_sales = df.groupby('Industry')['Sales (CR)'].sum().reset_index()
    fig1 = px.bar(industry_sales, x='Industry', y='Sales (CR)', color= 'Industry', title='Industry wise Sales Figures')
    fig1.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c1:
        st.plotly_chart(fig1)

    # 2. Company wise Revenue
    company_Revenue= filtered_df[['Name', 'Sales (CR)']]
    fig2 = px.bar(company_Revenue, x='Name', y='Sales (CR)', color= 'Name',title='Company wise Revenue')
    fig2.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c2:
        st.plotly_chart(fig2)

    c3,c4=st.columns(2)
    # 3. Company wise Net Profit
    company_profit = filtered_df[['Name', 'Net Profit (CR)']]
    fig3 = px.bar(company_profit, x='Name', y='Net Profit (CR)', title='Company wise Net Profit')
    fig3.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c3:
        st.plotly_chart(fig3)

    # Calculate Profit Margin
    filtered_df['Profit Margin (%)'] = (filtered_df['Net Profit (CR)'] / filtered_df['Sales (CR)']) * 100
    filtered_df['Profit Margin (%)'] = filtered_df['Profit Margin (%)'].round(1)

    # 4. Company wise Profit Margin
    company_profit_margin = filtered_df[['Name', 'Profit Margin (%)']]
    fig4 = px.line(company_profit_margin, x='Name', y='Profit Margin (%)', title='Company wise Profit Margin')
    fig4.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c4:
        st.plotly_chart(fig4)

    # 5. Company wise ROCE % displayed in line chart
    c5,c6=st.columns(2)
    company_roce = filtered_df[['Name', 'ROCE (%)']]
    fig5 = px.line(company_roce, x='Name', y='ROCE (%)', title='Company wise ROCE %')
    fig5.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c5:
         st.plotly_chart(fig5)

    # 6. Company wise Operating Profits
    company_operating_profit = filtered_df[['Name', 'Operating Profits (CR)']]
    fig6 = px.bar(company_operating_profit, x='Name', y='Operating Profits (CR)', title='Company wise Operating Profits')
    fig6.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c6:
        st.plotly_chart(fig6)

    # 7. Industry and Company wise EBIT
    c7,c8=st.columns(2)
    industry_company_ebit = filtered_df.groupby(['Industry', 'Name'])['EBIT (CR)'].sum().reset_index()
    fig7 = px.bar(industry_company_ebit, x='Name', y='EBIT (CR)', color='Industry', title='Industry and Company wise EBIT')
    fig7.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c7:
        st.plotly_chart(fig7)

    # 8. Taxes Paid per company
    taxes_per_company = filtered_df[['Name', 'Tax (CR)']]
    fig8 = px.bar(taxes_per_company, x='Name', y='Tax (CR)',title='Taxes Paid per Company')
    fig8.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c8:
        st.plotly_chart(fig8)

    # 9. Company wise IRR displayed in line chart
    c9,c10=st.columns(2)
    company_irr = filtered_df[['Name', 'IRR']]
    fig9 = px.line(company_irr, x='Name', y='IRR', title='Company wise IRR')
    fig9.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c9:
        st.plotly_chart(fig9)

    # 10. Company wise Cost Price
    company_CP = filtered_df[['Name', 'Current Price']]
    fig10 = px.line(company_CP, x='Name', y='Current Price', title='Company wise Stock Price')
    fig10.update_layout(height=300,  width=400,**chart_theme['layout'])
    with c10:
        st.plotly_chart(fig10)

    # Get top companies based on IRR for recommendations
    top_irr_companies = df.nlargest(5, 'IRR')[['Name', 'IRR']]

    # 11. Overall analysis summary and Recommendations of Investments
    summary = f"""
    **Summary and Recommendations:**
    - The IT and Finance industries have the highest sales figures, indicating strong market demand.
    - Companies like 'Infronics Sys.' and 'One Global Serv.' show high net profits, making them attractive for investment.
    - The top ROCE companies are leaders in their sectors, with high returns on capital employed.
    - Companies like 'Shree Pacetronix' and 'Hi-Green Carbon' have substantial operating profits, highlighting operational efficiency.
    - Taxes paid are highest among large-cap companies, impacting net profit margins.
    - Historical sales and profit growth analysis show that companies like 'Kriti Nutrients' and 'Shree Pacetronix' have consistent growth.
    - Companies with high IRR, such as {', '.join(top_irr_companies['Name'])}, show strong potential for future investment returns.
    - **Recommendations:** Focus on companies with high ROCE, consistent sales growth, strong net profit margins, and high IRR for long-term investments.
    """
    st.markdown(summary)

    # 12. Predict tab
    st.header("Predict")

    # 13. Create a selectbox for variables to predict
    variable = st.selectbox("Select variable to predict:", ["Sales", "Stock Price", "Operating Profit"])

    # Extract unique company names and add 'All' option
    unique_company_names = np.append(filtered_df['Name'].unique(), 'All')
    selected_company = st.selectbox("Select a company:", unique_company_names)

    st.write(f"You selected: {selected_company}")

    # Function to predict next year's value
    def predict_next_year_values(X, y):
        # Extend X to predict the next year (assuming monthly data for 1 year, adjust if different)
        future_X = np.array(range(len(X), len(X) + 12)).reshape(-1, 1)
        
        # Train the model and predict
        model = LinearRegression()
        model.fit(X, y)
        future_pred = model.predict(future_X)
        
        return future_pred

    if selected_company == 'All':
        # Prepare the figure for plotting
        fig11 = go.Figure()
        future_predictions = []
        actual_values = []

        # Loop through each company to predict next year's values
        for company in filtered_df['Name'].unique():
            company_data = filtered_df[filtered_df['Name'] == company]

            # Prepare data for prediction
            if variable == "Sales":
                y = company_data['Sales (CR)'].values
                y_label = "Sales (CR)"
            elif variable == "Stock Price":
                y = company_data['Current Price'].values
                y_label = "Current Price"
            elif variable == "Operating Profit":
                y = company_data['Operating Profits (CR)'].values
                y_label = "Operating Profits (CR)"
            
            X = np.array(range(len(y))).reshape(-1, 1)

            # Predict the next year's values
            future_pred = predict_next_year_values(X, y)
            future_predictions.append((company, future_pred[-1]))  # Taking the last value as the prediction for next year
            actual_values.append((company, y[-1]))  # Taking the last actual value

        # Convert predictions and actual values to DataFrame for easy plotting
        future_predictions_df = pd.DataFrame(future_predictions, columns=['Company', 'Predicted Value'])
        actual_values_df = pd.DataFrame(actual_values, columns=['Company', 'Actual Value'])

        # Plot predicted values for the next year for all companies
        fig11.add_trace(go.Bar(x=future_predictions_df['Company'], y=future_predictions_df['Predicted Value'], name='Predicted Values', marker_color='Orange'))
        fig11.add_trace(go.Scatter(x=actual_values_df['Company'], y=actual_values_df['Actual Value'], mode='lines+markers', name='Actual Values',line=dict(color='Light Blue')))

        # Add title and labels to the plot
        fig11.update_layout(
            title=f'Predicted {y_label} for Next Year for All Companies',
            xaxis_title='Company Names',
            yaxis_title=y_label
        )
    else:
        # Filter data based on the selected company
        company_data = filtered_df[filtered_df['Name'] == selected_company]

        # Prepare data for prediction
        if variable == "Sales":
            y = company_data['Sales (CR)'].values
            y_label = "Sales (CR)"
        elif variable == "Stock Price":
            y = company_data['Current Price'].values
            y_label = "Current Price"
        elif variable == "Operating Profit":
            y = company_data['Operating Profits (CR)'].values
            y_label = "Operating Profits (CR)"

        # Generate X values for the length of y
        X = np.array(range(len(y))).reshape(-1, 1)

        # Train the linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict future values
        future_X = np.array(range(len(y), len(y) + 12)).reshape(-1, 1)  # Predicting next 12 periods (assuming months)
        predicted_values = model.predict(np.vstack([X, future_X]))

        # Split the actual and predicted values for plotting
        actual_values = y
        predicted_future_values = predicted_values[len(y):]

        # Plot actual vs predicted values for the selected company
        fig11 = go.Figure()
        fig11.add_trace(go.Scatter(x=company_data.index, y=actual_values, mode='lines+markers', name='Actual', line=dict(color='Blue')))
        fig11.add_trace(go.Scatter(x=np.arange(len(company_data.index), len(company_data.index) + 12), y=predicted_future_values, mode='lines+markers', name='Predicted',line=dict(color='Orange')))

        # Add title and labels to the plot
        fig11.update_layout(
            title=f'Actual vs Predicted {y_label} for {selected_company}',
            xaxis_title='Time Period',
            yaxis_title=y_label
        )

    st.plotly_chart(fig11)
if __name__==' __main__ ':
    app() 