def get_character_type(char):
    if char == "": return None

    if char.isdigit():
        return "digit"
    elif char.isalnum():
        return "alnum"
    elif char.strip() == "":
        return "whitespace"
    else:
        return "other"

keywords = [
    "while", 
    "for", 
    "def", 
    "fn", 
    "class", 
    "struct", 
    "self", 
    "return", 
    "function", 
    "async", 
    "await",
    "import",
    "use",
    "as",
    "in",
    "if",
    "else",
    "elif",
    "from"
]

class Token():
    def __init__(self, text=""):
        self.text = str(text)
        self.character_type = get_character_type(text)
        self.data_type = None
        self.infer_type()
    def infer_type(self):
        if self.text == None or self.text == "": return
        
        if self.text.startswith('"') and self.text.endswith('"') and len(self.text) > 1:
            self.data_type = "double_string"
        elif self.text.startswith("'") and self.text.endswith("'") and len(self.text) > 1:
            self.data_type = "single_string"
        else:
            self.data_type = get_character_type(self.text[0])
            if self.data_type == "alnum" and self.text in keywords:
                self.data_type = "keyword"

class LexicalAnalyzer():
    def __init__(self):
        self.tokens = []
        self.current_token = None
        self.in_quote = False
        self.character_type = None
        self.quote_opener = None
    def push_token(self, also=None):
        if self.current_token != None and self.current_token.text != "":
            # print(f"\t\t\tPUSH '{self.current_token.text}'")
            self.current_token.infer_type()
            self.tokens.append(self.current_token)

        if also != None:
            # print(f"\t\t\tPUSH '{also}'")
            self.tokens.append(Token(also))

        self.current_token = Token()
    def lex(self, line):
        for ci, char in enumerate(line):
            quote_maybe = (not self.in_quote) or (ci == 0 or line[ci-1] != chr(92))
            if quote_maybe and (char == '"' or char == "'"):
                if self.quote_opener == char or self.quote_opener == None:
                    self.in_quote = not self.in_quote
                    self.quote_opener = char
                if not self.in_quote:
                    self.current_token.text += char
                    self.quote_opener = None
                self.push_token()
                if self.in_quote:
                    self.current_token.text += char
                continue
            if self.in_quote:
                self.current_token.text += char
                continue
            char_type = get_character_type(char)
            res12 = self.current_token.text if self.current_token != None else 'NOTEAX'
            # print(char, char_type, f"'{res12}'")
            if self.character_type != char_type:
                self.push_token(also=char if char_type == "other" else None)
                if char_type != None and char_type != "other":
                    self.current_token.text += char
            else:
                self.current_token.text += char
                # print(self.current_token.text)
            self.character_type = char_type
        
        self.push_token()

        return self.tokens

# tokens = LexicalAnalyzer().lex("print(\"Hello, World!\")")
# for token in tokens:
#     print(token.text, token.data_type)