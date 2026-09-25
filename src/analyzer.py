"""Text analyzer: read a text file, count words, print a report.

Refactored version. All mutable state is held on an Analyzer instance;
module-level functions are limited to pure helpers.
"""
import sys
import os
import time
import csv

# ---- Constants ----
DEFAULT_MIN_LEN = 3
TOP_N = 10
ENCODING = "utf-8"
FORMAT_TEXT = "text"
FORMAT_HTML = "html"
FORMAT_CSV = "csv"
INITIAL_AVERAGE = 0


# ---- Pure helpers (no state) ----

def read_file(path):
    with open(path, 'r', encoding=ENCODING) as fh:
        return fh.read()


def parse_lines(content):
    return content.split('\n')


def clean(w):
    w = w.lower()
    w = w.strip('.,!?;:"\'()[]{}')
    return w


def should_count(w, min_len):
    if w == "":
        return False
    if len(w) < min_len:
        return False
    return True


# ---- Analyzer: all mutable state lives here ----

class Analyzer:
    def __init__(self, min_len=DEFAULT_MIN_LEN, summary_only=False):
        self.min_len = min_len
        self.summary_only = summary_only
        self.words = {}
        self.word_count = 0
        self.char_count = 0
        self.lines = []
        self.input_file = ""
        self.generated_at = ""

    def load(self, path):
        content = read_file(path)
        self.lines = parse_lines(content)
        self.char_count = len(content)
        self.input_file = path
        self.generated_at = time.ctime()
        return content

    def analyze(self, content):
        for raw in content.split():
            w = clean(raw)
            if not should_count(w, self.min_len):
                continue
            self.word_count = self.word_count + 1
            self.words[w] = self.words.get(w, 0) + 1

    def sorted_items(self):
        return sorted(self.words.items(), key=lambda kv: -kv[1])

    def avg_len(self):
        total_len = 0
        for w in self.words:
            total_len = total_len + len(w) * self.words[w]
        if self.word_count > 0:
            return total_len / self.word_count
        return INITIAL_AVERAGE

    def longest(self):
        longest = ""
        for w in self.words:
            if len(w) > len(longest):
                longest = w
        return longest

    def shortest(self):
        shortest = None
        for w in self.words:
            if shortest is None or len(w) < len(shortest):
                shortest = w
        return shortest

    def format_text(self):
        out = []
        out.append("============ REPORT ============")
        out.append("file: " + self.input_file)
        out.append("generated: " + self.generated_at)
        out.append("total chars: " + str(self.char_count))
        out.append("total lines: " + str(len(self.lines)))
        out.append("total words: " + str(self.word_count))
        out.append("unique words: " + str(len(self.words)))
        out.append("avg word length: " + str(round(self.avg_len(), 2)))
        out.append("min word length: " + str(self.min_len))
        if not self.summary_only:
            out.append("-------- TOP 10 --------")
            items = self.sorted_items()
            for word, count in items[:TOP_N]:
                out.append("  " + word + ": " + str(count))
            out.append("longest word: " + self.longest())
            s = self.shortest()
            if s is not None:
                out.append("shortest word: " + s)
        out.append("================================")
        return "\n".join(out)

    def format_html(self):
        out = []
        out.append("<html><body>")
        out.append("<h1>Report</h1>")
        out.append("<p>file: " + self.input_file + "</p>")
        out.append("<p>generated: " + self.generated_at + "</p>")
        out.append("<p>total chars: " + str(self.char_count) + "</p>")
        out.append("<p>total lines: " + str(len(self.lines)) + "</p>")
        out.append("<p>total words: " + str(self.word_count) + "</p>")
        out.append("<p>unique words: " + str(len(self.words)) + "</p>")
        out.append("<p>avg word length: " + str(round(self.avg_len(), 2)) + "</p>")
        out.append("<p>min word length: " + str(self.min_len) + "</p>")
        if not self.summary_only:
            out.append("<h2>Top 10</h2><ul>")
            items = self.sorted_items()
            for word, count in items[:TOP_N]:
                out.append("<li>" + word + ": " + str(count) + "</li>")
            out.append("</ul>")
            out.append("<p>longest word: " + self.longest() + "</p>")
            s = self.shortest()
            if s is not None:
                out.append("<p>shortest word: " + s + "</p>")
        out.append("</body></html>")
        return "\n".join(out)

    def format_csv(self):
        out = []
        out.append("metric,value")
        out.append("input_file," + self.input_file)
        out.append("generated," + self.generated_at)
        out.append("total_chars," + str(self.char_count))
        out.append("total_lines," + str(len(self.lines)))
        out.append("total_words," + str(self.word_count))
        out.append("unique_words," + str(len(self.words)))
        out.append("avg_word_length," + str(round(self.avg_len(), 2)))
        out.append("min_word_length," + str(self.min_len))
        if not self.summary_only:
            items = self.sorted_items()
            for i, (word, count) in enumerate(items[:TOP_N]):
                out.append("word_" + str(i+1) + "," + word + ":" + str(count))
            out.append("longest," + self.longest())
            s = self.shortest()
            if s is not None:
                out.append("shortest," + s)
        return "\n".join(out)


def save_output(text, output_file):
    if output_file is not None:
        with open(output_file, 'w', encoding=ENCODING) as fh:
            fh.write(text)


def main():
    if len(sys.argv) < 2:
        print("usage: analyzer.py <file> [--format text|html|csv] [--output FILE] [--summary] [--min-length N]")
        sys.exit(1)
    f = sys.argv[1]
    if not os.path.exists(f):
        print("file not found: " + f)
        sys.exit(1)

    report_format = FORMAT_TEXT
    output_file = None
    summary_only = False
    min_len = DEFAULT_MIN_LEN

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

    analyzer = Analyzer(min_len=min_len, summary_only=summary_only)
    content = analyzer.load(f)
    analyzer.analyze(content)

    if report_format == FORMAT_HTML:
        text = analyzer.format_html()
    elif report_format == FORMAT_CSV:
        text = analyzer.format_csv()
    else:
        text = analyzer.format_text()

    print(text)
    save_output(text, output_file)


if __name__ == "__main__":
    main()