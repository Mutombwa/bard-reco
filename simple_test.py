import re

desc = 'ADT CASH DEPO02113002 0849667217'
pattern = r'ADT CASH DEPO[A-Z\d]+\s+(\d{10})\s*$'

print("="*60)
print("TESTING EXTRACTION")
print("="*60)
print(f"Input: '{desc}'")
print(f"Pattern: {pattern}")
print()

match = re.search(pattern, desc)

if match:
    print("PATTERN MATCHED!")
    print(f"  Full match: '{match.group(0)}'")
    print(f"  Captured group: '{match.group(1)}'")
    print()
    print("="*60)
    print(f"RESULT: {match.group(1)}")
    print("="*60)
else:
    print("NO MATCH")
    print()
    # Try to debug
    print("Let's test step by step:")
    if re.search(r'ADT CASH DEPO', desc):
        print("  ✓ 'ADT CASH DEPO' found")
    else:
        print("  ✗ 'ADT CASH DEPO' not found")
    
    if re.search(r'ADT CASH DEPO\d+', desc):
        print("  ✓ 'ADT CASH DEPO' + digits found")
    else:
        print("  ✗ 'ADT CASH DEPO' + digits not found")
    
    if re.search(r'ADT CASH DEPO[A-Z\d]+', desc):
        print("  ✓ 'ADT CASH DEPO' + [A-Z\\d]+ found")
    else:
        print("  ✗ 'ADT CASH DEPO' + [A-Z\\d]+ not found")
    
    if re.search(r'ADT CASH DEPO[A-Z\d]+\s+', desc):
        print("  ✓ 'ADT CASH DEPO' + [A-Z\\d]+ + space found")
    else:
        print("  ✗ 'ADT CASH DEPO' + [A-Z\\d]+ + space not found")
    
    if re.search(r'ADT CASH DEPO[A-Z\d]+\s+\d{10}', desc):
        print("  ✓ 'ADT CASH DEPO' + [A-Z\\d]+ + space + 10 digits found")
    else:
        print("  ✗ 'ADT CASH DEPO' + [A-Z\\d]+ + space + 10 digits not found")
