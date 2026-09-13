with open('scratch/new_overlays.py', 'r', encoding='utf-8') as f1:
    c1 = f1.read()
with open('scratch/test_all_classes.py', 'r', encoding='utf-8') as f2:
    c2 = f2.read()

part1 = c1.split('print("Classes 1-3 compiled successfully!")')[0]
idx4 = c2.find('class CartoonPainterOverlay:')
part2 = c2[idx4:]

full = part1 + '\n\n' + part2
with open('scratch/all_cartoons_combined.py', 'w', encoding='utf-8') as out:
    out.write(full)
print('Wrote all_cartoons_combined.py successfully!')
