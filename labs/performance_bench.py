
import pandas as pd
import numpy as np
import time

def main():
    print("📊 Starting Pandas Performance Benchmark (Task 5)...")
    
    source_file = 'cleaned_combined_products.csv'
    if not pd.io.common.file_exists(source_file):
        print(f"Error: {source_file} not found. Run cleaning script first.")
        return
        
    df_base = pd.read_csv(source_file)
    print(f"Base dataset has {len(df_base)} rows.")
    
    df = pd.concat([df_base] * 2, ignore_index=True)
    print(f"Benchmark dataset expanded to {len(df)} rows.")

    print("\n--- Operation: Calculate 10% Tax on Discount Price ---")
    
    start = time.time()
    _ = [x * 0.1 for x in df['discount_price']]
    loop_time = time.time() - start
    print(f"Method A (Python Loop): {loop_time:.4f} seconds")

    start = time.time()
    _ = df['discount_price'] * 0.1
    vector_time = time.time() - start
    print(f"Method B (Vectorization): {vector_time:.4f} seconds")

    speedup = loop_time / vector_time
    print(f"\n🚀 Vectorization is {speedup:.1f}x faster!")

    print("\n--- Memory Optimization ---")
    mem_before = df.memory_usage(deep=True).sum() / 1e6
    print(f"Memory Usage Before: {mem_before:.2f} MB")
    
    df['ratings'] = pd.to_numeric(df['ratings'], downcast='float')
    df['no_of_ratings'] = pd.to_numeric(df['no_of_ratings'], downcast='integer')
    
    mem_after = df.memory_usage(deep=True).sum() / 1e6
    print(f"Memory Usage After: {mem_after:.2f} MB")
    print(f"Saved: {mem_before - mem_after:.2f} MB")

if __name__ == "__main__":
    main()
