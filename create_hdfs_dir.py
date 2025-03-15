from hdfs import InsecureClient

# Replace the URL and user with your actual HDFS Namenode address and user
client = InsecureClient('http://namenode_host:50070', user='your_hdfs_user')
hdfs_dir = '/my_app_directory'

if not client.status(hdfs_dir, strict=False):
    client.makedirs(hdfs_dir)
    print(f"Created {hdfs_dir} successfully.")
else:
    print(f"Directory {hdfs_dir} already exists.")