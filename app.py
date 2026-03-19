import streamlit as st
import os
from datetime import datetime
import matplotlib.pyplot as plt

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="Cloud Storage Pro", layout="wide")

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
.header {
    font-size:34px;
    font-weight:700;
    text-align:center;
    margin-bottom:20px;
}
.card {
    background:white;
    padding:15px;
    border-radius:12px;
    margin-bottom:12px;
    box-shadow:0 4px 10px rgba(0,0,0,0.05);
}
.metric {
    background:white;
    padding:20px;
    border-radius:12px;
    text-align:center;
    border-left:5px solid #2563eb;
}
.section {
    font-size:22px;
    font-weight:600;
    margin-top:20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>☁️ Cloud Storage Pro Dashboard</div>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Controls")

search = st.sidebar.text_input("Search Files")
filter_type = st.sidebar.selectbox("Filter", ["All","Images","Documents"])
sort_by = st.sidebar.selectbox("Sort", ["Name","Size","Date"])

# ---------- DATA ----------
files = os.listdir(UPLOAD_FOLDER)

# ⚡ CACHED STATS (FASTER)
@st.cache_data
def get_stats(files):
    total_files = len(files)
    total_size = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER,f)) for f in files)/1024
    img_count = len([f for f in files if f.endswith(("png","jpg","jpeg"))])
    doc_count = len([f for f in files if f.endswith(("pdf","txt"))])
    return total_files, total_size, img_count, doc_count

total_files, total_size, img_count, doc_count = get_stats(files)

# ---------- DASHBOARD ----------
st.markdown("<div class='section'>📊 Dashboard</div>", unsafe_allow_html=True)

col1,col2,col3 = st.columns(3)
col1.markdown(f"<div class='metric'>Files<br><h2>{total_files}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric'>Storage KB<br><h2>{round(total_size,2)}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric'>Images<br><h2>{img_count}</h2></div>", unsafe_allow_html=True)

# ---------- CHART ----------
fig, ax = plt.subplots()
ax.pie([img_count, doc_count], labels=["Images","Docs"], autopct="%1.1f%%")
st.pyplot(fig)

# ---------- UPLOAD ----------
st.markdown("<div class='section'>📤 Upload File</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose file")

if uploaded_file:
    with st.spinner("Uploading..."):
        path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.success("Uploaded successfully")

# ---------- FILTER ----------
filtered = []
for f in files:
    if search.lower() in f.lower():
        if filter_type == "Images" and f.endswith(("png","jpg","jpeg")):
            filtered.append(f)
        elif filter_type == "Documents" and f.endswith(("pdf","txt")):
            filtered.append(f)
        elif filter_type == "All":
            filtered.append(f)

# ---------- SORT ----------
if sort_by == "Name":
    filtered.sort()
elif sort_by == "Size":
    filtered.sort(key=lambda x: os.path.getsize(os.path.join(UPLOAD_FOLDER,x)))
elif sort_by == "Date":
    filtered.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER,x)))

# ---------- FILE MANAGER ----------
st.markdown("<div class='section'>📂 File Manager</div>", unsafe_allow_html=True)

for file in filtered:
    path = os.path.join(UPLOAD_FOLDER,file)
    size = round(os.path.getsize(path)/1024,2)
    date = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d-%m-%Y")

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1,col2,col3 = st.columns([4,1,1])
    col1.write(f"📄 {file}")
    col2.write(f"{size} KB")
    col3.write(date)

    colA, colB, colC = st.columns(3)

    # Preview
    if file.endswith(("png","jpg","jpeg")):
        if colA.button("👁 Preview", key="p_"+file):
            st.image(path, width=200)

    # Download
    with open(path,"rb") as f:
        colB.download_button("⬇ Download", f, file)

    # Delete
    if colC.button("❌ Delete", key="d_"+file):
        os.remove(path)
        st.warning("Deleted")
        st.rerun()

    # Rename
    new_name = st.text_input("Rename file", key="rename_"+file)

    if st.button("✔ Apply Rename", key="apply_"+file):
        if new_name:
            new_path = os.path.join(UPLOAD_FOLDER, new_name)

            if os.path.exists(new_path):
                st.error("File already exists!")
            else:
                os.rename(path, new_path)
                st.success("Renamed successfully")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- RECENT ----------
st.markdown("<div class='section'>🕒 Recent Files</div>", unsafe_allow_html=True)

recent = sorted(files, key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER,x)), reverse=True)[:5]

for f in recent:
    st.write("•", f)