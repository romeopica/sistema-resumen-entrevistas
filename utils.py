def format_to_html(text):
    import re
    text = re.sub(r'##(.+?)##', r'<br><h2 class="text-lg">\1</h2><br>', text)
    text = re.sub(r'#(.+?)#', r'<h1 class="text-xl">\1</h1><br>', text)
    text = re.sub(r'\&(.+?)\&', r'<p class="text-base"><b>\1</b></p>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<p class="text-base">\1</p><br>', text)
    text = re.sub(r'\*(.+?)\*', r'<p class="text-base">\1</p>', text)
    text = re.sub(r'\%(.+?)\%', r'<br><p class="text-base">\1</p>', text)
    return text