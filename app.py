import streamlit as st
import os
from datetime import datetime
import matplotlib.pyplot as plt

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="Cloud Storage Pro", layout="wide")

# ---------- SESSION LOGIN ----------
if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.title("🔐 Login System")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.login = True
            st.success("Login success")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.login:
    login()
    st.stop()

# ---------- LOGOUT ----------
if st.sidebar.button("🚪 Logout"):
    st.session_state.login = False
    st.rerun()

# ---------- UI ----------
st.markdown("""
<style>
.stApp { background:#eef2f7; }
.header { font-size:34px; font-weight:700; text-align:center; margin-bottom:20px; color:#1e3a8a;}
.card { background:white; padding:15px; border-radius:12px; margin-bottom:10px;
box-shadow:0 3px 8px rgba(0,0,0,0.1);}
.metric { background:white; padding:20px; border-radius:12px; text-align:center;
border-left:6px solid #2563eb;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>☁️ Cloud Storage Pro Dashboard</div>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Controls")

search = st.sidebar.text_input("Search")
filter_type = st.sidebar.selectbox("Filter", ["All","Images","Documents"])
sort_by = st.sidebar.selectbox("Sort", ["Name","Size","Date"])

# ---------- DATA ----------
files = os.listdir(UPLOAD_FOLDER)

total_files = len(files)
total_size = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER,f)) for f in files)/1024 if files else 0
img_count = len([f for f in files if f.lower().endswith(("png","jpg","jpeg"))])
doc_count = len([f for f in files if f.lower().endswith(("pdf","txt"))])

# ---------- TABS ----------
tab1, tab2 = st.tabs(["📊 Dashboard", "📁 File Manager"])

# ================= DASHBOARD =================
with tab1:
    st.subheader("Overview")

    col1,col2,col3 = st.columns(3)
    col1.markdown(f"<div class='metric'>Files<br><h2>{total_files}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric'>Storage KB<br><h2>{round(total_size,2)}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric'>Images<br><h2>{img_count}</h2></div>", unsafe_allow_html=True)

    st.subheader("📊 File Distribution")

    if img_count == 0 and doc_count == 0:
        st.info("No files available to display chart")
    else:
        fig, ax = plt.subplots()
        ax.pie([img_count, doc_count], labels=["Images","Docs"], autopct="%1.1f%%")
        st.pyplot(fig)

    st.subheader("🕒 Recent Files")
    recent = sorted(files, key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER,x)), reverse=True)[:5]
    for f in recent:
        st.write("•", f)

# ================= FILE MANAGER =================
with tab2:
    st.subheader("Upload File")

    uploaded_file = st.file_uploader("Choose file")

    if uploaded_file:
        path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Uploaded successfully")
        st.rerun()

    # FILTER
    filtered = []
    for f in files:
        if search.lower() in f.lower():
            if filter_type == "Images" and f.lower().endswith(("png","jpg","jpeg")):
                filtered.append(f)
            elif filter_type == "Documents" and f.lower().endswith(("pdf","txt")):
                filtered.append(f)
            elif filter_type == "All":
                filtered.append(f)

    # SORT
    if sort_by == "Name":
        filtered.sort()
    elif sort_by == "Size":
        filtered.sort(key=lambda x: os.path.getsize(os.path.join(UPLOAD_FOLDER,x)))
    elif sort_by == "Date":
        filtered.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER,x)))

    st.subheader("Files")

    for file in filtered:
        path = os.path.join(UPLOAD_FOLDER,file)
        size = round(os.path.getsize(path)/1024,2)
        date = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d-%m-%Y")

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,1,1,1])

        col1.write(f"📄 {file}")
        col2.write(f"{size} KB")
        col3.write(date)

        # preview
        if file.lower().endswith(("png","jpg","jpeg")):
            if col4.button("👁", key="p_"+file):
                st.image(path, width=200)

        # download
        with open(path,"rb") as f:
            col5.download_button("⬇", f, file)

        # rename
        new_name = col6.text_input("", key="r_"+file, placeholder="Rename")
        if col6.button("✔", key="a_"+file):
            if new_name:
                os.rename(path, os.path.join(UPLOAD_FOLDER,new_name))
                st.success("Renamed")
                st.rerun()

        # delete
        if st.button("❌ Delete", key="d_"+file):
            os.remove(path)
            st.warning("Deleted")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
