import requests
import time
import os

INPUT_FILE = '../data/assemblies_ids.txt'
OUTPUT_FOLDER = '/beegfs/lvsea/mags_download'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    ids = [line.strip() for line in f if line.strip()]

print(f"Total {len(ids)} ID")
print(f"GCF: {sum(1 for id in ids if id.startswith('GCF'))}")
print(f"GCA: {sum(1 for id in ids if id.startswith('GCA'))}")
print("-" * 50)

for gcf in ids:
    print(f"Downloading {gcf}...")
    
    try:
        prefix = gcf.split('_')[0]
        
        digits = gcf.split('_')[1].split('.')[0]
        
        path = f"{prefix}/{digits[0:3]}/{digits[3:6]}/{digits[6:9]}/"
        
        base = f"https://ftp.ncbi.nlm.nih.gov/genomes/all/{path}"
        
        print(f"  Searching: {base}")
        
        resp = requests.get(base, timeout=30)
        resp.raise_for_status()
        
        downloaded = False
        
        for line in resp.text.split('\n'):
            if gcf in line:
                folder = line.split('href="')[1].split('"')[0]
                
                fna_url = base + folder + folder.rstrip('/') + "_genomic.fna.gz"
                
                print(f"  Downloading: {fna_url}")
                
                fna_data = requests.get(fna_url, timeout=60, stream=True)
                
                if fna_data.status_code == 200:
                    output_path = os.path.join(OUTPUT_FOLDER, f"{gcf}.fna.gz")
                    
                    total_size = int(fna_data.headers.get('content-length', 0))
                    block_size = 8192
                    
                    with open(output_path, 'wb') as f:
                        for chunk in fna_data.iter_content(chunk_size=block_size):
                            if chunk:
                                f.write(chunk)
                    
                    file_size = os.path.getsize(output_path) / (1024*1024)
                    print(f"  Success! Size: {file_size:.2f} MB")
                    downloaded = True
                else:
                    print(f"  Error: {fna_data.status_code}")
                break
        
        if not downloaded:
            print(f"  Trying alternative format...")
            
            alt_formats = ["_genomic.fna.gz", "_genomic.gbff.gz", "_genomic.gff.gz"]
            
            for line in resp.text.split('\n'):
                if gcf in line:
                    folder = line.split('href="')[1].split('"')[0]
                    
                    for alt_format in alt_formats:
                        alt_url = base + folder + folder.rstrip('/') + alt_format
                        alt_data = requests.head(alt_url, timeout=30)
                        
                        if alt_data.status_code == 200:
                            print(f"  Find alternative format: {alt_format}")
                            fna_data = requests.get(alt_url, timeout=60, stream=True)
                            
                            if fna_data.status_code == 200:
                                output_path = os.path.join(OUTPUT_FOLDER, f"{gcf}{alt_format}")
                                
                                with open(output_path, 'wb') as f:
                                    for chunk in fna_data.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                
                                file_size = os.path.getsize(output_path) / (1024*1024)
                                print(f"  Success! Size: {file_size:.2f} MB")
                                downloaded = True
                                break
                    
                    if downloaded:
                        break
            
            if not downloaded:
                print(f"  Couldn't find the file for {gcf}")
            
    except requests.exceptions.Timeout:
        print(f"  Connection timeout")
    except requests.exceptions.ConnectionError:
        print(f"  Connection error")
    except Exception as e:
        print(f"  Unexpected error: {e}")
    
    time.sleep(1)

print("\n" + "=" * 50)
print(f"Done! Files are saved to a folder: {os.path.abspath(OUTPUT_FOLDER)}")

if os.path.exists(OUTPUT_FOLDER):
    files = os.listdir(OUTPUT_FOLDER)
    print(f"Downloaded files: {len(files)}")
    for file in files[:5]:
        size = os.path.getsize(os.path.join(OUTPUT_FOLDER, file)) / (1024*1024)
        print(f"  - {file}: {size:.2f} MB")
    if len(files) > 5:
        print(f"  ... and {len(files) - 5}")
