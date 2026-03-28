import google.generativeai as genai
import pandas as pd

genai.configure(api_key="AIzaSyCtlXJnpRoS0PDksIXiXBgbl502SntXA0U")

def generate_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return "No data for AI summary."

    try:
        sample = df.head(10).fillna("N/A").to_string(index=False)
        prompt = f"""
You are a data analyst.
Analyze this dataset:
{sample}
"""


        response = genai.generate(
            model="Gemini-2.5-flash",
            prompt=prompt
        )
        return response.output_text

    except Exception as e:
        print("AI summary error:", e)
        return f"AI summary not available: {e}"
        

      
       
       
      

