import streamlit as st
import pulp
import numpy as np
import pandas as pd
from streamlit_option_menu import option_menu

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Chicken Feed Formulator",
    page_icon="🐔",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# CUSTOM CSS FOR MOBILE-FRIENDLY UI
# --------------------------------------------------
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    }
    
    /* Card styling */
    .css-1r6slb0 {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 50px;
        font-size: 18px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 5px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Results table */
    .results-table {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    /* Error message */
    .error-box {
        background: linear-gradient(135deg, #f56565 0%, #c53030 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #48bb78 0%, #2f855a 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
    
    /* Ingredient grid */
    .ingredient-grid {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        max-height: 400px;
        overflow-y: auto;
        border: 2px solid #e0e0e0;
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5em !important;
        margin-bottom: 30px !important;
    }
    
    h2 {
        color: #4a5568;
        font-size: 1.5em !important;
        margin-top: 20px !important;
        margin-bottom: 15px !important;
    }
    
    h3 {
        color: #718096;
        font-size: 1.2em !important;
    }
    
    /* Divider */
    .stDivider {
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATA (PRESERVED EXACTLY FROM KIVY APP)
# --------------------------------------------------
# المجموعات
energy_sources = ["Barley", "Corn, yellow", "Sorghum, grain", "Wheat bran"]
protein_sources = ["Soybean meal, solvent", "Soybean meal, dehulled solvent", 
                   "Fish meal, herring", "Meat meal", "Poultry by-product meal"]

ingredients_data = {
    "Barley": {"protein": 11.0, "energy": 2800, "calcium": 0.05},
    "Blood_meal": {"protein": 80.0, "energy": 2600, "calcium": 0.30},
    "Corn": {"protein": 8.5, "energy": 3300, "calcium": 0.03},
    "Fat": {"protein": 0.0, "energy": 8800, "calcium": 0.00},
    "Feather_meal": {"protein": 85.0, "energy": 2500, "calcium": 0.20},
    "Fish_meal_herring": {"protein": 60.0, "energy": 2900, "calcium": 5.5},
    "Fish_meal_menhaden": {"protein": 62.0, "energy": 3000, "calcium": 5.0},
    "Fish_meal_white": {"protein": 58.0, "energy": 2800, "calcium": 4.5},
    "Meat_meal": {"protein": 55.0, "energy": 2800, "calcium": 5.0},
    "Meat_and_bone_meal": {"protein": 50.0, "energy": 2600, "calcium": 10.0},
    "Poultry_byproduct_meal": {"protein": 60.0, "energy": 3000, "calcium": 4.0},
    "Sesame_meal": {"protein": 42.0, "energy": 2400, "calcium": 1.2},
    "Sorghum": {"protein": 10.0, "energy": 3100, "calcium": 0.04},
    "Soybean_heat": {"protein": 44.0, "energy": 2800, "calcium": 0.25},
    "Soybean_meal_solvent": {"protein": 44.0, "energy": 2700, "calcium": 0.25},
    "Soybean_meal_dehulled": {"protein": 48.0, "energy": 2800, "calcium": 0.25},
    "Sunflower_meal": {"protein": 35.0, "energy": 2200, "calcium": 0.35},
    "Wheat_bran": {"protein": 16.0, "energy": 1700, "calcium": 0.13},
    "Bone_meal": {"protein": 0.0, "energy": 0.0, "calcium": 30.0},
    "Calcium_carbonate": {"protein": 0.0, "energy": 0.0, "calcium": 38.0},
    "limestone": {"protein": 0.0, "energy": 0.0, "calcium": 36.0},
    "oyster": {"protein": 0.0, "energy": 0.0, "calcium": 35.0},
    "Phosphate_dicalcium": {"protein": 0.0, "energy": 0.0, "calcium": 23.0},
}

requirements = {
    "Starter": {"protein": 23, "energy": 3000, "calcium": 1.0},
    "Grower": {"protein": 20, "energy": 3100, "calcium": 0.9},
    "Finisher": {"protein": 18, "energy": 3200, "calcium": 0.8}
}

# Display names mapping
ingredient_display_names = {
    "Barley": "Barley",
    "Blood_meal": "Blood meal",
    "Corn": "Corn, yellow",
    "Fat": "Fat (animal, hydrolized)",
    "Feather_meal": "Feather meal, hydrolized",
    "Fish_meal_herring": "Fish meal, herring",
    "Fish_meal_menhaden": "Fish meal, menhaden",
    "Fish_meal_white": "Fish meal, white",
    "Meat_meal": "Meat meal",
    "Meat_and_bone_meal": "Meat-and bone meal",
    "Poultry_byproduct_meal": "Poultry by-product meal",
    "Sesame_meal": "Sesame meal, expeller",
    "Sorghum": "Sorghum, grain",
    "Soybean_heat": "Soybean, heat processed",
    "Soybean_meal_solvent": "Soybean meal, solvent",
    "Soybean_meal_dehulled": "Soybean meal, dehulled solvent",
    "Sunflower_meal": "Sunflower meal, dehulled solvent",
    "Wheat_bran": "Wheat bran",
    "Bone_meal": "Bone meal",
    "Calcium_carbonate": "Calcium carbonate",
    "limestone": "Limestone, ground",
    "oyster": "Oyster shell, ground",
    "Phosphate_dicalcium": "Phosphate dicalcium"
}

# Reverse mapping for selection
reverse_display_names = {v: k for k, v in ingredient_display_names.items()}

# --------------------------------------------------
# HELPER FUNCTIONS (PRESERVED FROM KIVY APP)
# --------------------------------------------------
def solve_three_equations(ingredients, requirements):
    """
    Solve system of 3 equations with 3 unknowns for ANY ingredient combination
    (Exactly as in the Kivy app)
    """
    
    # Get ingredient data
    ing1_data = ingredients_data[ingredients[0]]
    ing2_data = ingredients_data[ingredients[1]]
    ing3_data = ingredients_data[ingredients[2]]
    
    # Try multiple approaches to find a solution
    
    # Approach 1: Direct linear algebra
    try:
        A = np.array([
            [ing1_data["protein"], ing2_data["protein"], ing3_data["protein"]],
            [ing1_data["energy"], ing2_data["energy"], ing3_data["energy"]],
            [1, 1, 1]
        ])
        B = np.array([
            requirements["protein"] * 97,
            requirements["energy"] * 97, 
            97
        ])
        
        solution = np.linalg.solve(A, B)
        
        # Check if solution is physically possible (all positive)
        if all(x >= -0.1 for x in solution):  # Small tolerance for rounding errors
            # Adjust any slightly negative values to zero
            adjusted_solution = [max(0, x) for x in solution]
            
            # Re-normalize to 97% if needed
            total = sum(adjusted_solution)
            if abs(total - 97) > 0.1:
                adjusted_solution = [x * 97 / total for x in adjusted_solution]
            
            return adjusted_solution
            
    except np.linalg.LinAlgError:
        pass
    
    # Approach 2: Linear programming with relaxed constraints
    return solve_with_linear_programming(ingredients, requirements)

def solve_with_linear_programming(ingredients, requirements):
    """Enhanced linear programming that uses ALL ingredients (from Kivy app)"""
    
    prob = pulp.LpProblem("FeedFormulation", pulp.LpMinimize)
    
    # Variables with minimum usage constraints
    x1 = pulp.LpVariable(ingredients[0], lowBound=5, upBound=80)   # At least 5%
    x2 = pulp.LpVariable(ingredients[1], lowBound=5, upBound=80)   # At least 5%
    x3 = pulp.LpVariable(ingredients[2], lowBound=5, upBound=80)   # At least 5%
    
    # Get ingredient data
    ing1_data = ingredients_data[ingredients[0]]
    ing2_data = ingredients_data[ingredients[1]]
    ing3_data = ingredients_data[ingredients[2]]
    
    # Objective: minimize the deviation from requirements
    protein_dev = pulp.LpVariable("protein_dev", lowBound=0)
    energy_dev = pulp.LpVariable("energy_dev", lowBound=0)
    
    prob += protein_dev + energy_dev  # Minimize total deviation
    
    # Protein constraint
    protein_total = (
        x1 * ing1_data["protein"] +
        x2 * ing2_data["protein"] +
        x3 * ing3_data["protein"]
    )
    protein_target = requirements["protein"] * 97
    
    prob += protein_total >= protein_target
    prob += protein_total - protein_target <= protein_dev
    
    # Energy constraint  
    energy_total = (
        x1 * ing1_data["energy"] +
        x2 * ing2_data["energy"] +
        x3 * ing3_data["energy"]
    )
    energy_target = requirements["energy"] * 97
    
    prob += energy_total >= energy_target
    prob += energy_total - energy_target <= energy_dev
    
    # Sum to 97%
    prob += (x1 + x2 + x3 == 97)
    
    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if prob.status == 1:
        solution = [x1.value(), x2.value(), x3.value()]
        return solution
    else:
        # Fallback without minimum constraints
        return solve_with_linear_programming_fallback(ingredients, requirements)

def solve_with_linear_programming_fallback(ingredients, requirements):
    """Fallback without minimum constraints (from Kivy app)"""
    prob = pulp.LpProblem("FeedFormulation_Fallback", pulp.LpMinimize)
    
    x1 = pulp.LpVariable(ingredients[0], lowBound=0, upBound=97)
    x2 = pulp.LpVariable(ingredients[1], lowBound=0, upBound=97) 
    x3 = pulp.LpVariable(ingredients[2], lowBound=0, upBound=97)
    
    ing1_data = ingredients_data[ingredients[0]]
    ing2_data = ingredients_data[ingredients[1]]
    ing3_data = ingredients_data[ingredients[2]]
    
    # Simple objective
    prob += x1 + x2 + x3
    
    # Constraints
    prob += (
        x1 * ing1_data["protein"] +
        x2 * ing2_data["protein"] +
        x3 * ing3_data["protein"] >= requirements["protein"] * 97
    )
    
    prob += (
        x1 * ing1_data["energy"] +
        x2 * ing2_data["energy"] +
        x3 * ing3_data["energy"] >= requirements["energy"] * 97
    )
    
    prob += (x1 + x2 + x3 == 97)
    
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if prob.status == 1:
        return [x1.value(), x2.value(), x3.value()]
    else:
        # Last resort: proportional distribution based on protein content
        protein_sum = sum(ingredients_data[ing]["protein"] for ing in ingredients)
        return [97 * ingredients_data[ing]["protein"] / protein_sum for ing in ingredients]

# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
def main():
    # Small header with just the icon (optional)
    st.markdown("""
    <div style='text-align: center; padding: 10px; margin-bottom: 5px;'>
        <span style='font-size: 2em;'>🐔</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Home", "Settings", "Calculate"],
        icons=["house", "gear", "calculator"],
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa", "border-radius": "12px"},
            "icon": {"color": "#667eea", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "color": "#4a5568"},
            "nav-link-selected": {"background-color": "#667eea", "color": "white"},
        }
    )
    
    if selected == "Home":
        show_home()
    elif selected == "Settings":
        show_settings()
    elif selected == "Calculate":
        show_calculation()

def show_home():
    # Beautiful blue title for home page
    st.markdown("""
    <div style='text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 20px; margin: 0 0 25px 0; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);'>
        <h1 style='color: white; font-size: 3em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>🐔 Healthy Chicken</h1>
        <h2 style='color: white; font-size: 1.8em; margin: 10px 0 0 0; opacity: 0.95; font-weight: 400;'>Feed Formulator</h2>
        <p style='color: white; font-size: 1.1em; margin: 15px 0 0 0; opacity: 0.9;'>Optimize your poultry nutrition with science-based formulations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome card
    st.markdown("""
    <div class='css-1r6slb0'>
        <h2 style='color: #4a5568; margin-top: 0; border-bottom: 2px solid #667eea; padding-bottom: 10px;'>Welcome to Chicken Feed Formulator!</h2>
        <p style='font-size: 18px; color: #4a5568; line-height: 1.6;'>
            This application helps you formulate the optimal chicken feed mixture based on nutritional requirements.
        </p>
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 20px 0;'>
            <h3 style='color: white; margin-bottom: 15px;'>How it works:</h3>
            <ul style='color: white; font-size: 16px; line-height: 2;'>
                <li>📋 Select exactly 3 ingredients from the list</li>
                <li>🎯 Choose the broiler age stage (Starter/Grower/Finisher)</li>
                <li>⚙️ Click Calculate to get the optimal mixture</li>
                <li>📊 View detailed results with nutrient analysis</li>
            </ul>
        </div>
        <p style='text-align: center; margin-top: 20px;'>
            <strong>Click on Settings to begin!</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
def show_settings():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    
    # Age range selection
    st.markdown("<h2>🐣 Choose Broilers Age Range</h2>", unsafe_allow_html=True)
    age_range = st.selectbox(
        "",
        ["Starter", "Grower", "Finisher"],
        index=0,
        key="age_range_widget"  # Changed key name to avoid confusion
    )
    
    st.markdown("<h2>🥣 Select Exactly 3 Ingredients</h2>", unsafe_allow_html=True)
    
    # Ingredient selection in scrollable grid
    st.markdown("<div class='ingredient-grid'>", unsafe_allow_html=True)
    
    # Create columns for better organization
    col1, col2 = st.columns(2)
    
    # Split ingredients into two columns
    ingredients_list = list(ingredient_display_names.values())
    mid_point = len(ingredients_list) // 2
    
    selected_ingredients = []
    
    with col1:
        for ing in ingredients_list[:mid_point]:
            if st.checkbox(ing, key=f"cb_{ing}"):
                selected_ingredients.append(reverse_display_names[ing])
    
    with col2:
        for ing in ingredients_list[mid_point:]:
            if st.checkbox(ing, key=f"cb_{ing}"):
                selected_ingredients.append(reverse_display_names[ing])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Store in different session state keys (not the widget keys)
    if 'saved_ingredients' not in st.session_state:
        st.session_state['saved_ingredients'] = []
    
    if 'saved_age_range' not in st.session_state:
        st.session_state['saved_age_range'] = "Starter"
    
    # Validation button
    if st.button("✅ Validate Selection", key="validate"):
        if len(selected_ingredients) != 3:
            st.markdown("""
            <div class='error-box'>
                ❌ Please select exactly 3 ingredients for the calculation.
            </div>
            """, unsafe_allow_html=True)
        else:
            # Check energy and protein sources
            selected_display = [ingredient_display_names[ing] for ing in selected_ingredients]
            has_energy = any(source in selected_display for source in energy_sources)
            has_protein = any(source in selected_display for source in protein_sources)
            
            if not has_energy:
                st.markdown("""
                <div class='error-box'>
                    ❌ Please select at least one energy source (e.g., Corn).
                </div>
                """, unsafe_allow_html=True)
            elif not has_protein:
                st.markdown("""
                <div class='error-box'>
                    ❌ Please select at least one protein source (e.g., Soybean meal).
                </div>
                """, unsafe_allow_html=True)
            else:
                # Save to session state using different keys
                st.session_state['saved_ingredients'] = selected_ingredients
                st.session_state['saved_age_range'] = age_range
                st.markdown("""
                <div class='success-box'>
                    ✅ Selection validated! Go to Calculate tab.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_calculation():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    
    st.markdown("<h2>🧮 Calculate Optimal Formula</h2>", unsafe_allow_html=True)
    
    # Check if we have selections
    if 'saved_ingredients' not in st.session_state or len(st.session_state.get('saved_ingredients', [])) != 3:
        st.markdown("""
        <div class='error-box'>
            ⚠️ Please go to Settings and select exactly 3 ingredients first.
        </div>
        """, unsafe_allow_html=True)
    else:
        selected_ingredients = st.session_state['saved_ingredients']
        age_range = st.session_state['saved_age_range']
        
        # Fixed batch size of 100g
        batch_size_g = 100  # 100 grams
        
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 15px; border-radius: 12px; margin-bottom: 20px;'>
            <p><strong>Selected Age:</strong> {age_range}</p>
            <p><strong>Selected Ingredients:</strong></p>
            <ul>
                <li>{ingredient_display_names[selected_ingredients[0]]}</li>
                <li>{ingredient_display_names[selected_ingredients[1]]}</li>
                <li>{ingredient_display_names[selected_ingredients[2]]}</li>
            </ul>
            <p><strong>Batch Size:</strong> {batch_size_g} grams</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Calculations", key="calculate"):
            with st.spinner("Calculating optimal mix... Please wait"):
                try:
                    req = requirements[age_range]
                    solution = solve_three_equations(selected_ingredients, req)
                    
                    if any(x < 0 for x in solution) or any(x > 97 for x in solution):
                        st.markdown("""
                        <div class='error-box'>
                            ❌ No valid solution found. Please try different ingredients.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Show results
                        st.markdown("<h3>📊 Final Ration Mixture (100g Batch)</h3>", unsafe_allow_html=True)
                        
                        # Create results table with both % and grams
                        main_ingredients_total = 0
                        results_data = []
                        
                        for i, ing in enumerate(selected_ingredients):
                            percentage = max(0, min(97, solution[i]))
                            grams = (percentage / 100) * batch_size_g
                            ing_name = ingredient_display_names[ing]
                            results_data.append({
                                "Ingredient": ing_name,
                                "Percentage (%)": round(percentage, 2),
                                "Amount (g)": round(grams, 2)
                            })
                            main_ingredients_total += percentage
                        
                        # Add fixed additives
                        additives = [
                            ("Dicalcium Phosphate", 1.00),
                            ("Limestone", 0.91),
                            ("Methionine", 0.06)
                        ]
                        
                        for name, percent in additives:
                            grams = (percent / 100) * batch_size_g
                            results_data.append({
                                "Ingredient": name,
                                "Percentage (%)": percent,
                                "Amount (g)": round(grams, 2)
                            })
                        
                        # Calculate remaining additives
                        remaining_additives = 3.00 - (1.00 + 0.91 + 0.06)
                        grams_remaining = (remaining_additives / 100) * batch_size_g
                        results_data.append({
                            "Ingredient": "Additives*",
                            "Percentage (%)": round(remaining_additives, 2),
                            "Amount (g)": round(grams_remaining, 2)
                        })
                        
                        # Create DataFrame
                        df = pd.DataFrame(results_data)
                        
                        # Style the dataframe
                        st.dataframe(
                            df.style.apply(lambda x: ['background: #f0f2f6' if i % 2 == 0 else '' for i in range(len(x))], axis=0),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Totals
                        final_total_pct = main_ingredients_total + 3.00
                        final_total_grams = (final_total_pct / 100) * batch_size_g
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div style='text-align: right; font-size: 20px; font-weight: bold; margin-top: 10px;'>
                                Total (%): {final_total_pct:.2f}%
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div style='text-align: right; font-size: 20px; font-weight: bold; margin-top: 10px; color: #667eea;'>
                                Total (g): {final_total_grams:.2f}g
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Quick reference for common batch sizes
                        st.markdown("""
                        <p style='font-size: 14px; color: #718096; margin-top: 5px; text-align: center;'>
                            <strong>Quick Reference:</strong> For 1kg batch, multiply grams by 10 | For 5kg batch, multiply by 50
                        </p>
                        """, unsafe_allow_html=True)
                        
                        # Calculation note
                        st.markdown("""
                        <p style='font-size: 14px; color: #718096; margin-top: 10px;'>
                            * Calculated as [3.00 - (1.00 + 0.91 + 0.06)]
                        </p>
                        """, unsafe_allow_html=True)
                        
                        # Nutrient analysis
                        st.markdown("<h3>🧪 Nutrient Analysis (per 100g)</h3>", unsafe_allow_html=True)
                        
                        # Calculate actual nutrients achieved
                        protein_achieved = sum(solution[i] * ingredients_data[selected_ingredients[i]]["protein"] / 100 for i in range(3))
                        energy_achieved = sum(solution[i] * ingredients_data[selected_ingredients[i]]["energy"] / 100 for i in range(3))
                        calcium_achieved = sum(solution[i] * ingredients_data[selected_ingredients[i]]["calcium"] / 100 for i in range(3))
                        
                        # Add nutrients from fixed additives
                        calcium_achieved += (1.00 * 23.0 + 0.91 * 36.0) / 100
                        
                        req = requirements[age_range]
                        
                        # Calculate nutrients for the 100g batch
                        protein_g = (protein_achieved / 100) * batch_size_g
                        energy_kcal = (energy_achieved / 1000) * batch_size_g  # Convert kcal/kg to kcal/100g
                        calcium_g = (calcium_achieved / 100) * batch_size_g
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <div class='metric-label'>Protein</div>
                                <div class='metric-value'>{protein_achieved:.1f}%</div>
                                <div style='font-size: 12px;'>Target: {req['protein']}%</div>
                                <div style='font-size: 12px; margin-top: 5px;'>{protein_g:.2f}g per 100g</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <div class='metric-label'>Energy</div>
                                <div class='metric-value'>{energy_achieved:.0f}</div>
                                <div style='font-size: 12px;'>Target: {req['energy']} kcal/kg</div>
                                <div style='font-size: 12px; margin-top: 5px;'>{energy_kcal:.1f} kcal per 100g</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <div class='metric-label'>Calcium</div>
                                <div class='metric-value'>{calcium_achieved:.2f}%</div>
                                <div style='font-size: 12px;'>Target: {req['calcium']}%</div>
                                <div style='font-size: 12px; margin-top: 5px;'>{calcium_g:.2f}g per 100g</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Scaling guide
                        with st.expander("📏 Scaling Guide - Convert to any batch size"):
                            st.markdown("""
                            | Batch Size | Multiply 100g recipe by |
                            |------------|------------------------|
                            | 250g | 2.5× |
                            | 500g | 5× |
                            | 1kg | 10× |
                            | 2kg | 20× |
                            | 5kg | 50× |
                            | 10kg | 100× |
                            | 25kg | 250× |
                            | 50kg | 500× |
                            
                            **Example:** For a 2.5kg batch, multiply each ingredient amount by 25
                            """)
                        
                        # Add download button for results
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"feed_formulation_{age_range}_100g.csv",
                            mime="text/csv",
                            key="download_results"
                        )
                        
                        # Quality assessment
                        protein_diff = abs(protein_achieved - req['protein']) / req['protein'] * 100
                        energy_diff = abs(energy_achieved - req['energy']) / req['energy'] * 100
                        
                        if protein_diff <= 5 and energy_diff <= 5:
                            st.markdown("""
                            <div class='success-box'>
                                ✅ Excellent match with requirements!
                            </div>
                            """, unsafe_allow_html=True)
                        elif protein_diff <= 10 and energy_diff <= 10:
                            st.markdown("""
                            <div style='background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%); color: white; padding: 15px; border-radius: 12px; text-align: center; margin-top: 20px;'>
                                ⚠️ Good match - close to requirements
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style='background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); color: white; padding: 15px; border-radius: 12px; text-align: center; margin-top: 20px;'>
                                📊 Solution found - consider adjusting ingredients for better match
                            </div>
                            """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.markdown(f"""
                    <div class='error-box'>
                        ❌ Calculation error: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()