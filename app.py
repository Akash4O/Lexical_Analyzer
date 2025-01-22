from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

class Token:
    def __init__(self, token_type, value, regex, line, position):
        self.type = token_type
        self.value = value
        self.regex = regex
        self.line = line
        self.position = position

    def to_dict(self):
        return {
            "Type": self.type,
            "Value": self.value,
            "Regex": self.regex,
            "Line": self.line,
            "Position": self.position
        }

class LexicalAnalyzer:
    def __init__(self):
        self.keywords = {"if", "else", "while", "for", "int", "float", "string", "return", "void", "printf", "scanf"}
        self.token_patterns = [
            ("WHITESPACE", r"[ \t]+"),
            ("NEWLINE", r"\n"),
            ("INTEGER", r"\d+"),
            ("FLOAT", r"\d*\.\d+"),
            ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
            ("OPERATOR", r"[+\-*/=<>!]=?|&&|\|\|"),
            ("DELIMITER", r"[;,(){}\[\]]"),
            ("STRING", r'"[^"]*"'),
            ("COMMENT", r"//.*|/\*[\s\S]*?\*/")
        ]
        self.source_code = ""
        self.current_pos = 0
        self.current_line = 1
        self.current_col = 1

    def load_source(self, source_code):
        self.source_code = source_code
        self.current_pos = 0
        self.current_line = 1
        self.current_col = 1

    def get_next_token(self):
        if self.current_pos >= len(self.source_code):
            return Token("EOF", "", "", self.current_line, self.current_col)

        remaining_input = self.source_code[self.current_pos:]

        for token_type, regex in self.token_patterns:
            pattern = re.compile(rf"^{regex}")
            match = pattern.match(remaining_input)
            if match:
                value = match.group()

                if token_type == "WHITESPACE":
                    self.current_col += len(value)
                    self.current_pos += len(value)
                    return self.get_next_token()

                if token_type == "NEWLINE":
                    self.current_line += 1
                    self.current_col = 1
                    self.current_pos += len(value)
                    return self.get_next_token()

                if token_type == "COMMENT":
                    newlines = value.count("\n")
                    self.current_line += newlines
                    self.current_col = 1 if newlines else self.current_col + len(value)
                    self.current_pos += len(value)
                    return self.get_next_token()

                if token_type == "IDENTIFIER":
                    token_type = "KEYWORD" if value in self.keywords else "IDENTIFIER"

                token = Token(token_type, value, regex, self.current_line, self.current_col)
                self.current_col += len(value)
                self.current_pos += len(value)
                return token

        raise RuntimeError(f"Invalid token at line {self.current_line}, position {self.current_col}")

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            if token.type == "EOF":
                break
            tokens.append(token)
        return tokens

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    source_code = request.form.get('sourceCode', '')
    lexer = LexicalAnalyzer()
    lexer.load_source(source_code)
    try:
        tokens = lexer.tokenize()
        return jsonify({"tokens": [token.to_dict() for token in tokens]})
    except RuntimeError as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
