def read_excel(file_path):
    import pandas as pd
    return pd.read_excel(file_path)

def write_excel(dataframe, file_path):
    import pandas as pd
    dataframe.to_excel(file_path, index=False)

def extract_rj_number(comment):
    # Assuming RJ_Number is a specific pattern in the comment
    import re
    match = re.search(r'RJ_Number:\s*(\S+)', comment)
    return match.group(1) if match else None

def extract_payment_ref(comment):
    # Extracts the last word after the last '#' in the comment string
    import re
    match = re.search(r'#([^#\s]+(?: [^#\s]+)*)\s*$', comment)
    if match:
        return match.group(1).strip()
    return None

def format_output(results):
    # Convert results to a DataFrame for better formatting
    import pandas as pd
    return pd.DataFrame(results)