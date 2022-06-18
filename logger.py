from datetime import datetime

class Logger:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def info(self, message: str, style: str = ""):
        self.log(message, "INFO", style)
    
    def success(self, message: str, style: str = OKGREEN):
        self.log(message, "INFO", style)
        
    def important(self, message: str, style: str = OKBLUE):
        self.log(message, "INFO", style)

    def error(self, message: str, style: str = FAIL):
        self.log(message, "ERROR", style)

    def warning(self, message: str, style: str = WARNING):
        self.log(message, "WARNING", style)
    
    def header(self, message: str, style: str = HEADER+BOLD):
        self.log(message.upper(), "", style)

    def log(self, message: str, log_type: str, style: str = ""):
        print(f"{datetime.now()} | {style}{'['+log_type+']' if log_type!='' else ''}"
              f"{message if message.isupper() else message.capitalize()}"
              f"{self.ENDC if style!='' else ''}")


if __name__ == "__main__":
    l = Logger()
    l.header("hello world")
    l.info("info check")
    l.error("error check")
    l.warning("warning check")
    l.info("blue", l.OKBLUE)
    l.info("kek", l.OKCYAN)
    l.info("pek", l.OKGREEN)
    l.info("end", l.UNDERLINE+l.HEADER)
