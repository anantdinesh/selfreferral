import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Sanford Kidney Transplant Screener",
    page_icon="🏥",
    layout="centered"
)

# --- Logic Helper Functions ---
def calculate_bmi(height_ft, height_in, weight_lbs):
    if height_ft and weight_lbs:
        total_inches = (height_ft * 12) + height_in
        if total_inches > 0:
            bmi = (weight_lbs / (total_inches ** 2)) * 703
            return round(bmi, 1)
    return None

def determine_eligibility(data, bmi):
    status = 'eligible'
    messages = []
    
    # 1. HARD STOPS (Likely Ineligible)
    if data['active_cancer']:
        status = 'ineligible'
        messages.append("Active malignancy (cancer) is typically a contraindication. Generally, you must be cancer-free for a specific period (often 2-5 years) before being listed.")
    
    if data['active_infection']:
        status = 'ineligible'
        messages.append("Active systemic infections must be fully treated and resolved before transplantation can proceed.")
        
    if data['substance_abuse']:
        status = 'ineligible'
        messages.append("Active substance abuse is a contraindication. Programs typically require a demonstrated period of sobriety/abstinence.")

    # 2. CONDITIONAL / WARNINGS
    if status != 'ineligible':
        if data['heart_lung_disease']:
            status = 'conditional'
            messages.append("Severe heart or lung disease requires a detailed clearance by a specialist to ensure you are healthy enough for surgery.")
        
        if bmi:
            if bmi > 40:
                status = 'conditional'
                messages.append(f"Your calculated BMI is {bmi}. A BMI over 40 may delay listing. The team may work with you on a weight loss plan prior to surgery.")
            elif bmi > 35:
                status = 'conditional'
                messages.append(f"Your calculated BMI is {bmi}. While eligible, a BMI over 35 carries higher surgical risks.")

        if data['age'] and data['age'] > 75:
            status = 'conditional'
            messages.append("While there is no strict age limit, candidates over 75 undergo a more rigorous evaluation to ensure they can tolerate the surgery and medication.")

        if data['social_support'] == "No / Unsure":
            status = 'conditional'
            messages.append("Post-transplant care requires a dedicated support person. You will need to identify a support system to be listed.")

        # Kidney Function Check
        if data['on_dialysis'] == "No":
            if data['gfr'] and data['gfr'] > 20:
                status = 'conditional'
                messages.append("Typically, patients are listed for transplant when GFR drops below 20. If your GFR is between 20-30, you can still be evaluated, but waiting time may not accrue yet.")

    return status, messages

# --- UI Functions ---

def render_header():
    st.markdown("""
    <div style='background-color: #1e3a8a; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0;'>Sanford Kidney Transplant</h1>
        <p style='color: #bfdbfe; margin: 0;'>Self-Referral Eligibility Screener (Fargo, ND)</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("ℹ️ This form assesses potential eligibility based on standard transplant guidelines. It is not a medical diagnosis.")

def render_results():
    result = st.session_state.result
    status, messages = result['status'], result['messages']
    
    st.divider()
    st.subheader("Screening Results")

    # Display Status Box
    if status == 'eligible':
        st.success("## ✅ Likely Eligible for Evaluation")
        st.write("Based on your responses, you appear to meet the initial screening criteria for a kidney transplant evaluation at Sanford Fargo.")
    
    elif status == 'conditional':
        st.warning("## ⚠️ Conditional Eligibility")
        st.write("You may be eligible, but there are specific factors (BMI, age, or medical history) that the transplant team will need to evaluate closely.")
        
    elif status == 'ineligible':
        st.error("## ❌ Likely Ineligible at this time")
        st.write("Based on standard transplant guidelines, there are contraindications present that typically prevent listing.")

    # Display Messages
    if messages:
        with st.container():
            st.markdown("**Specific Considerations:**")
            for msg in messages:
                st.markdown(f"- {msg}")

    # Next Steps Section
    st.markdown("---")
    st.markdown("### ❤️ Next Steps")
    
    if status == 'ineligible':
        st.write("Please speak with your primary doctor or nephrologist to manage the conditions listed above. If your situation changes (e.g., cancer remission, infection cleared), you can re-apply.")
    else:
        st.write("You do **not** need a doctor's referral to start the process. You can self-refer by contacting the Sanford Transplant Center directly.")
        
        # Contact Card
        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            **📞 Call to Self-Refer:**
            
            **(701) 234-6246**
            
            or (701) 234-3360
            """)
        with col2:
            st.info("""
            **📍 Location:**
            
            **Sanford Broadway Medical Building**
            
            736 Broadway N, Fargo, ND 58102
            """)

    if st.button("Start Over"):
        st.session_state.result = None
        st.rerun()

