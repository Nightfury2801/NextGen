import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NexGen Dispatch Optimizer 🚚",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTS ---
# --- IMPORTANT ---
# This path must match the path used in your Colab notebook for loading data.
DATA_PATH = "/content/NextGen_data/"

ASSUMED_FUEL_PRICE_PER_LITER = 1.50
ASSUMED_LABOR_COST_PER_HOUR = 20.00

# --- DATA LOADING AND PROCESSING ---
@st.cache_data
def load_and_prepare_data(path):
    """
    Loads all datasets, cleans column names, merges them,
    and performs initial feature engineering.
    """
    
    # Helper function to clean column names
    def clean_col_names(df):
        """Converts all column names to lowercase with underscores."""
        # Check if df is valid
        if not hasattr(df, 'columns'):
            return df
        # Replace spaces, brackets, and slashes with underscores
        df.columns = df.columns.str.lower().str.replace(r'[\s\(\)/]', '_', regex=True)
        # Replace multiple underscores with a single one
        df.columns = df.columns.str.replace(r'__+', '_', regex=True)
        # Remove any leading/trailing underscores
        df.columns = df.columns.str.strip('_')
        return df

    try:
        # Load all datasets AND clean names immediately
        orders = clean_col_names(pd.read_csv(os.path.join(path, 'orders.csv')))
        performance = clean_col_names(pd.read_csv(os.path.join(path, 'delivery_performance.csv')))
        routes = clean_col_names(pd.read_csv(os.path.join(path, 'routes_distance.csv')))
        fleet = clean_col_names(pd.read_csv(os.path.join(path, 'vehicle_fleet.csv')))
        costs = clean_col_names(pd.read_csv(os.path.join(path, 'cost_breakdown.csv')))
        inventory = clean_col_names(pd.read_csv(os.path.join(path, 'warehouse_inventory.csv')))
        feedback = clean_col_names(pd.read_csv(os.path.join(path, 'customer_feedback.csv')))

    except FileNotFoundError as e:
        st.error(f"Error: Data file not found. Make sure all 7 CSV files are in the '{path}' folder.")
        st.error(f"Missing file: {e.filename}")
        return None, None, None, None
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None, None, None, None

    # --- Merge with standardized 'order_id' key ---
    master_df = pd.merge(orders, performance, on='order_id', how='left')
    master_df = pd.merge(master_df, routes, on='order_id', how='left')
    master_df = pd.merge(master_df, costs, on='order_id', how='left')

    # --- Data Cleaning & Feature Engineering ---

    # 1. Handle missing numerical data
    # Use the cleaned, lowercase column names
    num_cols_to_fill = [
        'distance_km', 'traffic_delays_hours', 'fuel_consumption_liters', 
        'toll_charges', 'delivery_cost', 'customer_rating'
    ]
    for col in num_cols_to_fill:
        if col in master_df.columns:
            median_val = master_df[col].median()
            master_df[col].fillna(median_val, inplace=True)
        else:
            # Add column with 0 if it's missing (e.g., no routes data)
            master_df[col] = 0.0 
    
    # 2. Create 'delivery_delay_hours' using the CLEANED, USER-REQUESTED column names
    master_df['promised_delivery_days'] = pd.to_datetime(master_df['promised_delivery_days'], errors='coerce')
    master_df['actual_delivery_days'] = pd.to_datetime(master_df['actual_delivery_days'], errors='coerce')
    
    master_df['delivery_delay_hours'] = (master_df['actual_delivery_days'] - master_df['promised_delivery_days']).dt.total_seconds() / 3600
    master_df['delivery_delay_hours'].fillna(0, inplace=True)
    
    return master_df, fleet, inventory, feedback

# Load the data
# We only need master_df and fleet_df for this dashboard
master_df, fleet_df, _, _ = load_and_prepare_data(DATA_PATH)

