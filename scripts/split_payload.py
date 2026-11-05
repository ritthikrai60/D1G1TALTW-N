with open('scripts/accurate_basement_payload.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Split before '# 3. ST-1'
p1, p2 = text.split('# 3. ST-1: PRIMARY FIRE EGRESS STAIR CORE')

with open('scripts/payload_part1.py', 'w', encoding='utf-8') as f:
    f.write(p1.strip())

with open('scripts/payload_part2.py', 'w', encoding='utf-8') as f:
    f.write(('# 3. ST-1: PRIMARY FIRE EGRESS STAIR CORE' + p2).strip())

print(f"Part 1 length: {len(p1)} chars")
print(f"Part 2 length: {len(p2)} chars")

