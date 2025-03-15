#!/bin/sh
python create_hdfs_dir.py
exec streamlit run dashboard.py --server.port=8000 --server.address=0.0.0.0