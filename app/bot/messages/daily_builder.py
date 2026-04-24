from pathlib import Path
from jinja2 import Template
from logger.logger import logging
from bot.messages.symbols import symbols

messages_logger = logging.getLogger(__name__)

class DailyBuilder():
    def __init__(self, last_data):
        self.du = last_data

        # date: {'cu-d', 'cu', 'cu-3m', 'cu-st', 'ag-d', \
        # 'ag', 'au-d', 'au-am', 'au-pm'}

    def build_text_jinja(self):
        if not self.du.test_unit_is_filled():
            return ""

        m = self.du.metals
        r = self.du.rates
        p = self.du.power
        
        avrg = "n/a"
        au_am = m.get("au-am")
        au_pm = m.get("au-pm")

        if au_am is not None and au_pm is not None:
            avrg = (au_am + au_pm) / 2

        context = {
            # unpack utf8 emoji dict
            **symbols,

            # Market Data (m)
            "cu_d": m.get("cu-d", "N/A"),
            "cu": m.get("cu", "N/A"),
            "cu_3m": m.get("cu-3m", "N/A"),
            "cu_st": m.get("cu-st", "N/A"),
            "au_am": m.get("au-am", "N/A"),
            "au_pm": m.get("au-pm", "N/A"),
            "ag": m.get("ag", "N/A"),
            "avrg": avrg,

            # Rates (r)
            "r_d": r.get("d", "N/A"),
            "r_usd": r.get("USD", "N/A"),
            "r_gbp": r.get("GBP", "N/A"),
            "r_chf": r.get("CHF", "N/A"),

            # Power Data (p)
            "p_d": p.get("d", "N/A"),
            "p_eur": p.get("EUR", "N/A"),
            "p_vol": p.get("VOL", "N/A")
        }

        # 2. Load and Render
        file_path = Path(__file__).parent / "text" / "daily_msg.txt"
        with open(file_path, 'r', encoding='utf-8') as f:
            template_str = f.read()

        template = Template(template_str)
        final_text = template.render(context)

        return final_text
