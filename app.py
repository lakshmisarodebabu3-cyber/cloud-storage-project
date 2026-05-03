import streamlit as st
import os
from datetime import datetime

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="Cloud Storage Pro", layout="wide")

# ---------- LOGIN ----------
if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.title("🔐 Login System")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.login = True
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
.stApp { background:#f4f7fb; }
.header { font-size:32px; font-weight:700; text-align:center; color:#1e3a8a;}
.card { background:white; padding:12px; border-radius:10px; margin-bottom:8px;
box-shadow:0 2px 6px rgba(0,0,0,0.08);}
.metric { background:white; padding:15px; border-radius:10px; text-align:center;
border-left:5px solid #2563eb;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>☁️ Cloud Storage Pro Dashboard</div>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Controls")
search = st.sidebar.text_input("Search")
filter_type = st.sidebar.selectbox("Filter", ["All","Images","Documents"])
sort_by = st.sidebar.selectbox("Sort", ["Name","Size","Date"])

# ---------- FILE LIST ----------
files = os.listdir(UPLOAD_FOLDER)

# ---------- DASHBOARD ----------
tab1, tab2 = st.tabs(["📊 Dashboard", "📁 File Manager"])

with tab1:
    total_files = len(files)
    total_size = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER,f)) for f in files)/1024 if files else 0
    img_count = len([f for f in files if f.lower().endswith(("png","jpg","jpeg"))])
    doc_count = len([f for f in files if f.lower().endswith(("pdf","txt"))])

    col1,col2,col3 = st.columns(3)
    col1.metric("Files", total_files)
    col2.metric("Storage (KB)", round(total_size,2))
    col3.metric("Images", img_count)

    st.info(f"Images: {img_count} | Documents: {doc_count}")

# ---------- FILE MANAGER ----------
with tab2:

    # 🔹 Upload
    uploaded_file = st.file_uploader("Upload File")

    if uploaded_file:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File uploaded successfully")

    # 🔹 Refresh files after upload
    files = os.listdir(UPLOAD_FOLDER)

    # 🔹 Filter
    filtered = []
    for f in files:
        if search.lower() in f.lower():
            if filter_type == "Images" and f.lower().endswith(("png","jpg","jpeg")):
                filtered.append(f)
            elif filter_type == "Documents" and f.lower().endswith(("pdf","txt")):
                filtered.append(f)
            elif filter_type == "All":
                filtered.append(f)

    # 🔹 Sort
    if sort_by == "Name":
        filtered.sort()
    elif sort_by == "Size":
        filtered.sort(key=lambda x: os.path.getsize(os.path.join(UPLOAD_FOLDER,x)))
    elif sort_by == "Date":
        filtered.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER,x)))

    st.subheader("Files")

    # 🔹 File Cards
    for file in filtered:
        path = os.path.join(UPLOAD_FOLDER, file)
        size = round(os.path.getsize(path)/1024,2)
        date = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d-%m-%Y")

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3,1,1,1,1])

            col1.write(f"📄 {file}")
            col2.write(f"{size} KB")
            col3.write(date)

            # Preview
            if file.lower().endswith(("png","jpg","jpeg")):
                if col4.button("👁", key=f"preview_{file}"):
                    st.image(path, width=200)

            # Download
            with open(path, "rb") as f:
                col5.download_button("⬇", f, file, key=f"download_{file}")

            # Rename (separate row)
            new_name = st.text_input(f"Rename {file}", key=f"rename_{file}")
            if st.button("Apply", key=f"apply_{file}"):
                if new_name:
                    os.rename(path, os.path.join(UPLOAD_FOLDER, new_name))
                    st.success("Renamed")
                    st.rerun()

            # Delete
            if st.button("❌ Delete", key=f"delete_{file}"):
                os.remove(path)
                st.warning("Deleted")
                st.rerun()

            st.divider()
