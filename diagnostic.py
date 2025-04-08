from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("HUB_SUPABASE_URL")
SUPABASE_KEY = os.getenv("HUB_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("HUB_SUPABASE_URL and HUB_SUPABASE_KEY must be set in the .env file.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def diagnostics():
    print("\nRunning Supabase Diagnostics...\n")

    # Check basic connection
    try:
        response = supabase.table('foodbank').select('*').limit(1).execute()
        print("Select * from foodbank SUCCESS! Response:")
        print(response)
        
        response = supabase.table('foodbankreservation').select('*').limit(1).execute()
        print("Select * from hub SUCCESS! Response:")
        print(response)
        
        
    except Exception as e:
        print("Select * from foodbank FAILED! Error:")
        print(str(e))
        
    try:
        foodbank_response = supabase.table('foodbank').select('*').eq('foodbankId', "5675fac3-f89a-4152-a862-e0cea4f661f0").execute()
        print("Select * from hub SUCCESS! Response:")
        print(foodbank_response)
    except Exception as e:
        print("Select * from foodbank FAILED! LLLOLOLOL Error:")
        print(str(e))

    # Manual SQL query to find column
    try:
        result = supabase.table('information_schema.columns').select('column_name').eq('table_name', 'foodbank').execute()
        print("Column names from information_schema:")
        print(result)
    except Exception as e:
        print("Fallback SQL query failed:", str(e))

if __name__ == "__main__":
    diagnostics()
