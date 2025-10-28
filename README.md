# **NexGen Prescriptive Dispatch Optimizer 🚚**

This project is a Streamlit web application built for the **NexGen Logistics Innovation Challenge**. It provides a data-driven tool for logistics managers to make optimal dispatch decisions, transforming operations from reactive to prescriptive.

## **1\. The Problem**

NexGen Logistics, a mid-sized logistics company, faces critical challenges in its operations, including:

* Delivery performance issues and delays.  
* Operational inefficiencies and high costs.  
* Sustainability concerns (CO2 emissions).  
* A need to build a data-driven, predictive decision-making culture.

This tool directly addresses the company's goal to **reduce operational costs by 15-20%** and **position itself as an innovation leader**.

## **2\. Our Solution**

The **Prescriptive Dispatch Optimizer** is an interactive dashboard that analyzes incoming orders and recommends the single best vehicle to dispatch.

Instead of just showing data (descriptive analytics), this tool provides a clear, actionable recommendation (prescriptive analytics) by balancing three competing factors:

* **💰 Cost:** Minimizes fuel, labor, and toll charges.  
* **⏰ Speed:** Minimizes travel and delay times.  
* **🌍 Sustainability:** Minimizes the total CO2 emissions for the trip.

A logistics manager can select any order, weigh the importance of cost vs. speed vs. sustainability, and instantly receive a ranked list of all suitable vehicles for the job.

## **3\. Tech Stack**

* **Python:** Core programming language.  
* **Streamlit:** For building the interactive web application.  
* **Pandas:** For data loading, cleaning, and manipulation.  
* **Plotly Express:** For creating interactive data visualizations.

## **4\. How to Run This Project Locally**

### **Prerequisites**

* Python 3.8+  
* All 7 dataset CSV files (orders.csv, vehicle\_fleet.csv, etc.)

### **Setup & Installation**

1. **Clone the repository (or download the files)** into a single project folder.  
2. **Place all 7 CSV files** into a sub-folder named NextGen\_data. The project structure should look like this:  
   NexGen\_Project/  
   ├── app.py  
   ├── README.md  
   └── NextGen\_data/  
       ├── orders.csv  
       ├── delivery\_performance.csv  
       ├── routes\_distance.csv  
       ├── vehicle\_fleet.csv  
       ├── cost\_breakdown.csv  
       ├── warehouse\_inventory.csv  
       └── customer\_feedback.csv

3. Update the DATA\_PATH in app.py:  
   If you are running this on your local computer (not Google Colab), open app.py and change the DATA\_PATH variable to:  
   DATA\_PATH \= "./NextGen\_data/"

4. **Create a virtual environment (Recommended):**  
   python \-m venv venv  
   source venv/bin/activate  \# On macOS/Linux  
   .\\venv\\Scripts\\activate   \# On Windows

5. Install the required libraries:  
   Create a requirements.txt file with the following content:  
   streamlit  
   pandas  
   plotly

   Then, run:  
   pip install \-r requirements.txt

6. Run the Streamlit App:  
   From your terminal, in the project's root directory, run:  
   streamlit run app.py

Your browser will automatically open to http://localhost:8501.

## **5\. Key Features**

* **Prescriptive Recommendation Engine:** Select any order and set priority weights for Cost, Speed, and Sustainability to get an optimized vehicle recommendation.  
* **Dynamic Filtering:** The entire app and all analyses can be filtered by Product Category and Order Priority via the sidebar.  
* **Interactive Analytics Dashboard (4+ Charts):**  
  1. **Vehicle Efficiency vs. Emissions:** A scatter plot to identify the most efficient and greenest vehicles in the fleet.  
  2. **Average Delivery Delay:** A bar chart showing average delays by order priority.  
  3. **Order Volume by Category:** A pie chart showing the distribution of business.  
  4. **Cost Distribution by Carrier:** A box plot to analyze cost variations between logistics partners.  
* **Data Export:** Download the currently filtered data as a CSV for further analysis.