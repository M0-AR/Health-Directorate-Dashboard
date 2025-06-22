import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import numpy as np

# Page configuration
st.set_page_config(
    page_title="لوحة تحكم مديرية صحة دمشق - Damascus Health Directorate Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Arabic RTL Support
st.markdown("""
<style>
    .main .block-container {
        direction: rtl;
        text-align: right;
    }
    .stSelectbox label, .stMultiSelect label {
        direction: rtl;
        text-align: right;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .department-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .department-header {
        background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .project-button {
        width: 100%;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .project-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    h1, h2, h3 {
        direction: rtl;
        text-align: right;
    }
    .stDataFrame {
        direction: rtl;
    }
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b, #ffa726);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .alert-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* Alert button styling */
    div[data-testid="stButton"] > button {
        width: 100%;
        background: linear-gradient(135deg, #6c5ce7, #a29bfe) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-weight: bold !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #5f4fcf, #8b7eff) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# Generate realistic Syrian mobile numbers (employee IDs)
def generate_syrian_mobile():
    """Generate realistic Syrian mobile numbers as employee IDs"""
    prefixes = ['0944', '0945', '0946', '0947', '0948', '0949',  # MTN
                '0954', '0955', '0956', '0957', '0958', '0959',  # Syriatel
                '0962', '0963', '0964', '0965', '0966', '0967']  # Other networks
    
    prefix = random.choice(prefixes)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return prefix + suffix

# Create comprehensive demo data for Damascus Health Directorate
@st.cache_data
def load_demo_data():
    """Load realistic demo data for Damascus Health Directorate"""
    
    # Real facilities in Damascus Health Directorate
    facilities = [
        "مستشفى الأسد الجامعي",
        "مستشفى المواساة الجامعي", 
        "مستشفى الأطفال الجامعي",
        "مستشفى دمشق (ابن النفيس)",
        "مستشفى الولادة الجامعي",
        "مستشفى العيون الجامعي",
        "مستشفى الأورام",
        "مستشفى الباسل للقلب",
        "مستشفى الشهيد يوسف العظمة",
        "مستشفى الهلال الأحمر",
        "مركز الشام الصحي",
        "مركز دوما الصحي",
        "مركز جرمانا الصحي",
        "مركز الميدان الصحي",
        "مركز القابون الصحي",
        "مركز صحي باب توما",
        "مركز صحي القصاع",
        "مركز صحي الزاهرة",
        "إدارة المديرية الرئيسية",
        "قسم الطوارئ المركزي",
        "مختبر الصحة العامة",
        "مركز مكافحة الأمراض"
    ]
    
    # Real Syrian names
    employee_names = [
        "د. محمد أحمد السعيد", "د. فاطمة علي حمود", "د. خالد محمود شاهين",
        "د. نور الدين عبد الله", "د. رنا صالح المصري", "د. عمر حسن الخوري",
        "د. ليلى إبراهيم نجار", "د. سامر محمد عثمان", "د. هند فاروق زيدان",
        "د. أحمد يوسف الحلبي", "د. مريم عبد الرحمن", "د. وليد محمد الأسود",
        "أ. سعاد أحمد مرعي", "أ. حسام الدين طالب", "أ. نادية سليم حداد",
        "ممرضة زينب علي", "ممرض محمد عماد", "ممرضة رغد حسن",
        "فني أيمن الشامي", "فني سوسن الدمشقي", "إداري عدنان المقداد",
        "إدارية رولا الخطيب", "محاسب غسان النابلسي", "أمن وليد الأحمد",
        "عامل نظافة أبو أحمد", "سائق محمود الحوراني", "مشرف طارق العمري",
        "د. باسل الشعار", "د. رامي الحكيم", "د. سلمى الترك",
        "د. عماد البيطار", "د. منى الصباغ", "د. جهاد الأتاسي",
        "أ. ياسمين العلي", "أ. معين الدندشي", "ممرضة أمل حيدر",
        "فني كمال السوري", "إداري نبيل الشيخ", "محاسبة رنا الحموي",
        "د. طلال المحمد", "د. نايا العبد الله", "ممرض سامي الحسن"
    ]
    
    # Departments
    departments = [
        "الطوارئ", "الجراحة العامة", "الباطنة", "الأطفال", "النسائية والتوليد",
        "العظام", "القلبية", "العصبية", "الجلدية", "العيون", "الأنف والأذن والحنجرة",
        "التخدير", "الأشعة", "المختبر", "الصيدلة", "التمريض", "الإدارة",
        "المحاسبة", "الأمن", "النظافة", "الصيانة", "السائقين", "الاستقبال"
    ]
    
    # Job titles
    job_titles = [
        "طبيب أخصائي", "طبيب مقيم", "طبيب عام", "رئيس قسم", "نائب رئيس قسم",
        "ممرض أول", "ممرض", "فني مختبر", "فني أشعة", "صيدلاني",
        "إداري", "محاسب", "مدير", "مشرف", "عامل نظافة", "سائق", "أمن"
    ]
    
    # Work locations
    work_locations = ["المكتب", "العيادة", "العمل الميداني", "عمل من المنزل", "مناوبة"]
    
    # Current projects and tasks
    current_projects = [
        "مشروع تطوير قسم الطوارئ", "تحديث نظام المختبرات", "تدريب الكادر الطبي",
        "مشروع التطعيم الشامل", "تطوير العيادات الخارجية", "نظام إدارة المرضى الإلكتروني",
        "مشروع صحة المجتمع", "تحديث أجهزة الأشعة", "برنامج الجودة الطبية",
        "مشروع الطب الوقائي", "تطوير قسم العمليات", "نظام الصيدلية الإلكتروني",
        "مشروع التأهيل الطبي", "تحديث قسم القلبية", "برنامج التثقيف الصحي",
        "مشروع رعاية الأمومة", "تطوير خدمات الأطفال", "نظام المواعيد الإلكتروني"
    ]
    
    project_statuses = [
        "بدء المشروع", "التخطيط", "قيد التنفيذ", "مرحلة التجريب", 
        "المراجعة النهائية", "قارب على الانتهاء", "متوقف مؤقتاً"
    ]
    
    current_tasks = [
        "إعداد التقارير الطبية", "فحص المرضى الجدد", "متابعة العمليات الجراحية",
        "تحديث قاعدة البيانات", "التدريب على النظام الجديد", "مراجعة البروتوكولات",
        "إجراء الفحوصات المخبرية", "صيانة الأجهزة الطبية", "تنظيم المخزون الطبي",
        "إعداد خطة العمل الشهرية", "متابعة المرضى المنومين", "تحضير العمليات",
        "مراجعة ملفات المرضى", "تطوير الإجراءات", "التنسيق مع الأقسام الأخرى"
    ]

    # Generate employee data
    employees_data = []
    for i in range(200):  # 200 employees
        emp_id = generate_syrian_mobile()
        name = random.choice(employee_names)
        facility = random.choice(facilities)
        department = random.choice(departments)
        job_title = random.choice(job_titles)
        current_project = random.choice(current_projects)
        project_status = random.choice(project_statuses)
        current_task = random.choice(current_tasks)
        task_progress = random.randint(10, 95)
        
        employees_data.append({
            'معرف الموظف': emp_id,
            'الاسم': name,
            'المنشأة': facility,
            'القسم': department,
            'المسمى الوظيفي': job_title,
            'المشروع الحالي': current_project,
            'حالة المشروع': project_status,
            'المهمة الحالية': current_task,
            'تقدم المهمة': f"{task_progress}%"
        })
    
    # Generate daily reports data
    daily_reports = []
    for _ in range(150):  # 150 daily reports
        emp = random.choice(employees_data)
        date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        daily_reports.append({
            'التاريخ': date.strftime('%Y-%m-%d'),
            'معرف الموظف': emp['معرف الموظف'],
            'الاسم': emp['الاسم'],
            'المنشأة': emp['المنشأة'],
            'القسم': emp['القسم'],
            'المشروع الحالي': emp['المشروع الحالي'],
            'المهمة الحالية': emp['المهمة الحالية'],
            'تقدم المهمة': emp['تقدم المهمة'],
            'موقع العمل': random.choice(work_locations),
            'وقت بدء العمل': f"{random.randint(7,9)}:{random.randint(0,59):02d}",
            'المهام المخطط لها': random.choice([
                "فحص المرضى الجدد", "متابعة المرضى المنومين", "العمليات الجراحية",
                "التقارير الطبية", "الاجتماعات الإدارية", "التدريب المستمر",
                "فحص الأشعة", "تحليل النتائج", "إدارة الصيدلية", "تنظيف الأقسام"
            ]),
            'حالة مهام الأمس': random.choice(["مكتملة", "مكتملة جزئياً", "متأخرة", "ملغاة"]),
            'التحديات': random.choice([
                "نقص في المعدات", "ازدحام المرضى", "نقص الكادر", "مشاكل تقنية",
                "لا توجد تحديات", "تأخير في الفحوصات", "مشاكل في التنسيق"
            ]),
            'نسبة الإنجاز': random.randint(60, 100),
            'ساعات العمل': random.randint(6, 12)
        })
    
    # Generate weekly reports
    weekly_reports = []
    for _ in range(80):  # 80 weekly reports
        emp = random.choice(employees_data)
        week_start = datetime.now() - timedelta(weeks=random.randint(0, 8))
        
        weekly_reports.append({
            'الأسبوع': week_start.strftime('%Y-%m-%d'),
            'معرف الموظف': emp['معرف الموظف'],
            'الاسم': emp['الاسم'],
            'المنشأة': emp['المنشأة'],
            'المشاريع النشطة': random.randint(1, 5),
            'المهام المكتملة': random.randint(15, 35),
            'المهام قيد التنفيذ': random.randint(3, 10),
            'المهام المتأخرة': random.randint(0, 5),
            'تقييم الأداء': random.choice(["ممتاز", "جيد جداً", "جيد", "مقبول"]),
            'معدل الحضور': f"{random.randint(85, 100)}%"
        })
    
    return {
        'employees': pd.DataFrame(employees_data),
        'daily_reports': pd.DataFrame(daily_reports),
        'weekly_reports': pd.DataFrame(weekly_reports),
        'facilities': facilities
    }

# Load data
data = load_demo_data()
employees_df = data['employees']
daily_df = data['daily_reports']
weekly_df = data['weekly_reports']
facilities = data['facilities']

# Header
st.markdown("""
<div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem; color: white;'>
    <h1>🏥 لوحة تحكم مديرية صحة دمشق</h1>
    <h2>Damascus Health Directorate Dashboard</h2>
    <h3>المدير: الدكتور أكرم معتوق</h3>
    <h4>Director: Dr. Akram Matouk</h4>
    <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.3);'>
        <p>🤖 مطور النظام: المهندس محمد الأشمر - خبير ذكاء اصطناعي</p>
        <p>System Developer: Eng. Mohammad Al-Ashmar - AI Expert</p>
    </div>
    <p>📅 {}</p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)

