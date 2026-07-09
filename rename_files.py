import os

folder = 'data/raw'
for f in os.listdir(folder):
    if '_max_yf.csv' in f:
        # Check if _max.csv already exists, if yes just delete the _yf version
        base = f.replace('_max_yf.csv', '')
        max_file = os.path.join(folder, f'{base}_max.csv')
        yf_file = os.path.join(folder, f)
        if os.path.exists(max_file):
            os.remove(yf_file)
            print(f"Deleted duplicate: {f}")
        else:
            os.rename(yf_file, max_file)
            print(f"Renamed: {f}")
    elif '_max_agent.csv' in f:
        base = f.replace('_max_agent.csv', '')
        max_file = os.path.join(folder, f'{base}_max.csv')
        agent_file = os.path.join(folder, f)
        if os.path.exists(max_file):
            os.remove(agent_file)
            print(f"Deleted duplicate: {f}")
        else:
            os.rename(agent_file, max_file)
            print(f"Renamed: {f}")

print("Done!")