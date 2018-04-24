import os
import shutil
from config import SEARCH_INDEX_DIR, SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine

print("Step 1. Delete old index")
try:
    shutil.rmtree(SEARCH_INDEX_DIR)
except OSError:
    print("No directory found...continuing...")

print("Step 2. Refresh Materialized View")
engine = create_engine(SQLALCHEMY_DATABASE_URI)
with engine.begin() as connection:
    result = connection.execute("REFRESH MATERIALIZED VIEW attrs.search_v8")
    print("Result", result)

print("Step 3. Rebuild Index")
build_index = os.path.join(SEARCH_INDEX_DIR.replace("search_index/", ""), "scripts", "search", "build_index.py")
result = os.system("python {}".format(build_index))
print("Result", result)
