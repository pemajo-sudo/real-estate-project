import os
import shutil

src = r"C:\Users\USER\.gemini\antigravity\brain\8d1a288e-28a7-4670-bba5-61aa0e7730d5\media__1775985111073.jpg"
dst_dir = r"d:\Sem 5\Business Application Development\Real Estate Grp Proj\real-estate-project\media"
dst = os.path.join(dst_dir, "about_hero_agent.jpg")

try:
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy(src, dst)
    print("Copy successful!")
except Exception as e:
    print(f"Error copying file: {e}")
