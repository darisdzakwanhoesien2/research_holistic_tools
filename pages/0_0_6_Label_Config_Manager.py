import streamlit as st
import json
import os
import pandas as pd

CONFIG_PATH = "data/label_code.json"

st.title("🏷 Section Label Configuration Manager")

# --------------------------------------------------
# Load Config
# --------------------------------------------------

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        label_config = json.load(f)
else:
    label_config = {}

st.subheader("📋 Current Label Mapping")

st.json(label_config)

# --------------------------------------------------
# Add New Label
# --------------------------------------------------

st.subheader("➕ Add / Update Label")

new_label = st.text_input("Section Label Key (e.g., methodology)")
variants = st.text_area(
    "Header Variants (one per line)",
    placeholder="methods\nresearch design\ndata and methods"
)

if st.button("Save / Update Label"):

    if new_label and variants:

        variant_list = [v.strip().lower() for v in variants.split("\n") if v.strip()]

        label_config[new_label.lower()] = variant_list

        os.makedirs("data", exist_ok=True)

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(label_config, f, indent=4)

        st.success("Label updated successfully!")

# --------------------------------------------------
# Delete Label
# --------------------------------------------------

st.subheader("🗑 Delete Label")

delete_label = st.selectbox("Select Label to Delete", list(label_config.keys()))

if st.button("Delete Label"):
    label_config.pop(delete_label)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(label_config, f, indent=4)

    st.warning("Label deleted.")
