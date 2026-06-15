import pandas as pd
from inspect_ai.log import read_eval_log

def display_past_results(log_path: str):
    # Load the log file
    log = read_eval_log(log_path)
    
    parsed_records = []
    for sample in log.samples:
        # Access metadata and scores
        meta = sample.metadata
        score_wrapper = sample.scores.get("groundedness_scorer_cot")
        
        parsed_records.append({
            "Property ID": meta.get("property_id", "N/A"),
            "Property Name": meta.get("property_name", "Unknown"),
            "Groundedness Score": score_wrapper.value if score_wrapper else 0.0,
            "Audit Transcript": score_wrapper.explanation if score_wrapper else "No trace."
        })

    # Create and display dataframe
    df = pd.DataFrame(parsed_records)
    pd.set_option("display.max_colwidth", 50)
    print(f"\n--- Results from: {log_path} ---")
    print(df.to_string(index=False))

if __name__ == "__main__":
    # Point to the specific log file you want to view
    target_log = "logs/2026-06-15T13-48-18-00-00_listing-generator-eval_kVS3m5AS6wxU9VpHB5p9bv.eval"
    display_past_results(target_log)