# Stop the app if data loading failed
if master_df is None or fleet_df is None:
    st.error("Data loading failed. Please check file paths and CSV column names.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.title("Filters")
st.sidebar.header("Order Filters")

# Use the cleaned column names (e.g., 'product_category')
category = st.sidebar.multiselect(
    "Select Product Category:",
    options=master_df['product_category'].unique(),
    default=master_df['product_category'].unique()
)

priority = st.sidebar.multiselect(
    "Select Delivery Priority:",
    options=master_df['priority'].unique(),
    default=master_df['priority'].unique()
)

# Apply filters
filtered_df = master_df[
    master_df['product_category'].isin(category) &
    master_df['priority'].isin(priority)
].copy()

if filtered_df.empty:
    st.warning("No data matches the current filters. Please adjust your selection.")
    st.stop()

# --- MAIN PAGE ---
st.title("🚚 NexGen Prescriptive Dispatch Optimizer")
st.markdown("An AI-powered tool to recommend the optimal vehicle for each order, balancing **Cost**, **Time**, and **Sustainability**.")

# --- OPTIMIZATION SECTION ---
st.header("1. Select an Order and Set Optimization Priorities")

col1, col2 = st.columns([1, 2])

with col1:
    # Use the cleaned column name 'order_id'
    selected_order_id = st.selectbox(
        "Choose an Order ID:",
        options=filtered_df['order_id']
    )
    
    order_details = filtered_df[filtered_df['order_id'] == selected_order_id].iloc[0]

    st.subheader(f"Details for {selected_order_id}")
    # Use cleaned column names
    st.metric("Product", order_details['product_category'])
    st.metric("Route", f"{order_details['origin']} ➔ {order_details['destination']}")
    st.metric("Required", "Refrigeration" if order_details['special_handling'] == 'Refrigerated' else "Standard")

with col2:
    st.subheader("Set Your Priorities:")
    weight_cost = st.slider(
        "Importance of 💰 Cost", 0.0, 1.0, 0.5, 0.05, 
        help="Higher value means cost reduction is more important."
    )
    weight_time = st.slider(
        "Importance of ⏰ Speed", 0.0, 1.0, 0.3, 0.05, 
        help="Higher value means faster delivery is more important."
    )
    weight_co2 = st.slider(
        "Importance of 🌍 Sustainability", 0.0, 1.0, 0.2, 0.05, 
        help="Higher value means lower CO2 emissions are more important."
    )
    
    total_weight = weight_cost + weight_time + weight_co2
    if total_weight > 0:
        weight_cost_norm = weight_cost / total_weight
        weight_time_norm = weight_time / total_weight
        weight_co2_norm = weight_co2 / total_weight
    else:
        weight_cost_norm, weight_time_norm, weight_co2_norm = 1/3, 1/3, 1/3

# --- RECOMMENDATION LOGIC ---
if st.button(f"🚀 Optimize Dispatch for {selected_order_id}", use_container_width=True):
    with st.spinner('Analyzing all vehicle combinations...'):
        
        # Use cleaned column name 'product_category'
        is_perishable = order_details['product_category'] in ['Food & Beverage', 'Healthcare']
        
        if is_perishable:
            # Use cleaned column name 'vehicle_type' and lowercase value
            suitable_vehicles = fleet_df[fleet_df['vehicle_type'] == 'refrigerated unit'].copy()
        else:
            suitable_vehicles = fleet_df[fleet_df['vehicle_type'] != 'refrigerated unit'].copy()

        if suitable_vehicles.empty:
            st.error(f"No suitable vehicles found for this order's requirements (Required: {'Refrigerated' if is_perishable else 'Standard'}).")
        else:
            # Check if fleet data has the required columns
            # **** USE CORRECTED LOWERCASE COLUMN NAMES ****
            # These names come from your CSVs after being processed by clean_col_names
            required_fleet_cols = ['vehicle_type', 'fuel_efficiency_km_per_l', 'co2_emissions_kg_per_km', 'capacity_kg']
            
            if not all(col in fleet_df.columns for col in required_fleet_cols):
                st.error(f"Fleet data is missing required columns. Expected: {required_fleet_cols}. Found: {list(fleet_df.columns)}. Please check your CSV.")
                st.stop()
                
            # Use cleaned column names
            distance = order_details['distance_km']
            traffic = order_details['traffic_delays_hours']
            tolls = order_details['toll_charges']
            
            def get_speed(v_type):
                # Use lowercase values for matching
                if v_type in ['express bike', 'van']: return 60
                if v_type == 'truck': return 45
                return 50 # Default for refrigerated unit

            suitable_vehicles['avg_speed_kmh'] = suitable_vehicles['vehicle_type'].apply(get_speed)
            suitable_vehicles['predicted_time_hours'] = (distance / suitable_vehicles['avg_speed_kmh']) + traffic

            # **** USE CORRECTED LOWERCASE COLUMN NAMES ****
            fuel_needed_liters = distance / suitable_vehicles['fuel_efficiency_km_per_l']
            fuel_cost = fuel_needed_liters * ASSUMED_FUEL_PRICE_PER_LITER
            labor_cost = suitable_vehicles['predicted_time_hours'] * ASSUMED_LABOR_COST_PER_HOUR
            suitable_vehicles['predicted_cost'] = fuel_cost + labor_cost + tolls
            
            # **** USE CORRECTED LOWERCASE COLUMN NAMES ****
            # The column name 'co2_emissions_kg_per_km' implies units are already in kg
            suitable_vehicles['predicted_co2_kg'] = distance * suitable_vehicles['co2_emissions_kg_per_km']

            def normalize(col):
                min_val = col.min()
                max_val = col.max()
                if max_val - min_val > 0:
                    return (col - min_val) / (max_val - min_val)
                return 0.0
            
            suitable_vehicles['norm_cost'] = normalize(suitable_vehicles['predicted_cost'])
            suitable_vehicles['norm_time'] = normalize(suitable_vehicles['predicted_time_hours'])
            suitable_vehicles['norm_co2'] = normalize(suitable_vehicles['predicted_co2_kg'])

            suitable_vehicles['optimization_score'] = (
                weight_cost_norm * suitable_vehicles['norm_cost'] +
                weight_time_norm * suitable_vehicles['norm_time'] +
                weight_co2_norm * suitable_vehicles['norm_co2']
            )
            
            suitable_vehicles = suitable_vehicles.sort_values('optimization_score')
            best_vehicle = suitable_vehicles.iloc[0]

            st.header("🏆 Recommendation")
            st.success(f"**Best Vehicle:** {best_vehicle['vehicle_id']} ({best_vehicle['vehicle_type']})")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Optimization Score", f"{best_vehicle['optimization_score']:.2f}", help="Lower is better. Based on your priorities.")
            c2.metric("Predicted Cost", f"${best_vehicle['predicted_cost']:.2f}")
            c3.metric("Predicted Time", f"{best_vehicle['predicted_time_hours']:.1f} hours")
            c4.metric("Predicted CO2", f"{best_vehicle['predicted_co2_kg']:.1f} kg")

            st.subheader("All Suitable Options (Sorted by Score)")
            # **** USE CORRECTED LOWERCASE COLUMN NAMES ****
            st.dataframe(suitable_vehicles[[
                'vehicle_id', 'vehicle_type', 'optimization_score', 
                'predicted_cost', 'predicted_time_hours', 'predicted_co2_kg', 
                'capacity_kg'
            ]].round(2))

# --- VISUALIZATIONS ---
st.header("2. Analytics Dashboard")

c1, c2 = st.columns((1, 1))

with c1:
    st.subheader("Vehicle Fleet: Efficiency vs. Emissions")
    # **** USE CORRECTED LOWERCASE COLUMN NAMES ****
    fig1 = px.scatter(
        fleet_df,
        x="fuel_efficiency_km_per_l",
        y="co2_emissions_kg_per_km",
        color="vehicle_type",
        size="capacity_kg",
        hover_name="vehicle_id",
        title="Vehicle Efficiency vs. CO2 Emissions"
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Average Delivery Delay by Priority")
    # Use cleaned column names
    delay_by_priority = filtered_df.groupby('priority')['delivery_delay_hours'].mean().reset_index()
    fig2 = px.bar(
        delay_by_priority,
        x='priority',
        y='delivery_delay_hours',
        color='priority',
        title='Average Delivery Delay (hours)',
        labels={'delivery_delay_hours': 'Avg. Delay (Hours)'}
    )
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns((1, 1))
with c3:
    st.subheader("Order Volume by Product Category")
    # Use cleaned column name
    category_counts = filtered_df['product_category'].value_counts()
    fig3 = px.pie(
        category_counts,
        values=category_counts.values,
        names=category_counts.index,
        title="Share of Orders by Product Category",
        hole=0.3
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader("Distribution of Delivery Costs by Carrier")
    # Use cleaned column names
    fig4 = px.box(
        filtered_df,
        x='carrier',
        y='delivery_cost',
        color='carrier',
        title='Delivery Cost Distribution by Carrier',
        labels={'delivery_cost': 'Delivery Cost'}
    )
    st.plotly_chart(fig4, use_container_width=True)

# --- DATA EXPORT ---
st.header("3. Export Filtered Data")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(filtered_df)

st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_logistics_data.csv",
    mime="text/csv",
    use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.info(
    "This app was created for the **Logistics Innovation Challenge**."
)
