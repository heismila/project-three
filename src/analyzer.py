import sys, os, time, csv
# ---- Constants (previously magic numbers and strings) ----
DEFAULT_MIN_LEN = 3
TOP_N = 10
ENCODING = "utf-8"
FORMAT_TEXT = "text"
FORMAT_HTML = "html"
FORMAT_CSV = "csv"
INITIAL_AVERAGE = 0
# global state everywhere
d = {}
lines = []
wc = 0
chars = 0
report_format = FORMAT_TEXT
output_file = None
summary_only = False
min_len = DEFAULT_MIN_LEN
input_file = ""
start_time_human = ""

def read_file(path):
    with open(path, 'r', encoding=ENCODING) as fh:
        return fh.read()


def parse_lines(content):
    return content.split('\n')

def clean(w):
    w = w.lower()
    w = w.strip('.,!?;:"\'()[]{}')
    return w
def should_count(w):
    if w == "":
        return False
    if len(w) < min_len:
        return False
    return True

def analyze(content):
    global d, wc
    ws = content.split()
    for raw in ws:
        w = clean(raw)
        if not should_count(w):
            continue
        wc = wc + 1
        d[w] = d.get(w, 0) + 1

def get_sorted_items():
    return sorted(d.items(), key=lambda kv: -kv[1])

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
        for word, count in items[:TOP_N]:
            out.append("  " + word + ": " + str(count))
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
        for word, count in items[:TOP_N]:
            out.append("<li>" + word + ": " + str(count) + "</li>")
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
        for i, (word, count) in enumerate(items[:TOP_N]):
            out.append("word_" + str(i+1) + "," + word + ":" + str(count))
        out.append("longest," + get_longest())
        s = get_shortest()
        if s is not None:
            out.append("shortest," + s)
    return "\n".join(out)

def save_output(text):
    global output_file
    if output_file is not None:
        with open(output_file, 'w', encoding=ENCODING) as fh:
            fh.write(text)

def main():
    global report_format, output_file, summary_only, min_len, input_file, start_time_human, lines, chars
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
        c = read_file(f)
    lines = parse_lines(c)
    chars = len(c)
    analyze(c)
    if report_format == "html":
        text = format_html()
    elif report_format == "csv":
        text = format_csv()
    else:
        text = format_text()
    print(text)
    save_output(text)
    

if __name__ == "__main__":
    main()
