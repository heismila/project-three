import sys, os, time, csv

# global state everywhere
d = {}
lines = []
wc = 0
chars = 0
start_time = 0
report_format = "text"
output_file = None
summary_only = False
min_len = 3
input_file = ""
start_time_human = ""

def read_it(f):
    global lines, chars
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    chars = len(content)
    lines = content.split('\n')
    return content

def clean(w):
    w = w.lower()
    w = w.strip('.,!?;:"\'()[]{}')
    return w

def analyze(content):
    global d, wc, min_len
    ws = content.split()
    for i in range(len(ws)):
        w = ws[i]
        if w == "":
            continue
        w = clean(w)
        if w == "":
            continue
        if len(w) < min_len:
            continue
        wc = wc + 1
        if w in d:
            d[w] = d[w] + 1
        else:
            d[w] = 1

def get_sorted_items():
    items = []
    for k in d:
        items.append((k, d[k]))
    for i in range(len(items)):
        for j in range(len(items) - 1):
            if items[j][1] < items[j+1][1]:
                tmp = items[j]
                items[j] = items[j+1]
                items[j+1] = tmp
    return items

def get_avg_len():
    total_len = 0
    for w in d:
        total_len = total_len + len(w) * d[w]
    if wc > 0:
        return total_len / wc
    return 0

def get_longest():
    longest = ""
    for w in d:
        if len(w) > len(longest):
            longest = w
    return longest

def get_shortest():
    shortest = None
    for w in d:
        if shortest is None or len(w) < len(shortest):
            shortest = w
    return shortest

def format_text():
    global d, wc, chars, lines, summary_only, min_len, input_file, start_time_human
    out = []
    out.append("============ REPORT ============")
    out.append("file: " + input_file)
    out.append("generated: " + start_time_human)
    out.append("total chars: " + str(chars))
    out.append("total lines: " + str(len(lines)))
    out.append("total words: " + str(wc))
    out.append("unique words: " + str(len(d)))
    out.append("avg word length: " + str(round(get_avg_len(), 2)))
    out.append("min word length: " + str(min_len))
    if not summary_only:
        out.append("-------- TOP 10 --------")
        items = get_sorted_items()
        for i in range(min(10, len(items))):
            out.append("  " + items[i][0] + ": " + str(items[i][1]))
        out.append("longest word: " + get_longest())
        s = get_shortest()
        if s is not None:
            out.append("shortest word: " + s)
    out.append("================================")
    return "\n".join(out)

def format_html():
    global d, wc, chars, lines, summary_only, min_len, input_file, start_time_human
    out = []
    out.append("<html><body>")
    out.append("<h1>Report</h1>")
    out.append("<p>file: " + input_file + "</p>")
    out.append("<p>generated: " + start_time_human + "</p>")
    out.append("<p>total chars: " + str(chars) + "</p>")
    out.append("<p>total lines: " + str(len(lines)) + "</p>")
    out.append("<p>total words: " + str(wc) + "</p>")
    out.append("<p>unique words: " + str(len(d)) + "</p>")
    out.append("<p>avg word length: " + str(round(get_avg_len(), 2)) + "</p>")
    out.append("<p>min word length: " + str(min_len) + "</p>")
    if not summary_only:
        out.append("<h2>Top 10</h2><ul>")
        items = get_sorted_items()
        for i in range(min(10, len(items))):
            out.append("<li>" + items[i][0] + ": " + str(items[i][1]) + "</li>")
        out.append("</ul>")
        out.append("<p>longest word: " + get_longest() + "</p>")
        s = get_shortest()
        if s is not None:
            out.append("<p>shortest word: " + s + "</p>")
    out.append("</body></html>")
    return "\n".join(out)

def format_csv():
    global d, wc, chars, lines, summary_only, min_len, input_file, start_time_human
    out = []
    out.append("metric,value")
    out.append("input_file," + input_file)
    out.append("generated," + start_time_human)
    out.append("total_chars," + str(chars))
    out.append("total_lines," + str(len(lines)))
    out.append("total_words," + str(wc))
    out.append("unique_words," + str(len(d)))
    out.append("avg_word_length," + str(round(get_avg_len(), 2)))
    out.append("min_word_length," + str(min_len))
    if not summary_only:
        items = get_sorted_items()
        for i in range(min(10, len(items))):
            out.append("word_" + str(i+1) + "," + items[i][0] + ":" + str(items[i][1]))
        out.append("longest," + get_longest())
        s = get_shortest()
        if s is not None:
            out.append("shortest," + s)
    return "\n".join(out)

def save_output(text):
    global output_file
    if output_file is not None:
        with open(output_file, 'w', encoding='utf-8') as fh:
            fh.write(text)

def main():
    global report_format, output_file, start_time, summary_only, min_len, input_file, start_time_human
    start_time = time.time()
    start_time_human = time.ctime()
    if len(sys.argv) < 2:
        print("usage: analyzer.py <file> [--format text|html|csv] [--output FILE] [--summary] [--min-length N]")
        sys.exit(1)
    f = sys.argv[1]
    input_file = f
    if not os.path.exists(f):
        print("file not found: " + f)
        sys.exit(1)
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--format" and i + 1 < len(sys.argv):
            report_format = sys.argv[i+1]
            i = i + 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i+1]
            i = i + 2
        elif sys.argv[i] == "--summary":
            summary_only = True
            i = i + 1
        elif sys.argv[i] == "--min-length" and i + 1 < len(sys.argv):
            min_len = int(sys.argv[i+1])
            i = i + 2
        else:
            i = i + 1
    c = read_it(f)
    analyze(c)
    if report_format == "html":
        text = format_html()
    elif report_format == "csv":
        text = format_csv()
    else:
        text = format_text()
    print(text)
    save_output(text)
    elapsed = time.time() - start_time
    # not printed, but kept for future use
    _ = elapsed

if __name__ == "__main__":
    main()
