import streamlit as st

st.set_page_config(page_title="Health Dashboard Test", layout="wide")

st.title("🏥 Damascus Health Directorate Dashboard - Test")
st.write("✅ If you can see this, the deployment is working!")

st.markdown("---")
st.markdown("### 🚀 Ready to launch the full dashboard!")
st.markdown("**Main Dashboard File:** `demo_manager_dashboard.py`")

if st.button("🏥 Launch Full Dashboard"):
    st.balloons()
    st.success("✅ Deployment successful! Now switch to demo_manager_dashboard.py") 