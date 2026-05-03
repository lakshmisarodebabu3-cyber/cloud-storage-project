import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="Cloud Storage Pro", layout="wide")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- LOGIN ----------
if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.title("🔐 Cloud Storage Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

if not st.session_state.login:
    login()
    st.stop()

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Controls")

if st.sidebar.button("🚪 Logout"):
    st.session_state.login = False
    st.rerun()

search = st.sidebar.text_input("🔍 Search Files")
filter_type = st.sidebar.selectbox("📂 Filter", ["All", "Images", "Documents"])
sort_by = st.sidebar.selectbox("📊 Sort By", ["Name", "Size", "Date"])

# ---------- GET FILES ----------
def get_files():
    return os.listdir(UPLOAD_FOLDER)

files = get_files()

# ---------- HEADER ----------
st.markdown("<h1 style='text-align:center;color:#1e3a8a;'>☁️ Cloud Storage Pro</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Dashboard", "📁 File Manager"])

# ================= DASHBOARD =================
with tab1:
    total_files = len(files)
    total_size = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER,f)) for f in files)/1024 if files else 0
    img_count = len([f for f in files if f.lower().endswith(("png","jpg","jpeg"))])
    doc_count = len([f for f in files if f.lower().endswith(("pdf","txt"))])

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Files", total_files)
    c2.metric("Storage (KB)", round(total_size,2))
    c3.metric("Images", img_count)

    st.info(f"Images: {img_count} | Documents: {doc_count}")

# ================= FILE MANAGER =================
with tab2:

    uploaded_file = st.file_uploader("Upload File")

    if uploaded_file:
        path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Uploaded successfully")
        st.rerun()

    files = get_files()

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

    st.subheader("📁 Files")

    for file in filtered:
        path = os.path.join(UPLOAD_FOLDER, file)
        size = round(os.path.getsize(path)/1024,2)
        date = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d-%m-%Y")

        c1, c2, c3, c4, c5 = st.columns([3,1,1,1,1])

        c1.write(f"📄 {file}")
        c2.write(f"{size} KB")
        c3.write(date)

        # 👁 VIEW (FINAL FIX)
        if file.lower().endswith(("png","jpg","jpeg")):
            if c4.button("👁", key=f"view_{file}"):
                with open(path, "rb") as img:
                    st.image(img.read(), caption=file, use_container_width=True)

        # ⬇ DOWNLOAD
        with open(path, "rb") as f:
            c5.download_button("⬇", f, file, key=f"dl_{file}")

        # RENAME
        new_name = st.text_input("Rename", key=f"rename_{file}")
        if st.button("Apply", key=f"apply_{file}"):
            if new_name:
                os.rename(path, os.path.join(UPLOAD_FOLDER, new_name))
                st.success("Renamed")
                st.rerun()

        # DELETE
        if st.button("❌ Delete", key=f"del_{file}"):
            os.remove(path)
            st.warning("Deleted")
            st.rerun()

        st.divider()
