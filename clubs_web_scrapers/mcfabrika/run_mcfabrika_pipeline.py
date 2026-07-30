
import subprocess
import sys
import time
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
scripts = [
 "mcfabrika_web_events.py"
,"mcfabrika_clean_csv.py" 
,"mcfabrica_fetch_fb_link.py" 
]


print("=" * 80)
print("PIPELINE START")
print("Started:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)
pipeline_start = time.time()
for script in scripts:
	print("\n" + "-" * 80)
	print(f"Running {script}")

	script_start = time.time()
	print("Started: ",
		datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	result = subprocess.run(
		["python3", script],
        	cwd="/home/deploy/webscrapers/clubs_web_scrapers/mcfabrika",
	)
	script_end = time.time()
	duration = script_end - script_start
	print("Finished:",
		datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	print(f"Duration: {duration:.1f} seconds")
	if result.returncode != 0:
		print(f"\n ERROR: {script} failed.")
		sys.exit(1)
# =========================================================
# SUMMARY
# =========================================================
pipeline_end = time.time()
total = pipeline_end - pipeline_start

hours = int(total // 3600)
minutes = int((total % 3600) // 60)
seconds = int(total % 60)

print("\n" + "=" * 80)
print("PIPELINE COMPLETE")
print("Finished:",
      datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(f"Total runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