# Sidebar filters
st.sidebar.markdown("## 🔍 المرشحات / Filters")

# Facility filter
selected_facilities = st.sidebar.multiselect(
    "اختر المنشآت / Select Facilities:",
    facilities,
    default=facilities[:5]
)

# Date range filter
date_range = st.sidebar.date_input(
    "نطاق التاريخ / Date Range:",
    value=[datetime.now() - timedelta(days=7), datetime.now()],
    max_value=datetime.now()
)

# Department filter
departments = employees_df['القسم'].unique()
selected_departments = st.sidebar.multiselect(
    "اختر الأقسام / Select Departments:",
    departments,
    default=list(departments)[:5]
)

# Filter data based on selections
if selected_facilities:
    filtered_employees = employees_df[employees_df['المنشأة'].isin(selected_facilities)]
    filtered_daily = daily_df[daily_df['المنشأة'].isin(selected_facilities)]
    filtered_weekly = weekly_df[weekly_df['المنشأة'].isin(selected_facilities)]
else:
    filtered_employees = employees_df
    filtered_daily = daily_df
    filtered_weekly = weekly_df

if selected_departments:
    filtered_employees = filtered_employees[filtered_employees['القسم'].isin(selected_departments)]
    filtered_daily = filtered_daily[filtered_daily['القسم'].isin(selected_departments)]

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='metric-card'>
        <h3>👥 إجمالي الموظفين</h3>
        <h2>{}</h2>
        <p>Total Employees</p>
    </div>
    """.format(len(filtered_employees)), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card'>
        <h3>🏥 المنشآت النشطة</h3>
        <h2>{}</h2>
        <p>Active Facilities</p>
    </div>
    """.format(len(selected_facilities) if selected_facilities else len(facilities)), unsafe_allow_html=True)

