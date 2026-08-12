from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
source = ASSETS / "app.png"
if not source.exists(): raise SystemExit("assets/app.png is required")
logo = Image.open(source).convert("RGBA")
logo.save(ASSETS / "app.ico", format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
def fit_logo(size):
    im=logo.copy(); im.thumbnail(size,Image.Resampling.LANCZOS); return im
splash=Image.new("RGB",(720,390),"#f5f8fb"); d=ImageDraw.Draw(splash); mark=fit_logo((150,150)); splash.paste(mark,((720-mark.width)//2,38),mark); d.text((360,220),"Forensic CV Manager",anchor="mm",fill="#1f4e79",font=ImageFont.load_default(size=28)); d.text((360,260),"Professional Portfolio Management",anchor="mm",fill="#495057",font=ImageFont.load_default(size=16)); splash.save(ASSETS/"splash.png")
small=Image.new("RGB",(55,55),"white"); sm=fit_logo((48,48)); small.paste(sm,((55-sm.width)//2,(55-sm.height)//2),sm); small.save(ASSETS/"installer_small.bmp")
wizard=Image.new("RGB",(164,314),"#f5f8fb"); wd=ImageDraw.Draw(wizard); wm=fit_logo((118,118)); wizard.paste(wm,((164-wm.width)//2,56),wm); wd.text((82,205),"Forensic CV",anchor="mm",fill="#1f4e79",font=ImageFont.load_default(size=18)); wd.text((82,229),"Manager",anchor="mm",fill="#1f4e79",font=ImageFont.load_default(size=18)); wizard.save(ASSETS/"installer_wizard.bmp")
print("Branding assets prepared.")
