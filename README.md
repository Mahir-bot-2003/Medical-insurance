# Medical-insurance
# Insurance Cost Prediction using Linear Regression  

## 📌 Introduction  
This project predicts **individual medical insurance costs** based on personal attributes such as age, BMI, smoking status, and region. By applying **Linear Regression**, the goal is to understand the factors influencing insurance premiums and build a predictive model that estimates charges accurately.  
---

## 📂 Dataset  
The project uses the **insurance.csv** dataset containing **1338 rows** and the following columns:  

- **age**: Age of the primary beneficiary  
- **sex**: Gender (male, female)  
- **bmi**: Body Mass Index (BMI)  
- **children**: Number of children covered by insurance  
- **smoker**: Smoking status (yes, no)  
- **region**: Residential area in the US (northeast, southeast, southwest, northwest)  
- **charges**: Individual medical costs (target variable)  

---

## 🔄 Project Workflow  
1. **Data Loading & Exploration**  
   - Load data using pandas  
   - Inspect structure with `.info()` and `.describe()`  

2. **Exploratory Data Analysis (EDA)**  
   - Visualizations (seaborn & matplotlib)  
   - Key insights:  
     - Charges are right-skewed  
     - Smokers have significantly higher costs  
     - Costs rise with age (especially for smokers)  

3. **Data Preprocessing**  
   - Encode categorical variables (`sex`, `smoker`, `region`) using one-hot encoding  

4. **Model Training**  
   - Split dataset into training (80%) and testing (20%)  
   - Train a **Linear Regression** model using scikit-learn  

5. **Model Evaluation**  
   - **RMSE**: 5796.28  
   - **R² Score**: 0.78 (model explains 78% of variability in charges)  

---

## 📊 Results  
- **RMSE**: 5796.28  
- **R² Score**: 0.78  
- Smoking status and age are the most significant predictors of insurance costs.  

---

## ✨ Features  
- Predicts insurance charges based on personal factors  
- End-to-end pipeline: data exploration → preprocessing → training → evaluation  
- Visual analysis to identify key patterns in insurance costs  

---

## ⚙️ Requirements  
The project requires the following Python libraries:  

- pandas  
- numpy  
- matplotlib  
- seaborn  
- scikit-learn  

---


   git clone https://github.com/yourusername/insurance-cost-prediction.git
   cd insurance-cost-prediction