# --- Main Application Loop ---

def main():
    if 'result' not in st.session_state:
        st.session_state.result = None

    # If results exist, show them (and hide form)
    if st.session_state.result:
        render_header()
        render_results()
        return

    # --- Render Form ---
    render_header()

    with st.container():
        # 1. Demographics
        st.subheader("👤 Basic Information")
        age = st.number_input("Age", min_value=0, max_value=120, step=1, format="%d", value=None)

        st.divider()

        # 2. Kidney Health
        st.subheader("🏥 Kidney Health")
        on_dialysis = st.radio("Are you currently on dialysis?", ["Yes", "No"], index=None)
        
        gfr = None
        if on_dialysis == "No":
            gfr = st.number_input("What is your most recent GFR? (Found on BMP/CMP labs)", min_value=0.0, step=1.0)

        st.divider()

        # 3. Body Measurements (BMI)
        st.subheader("⚖️ Body Measurements")
        col1, col2 = st.columns(2)
        with col1:
            height_ft = st.selectbox("Height (Feet)", options=[4, 5, 6, 7], index=None)
        with col2:
            height_in = st.selectbox("Height (Inches)", options=list(range(0, 12)), index=None)
            
        weight = st.number_input("Weight (lbs)", min_value=0, step=1, value=None)

        # Live BMI Calc
        current_bmi = calculate_bmi(height_ft, height_in if height_in is not None else 0, weight)
        if current_bmi:
            color = "red" if current_bmi > 40 else ("orange" if current_bmi > 35 else "green")
            st.markdown(f"**Calculated BMI:** :{color}[{current_bmi}]")

        st.divider()

        # 4. Medical History
        st.subheader("🩺 Medical History")
        st.caption("Check any conditions that **currently** apply to you:")
        
        active_cancer = st.checkbox("Active Cancer / Malignancy")
        active_infection = st.checkbox("Active Infection (requiring antibiotics)")
        substance_abuse = st.checkbox("Active Substance Abuse (Alcohol or Drugs)")
        heart_lung_disease = st.checkbox("Severe Heart or Lung Disease (e.g., COPD requiring O2)")

        st.divider()

        # 5. Social Support
        st.subheader("👥 Social Support")
        social_support = st.radio(
            "Do you have a dedicated support person (friend or family member) who can assist you after surgery?",
            ["Yes", "No / Unsure"],
            index=None
        )

        st.divider()

        # Validate Button
        form_valid = True
        if age is None or height_ft is None or weight is None or on_dialysis is None or social_support is None:
            form_valid = False
        
        if on_dialysis == "No" and (gfr is None or gfr == 0):
            form_valid = False

        if st.button("Check Eligibility", type="primary", use_container_width=True, disabled=not form_valid):
            # Compile Data
            data = {
                'age': age,
                'on_dialysis': on_dialysis,
                'gfr': gfr,
                'active_cancer': active_cancer,
                'active_infection': active_infection,
                'substance_abuse': substance_abuse,
                'heart_lung_disease': heart_lung_disease,
                'social_support': social_support == "Yes"
            }
            
            status, messages = determine_eligibility(data, current_bmi)
            st.session_state.result = {'status': status, 'messages': messages}
            st.rerun()
            
        if not form_valid:
            st.caption("Please complete all required fields above to proceed.")

if __name__ == "__main__":
    main()
