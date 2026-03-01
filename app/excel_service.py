import pandas as pd

def save_jobs_to_excel(jobs):
    df = pd.DataFrame(jobs)
    df.to_excel("filtered_jobs.xlsx", index=False)
    print("📊 Saved filtered_jobs.xlsx")