with col3:
    avg_completion = filtered_daily['نسبة الإنجاز'].mean() if not filtered_daily.empty else 0
    st.markdown("""
    <div class='metric-card'>
        <h3>📊 متوسط الإنجاز</h3>
        <h2>{:.1f}%</h2>
        <p>Average Completion</p>
    </div>
    """.format(avg_completion), unsafe_allow_html=True)

with col4:
    daily_reports_count = len(filtered_daily)
    st.markdown("""
    <div class='metric-card'>
        <h3>📋 التقارير اليومية</h3>
        <h2>{}</h2>
        <p>Daily Reports</p>
    </div>
    """.format(daily_reports_count), unsafe_allow_html=True)

# Charts section
st.markdown("---")
st.markdown("## 📊 التحليلات / Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏥 توزيع الموظفين حسب المنشأة")
    if not filtered_employees.empty:
        facility_counts = filtered_employees['المنشأة'].value_counts()
        fig = px.pie(
            values=facility_counts.values,
            names=facility_counts.index,
            title="Employee Distribution by Facility"
        )
        fig.update_layout(font=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📈 معدل الإنجاز الأسبوعي")
    if not filtered_daily.empty:
        daily_completion = filtered_daily.groupby('التاريخ')['نسبة الإنجاز'].mean().reset_index()
        fig = px.line(
            daily_completion,
            x='التاريخ',
            y='نسبة الإنجاز',
            title="Weekly Completion Rate",
            markers=True
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Completion %")
        st.plotly_chart(fig, use_container_width=True)

# Current Projects Status
st.markdown("### 📋 حالة المشاريع الحالية / Current Projects Status")
col1, col2 = st.columns(2)

with col1:
    if not filtered_employees.empty:
        project_counts = filtered_employees['حالة المشروع'].value_counts()
        fig = px.pie(
            values=project_counts.values,
            names=project_counts.index,
            title="Project Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(font=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if not filtered_employees.empty:
        # Convert progress to numeric for analysis
        filtered_employees['تقدم المهمة_رقم'] = filtered_employees['تقدم المهمة'].str.replace('%', '').astype(int)
        avg_progress_by_project = filtered_employees.groupby('المشروع الحالي')['تقدم المهمة_رقم'].mean().sort_values(ascending=False).head(8)
        
        st.markdown("**💡 انقر على أي مشروع في الرسم البياني لعرض التفاصيل**")
        
        # Create clickable project buttons for chart
        # Get the default index for selectbox
        default_index = 0
        if 'selected_project' in st.session_state and st.session_state.selected_project:
            try:
                default_index = list(avg_progress_by_project.index).index(st.session_state.selected_project) + 1
            except ValueError:
                default_index = 0
        
        selected_chart_project = st.selectbox(
            "اختر مشروع من الرسم البياني:",
            ["اختر مشروع..."] + list(avg_progress_by_project.index),
            index=default_index,
            key="chart_project_selector"
        )
        
        if selected_chart_project != "اختر مشروع...":
            st.session_state.selected_project = selected_chart_project
        elif selected_chart_project == "اختر مشروع..." and 'selected_project' in st.session_state:
            # Reset if user selects the default option
            del st.session_state.selected_project
        
        fig = px.bar(
            x=avg_progress_by_project.values,
            y=avg_progress_by_project.index,
            orientation='h',
            title="Average Progress by Project",
            labels={'x': 'Average Progress %', 'y': 'Project'},
            color=avg_progress_by_project.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# Project Details Modal/Popup
if 'selected_project' in st.session_state and st.session_state.selected_project and st.session_state.selected_project != "اختر مشروع..." and st.session_state.selected_project is not None:
    st.markdown("---")
    
    # Close button at the top
    col_title, col_close = st.columns([4, 1])
    with col_title:
        st.markdown(f"## 📋 تفاصيل المشروع: {st.session_state.selected_project}")
        st.markdown("### Project Details")
    with col_close:
        if st.button("❌ إغلاق", key="close_project_top", help="إغلاق تفاصيل المشروع"):
            # Clear the project selection
            if 'selected_project' in st.session_state:
                del st.session_state.selected_project
            # Force rerun to refresh the page
            st.rerun()
    
    # Get project team data
    project_team = filtered_employees[filtered_employees['المشروع الحالي'] == st.session_state.selected_project].copy()
    
    if not project_team.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_team = len(project_team)
            avg_progress = project_team['تقدم المهمة_رقم'].mean()
            st.markdown(f"""
            <div class='metric-card'>
                <h4>👥 إجمالي الفريق</h4>
                <h2>{total_team}</h2>
                <p>Total Team Members</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h4>📊 متوسط التقدم</h4>
                <h2>{avg_progress:.1f}%</h2>
                <p>Average Progress</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            facilities_count = project_team['المنشأة'].nunique()
            st.markdown(f"""
            <div class='metric-card'>
                <h4>🏥 المنشآت المشاركة</h4>
                <h2>{facilities_count}</h2>
                <p>Participating Facilities</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Team members details with direct contact
        st.markdown("### 👥 أعضاء الفريق / Team Members")
        
        # Group by facility for better organization
        for facility in project_team['المنشأة'].unique():
            facility_team = project_team[project_team['المنشأة'] == facility]
            
            st.markdown(f"""
            <div class='department-header'>
                <h4>🏥 {facility} ({len(facility_team)} موظف)</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Display team members in expandable format
            for idx, member in facility_team.iterrows():
                progress_color = "#4CAF50" if int(member['تقدم المهمة'].replace('%', '')) >= 75 else "#FF9800" if int(member['تقدم المهمة'].replace('%', '')) >= 50 else "#F44336"
                
                with st.expander(f"📞 {member['الاسم']} - {member['معرف الموظف']} ({member['تقدم المهمة']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **📋 معلومات الموظف:**
                        - 📞 **رقم الهاتف:** {member['معرف الموظف']}
                        - 🏢 **القسم:** {member['القسم']}
                        - 💼 **المسمى الوظيفي:** {member['المسمى الوظيفي']}
                        - 🎯 **المهمة الحالية:** {member['المهمة الحالية']}
                        """)
                        
                        # Direct call button (simulated)
                        if st.button(f"📞 اتصال مباشر", key=f"call_{member['معرف الموظف']}", help=f"الاتصال بـ {member['الاسم']}"):
                            st.success(f"🔄 جاري الاتصال بـ {member['الاسم']} على الرقم {member['معرف الموظف']}")
                    
                    with col2:
                        st.markdown(f"""
                        **📊 حالة العمل:**
                        - 🏥 **المنشأة:** {member['المنشأة']}
                        - 📈 **تقدم المهمة:** {member['تقدم المهمة']}
                        - 🎯 **حالة المشروع:** {member['حالة المشروع']}
                        """)
                        
                        # Progress bar
                        progress_val = int(member['تقدم المهمة'].replace('%', ''))
                        st.progress(progress_val / 100)
                        
                        # Find facility manager (simulate with realistic data)
                        facility_managers = {
                            "مستشفى الأسد الجامعي": "د. محمد الأسود - 0944123456",
                            "مستشفى المواساة الجامعي": "د. فاطمة حمود - 0955234567", 
                            "مستشفى الأطفال الجامعي": "د. خالد شاهين - 0946345678",
                            "مستشفى دمشق (ابن النفيس)": "د. نور عبد الله - 0957456789",
                            "مستشفى الولادة الجامعي": "د. رنا المصري - 0944567890",
                            "مستشفى العيون الجامعي": "د. عمر الخوري - 0955678901",
                            "مستشفى الأورام": "د. ليلى نجار - 0946789012",
                            "مستشفى الباسل للقلب": "د. سامر عثمان - 0957890123",
                            "مستشفى الشهيد يوسف العظمة": "د. هند زيدان - 0944901234",
                            "مستشفى الهلال الأحمر": "د. أحمد الحلبي - 0955012345",
                            "مركز الشام الصحي": "د. مريم عبد الرحمن - 0946123456",
                            "مركز دوما الصحي": "د. وليد الأسود - 0957234567",
                            "مركز جرمانا الصحي": "أ. سعاد مرعي - 0944345678",
                            "مركز الميدان الصحي": "أ. حسام طالب - 0955456789",
                            "مركز القابون الصحي": "أ. نادية حداد - 0946567890",
                            "مركز صحي باب توما": "د. باسل الشعار - 0957678901",
                            "مركز صحي القصاع": "د. رامي الحكيم - 0944789012",
                            "مركز صحي الزاهرة": "د. سلمى الترك - 0955890123",
                            "إدارة المديرية الرئيسية": "د. أكرم معتوق - 0946901234",
                            "قسم الطوارئ المركزي": "د. عماد البيطار - 0957012345",
                            "مختبر الصحة العامة": "د. منى الصباغ - 0944123789",
                            "مركز مكافحة الأمراض": "د. جهاد الأتاسي - 0955234890"
                        }
                        
                        facility_manager = facility_managers.get(member['المنشأة'], "غير محدد")
                        manager_name = facility_manager.split(" - ")[0] if " - " in facility_manager else facility_manager
                        manager_phone = facility_manager.split(" - ")[1] if " - " in facility_manager else ""
                        
                        st.info(f"👨‍💼 مدير المنشأة: {manager_name}")
                        if manager_phone:
                            if st.button(f"📞 اتصال بالمدير", key=f"call_manager_{member['معرف الموظف']}", help=f"الاتصال بـ {manager_name}"):
                                st.success(f"🔄 جاري الاتصال بمدير المنشأة {manager_name} على الرقم {manager_phone}")
        
        # Project statistics
        st.markdown("### 📈 إحصائيات المشروع / Project Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Progress distribution
            progress_ranges = {
                "عالي (75-100%)": len(project_team[project_team['تقدم المهمة_رقم'] >= 75]),
                "متوسط (50-74%)": len(project_team[(project_team['تقدم المهمة_رقم'] >= 50) & (project_team['تقدم المهمة_رقم'] < 75)]),
                "منخفض (أقل من 50%)": len(project_team[project_team['تقدم المهمة_رقم'] < 50])
            }
            
            fig = px.pie(
                values=list(progress_ranges.values()),
                names=list(progress_ranges.keys()),
                title="توزيع مستوى التقدم / Progress Distribution",
                color_discrete_sequence=['#4CAF50', '#FF9800', '#F44336']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Department distribution
            dept_counts = project_team['القسم'].value_counts()
            fig = px.bar(
                x=dept_counts.values,
                y=dept_counts.index,
                orientation='h',
                title="توزيع الأقسام / Department Distribution",
                labels={'x': 'عدد الموظفين', 'y': 'القسم'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Close button
        if st.button("❌ إغلاق تفاصيل المشروع / Close Project Details", key="close_project"):
            # Clear the project selection
            if 'selected_project' in st.session_state:
                del st.session_state.selected_project
            # Force rerun to refresh the page
            st.rerun()
    
    st.markdown("---")

# Department analysis
st.markdown("### 🏢 تحليل الأقسام / Department Analysis")
col1, col2 = st.columns(2)

with col1:
    if not filtered_employees.empty:
        dept_counts = filtered_employees['القسم'].value_counts().head(10)
        fig = px.bar(
            x=dept_counts.values,
            y=dept_counts.index,
            orientation='h',
            title="Top 10 Departments by Employee Count",
            labels={'x': 'Number of Employees', 'y': 'Department'}
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if not filtered_daily.empty:
        dept_performance = filtered_daily.groupby('القسم')['نسبة الإنجاز'].mean().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=dept_performance.values,
            y=dept_performance.index,
            orientation='h',
            title="Top 10 Departments by Performance",
            labels={'x': 'Average Completion %', 'y': 'Department'}
        )
        st.plotly_chart(fig, use_container_width=True)

# Alerts and notifications
st.markdown("---")
st.markdown("## ⚠️ التنبيهات والإشعارات / Alerts & Notifications")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚨 تحديات المعدات", key="equipment_alert", help="انقر لعرض تفاصيل تحديات المعدات"):
        st.session_state.selected_alert = "equipment"
    st.markdown("""
    <div class='alert-card'>
        <h4>12 تقرير عن نقص المعدات</h4>
        <p>Equipment Shortage Reports</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("⏰ التأخيرات", key="delay_alert", help="انقر لعرض تفاصيل المهام المتأخرة"):
        st.session_state.selected_alert = "delays"
    st.markdown("""
    <div class='alert-card'>
        <h4>8 مهام متأخرة تحتاج متابعة</h4>
        <p>Delayed Tasks Need Follow-up</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("👥 نقص الكادر", key="staffing_alert", help="انقر لعرض تفاصيل نقص الكادر"):
        st.session_state.selected_alert = "staffing"
    st.markdown("""
    <div class='alert-card'>
        <h4>5 أقسام تحتاج تعزيز</h4>
        <p>Departments Need Staffing</p>
    </div>
    """, unsafe_allow_html=True)

# Alert Details Modal/Popup
if 'selected_alert' in st.session_state and st.session_state.selected_alert:
    st.markdown("---")
    
    if st.session_state.selected_alert == "equipment":
        st.markdown("## 🚨 تفاصيل تحديات المعدات / Equipment Shortage Details")
        
        # Generate realistic equipment shortage data
        equipment_issues = [
            {"التاريخ": "2025-01-20", "المنشأة": "مستشفى الأسد الجامعي", "القسم": "الطوارئ", 
             "المعدة المطلوبة": "جهاز تنفس صناعي", "الموظف المبلغ": "د. محمد أحمد السعيد", 
             "رقم الهاتف": "0944123456", "الأولوية": "عاجل", "المدير": "د. محمد الأسود - 0944123456"},
            {"التاريخ": "2025-01-19", "المنشأة": "مستشفى الأطفال الجامعي", "القسم": "العناية المركزة", 
             "المعدة المطلوبة": "مضخة حقن", "الموظف المبلغ": "د. فاطمة علي حمود", 
             "رقم الهاتف": "0955234567", "الأولوية": "عاجل", "المدير": "د. خالد شاهين - 0946345678"},
            {"التاريخ": "2025-01-18", "المنشأة": "مركز الشام الصحي", "القسم": "المختبر", 
             "المعدة المطلوبة": "جهاز تحليل الدم", "الموظف المبلغ": "د. خالد محمود شاهين", 
             "رقم الهاتف": "0946345678", "الأولوية": "متوسط", "المدير": "د. مريم عبد الرحمن - 0946123456"},
            {"التاريخ": "2025-01-17", "المنشأة": "مستشفى الولادة الجامعي", "القسم": "العمليات", 
             "المعدة المطلوبة": "منظار جراحي", "الموظف المبلغ": "د. نور الدين عبد الله", 
             "رقم الهاتف": "0957456789", "الأولوية": "عاجل", "المدير": "د. رنا المصري - 0944567890"}
        ]
        
        for i, issue in enumerate(equipment_issues[:4], 1):
            priority_color = "#ff6b6b" if issue["الأولوية"] == "عاجل" else "#ffa726"
            with st.expander(f"🚨 {issue['المعدة المطلوبة']} - {issue['المنشأة']} ({issue['الأولوية']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **📋 تفاصيل التقرير:**
                    - 📅 **التاريخ:** {issue['التاريخ']}
                    - 🏥 **المنشأة:** {issue['المنشأة']}
                    - 🏢 **القسم:** {issue['القسم']}
                    - 🔧 **المعدة المطلوبة:** {issue['المعدة المطلوبة']}
                    - ⚠️ **الأولوية:** {issue['الأولوية']}
                    """)
                    
                with col2:
                    st.markdown(f"""
                    **👥 معلومات الاتصال:**
                    - 👨‍⚕️ **الموظف المبلغ:** {issue['الموظف المبلغ']}
                    - 📞 **رقم الهاتف:** {issue['رقم الهاتف']}
                    - 👨‍💼 **مدير المنشأة:** {issue['المدير'].split(' - ')[0]}
                    - 📱 **هاتف المدير:** {issue['المدير'].split(' - ')[1]}
                    """)
                
                col3, col4, col5 = st.columns(3)
                with col3:
                    if st.button(f"📞 اتصال بالموظف", key=f"call_emp_{i}", help=f"الاتصال بـ {issue['الموظف المبلغ']}"):
                        st.success(f"🔄 جاري الاتصال بـ {issue['الموظف المبلغ']} على الرقم {issue['رقم الهاتف']}")
                
                with col4:
                    if st.button(f"📞 اتصال بالمدير", key=f"call_mgr_{i}", help=f"الاتصال بمدير المنشأة"):
                        manager_phone = issue['المدير'].split(' - ')[1]
                        manager_name = issue['المدير'].split(' - ')[0]
                        st.success(f"🔄 جاري الاتصال بـ {manager_name} على الرقم {manager_phone}")
                
                with col5:
                    if st.button(f"✅ تم الحل", key=f"resolve_{i}", help="تسجيل حل المشكلة"):
                        st.success(f"✅ تم تسجيل حل مشكلة {issue['المعدة المطلوبة']}")
    
    elif st.session_state.selected_alert == "delays":
        st.markdown("## ⏰ تفاصيل المهام المتأخرة / Delayed Tasks Details")
        
        # Generate realistic delayed tasks data
        delayed_tasks = [
            {"التاريخ": "2025-01-15", "المنشأة": "مستشفى المواساة الجامعي", "القسم": "الأشعة", 
             "المهمة": "تحديث نظام الأشعة", "الموظف": "د. رنا صالح المصري", 
             "رقم الهاتف": "0955234567", "التأخير": "5 أيام", "المدير": "د. فاطمة حمود - 0955234567"},
            {"التاريخ": "2025-01-12", "المنشأة": "مركز دوما الصحي", "القسم": "الصيدلة", 
             "المهمة": "جرد الأدوية الشهري", "الموظف": "د. عمر حسن الخوري", 
             "رقم الهاتف": "0946345678", "التأخير": "8 أيام", "المدير": "د. وليد الأسود - 0957234567"},
            {"التاريخ": "2025-01-10", "المنشأة": "مستشفى العيون الجامعي", "القسم": "العمليات", 
             "المهمة": "تقرير العمليات الشهري", "الموظف": "د. ليلى إبراهيم نجار", 
             "رقم الهاتف": "0957456789", "التأخير": "10 أيام", "المدير": "د. عمر الخوري - 0955678901"}
        ]
        
        for i, task in enumerate(delayed_tasks[:3], 1):
            delay_days = int(task["التأخير"].split()[0])
            delay_color = "#ff6b6b" if delay_days > 7 else "#ffa726"
            
            with st.expander(f"⏰ {task['المهمة']} - {task['المنشأة']} (متأخر {task['التأخير']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **📋 تفاصيل المهمة:**
                    - 📅 **تاريخ الاستحقاق:** {task['التاريخ']}
                    - 🏥 **المنشأة:** {task['المنشأة']}
                    - 🏢 **القسم:** {task['القسم']}
                    - 📝 **المهمة:** {task['المهمة']}
                    - ⏰ **مدة التأخير:** {task['التأخير']}
                    """)
                    
                with col2:
                    st.markdown(f"""
                    **👥 معلومات الاتصال:**
                    - 👨‍⚕️ **الموظف المسؤول:** {task['الموظف']}
                    - 📞 **رقم الهاتف:** {task['رقم الهاتف']}
                    - 👨‍💼 **مدير المنشأة:** {task['المدير'].split(' - ')[0]}
                    - 📱 **هاتف المدير:** {task['المدير'].split(' - ')[1]}
                    """)
                
                col3, col4, col5 = st.columns(3)
                with col3:
                    if st.button(f"📞 اتصال بالموظف", key=f"call_delay_emp_{i}"):
                        st.success(f"🔄 جاري الاتصال بـ {task['الموظف']} على الرقم {task['رقم الهاتف']}")
                
                with col4:
                    if st.button(f"📞 اتصال بالمدير", key=f"call_delay_mgr_{i}"):
                        manager_phone = task['المدير'].split(' - ')[1]
                        manager_name = task['المدير'].split(' - ')[0]
                        st.success(f"🔄 جاري الاتصال بـ {manager_name} على الرقم {manager_phone}")
                
                with col5:
                    if st.button(f"✅ تم الإنجاز", key=f"complete_{i}"):
                        st.success(f"✅ تم تسجيل إنجاز المهمة: {task['المهمة']}")
    
    elif st.session_state.selected_alert == "staffing":
        st.markdown("## 👥 تفاصيل نقص الكادر / Staffing Shortage Details")
        
        # Generate realistic staffing shortage data
        staffing_needs = [
            {"المنشأة": "مستشفى الأورام", "القسم": "التمريض", "النقص": "3 ممرضين", 
             "التخصص المطلوب": "تمريض الأورام", "المدير": "د. ليلى نجار - 0946789012", "الأولوية": "عاجل"},
            {"المنشأة": "مركز القابون الصحي", "القسم": "المختبر", "النقص": "فني مختبر واحد", 
             "التخصص المطلوب": "تحاليل طبية", "المدير": "أ. نادية حداد - 0946567890", "الأولوية": "متوسط"},
            {"المنشأة": "مستشفى الباسل للقلب", "القسم": "القلبية", "النقص": "طبيب أخصائي", 
             "التخصص المطلوب": "جراحة القلب", "المدير": "د. سامر عثمان - 0957890123", "الأولوية": "عاجل"},
            {"المنشأة": "مركز جرمانا الصحي", "القسم": "الأشعة", "النقص": "فني أشعة", 
             "التخصص المطلوب": "تصوير طبي", "المدير": "أ. سعاد مرعي - 0944345678", "الأولوية": "متوسط"}
        ]
        
        for i, need in enumerate(staffing_needs[:4], 1):
            priority_color = "#ff6b6b" if need["الأولوية"] == "عاجل" else "#ffa726"
            
            with st.expander(f"👥 {need['النقص']} - {need['المنشأة']} ({need['الأولوية']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **📋 تفاصيل النقص:**
                    - 🏥 **المنشأة:** {need['المنشأة']}
                    - 🏢 **القسم:** {need['القسم']}
                    - 👥 **النقص المطلوب:** {need['النقص']}
                    - 🎓 **التخصص:** {need['التخصص المطلوب']}
                    - ⚠️ **الأولوية:** {need['الأولوية']}
                    """)
                    
                with col2:
                    st.markdown(f"""
                    **👥 معلومات الاتصال:**
                    - 👨‍💼 **مدير المنشأة:** {need['المدير'].split(' - ')[0]}
                    - 📱 **هاتف المدير:** {need['المدير'].split(' - ')[1]}
                    """)
                    
                    st.markdown(f"""
                    **📊 إجراءات مقترحة:**
                    - 📢 نشر إعلان توظيف
                    - 🔄 نقل موظف من منشأة أخرى
                    - 📞 التواصل مع الجامعات
                    """)
                
                col3, col4, col5 = st.columns(3)
                with col3:
                    if st.button(f"📞 اتصال بالمدير", key=f"call_staff_mgr_{i}"):
                        manager_phone = need['المدير'].split(' - ')[1]
                        manager_name = need['المدير'].split(' - ')[0]
                        st.success(f"🔄 جاري الاتصال بـ {manager_name} على الرقم {manager_phone}")
                
                with col4:
                    if st.button(f"📢 نشر إعلان", key=f"post_job_{i}"):
                        st.success(f"📢 تم نشر إعلان توظيف لـ {need['النقص']} في {need['القسم']}")
                
                with col5:
                    if st.button(f"✅ تم التوظيف", key=f"hired_{i}"):
                        st.success(f"✅ تم تسجيل التوظيف الجديد في {need['القسم']}")
    
    # Close button for alerts
    if st.button("❌ إغلاق تفاصيل التنبيه / Close Alert Details", key="close_alert"):
        del st.session_state.selected_alert
        st.rerun()
    
    st.markdown("---")

# Recent reports table
st.markdown("---")
st.markdown("## 📋 التقارير الحديثة / Recent Reports")

if not filtered_daily.empty:
    recent_reports = filtered_daily.sort_values('التاريخ', ascending=False).head(20)
    st.dataframe(
        recent_reports[['التاريخ', 'الاسم', 'المنشأة', 'القسم', 'المشروع الحالي', 'المهمة الحالية', 'تقدم المهمة', 'موقع العمل', 'نسبة الإنجاز', 'التحديات']],
        use_container_width=True
    )
else:
    st.info("لا توجد تقارير للفترة المحددة / No reports for selected period")

# Employee Projects & Tasks
st.markdown("---")
st.markdown("## 🎯 المشاريع والمهام الحالية / Current Projects & Tasks")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🚀 أهم المشاريع النشطة / Top Active Projects")
    if not filtered_employees.empty:
        top_projects = filtered_employees['المشروع الحالي'].value_counts().head(10)
        
        # Create project selection buttons
        for i, (project, count) in enumerate(top_projects.items(), 1):
            avg_progress = filtered_employees[filtered_employees['المشروع الحالي'] == project]['تقدم المهمة_رقم'].mean()
            
            # Create a unique key for each button
            button_key = f"project_btn_{i}_{project.replace(' ', '_')}"
            
            if st.button(f"📋 {project}", key=button_key, help="انقر لعرض تفاصيل المشروع"):
                st.session_state.selected_project = project
                st.rerun()
            
            # Display project summary
            st.markdown(f"""
            <div class='department-card'>
                <p>👥 عدد الموظفين: {count} | 📊 متوسط التقدم: {avg_progress:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("#### ⚠️ المشاريع التي تحتاج متابعة / Projects Needing Attention")
    if not filtered_employees.empty:
        low_progress_projects = filtered_employees.groupby('المشروع الحالي')['تقدم المهمة_رقم'].mean().sort_values().head(5)
        
        for i, (project, avg_progress) in enumerate(low_progress_projects.items(), 1):
            employee_count = len(filtered_employees[filtered_employees['المشروع الحالي'] == project])
            status_color = "#ff6b6b" if avg_progress < 50 else "#ffa726"
            
            # Create button for attention projects
            attention_button_key = f"attention_btn_{i}_{project.replace(' ', '_')}"
            
            if st.button(f"⚠️ {project}", key=attention_button_key, help="انقر لعرض تفاصيل المشروع"):
                st.session_state.selected_project = project
                st.rerun()
            
            st.markdown(f"""
            <div style='background: {status_color}; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; color: white;'>
                <p>👥 {employee_count} موظف | 📊 {avg_progress:.1f}% مكتمل</p>
            </div>
            """, unsafe_allow_html=True)

# Project Details Modal/Popup - Show after current projects section
if 'selected_project' in st.session_state and st.session_state.selected_project and st.session_state.selected_project != "اختر مشروع..." and st.session_state.selected_project is not None:
    st.markdown("---")
    
    # Close button at the top
    col_title, col_close = st.columns([4, 1])
    with col_title:
        st.markdown(f"## 📋 تفاصيل المشروع: {st.session_state.selected_project}")
        st.markdown("### Project Details")
    with col_close:
        if st.button("❌ إغلاق", key="close_project_main", help="إغلاق تفاصيل المشروع"):
            # Clear the project selection
            if 'selected_project' in st.session_state:
                del st.session_state.selected_project
            # Force rerun to refresh the page
            st.rerun()
    
    # Get project team members
    project_team = filtered_employees[filtered_employees['المشروع الحالي'] == st.session_state.selected_project]
    
    if not project_team.empty:
        # Project overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_members = len(project_team)
            st.markdown(f"""
            <div class='metric-card'>
                <h4>👥 أعضاء الفريق</h4>
                <h3>{total_members}</h3>
                <p>Team Members</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_progress = project_team['تقدم المهمة_رقم'].mean()
            st.markdown(f"""
            <div class='metric-card'>
                <h4>📊 متوسط التقدم</h4>
                <h3>{avg_progress:.1f}%</h3>
                <p>Average Progress</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            facilities_count = project_team['المنشأة'].nunique()
            st.markdown(f"""
            <div class='metric-card'>
                <h4>🏥 المنشآت المشاركة</h4>
                <h3>{facilities_count}</h3>
                <p>Participating Facilities</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            departments_count = project_team['القسم'].nunique()
            st.markdown(f"""
            <div class='metric-card'>
                <h4>🏢 الأقسام المشاركة</h4>
                <h3>{departments_count}</h3>
                <p>Participating Departments</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Team members by facility
        st.markdown("### 👥 أعضاء الفريق حسب المنشأة / Team Members by Facility")
        
        for facility in project_team['المنشأة'].unique():
            facility_team = project_team[project_team['المنشأة'] == facility]
            
            with st.expander(f"🏥 {facility} ({len(facility_team)} موظف)"):
                for idx, member in facility_team.iterrows():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"""
                        **👤 {member['الاسم']}**  
                        📱 {member['معرف الموظف']}  
                        🏢 {member['القسم']}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **📋 المهمة الحالية:**  
                        {member['المهمة الحالية']}  
                        **📊 التقدم:** {member['تقدم المهمة']}
                        """)
                    
                    with col3:
                        # Get work location from daily reports if available, otherwise use default
                        work_location = "المكتب"  # Default work location
                        if member['معرف الموظف'] in daily_df['معرف الموظف'].values:
                            latest_report = daily_df[daily_df['معرف الموظف'] == member['معرف الموظف']].iloc[-1]
                            work_location = latest_report.get('موقع العمل', 'المكتب')
                        
                        st.markdown(f"""
                        **📍 موقع العمل:**  
                        {work_location}  
                        **🔄 حالة المشروع:** {member['حالة المشروع']}
                        """)
                    
                    with col4:
                        if st.button(f"📞 اتصال", key=f"call_{member['معرف الموظف']}_project"):
                            st.success(f"🔄 جاري الاتصال بـ {member['الاسم']} على الرقم {member['معرف الموظف']}")
                        
                        # Get challenges from daily reports if available
                        challenges = None
                        if member['معرف الموظف'] in daily_df['معرف الموظف'].values:
                            latest_report = daily_df[daily_df['معرف الموظف'] == member['معرف الموظف']].iloc[-1]
                            challenges = latest_report.get('التحديات', None)
                        
                        if challenges and challenges != 'لا توجد تحديات':
                            st.warning(f"⚠️ تحدي: {challenges}")
        
        # Project statistics
        st.markdown("### 📊 إحصائيات المشروع / Project Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Progress distribution
            progress_ranges = {
                '0-25%': len(project_team[project_team['تقدم المهمة_رقم'] <= 25]),
                '26-50%': len(project_team[(project_team['تقدم المهمة_رقم'] > 25) & (project_team['تقدم المهمة_رقم'] <= 50)]),
                '51-75%': len(project_team[(project_team['تقدم المهمة_رقم'] > 50) & (project_team['تقدم المهمة_رقم'] <= 75)]),
                '76-100%': len(project_team[project_team['تقدم المهمة_رقم'] > 75])
            }
            
            fig = px.pie(
                values=list(progress_ranges.values()),
                names=list(progress_ranges.keys()),
                title="توزيع نسب التقدم / Progress Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Department participation
            dept_participation = project_team['القسم'].value_counts()
            
            fig = px.bar(
                x=dept_participation.values,
                y=dept_participation.index,
                orientation='h',
                title="مشاركة الأقسام / Department Participation"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Close button at bottom
        if st.button("❌ إغلاق تفاصيل المشروع / Close Project Details", key="close_project_bottom"):
            # Clear the project selection
            if 'selected_project' in st.session_state:
                del st.session_state.selected_project
            # Force rerun to refresh the page
            st.rerun()

# Employee directory
st.markdown("---")
st.markdown("## 👥 دليل الموظفين والمشاريع / Employee & Project Directory")

if not filtered_employees.empty:
    # Advanced search functionality
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 البحث عن موظف / Search Employee:", placeholder="الاسم أو رقم الهاتف")
    
    with col2:
        project_search = st.selectbox("🎯 البحث بالمشروع / Search by Project:", 
                                    ["جميع المشاريع"] + list(filtered_employees['المشروع الحالي'].unique()))
    
    with col3:
        status_search = st.selectbox("📊 البحث بحالة المشروع / Search by Status:", 
                                   ["جميع الحالات"] + list(filtered_employees['حالة المشروع'].unique()))
    
    # Apply filters
    display_df = filtered_employees.copy()
    
    if search_term:
        display_df = display_df[
            display_df['الاسم'].str.contains(search_term, case=False, na=False) |
            display_df['معرف الموظف'].str.contains(search_term, case=False, na=False)
        ]
    
    if project_search != "جميع المشاريع":
        display_df = display_df[display_df['المشروع الحالي'] == project_search]
    
    if status_search != "جميع الحالات":
        display_df = display_df[display_df['حالة المشروع'] == status_search]
    
    # Display results
    if not display_df.empty:
        st.dataframe(
            display_df[['معرف الموظف', 'الاسم', 'المنشأة', 'القسم', 'المشروع الحالي', 'حالة المشروع', 'المهمة الحالية', 'تقدم المهمة']],
            use_container_width=True
        )
        st.info(f"عرض {len(display_df)} من أصل {len(filtered_employees)} موظف")
    else:
        st.warning("لا توجد نتائج للبحث المحدد / No results found for the specified search")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏥 مديرية صحة دمشق - نظام متابعة الموظفين</p>
    <p>Damascus Health Directorate - Employee Tracking System</p>
    <div style='margin: 1rem 0; padding: 1rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 8px; border: 1px solid #dee2e6;'>
        <p style='color: #495057; font-weight: bold;'>🤖 تطوير وبرمجة: المهندس محمد الأشمر - خبير ذكاء اصطناعي</p>
        <p style='color: #6c757d;'>Developed by: Eng. Mohammad Al-Ashmar - AI Expert</p>
        <p style='color: #6c757d; font-size: 0.9em;'>💡 نظام ذكي لإدارة ومتابعة الموظفين باستخدام تقنيات الذكاء الاصطناعي</p>
        <p style='color: #6c757d; font-size: 0.9em;'>Smart Employee Management & Tracking System using AI Technologies</p>
    </div>
    <p>آخر تحديث: {} | Last Updated: {}</p>
</div>
""".format(
    datetime.now().strftime('%Y-%m-%d %H:%M'),
    datetime.now().strftime('%Y-%m-%d %H:%M')
), unsafe_allow_html=True) 