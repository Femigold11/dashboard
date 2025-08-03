import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')
 
# Set the page configuration
# This sets the title, icon, and layout of the Streamlit app
st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:",layout="wide")


st.title(" :bar_chart: Acepoints Superstore Dashboard")

#adjut padding to avoid overlap with header
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True) 

# Upload and Load the dataset
fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])

if fl is not None:
    try:
        df = pd.read_csv(fl, encoding="ISO-8859-1")
        st.success("File uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    # Use a bundled fallback CSV
    try:
        df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")
        st.info("Using default Superstore.csv from project directory.")
    except FileNotFoundError:
        st.error("No file uploaded and default 'Superstore.csv' not found in the repo.")
        st.stop()



col1, col2 = st.columns((2))  #columns for our page layout
df["Order Date"] = pd.to_datetime(df["Order Date"]) #convert the "Order Date" column to datetime format
#create a date picker for selecting the date range
#getting the min and max date from the "Order Date" column
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter the dataframe based on the selected date range
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

#create a sidebar to filter the data by "Region"
# This allows users to select multiple regions from the sidebar
st.sidebar.header("Choose your filter: ")
# Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

  #Create a sidebar filter for state
  # Create for State
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

    # Create a sidebar filter for city
city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# Filter the data based on Region, State and City
if not region and not state and not city: #if u are not selecting any filter
    filtered_df = df   #show the original dataframe
elif not state and not city:  #if a user selects only region
    filtered_df = df[df["Region"].isin(region)] #filter the dataframe based on the selected region
elif not region and not city: #if a user selects only state
    filtered_df = df[df["State"].isin(state)] #filter the dataframe based on the selected state
elif state and city: #if a user selects both state and city
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)] #filter the dataframe based on the selected state and city
elif region and city: # if a user selects both region and city
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)] #filter the dataframe based on the selected region and city
elif region and state: # if a user selects both region and state
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)] #filter the dataframe based on the selected region and state
elif city:  # if a user selects only city
    filtered_df = df3[df3["City"].isin(city)] #filter the dataframe based on the selected city
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)] #filter the dataframe based on the selected region, state and city

# Display the filtered dataframe
# st.subheader("Filtered Data")
#Create a table to display the filtered data
# st.dataframe(filtered_df)   #here is a commented code
# Create a bar chart to visualize Sales by Category
category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()


with col1:
    st.subheader("Category by Sales") #bar chart
    # Create a bar chart to visualize Sales by Category
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Region by Sales") #pie chart
    # Create a pie chart to visualize Sales by Region
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

#Viewing the dataset of the visualization
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
    
    #Time Series Analysis
    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

#download the time series data
with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

    # Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

#CREATE SEGMENT BY SALES
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment by Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category by Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

    #CREATE A TABLE FOR A SELECTED COLUMN
    import plotly.figure_factory as ff
st.subheader(":point_right: Month by Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]] #Selecting 5 rows for the table
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month by sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot

# Create the scatter plot

data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
# Update layout safel
data1.update_layout(
    title=dict(
        text="Relationship between Sales and Profits using Scatter Plot.",
        font=dict(size=20),
         x=0,                # Position: 0 = far left, 0.5 = center, 1 = right
        xanchor='left'
    ),
    xaxis_title="Sales",
    xaxis=dict(
        tickfont=dict(size=16)
    ),
    yaxis_title="Profit",
    yaxis=dict(
        tickfont=dict(size=16)
    )
)

# Render in Streamlit
st.plotly_chart(data1, use_container_width=True)

# DOWNLOAD TOP 500 ROWS OF THE DATASET

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

    # DOWNLOAD ORIGINAL DATASET
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button('Download Data', data=csv, file_name='Data.csv', mime='text/csv',
                        help='Click here to download the data as a CSV file')


