import os
import glob
import re
import pandas as pd
from collections import defaultdict

def consolidate_summaries(search_dir="downloaded-artifacts", output_dir="output"):
    # Pattern to match:
    # batch_summary_{batch_index}_{date}.csv (US stocks)
    # batch_summary_{universe}_{batch_index}_{date}.csv (other universes like uk_etfs)
    pattern = r"batch_summary_(?:([a-zA-Z0-9_\-]+)_)?(\d+)_(\d{4}-\d{2}-\d{2})\.csv$"
    
    # Group files by (universe_name, date)
    groups = defaultdict(list)
    
    # Search for all CSV files in the search directory
    csv_files = glob.glob(os.path.join(search_dir, "**", "*.csv"), recursive=True)
    
    # Also scan root folder for any local/direct batch files
    csv_files.extend(glob.glob("batch_summary_*.csv"))
    
    # Remove duplicate entries from double glob
    csv_files = list(set(csv_files))
    
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        match = re.match(pattern, filename)
        if match:
            universe = match.group(1) or ""
            date_str = match.group(3)
            groups[(universe, date_str)].append(filepath)
            
    os.makedirs(output_dir, exist_ok=True)
    
    for (universe, date_str), files in groups.items():
        print(f"\nConsolidating {len(files)} files for universe='{universe or 'US Stocks'}' date='{date_str}'...")
        
        # Read and concat new batch data
        dfs = []
        for f in files:
            try:
                dfs.append(pd.read_csv(f))
            except Exception as e:
                print(f"Error reading {f}: {e}")
                
        if not dfs:
            continue
            
        new_df = pd.concat(dfs, ignore_index=True)
        
        # Determine output file name
        universe_suffix = f"_{universe}" if universe else ""
        output_filename = os.path.join(output_dir, f"summary{universe_suffix}_{date_str}.csv")
        
        # Load existing consolidated summary if it exists
        if os.path.exists(output_filename):
            try:
                existing_df = pd.read_csv(output_filename)
                combined = pd.concat([existing_df, new_df], ignore_index=True)
                combined = combined.drop_duplicates(subset=['ticker'], keep='last')
            except Exception as e:
                print(f"Error loading existing summary {output_filename}: {e}")
                combined = new_df
        else:
            combined = new_df
            
        # Sort by ticker name for clean diffs
        combined = combined.sort_values(by='ticker').reset_index(drop=True)
        
        # Save updated summary
        combined.to_csv(output_filename, index=False)
        print(f"Saved {len(combined)} tickers to {output_filename}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Consolidate batch summaries by universe and date")
    parser.add_argument("--search-dir", default="downloaded-artifacts", help="Directory to search for batch summaries")
    parser.add_argument("--output-dir", default="output", help="Directory to save consolidated summaries")
    args = parser.parse_args()
    
    consolidate_summaries(args.search_dir, args.output_dir)
