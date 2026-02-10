from markdown import markdown

with open('BEST_BETS_DEEP_DIVE.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

html_content = markdown(md_content, extensions=['tables'])

html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Best Bets Deep Dive</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 40px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; }
        h2 { color: #34495e; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        blockquote { background: #f9f9f9; border-left: 5px solid #3498db; padding: 15px; margin: 20px 0; }
        pre { background: #f4f4f4; padding: 15px; overflow-x: auto; }
    </style>
</head>
<body>
""" + html_content + """
</body>
</html>"""

with open('BEST_BETS_DEEP_DIVE.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print('HTML created successfully')
